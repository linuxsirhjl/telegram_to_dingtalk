# 代理配置说明

## 为什么需要代理？

Telegram 在某些地区可能无法直接连接，需要通过代理访问。

## 如何配置代理？

在 `.env` 文件中添加以下配置：

```bash
# 代理类型: socks5, http, https
PROXY_TYPE=socks5

# 代理地址
PROXY_HOST=127.0.0.1

# 代理端口
PROXY_PORT=1080

# 如果代理需要认证，填写用户名和密码；否则留空
PROXY_USERNAME=
PROXY_PASSWORD=
```

## 常见代理配置示例

### 1. Clash / ClashX

```bash
PROXY_TYPE=socks5
PROXY_HOST=127.0.0.1
PROXY_PORT=7890
PROXY_USERNAME=
PROXY_PASSWORD=
```

### 2. V2Ray / V2RayN

```bash
PROXY_TYPE=socks5
PROXY_HOST=127.0.0.1
PROXY_PORT=10808
PROXY_USERNAME=
PROXY_PASSWORD=
```

### 3. Shadowsocks

```bash
PROXY_TYPE=socks5
PROXY_HOST=127.0.0.1
PROXY_PORT=1080
PROXY_USERNAME=
PROXY_PASSWORD=
```

### 4. HTTP 代理

```bash
PROXY_TYPE=http
PROXY_HOST=127.0.0.1
PROXY_PORT=7890
PROXY_USERNAME=
PROXY_PASSWORD=
```

## 如何找到代理端口？

### Clash / ClashX
1. 打开 Clash 设置
2. 查看 "端口设置" 或 "Port Settings"
3. 找到 SOCKS5 端口（通常是 7890 或 7891）

### V2Ray / V2RayN
1. 打开 V2Ray 设置
2. 查看 "参数设置" → "本地监听端口"
3. SOCKS 端口通常是 10808

### Shadowsocks
1. 打开 Shadowsocks 设置
2. 查看 "本地 Socks5 监听端口"
3. 通常是 1080

## 测试代理是否可用

配置好代理后，运行：

```bash
python list_groups.py
```

如果看到 "✅ 使用代理: socks5://127.0.0.1:7890" 并成功连接，说明代理配置正确。

## 常见问题

### Q: 提示 TimeoutError
- 检查代理软件是否正在运行
- 检查代理端口是否正确
- 尝试更换代理类型（socks5 → http）

### Q: 提示 Connection refused
- 代理软件未启动
- 端口号错误

### Q: 不需要代理怎么办？
- 将代理配置项留空或删除即可
- 程序会自动直连 Telegram
