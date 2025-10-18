# 快速上手指南（中文版）

> 5分钟内启动并运行 Web Reverse Proxy API！

## 目录
- [步骤 1：安装项目](#步骤-1安装项目)
- [步骤 2：配置 API Key](#步骤-2配置-api-key)
- [步骤 3：启动服务](#步骤-3启动服务)
- [步骤 4：测试 API](#步骤-4测试-api)
- [步骤 5：更多示例](#步骤-5更多示例)
- [Docker 部署](#docker-部署)
- [常见问题](#常见问题)
- [下一步](#下一步)

---

## 步骤 1：安装项目

### 1.1 克隆仓库
```bash
git clone <repository-url>
cd web-reverse-proxy-api
```

### 1.2 创建虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate.bat
```

### 1.3 安装依赖
```bash
pip install -r requirements.txt
```

**依赖列表：**
- Flask 3.0.0 - Web 框架
- flask-cors - CORS 支持
- requests 2.31.0 - HTTP 客户端
- pydantic 2.5.0 - 数据验证
- python-dotenv 1.0.0 - 环境变量管理

---

## 步骤 2：配置 API Key

### 2.1 复制环境变量模板
```bash
cp .env.example .env
```

如果项目中没有 `.env.example`，可以手动创建 `.env` 文件。

### 2.2 编辑 `.env` 文件
```bash
# 使用你喜欢的编辑器打开 .env 文件
nano .env
# 或
vim .env
# 或
code .env
```

### 2.3 设置必要的环境变量
```env
# 主 API Key（必须修改）
API_KEY=my-super-secret-key-12345

# 基础 URL（可选，默认值）
BASE_URL=http://localhost:5000

# 服务端口（可选，默认值）
PORT=5000

# 调试模式（可选，生产环境请设为 False）
DEBUG=False
```

> ⚠️ **安全提示**：请将 `API_KEY` 修改为强密码，不要使用默认值！

---

## 步骤 3：启动服务

### 方式 1：直接运行（推荐）
```bash
python app.py
```

### 方式 2：使用 Flask CLI
```bash
flask --app app run --host=0.0.0.0 --port=5000
```

### 方式 3：使用启动脚本
```bash
chmod +x run.sh
./run.sh
```

**启动成功提示：**
```
 * Serving Flask app 'app'
 * Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

> 服务将在 `http://0.0.0.0:5000` 监听所有网络接口。

---

## 步骤 4：测试 API

### 4.1 健康检查（无需认证）

**命令：**
```bash
curl http://localhost:5000/health
```

**预期输出：**
```json
{
  "status": "healthy",
  "base_url": "http://localhost:5000"
}
```

✅ 如果看到以上输出，说明服务运行正常！

---

### 4.2 创建第一个会话

**命令：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-super-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的第一个会话",
    "description": "测试 httpbin.org 的 POST 接口",
    "target": {
      "url": "https://httpbin.org/post",
      "method": "POST"
    },
    "input_mappings": [
      {
        "input_key": "message",
        "target_field": "message",
        "transport": "form"
      }
    ]
  }'
```

> 注意：将 `my-super-secret-key-12345` 替换为你在 `.env` 中设置的 `API_KEY`。

**预期响应：**
```json
{
  "success": true,
  "session": {
    "session_id": "abc-123-def-456",
    "api_key": "generated-session-key-xyz789",
    "base_url": "http://localhost:5000/api/v1/sessions/abc-123-def-456",
    "target_url": "https://httpbin.org/post",
    "fields": [
      {
        "input_key": "message",
        "target_field": "message",
        "transport": "form"
      }
    ]
  }
}
```

📝 **重要：** 请记下返回的 `session_id` 和 `api_key`，接下来会用到！

---

### 4.3 执行会话（发送请求）

**命令：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session_id>/execute \
  -H "X-API-Key: <session_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "message": "你好，世界！"
    }
  }'
```

**实际示例：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/abc-123-def-456/execute \
  -H "X-API-Key: generated-session-key-xyz789" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "message": "你好，世界！"
    }
  }'
```

**预期响应：**
```json
{
  "success": true,
  "response": {
    "status_code": 200,
    "headers": {
      "Content-Type": "application/json",
      "Content-Length": "500"
    },
    "url": "https://httpbin.org/post",
    "elapsed_ms": 234.56,
    "body": "{\"args\": {}, \"data\": \"\", \"files\": {}, \"form\": {\"message\": \"你好，世界！\"}, \"headers\": {...}, \"json\": null, \"origin\": \"...\", \"url\": \"https://httpbin.org/post\"}"
  }
}
```

🎉 **恭喜！** 你已经成功通过 API 向目标网站发送了请求！

---

### 4.4 列出所有会话

**命令：**
```bash
curl http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-super-secret-key-12345"
```

**预期响应：**
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "abc-123-def-456",
      "base_url": "http://localhost:5000/api/v1/sessions/abc-123-def-456",
      "target_url": "https://httpbin.org/post",
      "created_at": "2023-01-01T10:30:00Z"
    }
  ],
  "count": 1
}
```

---

### 4.5 删除会话

**命令：**
```bash
curl -X DELETE http://localhost:5000/api/v1/sessions/<session_id> \
  -H "X-API-Key: my-super-secret-key-12345"
```

**预期响应：**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

---

## 步骤 5：更多示例

### 示例 1：GET 请求 + 查询参数

**场景：** 将搜索接口转换为 API。

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-super-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "搜索 API",
    "target": {
      "url": "https://httpbin.org/get",
      "method": "GET"
    },
    "input_mappings": [
      {
        "input_key": "keyword",
        "target_field": "q",
        "transport": "query"
      },
      {
        "input_key": "page",
        "target_field": "page",
        "transport": "query"
      }
    ]
  }'
```

**执行搜索：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session_id>/execute \
  -H "X-API-Key: <session_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "keyword": "Python",
      "page": "1"
    }
  }'
```

实际请求的 URL 将是：`https://httpbin.org/get?q=Python&page=1`

---

### 示例 2：JSON 请求体

**场景：** 向现代 REST API 发送 JSON 数据。

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-super-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "JSON API",
    "target": {
      "url": "https://httpbin.org/post",
      "method": "POST",
      "use_json": true
    },
    "input_mappings": [
      {
        "input_key": "data",
        "target_field": "data",
        "transport": "json"
      },
      {
        "input_key": "user_id",
        "target_field": "user_id",
        "transport": "json"
      }
    ]
  }'
```

**执行请求：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session_id>/execute \
  -H "X-API-Key: <session_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "data": "测试数据",
      "user_id": 12345
    }
  }'
```

---

### 示例 3：自定义 Header

**场景：** 需要传递认证 token 或其他自定义 Header。

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-super-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Header API",
    "target": {
      "url": "https://httpbin.org/post",
      "method": "POST"
    },
    "input_mappings": [
      {
        "input_key": "auth_token",
        "target_field": "Authorization",
        "transport": "header"
      },
      {
        "input_key": "data",
        "target_field": "data",
        "transport": "form"
      }
    ]
  }'
```

**执行请求：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session_id>/execute \
  -H "X-API-Key: <session_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "auth_token": "Bearer my-token-12345",
      "data": "重要数据"
    }
  }'
```

---

### 示例 4：混合传输方式

**场景：** 同时使用表单、查询参数和 Header。

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-super-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "混合传输示例",
    "target": {
      "url": "https://httpbin.org/post",
      "method": "POST"
    },
    "input_mappings": [
      {
        "input_key": "username",
        "target_field": "user",
        "transport": "form"
      },
      {
        "input_key": "page",
        "target_field": "page",
        "transport": "query"
      },
      {
        "input_key": "token",
        "target_field": "X-Auth-Token",
        "transport": "header"
      }
    ]
  }'
```

---

## Docker 部署

### 前置条件
- 已安装 Docker
- 已安装 Docker Compose

### 使用 Docker Compose 启动

```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建镜像
docker-compose up -d --build
```

### 使用 Docker 命令启动

```bash
# 构建镜像
docker build -t web-reverse-proxy-api .

# 运行容器
docker run -d \
  -p 5000:5000 \
  -e API_KEY=my-super-secret-key \
  -e BASE_URL=http://localhost:5000 \
  --name proxy-api \
  web-reverse-proxy-api

# 查看日志
docker logs -f proxy-api

# 停止容器
docker stop proxy-api

# 删除容器
docker rm proxy-api
```

---

## 常见问题

### Q: 出现 "Unauthorized" 错误
**A:** 
- 确保在请求头中正确设置了 `X-API-Key`
- 创建和管理会话需要使用**主 API Key**（`.env` 中配置的）
- 执行会话需要使用**会话 API Key**（创建会话时返回的）

### Q: 出现 "Session not found" 错误
**A:** 
- 检查 `session_id` 是否正确
- 会话存储在内存中，重启服务后会丢失
- 使用 `GET /api/v1/sessions` 查看当前所有会话

### Q: 连接被拒绝（Connection Refused）
**A:** 
- 确保 Flask 应用正在运行
- 检查端口是否被占用：`lsof -i :5000`（macOS/Linux）或 `netstat -ano | findstr :5000`（Windows）
- 尝试访问 `http://127.0.0.1:5000/health` 而不是 `localhost`

### Q: 目标网站返回 403/401 错误
**A:** 
- 目标网站可能需要特定的 Header（如 `User-Agent`）
- 在会话的 `target.headers` 中添加必要的请求头
- 某些网站可能有反爬虫机制，需要处理 Cookie 或验证码

### Q: 如何处理中文或特殊字符？
**A:** 
- 使用 UTF-8 编码
- curl 中可以使用 `--data-raw` 或 `--data-binary`
- 确保 `Content-Type: application/json` 设置正确

### Q: 会话数据会持久化吗？
**A:** 
- 当前版本会话存储在内存中
- 重启服务后所有会话会丢失
- 如需持久化，可修改 `session_manager.py` 使用 Redis 或数据库

---

## 下一步

### 📚 深入学习
- 阅读完整的 [API 文档（中文）](API_DOCUMENTATION_CN.md)
- 了解 [架构设计（中文）](ARCHITECTURE_CN.md)
- 查看 [项目 README（中文）](README_CN.md)

### 🧪 运行示例
```bash
# Python 示例
python examples/example_usage.py

# cURL 示例
chmod +x examples/curl_examples.sh
./examples/curl_examples.sh
```

### 📮 导入 Postman 集合
1. 打开 Postman
2. 点击 `Import`
3. 选择 `postman_collection.json`
4. 设置环境变量：
   - `base_url`: `http://localhost:5000`
   - `master_api_key`: 你的主 API Key
   - `session_id`: 创建会话后获得
   - `session_api_key`: 创建会话后获得

### 🚀 生产部署
- 使用 Gunicorn 或 UWSGI 作为 WSGI 服务器
- 配置 Nginx 作为反向代理
- 启用 HTTPS（使用 Let's Encrypt）
- 设置日志和监控（Sentry、ELK 等）
- 实现会话持久化（Redis、PostgreSQL 等）

### 💡 进阶技巧
- 在 `proxy_client.py` 中添加重试逻辑
- 在 `auth.py` 中实现 IP 白名单
- 添加限流（使用 Flask-Limiter）
- 实现 Webhook 回调功能
- 添加缓存层（使用 Redis）

---

## 支持与反馈

遇到问题？
- 📖 查看 [完整文档](README_CN.md)
- 🐛 提交 [Issue](https://github.com/your-repo/issues)
- 💬 参与 [Discussions](https://github.com/your-repo/discussions)
- 🤝 贡献 [Pull Request](https://github.com/your-repo/pulls)

---

## 相关资源

- [项目主页（中文）](README_CN.md)
- [API 文档（中文）](API_DOCUMENTATION_CN.md)
- [架构文档（中文）](ARCHITECTURE_CN.md)
- [English README](README.md)
- [English API Documentation](API_DOCUMENTATION.md)
- [English Quickstart](QUICKSTART.md)

---

**现在开始使用 Web Reverse Proxy API，将任何网页表单转换为强大的 API！** 🎉
