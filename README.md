# Token Dashboard

macOS 菜单栏 Token 用量监视器，统计 **pi-agent** 和 **OpenCode** 的 token 输入/输出/缓存使用量。

## 功能

- 📊 菜单栏点击弹出 Dashboard
- 🔀 切换数据源：Pi-Agent / OpenCode
- 📅 三个时间范围：今日 / 近 7 天 / 近 30 天
- 📈 按模型分组，输入、输出、缓存三条独立横条
- 🔄 每 30 秒自动刷新，支持手动刷新
- ⏻ 弹窗底部退出按钮

## 数据来源

| 工具 | 路径 | 格式 |
|------|------|------|
| Pi-Agent | `~/.pi/agent/sessions/*.jsonl` | JSONL |
| OpenCode | `~/.local/share/opencode/opencode.db` | SQLite |

## 运行

### 源码运行

```bash
git clone git@github.com:vate34/token_dash.git
cd token_dash
uv sync
bash run.sh
```

### 打包为 .app

```bash
uv run python setup.py py2app
open dist/Token\ Dash.app
```

打包产物在 `dist/Token Dash.app`，可拖入「应用程序」文件夹使用。

## 停止

点击弹窗底部 `⏻ 退出` 按钮，或终端执行：

```bash
pkill -f "Token Dash"
```

## 格式化规则

| Token 数量 | 显示 |
|-----------|------|
| < 1,000 | 直接展示（如 `847`） |
| 1,000 ~ 999,999 | K 单位，1 位小数（如 `12.3K`） |
| ≥ 1,000,000 | M 单位，1 位小数（如 `2.5M`） |

## 技术栈

- Python 3.12+ / PyObjC (AppKit + WebKit)
- 内嵌 HTML + 原生 CSS（无框架依赖）
- uv 管理依赖与打包运行
