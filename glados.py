#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GLaDOS check-in with strict outcome classification and safe diagnostics.

This integrates the publicly known, authenticated /api/user/checkin endpoint.
It deliberately does NOT forge Cloudflare tokens, CAPTCHA responses, or unknown
challenge proofs. If the site requires a newer check-in challenge, this
script reports that as an unresolved protocol change, never a fake success.
"""

import os
import sys
from typing import Dict, List, Optional, Tuple

import requests

BASE = "https://glados.cloud"
STATUS_URL = BASE + "/api/user/status"
CHECKIN_URL = BASE + "/api/user/checkin"
TIMEOUT = (8, 25)


class CheckinFailure(Exception):
    """An expected error that is safe to print in public CI logs."""


def env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "yes", "true", "on"}


def cookie_list(setting: str) -> List[str]:
    # Retain the original project's multi-account '&' convention, and also
    # accept one complete HTTP Cookie header per line. Never split on ';'.
    return [x.strip() for x in setting.replace("\r", "").replace("\n", "&").split("&") if x.strip()]


def has_new_session(cookie: str) -> bool:
    fields = [x.strip().partition("=")[0].lower() for x in cookie.split(";")]
    return "gld:sess" in fields and "gld:sess.sig" in fields


def parse_response(response: requests.Response, label: str) -> Dict:
    """Never log arbitrary response text, request headers, email or cookies."""
    code = response.status_code
    media = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
    cf = "是" if bool(response.headers.get("CF-Ray")) else "否"
    print(f"[{label}] HTTP={code}; 类型={media or '未知'}; CF-Ray响应头={cf}", flush=True)

    if media in ("text/html", "application/xhtml+xml"):
        raise CheckinFailure(f"{label}: 返回验证/网页内容（HTTP {code}），需从官网完成正常验证")
    if code in (401, 403):
        raise CheckinFailure(f"{label}: HTTP {code}，认证或访问策略拒绝；核对 Cookie、UA 和官网状态")
    if code == 429:
        raise CheckinFailure(f"{label}: HTTP 429，服务端限流；不要继续重试")
    if code >= 500:
        raise CheckinFailure(f"{label}: HTTP {code}，服务端错误；本次无法确认签到结果")
    if not 200 <= code < 300:
        raise CheckinFailure(f"{label}: HTTP {code}，请求未成功")
    try:
        value = response.json()
    except ValueError:
        raise CheckinFailure(f"{label}: 响应不是 JSON，可能发生网络验证或接口变更") from None
    if not isinstance(value, dict):
        raise CheckinFailure(f"{label}: JSON 格式不符合预期")
    return value


def status_ok(payload: Dict) -> bool:
    data = payload.get("data")
    return (isinstance(data, dict) and bool(data.get("email")) and "leftDays" in data)


def classify_checkin(payload: Dict) -> str:
    """Return a known, confirmed result or raise; never guess from code alone."""
    message = payload.get("message")
    msg = message.lower().strip() if isinstance(message, str) else ""
    reason = payload.get("reason")
    why = reason.lower().strip() if isinstance(reason, str) else ""
    code = payload.get("code")

    if "cloudflare" in msg or "verification failed" in msg or "cloudflare" in why:
        raise CheckinFailure(
            "签到接口拒绝验证：Cloudflare verification failed。"
            "当前 API 返回了业务级拒绝，不能仅凭刷新 Cookie 断定已修复；"
            "请核对官网现行 challenge/验证流程。"
        )
    if "device-mismatch" in why or "automated check-in detected" in msg:
        raise CheckinFailure(
            "设备会话校验失败（device-mismatch）；重新网页登录，"
            "并同步更新 gld:sess/gld:sess.sig 与同一浏览器的 User-Agent。"
        )
    if "challenge" in msg or "proof" in msg or "nonce" in msg:
        raise CheckinFailure(
            "签到需要新的 challenge/nonce/proof 流程；旧 token 请求不足以完成签到。"
        )
    if "today's observation logged" in msg or "checkin repeats" in msg:
        return "今日已签到（服务端确认）"
    if code == 0 and (msg.startswith("checkin!") or "checkin success" in msg or "check-in success" in msg):
        return "签到成功（服务端确认）"
    if code == 0 and ("observation logged" in msg or msg == "checkin"):
        return "签到成功（服务端确认）"
    # We intentionally reject code 0 with no recognizable success message.
    # Otherwise an unrelated successful HTTP request could become a fake check-in.
    safe_reason = why if why in {"device-mismatch", "expired", "invalid-session", "unauthorized"} else "未提供/不在已知范围"
    raise CheckinFailure(f"签到未确认：业务码={str(code)[:20]}，原因={safe_reason}；请检查官网对应记录")


def check_account(cookie: str, user_agent: str, *, session=None, diagnose_only=False) -> str:
    if not has_new_session(cookie):
        raise CheckinFailure(
            "Cookie 缺少 gld:sess 或 gld:sess.sig；请从官网登录后的 /api/user/status 请求中更新完整 Cookie"
        )
    if not user_agent:
        raise CheckinFailure("未设置 GLADOS_USER_AGENT；请填写获取 Cookie 时相同浏览器的 User-Agent")

    client = session if session is not None else requests.Session()
    client.headers.update({
        "Cookie": cookie,
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
        "Origin": BASE,
        "Referer": BASE + "/console/checkin",
    })
    # Read-only, verified session check comes first.
    status = parse_response(client.get(STATUS_URL, timeout=TIMEOUT), "状态接口")
    if not status_ok(status):
        raise CheckinFailure("状态接口没有返回有效登录信息，检查 Cookie 或登录状态")
    if diagnose_only:
        return "只读诊断通过：账号会话有效；未调用签到接口"

    # One POST only. No blind retries (the server might have recorded a check-in
    # before a connection dropped) and no unsafe fallback to other domains.
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    result = parse_response(
        client.post(CHECKIN_URL, headers=headers, json={"token": "glados.cloud"}, timeout=TIMEOUT),
        "签到接口",
    )
    return classify_checkin(result)


def notify_pushplus(token: str, title: str, content: str) -> None:
    if not token:
        return
    try:
        response = requests.post(
            "https://www.pushplus.plus/send",
            json={"token": token, "title": title, "content": content},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print("[推送] PushPlus 失败：" + type(exc).__name__, flush=True)


def main() -> int:
    cookies = cookie_list(os.environ.get("GLADOS_COOKIE", ""))
    if not cookies:
        print("配置错误：GitHub Secret GLADOS_COOKIE 未设置")
        return 1
    user_agent = os.environ.get("GLADOS_USER_AGENT", "").strip()
    diagnose = env_true("CHECKIN_DIAGNOSTIC_ONLY")
    print("运行模式：" + ("只读登录诊断" if diagnose else "正式签到"), flush=True)
    print("浏览器 User-Agent：" + ("已配置" if user_agent else "未配置"), flush=True)

    failed, reports = False, []
    for index, cookie in enumerate(cookies, 1):
        try:
            result = check_account(cookie, user_agent, diagnose_only=diagnose)
            reports.append(f"账号 {index}：{result}")
        except CheckinFailure as exc:
            failed = True
            reports.append(f"账号 {index}：失败；{exc}")
        except requests.RequestException as exc:
            failed = True
            # No raw response or URL, which could contain credentials.
            reports.append(f"账号 {index}：网络异常 {type(exc).__name__}，签到未确认")
        print(reports[-1], flush=True)

    if not diagnose:
        notify_pushplus(
            os.environ.get("PUSHPLUS_TOKEN", "").strip(),
            "GLaDOS 自动签到" + ("失败" if failed else "结果"),
            "\n".join(reports),
        )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
