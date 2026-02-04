# GLaDOS 自动签到 (GLaDOS Check-in Auto)

本项目用于实现 GLaDOS 服务的自动签到，支持多种运行方式（本地、GitHub Actions、青龙面板），帮助你轻松保持账号活跃。

## ✨ 特性

- 自动签到 GLaDOS 账号
- 支持多账号管理
- 支持 PushPlus 消息推送通知
- 自动查询并显示剩余天数

## 🚀 快速开始

### 1. 获取 Cookie

1. 登录 [GLaDOS 控制台](https://glados.cloud/console/checkin)。
2. 按 `F12` 打开浏览器开发者工具，切换到 **Network** (网络) 标签。
3. 点击页面上的“签到”按钮。
4. 在 Network 面板中找到名为 `checkin` 的请求。
5. 在 Request Headers (请求头) 中找到 `cookie` 字段，复制其完整内容。

> **注意:** `cookie` 包含敏感信息，请勿泄露给他人。

### 2. 配置环境变量

项目依赖以下环境变量运行，请根据你的运行环境进行配置：

| 变量名 | 必填 | 说明 |
| :--- | :--- | :--- |
| `GLADOS_COOKIE` | ✅ | 你的 GLaDOS 账号 Cookie。**多账号**请使用 `&` 符号连接，例如：`cookie1&cookie2` |
| `PUSHPLUS_TOKEN` | ❌ | (可选) [PushPlus](http://www.pushplus.plus/) 的 Token，用于接收签到结果通知 |

---

## 🛠️ 部署方式

### 方式一：GitHub Actions (推荐)

利用 GitHub 的免费计算资源进行每日自动签到。

1. **Fork 本仓库**: 点击页面右上角的 `Fork` 按钮，将项目复制到你的 GitHub 账户下。
2. **配置 Secrets**:
   - 进入你 Fork 后的仓库页面。
   - 点击 `Settings` -> `Secrets and variables` -> `Actions`。
   - 点击 `New repository secret`。
   - 添加 `GLADOS_COOKIE`，填入你的 Cookie 值。
   - (可选) 添加 `PUSHPLUS_TOKEN`，填入你的 PushPlus Token。
3. **激活 Workflow**:
   - 点击仓库上方的 `Actions` 标签。
   - 如果看到警告提示，点击 "I understand my workflows, go ahead and enable them"。
   - 可以在左侧选择 "开始每日签到"，然后点击 `Run workflow` 手动触发一次测试。
   - **重要:** 只有当你对仓库进行了一次操作（如 Star）或手动触发后，定时任务才会生效。请点击右上角的 **Star** ⭐ 以激活定时任务。

### 方式二：青龙面板 (Qinglong Panel)

适用于已有青龙面板环境的用户。

1. **添加脚本**:
   - 将项目中的 `glados_Qinglong.py` 文件内容复制并添加到青龙面板的脚本管理中。
   - 或者在订阅管理中添加本仓库地址。
2. **设置环境变量**:
   - 在“环境变量”菜单中添加 `GLADOS_COOKIE`。
3. **设置定时任务**:
   - 建议设置为每天运行一次，例如 `30 9 * * *` (每天上午9:30)。

### 方式三：本地/服务器运行

1. **克隆仓库**:
   ```bash
   git clone https://github.com/weichao/GLaDOS_checkin_auto.git
   cd GLaDOS_checkin_auto
   ```
2. **安装依赖**:
   ```bash
   pip3 install requests
   ```
3. **运行脚本**:
   ```bash
   # 设置环境变量并运行
   export GLADOS_COOKIE='你的cookie内容'
   python3 glados.py
   ```

## ❓ 常见问题

**Q: 为什么运行日志显示“未获取到COOKIE变量”？**
A: 请检查你的环境变量名称是否准确为 `GLADOS_COOKIE`，并确保内容不为空。

**Q: 如何配置多个账号？**
A: 在 `GLADOS_COOKIE` 变量中，将多个账号的完整 Cookie 字符串用 `&` 符号连接即可。

**Q: 签到失败或显示 Cookie 过期？**
A: GLaDOS 的 Cookie 可能会定期失效，请按照“获取 Cookie”步骤重新获取并更新环境变量。

## ⚠️ 免责声明

本项目仅供学习和交流使用，请勿用于非法用途。使用本脚本所产生的任何后果由使用者自行承担。
