# API 文档（中文版）

## 基础信息

### 基础 URL
`http://localhost:5000` （可在 `.env` 文件中修改 `BASE_URL` 配置）

### API 版本
`v1`

所有 API 路径都以 `/api/v1` 作为前缀。

## 认证机制

### 主 API Key（Master API Key）
用于管理会话的创建、查询、删除等操作。

**支持的认证方式：**
- **HTTP Header**：`X-API-Key: your-master-api-key`
- **Authorization Header**：`Authorization: Bearer your-master-api-key`
- **查询参数**：`?api_key=your-master-api-key`

> 主 API Key 在 `.env` 文件中通过 `API_KEY` 环境变量配置。

### 会话 API Key（Session API Key）
用于执行特定会话的请求。每个会话在创建时会生成唯一的 API Key。

**支持的认证方式：**
- **HTTP Header**：`X-API-Key: session-api-key`
- **Authorization Header**：`Authorization: Bearer session-api-key`

> 会话 API Key 只能在创建会话时获取一次，请妥善保存。

## API Endpoints

### 1. 健康检查

**请求：**
```
GET /health
```

**说明：**  
检查服务是否正常运行。

**认证：** 无需认证

**响应示例：**
```json
{
  "status": "healthy",
  "base_url": "http://localhost:5000"
}
```

**HTTP 状态码：** `200 OK`

---

### 2. 获取 API 信息

**请求：**
```
GET /api/v1/info
```

**说明：**  
获取 API 版本、基础 URL 和可用的 Endpoint 列表。

**认证：** 主 API Key

**请求头：**
```
X-API-Key: your-master-api-key
```

**响应示例：**
```json
{
  "base_url": "http://localhost:5000",
  "api_version": "v1",
  "endpoints": {
    "create_session": "http://localhost:5000/api/v1/sessions",
    "list_sessions": "http://localhost:5000/api/v1/sessions",
    "execute": "http://localhost:5000/api/v1/sessions/<session_id>/execute",
    "delete_session": "http://localhost:5000/api/v1/sessions/<session_id>"
  }
}
```

**HTTP 状态码：** `200 OK`

---

### 3. 创建会话

**请求：**
```
POST /api/v1/sessions
```

**说明：**  
创建一个新的代理会话，配置目标 URL 和字段映射关系。

**认证：** 主 API Key

**请求头：**
```
X-API-Key: your-master-api-key
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "会话名称",
  "description": "可选的描述信息",
  "target": {
    "url": "https://example.com/form",
    "method": "POST",
    "headers": {
      "Custom-Header": "value"
    },
    "query_parameters": {
      "param1": "value1"
    },
    "use_json": false
  },
  "input_mappings": [
    {
      "input_key": "api_field_name",
      "target_field": "web_form_field_name",
      "transport": "form"
    }
  ]
}
```

**请求体字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | string | 是 | 会话的可读名称 |
| `description` | string | 否 | 会话描述 |
| `target.url` | string | 是 | 目标网站的 URL |
| `target.method` | string | 否 | HTTP 方法（GET、POST、PUT、DELETE、PATCH），默认 POST |
| `target.headers` | object | 否 | 发送给目标站点的自定义 HTTP 请求头 |
| `target.query_parameters` | object | 否 | 静态查询参数 |
| `target.use_json` | boolean | 否 | 是否以 JSON 格式发送，默认 false |
| `input_mappings` | array | 是 | 字段映射配置列表 |
| `input_mappings[].input_key` | string | 是 | API 请求中的字段名 |
| `input_mappings[].target_field` | string | 是 | 目标网站中的字段名 |
| `input_mappings[].transport` | string | 是 | 传输方式：`form`、`query`、`header`、`json` |

**传输方式（Transport）说明：**

| 值 | 描述 | Content-Type |
| --- | --- | --- |
| `form` | 作为表单数据发送 | `application/x-www-form-urlencoded` |
| `query` | 添加到 URL 查询参数 | - |
| `header` | 作为 HTTP 请求头发送 | - |
| `json` | 在 JSON 请求体中发送 | `application/json` |

**响应示例：**
```json
{
  "success": true,
  "session": {
    "session_id": "abc-123-def-456",
    "api_key": "generated-session-api-key",
    "base_url": "http://localhost:5000/api/v1/sessions/abc-123-def-456",
    "target_url": "https://example.com/form",
    "fields": [
      {
        "input_key": "api_field_name",
        "target_field": "web_form_field_name",
        "transport": "form"
      }
    ]
  }
}
```

