# Agent Guidelines for GLaDOS_checkin_auto | GLaDOS自动签到项目Agent指南

[English Version](#english-version) | [中文版本](#中文版本)

---

<a name="english-version"></a>
# English Version

This document defines the standards, workflows, and conventions for AI agents operating within this repository. Adhere to these guidelines to ensure consistency and functionality.

## 1. Project Overview

This repository hosts automation scripts for GLaDOS Check-in services. It is designed to run in multiple environments:
- **Local/Server:** Standalone Python execution.
- **GitHub Actions:** Scheduled daily runs via workflows.
- **Qinglong Panel:** Compatible script (`glados_Qinglong.py`) for containerized task managers.

## 2. Environment & Installation

### Requirements
- Python 3.9 or higher.
- External libraries: `requests`.

### Setup Commands
Agents should assume a fresh environment and verify dependencies.

```bash
# Install dependencies
pip install requests

# Verify installation
python3 -c "import requests; print('requests installed')"
```

### Environment Variables
The scripts rely heavily on environment variables for configuration.
- `GLADOS_COOKIE`: (Required) The user's cookie string. Multiple cookies can be separated by `&`.
- `PUSHPLUS_TOKEN`: (Optional) Token for PushPlus notifications.

## 3. Build, Test, and Lint

Since this is a script-based project, there is no formal build step.

### Running the Application
To execute the main logic:

```bash
# standard run
python3 glados.py

# qinglong panel version
python3 glados_Qinglong.py
```

### Testing
There are no formal unit tests (pytest/unittest). Verification is done by execution.
**Agent verification protocol:**
1.  **Syntax Check:** Before committing, always run a syntax check.
    ```bash
    python3 -m py_compile glados.py
    python3 -m py_compile glados_Qinglong.py
    ```
2.  **Dry Run (if applicable):** If modifying logic, simulate a run if mocked data can be injected, otherwise rely on static analysis.

### Linting
The project does not enforce strict PEP 8, but agents should ensure code validity.
- **Recommended Linter:** `flake8` (soft enforcement).
- **Critical:** Ensure no syntax errors exist.

## 4. Code Style & Conventions

**CRITICAL:** Mimic the existing coding style found in the file you are editing. Do not refactor for purely aesthetic reasons unless requested.

### Formatting
- **Indentation:** 4 spaces.
- **Line Length:** No strict limit, but keep it readable.
- **Quotes:** Single quotes `'` and double quotes `"` are used interchangeably. Follow the local context.

### Imports
- **Style:** Compact imports are common (e.g., `import requests,json,os`).
- **Guideline:** If editing an existing import line, maintain the compact style. For new modules, you may use separate lines if it improves clarity, but prefer consistency.

### Naming Conventions
- **Variables:** Predominantly **camelCase** (e.g., `sckey`, `sendContent`, `leftDays`, `checkIn`).
- **Functions:** Mixed.
    - `start()`
    - `main_handler(event, context)` (Serverless entry point pattern)
- **Constants:** No specific convention observed; often lowercase variables used as constants.

### Language & Comments
- **Language:** **Chinese (Simplified)** is used for all comments and print outputs.
- **Agent Rule:** When adding comments or logging, use Chinese to match the existing codebase.
    - Example: `print('未获取到COOKIE变量')`

### Error Handling
- **Pattern:** Explicit checks on response content rather than try/except blocks.
    - Example: `if 'message' in checkin.text:`
- **Network Calls:** Often lack timeout parameters. When adding new requests, follow existing patterns but consider adding safety if the task implies robustness.

## 5. Repository Structure

- `glados.py`: The primary script. Contains the core logic for check-in, status checking, and notification.
- `glados_Qinglong.py`: A variant of the main script adapted for the Qinglong panel environment (often structure slightly different for handlers).
- `runGladosAction.yml`: (and `.github/workflows/runGladosAction.yml`) Configuration for GitHub Actions.
    - **Schedule:** Runs at 01:30 UTC.
    - **Secrets:** Uses `${{ secrets.GLADOS_COOKIE }}` and `${{ secrets.PUSHPLUS_TOKEN }}`.

## 6. Git & Workflow Rules

- **Commit Messages:** Clear and concise. English is acceptable for commit messages unless the user prompts in Chinese.
- **Refactoring:** Do not introduce complex abstractions (classes/OOP) if the script is procedural. Keep it simple.
- **Updates:** If you update logic in `glados.py`, check if `glados_Qinglong.py` requires a similar update to maintain feature parity.

## 7. Configuration Management

**Never commit secrets.**
- If you need to test with credentials, use environment variables or a local `.env` file (ensure it is gitignored).
- The `GLADOS_COOKIE` contains sensitive session data.

## 8. Specific Logic Notes

- **Cookie Handling:** The script splits the `GLADOS_COOKIE` env var by `&` to support multiple accounts.
- **Notification:** Uses PushPlus. The URL construction is manual string concatenation.
    - `requests.get('http://www.pushplus.plus/send?token=' + ...)`
- **Check-in API:**
    - Checkin URL: `https://glados.cloud/api/user/checkin`
    - Status URL: `https://glados.cloud/api/user/status`
    - Payload: `{'token': 'glados.one'}`

---

<a name="中文版本"></a>
# 中文版本 (Chinese Version)

本文档定义了在此代码库中运行的AI Agent的标准、工作流和约定。请遵守这些准则以确保一致性和功能性。

## 1. 项目概览

此代码库包含GLaDOS签到服务的自动化脚本。它被设计为可以在多种环境中运行：
- **本地/服务器:** 独立的Python执行。
- **GitHub Actions:** 通过工作流进行每日定时运行。
- **青龙面板 (Qinglong Panel):** 兼容容器化任务管理器的脚本 (`glados_Qinglong.py`)。

## 2. 环境与安装

### 需求
- Python 3.9 或更高版本。
- 外部库: `requests`.

### 设置命令
Agent应假设是一个全新的环境并验证依赖项。

```bash
# 安装依赖
pip install requests

# 验证安装
python3 -c "import requests; print('requests installed')"
```

### 环境变量
脚本严重依赖环境变量进行配置。
- `GLADOS_COOKIE`: (必需) 用户的Cookie字符串。多个Cookie可以使用 `&` 分隔。
- `PUSHPLUS_TOKEN`: (可选) 用于PushPlus通知的Token。

## 3. 构建、测试与Lint

由于这是一个基于脚本的项目，没有正式的构建步骤。

### 运行应用
执行主要逻辑：

```bash
# 标准运行
python3 glados.py

# 青龙面板版本
python3 glados_Qinglong.py
```

### 测试
没有正式的单元测试 (pytest/unittest)。通过执行进行验证。
**Agent验证协议:**
1.  **语法检查:** 在提交之前，始终运行语法检查。
    ```bash
    python3 -m py_compile glados.py
    python3 -m py_compile glados_Qinglong.py
    ```
2.  **试运行 (如果适用):** 如果修改逻辑，在可以注入模拟数据的情况下模拟运行，否则依赖静态分析。

### Linting (代码检查)
项目不强制执行严格的 PEP 8，但Agent应确保代码有效性。
- **推荐 Linter:** `flake8` (软性执行)。
- **关键:** 确保不存在语法错误。

## 4. 代码风格与约定

**关键:** 模仿你正在编辑的文件中现有的代码风格。除非有要求，否则不要为了纯粹的美学原因进行重构。

### 格式化
- **缩进:** 4个空格。
- **行长:** 没有严格限制，但保持可读性。
- **引号:** 单引号 `'` 和双引号 `"` 可以互换使用。遵循局部上下文。

### 导入 (Imports)
- **风格:** 紧凑的导入很常见 (例如 `import requests,json,os`)。
- **准则:** 如果编辑现有的导入行，请保持紧凑风格。对于新模块，如果能提高清晰度可以使用单独的行，但首选保持一致性。

### 命名约定
- **变量:** 主要使用 **camelCase** (例如 `sckey`, `sendContent`, `leftDays`, `checkIn`)。
- **函数:** 混合使用。
    - `start()`
    - `main_handler(event, context)` (Serverless 入口点模式)
- **常量:** 没有观察到特定约定；通常使用小写变量作为常量。

### 语言与注释
- **语言:** **简体中文** 用于所有注释和打印输出。
- **Agent规则:** 添加注释或日志记录时，使用中文以匹配现有代码库。
    - 示例: `print('未获取到COOKIE变量')`

### 错误处理
- **模式:** 显式检查响应内容而不是 try/except 块。
    - 示例: `if 'message' in checkin.text:`
- **网络调用:** 通常缺少超时参数。添加新请求时，遵循现有模式，但如果任务暗示健壮性，可以考虑添加安全性。

## 5. 仓库结构

- `glados.py`: 主脚本。包含签到、状态检查和通知的核心逻辑。
- `glados_Qinglong.py`: 适应青龙面板环境的主脚本变体 (处理程序结构略有不同)。
- `runGladosAction.yml`: (以及 `.github/workflows/runGladosAction.yml`) GitHub Actions 配置。
    - **Schedule:** 在 01:30 UTC 运行。
    - **Secrets:** 使用 `${{ secrets.GLADOS_COOKIE }}` 和 `${{ secrets.PUSHPLUS_TOKEN }}`。

## 6. Git & 工作流规则

- **提交信息:** 清晰简洁。除非用户提示使用中文，否则英文用于提交信息是可以接受的。
- **重构:** 如果脚本是过程式的，不要引入复杂的抽象 (类/OOP)。保持简单。
- **更新:** 如果更新 `glados.py` 中的逻辑，请检查 `glados_Qinglong.py` 是否需要类似的更新以保持功能对等。

## 7. 配置管理

**切勿提交机密 (Secrets)。**
- 如果需要使用凭据进行测试，请使用环境变量或本地 `.env` 文件 (确保已忽略该文件)。
- `GLADOS_COOKIE` 包含敏感的会话数据。

## 8. 特定逻辑说明

- **Cookie 处理:** 脚本通过 `&` 分割 `GLADOS_COOKIE` 环境变量以支持多个账户。
- **通知:** 使用 PushPlus。URL 构建是手动字符串拼接。
    - `requests.get('http://www.pushplus.plus/send?token=' + ...)`
- **签到 API:**
    - Checkin URL: `https://glados.cloud/api/user/checkin`
    - Status URL: `https://glados.cloud/api/user/status`
    - Payload: `{'token': 'glados.one'}`

---
*Generated by opencode*
