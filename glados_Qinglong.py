import requests, json, os


def readResponse(response, label):
    if response.status_code in (401, 403):
        raise ValueError(label + "认证失败，请更新 GLADOS_COOKIE")
    if not 200 <= response.status_code < 300:
        raise ValueError(label + "请求失败，HTTP " + str(response.status_code))
    try:
        result = response.json()
    except ValueError:
        raise ValueError(label + "返回非 JSON 响应") from None
    if not isinstance(result, dict):
        raise ValueError(label + "返回格式异常")
    return result

# pushplus秘钥
sckey = os.environ.get("PUSHPLUS_TOKEN", "")
sendContent = ""
# glados账号cookie
cookies = os.environ.get("GLADOS_COOKIE", "").split("&")
if cookies[0] == "":
    print("未获取到COOKIE变量")
    cookies = []
    exit(1)


def start():
    global sendContent
    sendContent = ""
    url = "https://glados.cloud/api/user/checkin"
    url2 = "https://glados.cloud/api/user/status"
    referer = "https://glados.cloud/console/checkin"
    origin = "https://glados.cloud"
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    payload = {"token": "glados.cloud"}
    failed = False
    for account, cookie in enumerate(cookies, 1):
        email = "账号 " + str(account)
        try:
            checkin = requests.post(
                url,
                headers={
                    "cookie": cookie,
                    "referer": referer,
                    "origin": origin,
                    "user-agent": useragent,
                    "content-type": "application/json;charset=UTF-8",
                },
                data=json.dumps(payload),
                timeout=30,
            )
            checkinData = readResponse(checkin, "签到接口")
            state = requests.get(
                url2,
                headers={
                    "cookie": cookie,
                    "referer": referer,
                    "origin": origin,
                    "user-agent": useragent,
                },
                timeout=30,
            )
            stateData = readResponse(state, "状态接口")
            data = stateData.get("data")
            if not isinstance(data, dict) or "leftDays" not in data or "email" not in data:
                raise ValueError("状态接口未返回账号信息，请检查 GLADOS_COOKIE 是否失效")
            time = str(data["leftDays"]).split(".")[0]
            email = str(data["email"])
            mess = str(checkinData.get("message", "签到接口未返回结果"))
            # code=1 也可能表示当天已签到，仅认可已确认的提示。
            alreadyChecked = (
                checkinData.get("code") == 1
                and mess == "Today's observation logged. Return tomorrow for more points."
            )
            if alreadyChecked:
                mess = "今日已签到，无需重复签到"
            elif checkinData.get("code") != 0:
                failed = True
                mess = "签到失败：" + mess
            result = email + "\n----结果----\n" + mess + "\n----剩余(" + time + ")天\n"
        except (ValueError, requests.RequestException) as error:
            failed = True
            # 网络异常只输出类型，避免日志泄露请求凭据。
            reason = str(error) if isinstance(error, ValueError) else "网络请求失败：" + type(error).__name__
            result = email + "\n----结果----\n" + reason + "\n"
        print(result)
        sendContent += result
    if sckey != "":
        requests.get(
            "http://www.pushplus.plus/send?token="
            + sckey
            + ("&title=VPN签到异常" if failed else "&title=VPN签到成功")
            + "&content="
            + sendContent
        )
    if failed:
        raise SystemExit(1)


def main_handler(event, context):
    return start()


if __name__ == "__main__":
    start()