**HTTP 状态码：**
- `201 Created` - 成功创建
- `400 Bad Request` - 请求体验证失败
- `401 Unauthorized` - 认证失败
- `500 Internal Server Error` - 服务器错误

---

### 4. 列出所有会话

**请求：**
```
GET /api/v1/sessions
```

**说明：**  
获取当前所有已创建的会话列表。

**认证：** 主 API Key

**请求头：**
```
X-API-Key: your-master-api-key
```

**响应示例：**
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "abc-123",
      "base_url": "http://localhost:5000/api/v1/sessions/abc-123",
      "target_url": "https://example.com",
      "created_at": "2023-01-01T00:00:00Z"
    },
    {
      "session_id": "def-456",
      "base_url": "http://localhost:5000/api/v1/sessions/def-456",
      "target_url": "https://httpbin.org/post",
      "created_at": "2023-01-02T10:30:00Z"
    }
  ],
  "count": 2
}
```

**HTTP 状态码：**
- `200 OK` - 成功
- `401 Unauthorized` - 认证失败

---

### 5. 获取会话详情

**请求：**
```
GET /api/v1/sessions/<session_id>
```

**说明：**  
获取指定会话的详细配置信息。

**认证：** 主 API Key

**路径参数：**
- `session_id` - 会话唯一标识符

**请求头：**
```
X-API-Key: your-master-api-key
```

**响应示例：**
```json
{
  "success": true,
  "session": {
    "session_id": "abc-123",
    "base_url": "http://localhost:5000/api/v1/sessions/abc-123",
    "target_url": "https://example.com",
    "created_at": "2023-01-01T00:00:00Z",
    "fields": [
      {
        "input_key": "name",
        "target_field": "full_name",
        "transport": "form"
      },
      {
        "input_key": "email",
        "target_field": "email_address",
        "transport": "form"
      }
    ]
  }
}
```

**HTTP 状态码：**
- `200 OK` - 成功
- `401 Unauthorized` - 认证失败
- `404 Not Found` - 会话不存在

---

### 6. 执行会话（核心功能）

**请求：**
```
POST /api/v1/sessions/<session_id>/execute
```

**说明：**  
使用指定会话的配置向目标网站发送请求。

**认证：** 会话 API Key

**路径参数：**
- `session_id` - 会话唯一标识符

**请求头：**
```
X-API-Key: session-api-key
Content-Type: application/json
```

**请求体：**
```json
{
  "payload": {
    "field1": "value1",
    "field2": "value2"
  },
  "extra_headers": {
    "Custom-Header": "value"
  },
  "query_parameters": {
    "param": "value"
  }
}
```

**请求体字段说明：**

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `payload` | object | 是 | 要发送的数据，键名必须与 `input_mappings` 中的 `input_key` 对应 |
| `extra_headers` | object | 否 | 额外的 HTTP 请求头，会与会话配置合并 |
| `query_parameters` | object | 否 | 额外的查询参数，会与会话配置合并 |

**响应示例：**
```json
{
  "success": true,
  "response": {
    "status_code": 200,
    "headers": {
      "content-type": "application/json",
      "server": "nginx"
    },
    "url": "https://example.com/form",
    "elapsed_ms": 234.56,
    "body": "{\"result\": \"success\", \"message\": \"Data received\"}"
  }
}
```

**响应字段说明：**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `success` | boolean | 是否成功执行 |
| `response.status_code` | integer | 目标网站返回的 HTTP 状态码 |
| `response.headers` | object | 目标网站返回的响应头 |
| `response.url` | string | 实际请求的完整 URL |
| `response.elapsed_ms` | float | 请求耗时（毫秒） |
| `response.body` | string | 目标网站返回的原始响应体 |

**HTTP 状态码：**
- `200 OK` - 成功执行
- `400 Bad Request` - 请求体验证失败
- `401 Unauthorized` - 认证失败
- `404 Not Found` - 会话不存在
- `500 Internal Server Error` - 执行过程中发生错误

---

### 7. 删除会话

**请求：**
```
DELETE /api/v1/sessions/<session_id>
```

**说明：**  
删除指定的会话。

**认证：** 主 API Key

**路径参数：**
- `session_id` - 会话唯一标识符

**请求头：**
```
X-API-Key: your-master-api-key
```

**响应示例：**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

**HTTP 状态码：**
- `200 OK` - 成功删除
- `401 Unauthorized` - 认证失败
- `404 Not Found` - 会话不存在

---

## 使用示例

### 示例 1：简单表单代理

**场景：** 将网站的联系表单转换为 API。

**步骤 1：创建会话**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: your-master-api-key" \
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

**步骤 2：执行请求**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session-id>/execute \
  -H "X-API-Key: <session-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "name": "张三",
      "email": "zhangsan@example.com",
      "message": "你好，我对你们的产品很感兴趣。"
    }
  }'
```

