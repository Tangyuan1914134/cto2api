# 网页逆向代理 API

这个项目可以将任何网页表单转换为API驱动的接口，通过创建一个反向代理服务。用户可以通过REST API提交表单输入，并实时获取目标网站的响应。

## 功能特点

- 为每个代理会话生成Base URL和API密钥
- 服务器级和会话级的安全API密钥认证
- 将API有效载荷映射到目标网页表单字段
- 支持查询参数、表单数据、JSON有效载荷和请求头注入
- 返回详细响应，包括状态码、响应头和响应体
- 易于扩展的配置

## 快速开始

### 系统要求
- Python 3.10+
- Pip 或其他Python包管理器

### 安装步骤

1. 克隆仓库
2. 创建虚拟环境：`python -m venv venv`
3. 激活虚拟环境：
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
4. 安装依赖：`pip install -r requirements.txt`
5. 复制 `.env.example` 为 `.env` 并更新您的API密钥和基础URL

### 运行项目

```bash
python app.py
```

或使用提供的脚本：
```bash
./run.sh
```

API将在 `http://localhost:5000/` 上可用。

### 使用Docker运行

```bash
docker-compose up
```

## 使用说明

### 工作流程

1. **创建会话** - 配置目标网站和字段映射
2. **获取凭证** - 系统返回 `session_id` 和 `api_key`
3. **执行请求** - 使用会话凭证发送数据到目标网站
4. **接收响应** - 获取目标网站的实时响应

### 1. 创建会话

`POST /api/v1/sessions`

请求头：
```
X-API-Key: your-master-api-key
Content-Type: application/json
```

请求体示例：
```json
{
  "name": "示例会话",
  "description": "代理到 example.com",
  "target": {
    "url": "https://httpbin.org/post",
    "method": "POST",
    "headers": {
      "User-Agent": "ProxyClient"
    }
  },
  "input_mappings": [
    {
      "input_key": "text",
      "target_field": "input",
      "transport": "form"
    }
  ]
}
```

响应：
```json
{
  "success": true,
  "session": {
    "session_id": "<会话ID>",
    "api_key": "<生成的会话API密钥>",
    "base_url": "http://localhost:5000/api/v1/sessions/<会话ID>",
    "target_url": "https://httpbin.org/post",
    "fields": [...]
  }
}
```

### 2. 执行会话（发送数据到目标网站）

`POST /api/v1/sessions/<session_id>/execute`

请求头：
```
X-API-Key: <会话API密钥>
Content-Type: application/json
```

请求体：
```json
{
  "payload": {
    "text": "你好世界"
  }
}
```

响应：
```json
{
  "success": true,
  "response": {
    "status_code": 200,
    "headers": { "Content-Type": "application/json" },
    "url": "https://httpbin.org/post",
    "elapsed_ms": 123.45,
    "body": "{...目标网站的响应...}"
  }
}
```

### 3. 列出所有会话

`GET /api/v1/sessions`

请求头：
```
X-API-Key: your-master-api-key
```

### 4. 删除会话

`DELETE /api/v1/sessions/<session_id>`

请求头：
```
X-API-Key: your-master-api-key
```

## 字段映射说明

### Transport 类型

- `form` - 作为表单数据发送 (application/x-www-form-urlencoded)
- `query` - 添加到URL查询参数
- `header` - 作为HTTP请求头发送
- `json` - 在JSON正文中发送

### 示例配置

#### 表单提交
```json
{
  "input_key": "username",
  "target_field": "user_name",
  "transport": "form"
}
```

#### 查询参数
```json
{
  "input_key": "page",
  "target_field": "page",
  "transport": "query"
}
```

#### 请求头
```json
{
  "input_key": "auth_token",
  "target_field": "Authorization",
  "transport": "header"
}
```

#### JSON负载
```json
{
  "input_key": "data",
  "target_field": "payload",
  "transport": "json"
}
```

## 使用场景

### 场景1：联系表单代理

将网站的联系表单转换为API：

```bash
# 创建会话
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "联系表单",
    "target": {
      "url": "https://example.com/contact",
      "method": "POST"
    },
    "input_mappings": [
      {
        "input_key": "name",
        "target_field": "full_name",
        "transport": "form"
      },
      {
        "input_key": "email",
        "target_field": "email_address",
        "transport": "form"
      },
      {
        "input_key": "message",
        "target_field": "message",
        "transport": "form"
      }
    ]
  }'
```

### 场景2：搜索引擎查询

将搜索查询转换为API：

```json
{
  "name": "搜索API",
  "target": {
    "url": "https://example.com/search",
    "method": "GET"
  },
  "input_mappings": [
    {
      "input_key": "query",
      "target_field": "q",
      "transport": "query"
    },
    {
      "input_key": "page",
      "target_field": "page",
      "transport": "query"
    }
  ]
}
```

### 场景3：API包装器

包装现有的复杂API：

```json
{
  "name": "API包装器",
  "target": {
    "url": "https://api.example.com/data",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer static-token"
    },
    "use_json": true
  },
  "input_mappings": [
    {
      "input_key": "data",
      "target_field": "payload",
      "transport": "json"
    },
    {
      "input_key": "user_id",
      "target_field": "X-User-ID",
      "transport": "header"
    }
  ]
}
```

## 安全性

### 双层认证

1. **主API密钥** - 用于管理会话（创建、列出、删除）
2. **会话API密钥** - 为每个会话生成，用于执行请求

### 认证方法

支持三种认证方式：
- HTTP请求头：`X-API-Key: your-key`
- Bearer令牌：`Authorization: Bearer your-key`
- 查询参数：`?api_key=your-key`

## 配置说明

### 环境变量

在 `.env` 文件中配置：

```
API_KEY=your-secret-master-api-key
BASE_URL=http://localhost:5000
TARGET_WEB_URL=https://example.com
PORT=5000
DEBUG=False
```

## 示例代码

查看 `examples/` 目录获取完整示例：

- `example_usage.py` - Python客户端示例
- `curl_examples.sh` - cURL命令示例

运行Python示例：
```bash
python examples/example_usage.py
```

运行cURL示例：
```bash
./examples/curl_examples.sh
```

## 开发和测试

### 安装开发依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python app.py
```

### 测试健康检查

```bash
curl http://localhost:5000/health
```

## 常见问题

### Q: 如何更改API密钥？
A: 在 `.env` 文件中设置 `API_KEY` 环境变量。

### Q: 可以同时创建多少个会话？
A: 没有硬性限制，但建议根据服务器资源合理创建。

### Q: 会话数据存储在哪里？
A: 目前会话存储在内存中。重启服务会丢失所有会话。

### Q: 支持HTTPS吗？
A: 支持。目标URL可以是HTTPS，代理会正确处理。

### Q: 如何处理cookies？
A: 每次请求都是独立的。如需会话管理，可在headers中传递cookies。

## 架构说明

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   客户端    │ ───> │  代理API     │ ───> │  目标网站   │
│             │      │  (本项目)    │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
     API请求            转换&转发             网页表单
```

1. 客户端使用API密钥发送请求
2. 代理API根据配置转换数据格式
3. 转发到目标网站
4. 接收响应并返回给客户端

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
