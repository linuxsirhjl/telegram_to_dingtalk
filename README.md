# Telegram 到钉钉消息转发工具

自动转发Telegram 公开群组的消息转发到钉钉群。

## 功能特性

- ✅ 监控多个 Telegram 公开群组
- ✅ 自动转发新消息到钉钉
- ✅ 支持文本、图片等多种消息类型
- ✅ 消息去重，避免重复推送
- ✅ 支持钉钉加签安全设置
- ✅ 断点续传，程序重启后不会重复推送历史消息

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 获取 Telegram API 凭证

1. 访问 https://my.telegram.org
2. 登录你的 Telegram 账号
3. 点击 "API development tools"
4. 创建一个新应用，获取 `api_id` 和 `api_hash`

### 3. 获取钉钉 Webhook

1. 打开钉钉群，点击右上角设置
2. 选择"智能群助手" → "添加机器人" → "自定义"
3. 设置机器人名称和安全设置：
   - **推荐使用"加签"方式**：勾选"加签"，复制密钥（Secret）
   - 或使用"自定义关键词"：添加关键词（如"Telegram"）
4. 复制 Webhook URL

### 4. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写以下配置：

```bash
# ==================== Telegram 配置 ====================
# 从 https://my.telegram.org 获取
TELEGRAM_API_ID=12345678                    # 替换为你的 API ID
TELEGRAM_API_HASH=abcdef1234567890abcdef   # 替换为你的 API Hash
TELEGRAM_PHONE=+8613800138000              # 替换为你的手机号（带国际区号）

# ==================== 钉钉配置 ====================
# 从钉钉群机器人设置中获取
DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxxxx  # 替换为你的 Webhook

# 如果使用了"加签"安全设置，填写密钥；否则留空
DINGTALK_SECRET=SECxxxxxxxxxxxxxxxxxxxx    # 替换为你的加签密钥（可选）

# ==================== 监控群组配置 ====================
# 可以是群组用户名（如 @groupname）或群组 ID（数字）
# 多个群组用逗号分隔
TELEGRAM_GROUPS=@your_group_name           # 替换为你要监控的群组

# 检查间隔（秒），默认 60 秒
CHECK_INTERVAL=60
```

### 5. 运行程序

```bash
python main.py
```

首次运行时，会要求你输入 Telegram 验证码进行登录。

## 配置说明

### 必填配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `TELEGRAM_API_ID` | Telegram API ID | `12345678` |
| `TELEGRAM_API_HASH` | Telegram API Hash | `abcdef1234567890` |
| `TELEGRAM_PHONE` | 你的手机号（带国际区号） | `+8613800138000` |
| `DINGTALK_WEBHOOK` | 钉钉机器人 Webhook URL | `https://oapi.dingtalk.com/robot/send?access_token=xxx` |
| `TELEGRAM_GROUPS` | 要监控的群组列表 | `@group1,@group2` |

### 可选配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DINGTALK_SECRET` | 钉钉加签密钥（推荐配置） | 空 |
| `CHECK_INTERVAL` | 检查新消息的间隔（秒） | `60` |

## 如何找到 Telegram 群组标识

### 方法 1：使用群组用户名（推荐）

如果群组是公开的，可以直接使用 `@username` 格式：

```bash
TELEGRAM_GROUPS=@python_group,@tech_news
```

### 方法 2：使用群组 ID

1. 将机器人 [@userinfobot](https://t.me/userinfobot) 添加到群组
2. 机器人会显示群组 ID（负数，如 `-1001234567890`）
3. 使用该 ID：

```bash
TELEGRAM_GROUPS=-1001234567890,-1009876543210
```

## 钉钉安全设置说明

钉钉机器人提供三种安全设置方式：

### 方式1：加签（推荐）✅

- 最安全的方式
- 在钉钉机器人设置中勾选"加签"，复制密钥
- 将密钥填入 `.env` 文件的 `DINGTALK_SECRET`
- 程序会自动生成签名

### 方式2：自定义关键词 ✅

- 在钉钉机器人设置中选择"自定义关键词"
- **添加关键词：`Telegram`**（必须是这个词）
- 程序发送的所有消息都会自动包含"Telegram"关键词
- `.env` 文件中 `DINGTALK_SECRET` 留空即可

### 方式3：IP 地址

- 仅允许指定 IP 访问
- 适合固定 IP 的服务器
- 不需要额外配置

**重要提示**：程序已经在所有消息中自动包含"Telegram"关键词，所以如果你使用"自定义关键词"方式，请务必在钉钉机器人设置中添加关键词"Telegram"。

## 注意事项

1. **首次运行**：需要输入 Telegram 验证码登录，之后会保存 session
2. **群组权限**：只能监控你已加入的公开群组
3. **消息去重**：程序会记录已处理的消息 ID，避免重复推送
4. **状态保存**：消息处理状态保存在 `last_state.json`，删除此文件会重新推送历史消息
5. **API 限制**：Telegram API 有速率限制，建议 `CHECK_INTERVAL` 不要设置太小

## 目录结构

```
telegram_to_dingtalk/
├── config/
│   └── settings.py          # 配置管理
├── core/
│   ├── telegram_client.py   # Telegram 客户端
│   ├── notifier.py          # 钉钉通知
│   ├── storage.py           # 状态存储
│   └── message_formatter.py # 消息格式化
├── main.py                  # 主程序
├── requirements.txt         # 依赖列表
├── .env.example            # 配置示例
└── README.md               # 说明文档
```

## 常见问题

### Q: 如何停止程序？

按 `Ctrl+C` 即可优雅退出。

### Q: 程序重启后会重复推送历史消息吗？

不会。程序会保存已处理的消息 ID，重启后会跳过这些消息。

### Q: 可以监控私有群组吗？

可以，但需要你的账号已加入该群组。使用群组 ID 而不是用户名。

### Q: 钉钉提示"签名不匹配"？

检查 `DINGTALK_SECRET` 是否正确，确保复制了完整的密钥（包括 `SEC` 前缀）。

### Q: 如何查看日志？

程序会在控制台输出详细日志，包括消息处理状态和错误信息。

## 许可证

MIT License