---

### 示例 2：GET 请求与查询参数

**场景：** 将搜索接口转换为 API。

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: your-master-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "搜索 API",
    "target": {
      "url": "https://example.com/search",
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

执行搜索：
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session-id>/execute \
  -H "X-API-Key: <session-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "keyword": "Python",
      "page": "1"
    }
  }'
```

实际请求的 URL 将是：`https://example.com/search?q=Python&page=1`

---

### 示例 3：JSON API 与自定义 Header

**场景：** 包装一个需要认证的 REST API。

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: your-master-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API 包装器",
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
  }'
```

执行请求：
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session-id>/execute \
  -H "X-API-Key: <session-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "data": {"key": "value"},
      "user_id": "12345"
    }
  }'
```

实际发送到目标的请求：
- URL: `https://api.example.com/data`
- Method: `POST`
- Headers: 
  - `Authorization: Bearer static-token`
  - `X-User-ID: 12345`
  - `Content-Type: application/json`
- Body: `{"payload": {"key": "value"}}`

---

### 示例 4：混合传输方式

**场景：** 同时使用表单、查询参数和 Header。

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: your-master-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "混合传输",
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

## 错误响应格式

所有 API 错误响应都遵循统一的格式：

```json
{
  "success": false,
  "error": "错误类型",
  "message": "可选的详细错误描述",
  "details": {}
}
```

### 常见 HTTP 状态码

| 状态码 | 说明 |
| --- | --- |
| `200 OK` | 请求成功 |
| `201 Created` | 资源创建成功 |
| `400 Bad Request` | 请求参数验证失败 |
| `401 Unauthorized` | 认证失败或 API Key 无效 |
| `404 Not Found` | 资源不存在（如会话未找到） |
| `500 Internal Server Error` | 服务器内部错误 |

### 错误示例

**认证失败：**
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Invalid or missing API key"
}
```

**会话不存在：**
```json
{
  "success": false,
  "error": "Session not found"
}
```

**请求体验证错误：**
```json
{
  "success": false,
  "error": "Validation error",
  "details": [
    {
      "loc": ["body", "target", "url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 最佳实践

### 1. 安全性
- 生产环境必须使用 HTTPS
- 定期轮换主 API Key
- 为不同用途创建独立的会话
- 将 API Key 存储在环境变量中，避免硬编码

### 2. 性能优化
- 复用会话而非频繁创建新会话
- 根据目标站点的限流策略合理控制请求频率
- 对于长期使用的配置，可考虑将会话 ID 持久化存储

### 3. 错误处理
- 始终检查 `success` 字段判断请求是否成功
- 处理目标站点的各种 HTTP 状态码
- 记录 `elapsed_ms` 用于性能监控
- 解析 `response.body` 时注意内容类型

### 4. 调试技巧
- 使用 `response.url` 查看实际请求的 URL
- 检查 `response.headers` 了解目标站点的响应信息
- 启用服务端的 DEBUG 模式查看详细日志
- 使用 Postman 或类似工具导入 `postman_collection.json` 快速测试

---

## 附录

### A. 完整字段映射参考

| transport | 数据去向 | 示例 |
| --- | --- | --- |
| `form` | 表单数据（body） | `name=value` |
| `json` | JSON 请求体（body） | `{"name": "value"}` |
| `query` | URL 查询参数 | `?name=value` |
| `header` | HTTP 请求头 | `X-Custom-Name: value` |

### B. 支持的 HTTP 方法
- GET
- POST
- PUT
- DELETE
- PATCH

### C. Postman 集合
项目提供了完整的 Postman 集合文件：`postman_collection.json`，可直接导入到 Postman 中使用，包含所有 API 端点的示例请求。

### D. 相关资源
- [项目主页（中文）](README_CN.md)
- [快速开始指南（中文）](QUICKSTART_CN.md)
- [架构文档（中文）](ARCHITECTURE_CN.md)
- [英文 API 文档](API_DOCUMENTATION.md)

---

## 更新日志

**版本：v1**
- 初始版本发布
- 支持基础会话管理
- 支持四种传输方式（form、json、query、header）
- 双重认证机制
- 完整的响应信息返回

---

如有问题或建议，欢迎提交 Issue 或 Pull Request。
