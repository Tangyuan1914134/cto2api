# 网页逆向代理 API（Web Reverse Proxy API）

> Web Reverse Proxy API 将传统网页表单转换为标准化的 RESTful API，使您可以通过编程方式操控任意网站的表单、搜索或数据接口，无需编写爬虫或手动交互。

## 目录
- [1. 项目概览](#1-项目概览)
  - [1.1 解决的问题](#11-解决的问题)
  - [1.2 核心功能亮点](#12-核心功能亮点)
- [2. 典型使用场景](#2-典型使用场景)
  - [2.1 联系表单 API 化](#21-联系表单-api-化)
  - [2.2 搜索/查询自动化](#22-搜索查询自动化)
  - [2.3 包装现有 API 或内部系统](#23-包装现有-api-或内部系统)
- [3. 架构总览](#3-架构总览)
  - [3.1 架构图](#31-架构图)
  - [3.2 核心组件说明](#32-核心组件说明)
  - [3.3 数据流与生命周期](#33-数据流与生命周期)
- [4. 快速开始](#4-快速开始)
  - [4.1 环境要求](#41-环境要求)
  - [4.2 本地运行步骤](#42-本地运行步骤)
  - [4.3 使用 Docker 运行](#43-使用-docker-运行)
  - [4.4 基础验证](#44-基础验证)
- [5. 核心概念](#5-核心概念)
  - [5.1 会话（Session）模型](#51-会话session模型)
  - [5.2 输入映射（Input Mapping）](#52-输入映射input-mapping)
  - [5.3 安全与认证机制](#53-安全与认证机制)
- [6. API 使用指南](#6-api-使用指南)
  - [6.1 认证方式](#61-认证方式)
  - [6.2 Endpoint 速查表](#62-endpoint-速查表)
  - [6.3 完整工作流示例](#63-完整工作流示例)
  - [6.4 扩展参数与响应格式](#64-扩展参数与响应格式)
- [7. 配置与部署](#7-配置与部署)
  - [7.1 环境变量](#71-环境变量)
  - [7.2 生产部署建议](#72-生产部署建议)
- [8. 项目结构](#8-项目结构)
- [9. 开发与测试指南](#9-开发与测试指南)
- [10. 常见问题（FAQ）](#10-常见问题faq)
- [11. 未来规划（Roadmap）](#11-未来规划roadmap)
- [12. 贡献指南与许可证](#12-贡献指南与许可证)
  - [12.1 贡献流程](#121-贡献流程)
  - [12.2 许可证](#122-许可证)
- [13. 相关资源](#13-相关资源)

## 1. 项目概览

### 1.1 解决的问题
- 将只能人工提交的网页表单转换为可编程的接口，方便自动化流程接入。
- 避免编写复杂的爬虫或手动解析 HTML，只需配置映射关系即可转发请求。
- 统一管理认证、重试、日志等通用逻辑，让团队可以快速构建“网站→API”层。
- 便于在旧系统上方搭建现代化的服务层，实现系统集成或低代码场景。

### 1.2 核心功能亮点
- 🔐 **双重认证**：主 API Key 管理会话，会话级 API Key 执行请求，确保安全性。
- 🔀 **灵活的字段映射**：支持表单（form）、查询参数（query）、请求头（header）、JSON 等多种传输方式。
- ⚙️ **高度可配置**：目标 URL、HTTP Method、静态 Header/Query 参数均可通过配置完成。
- 📦 **完整响应信息**：返回状态码、响应头、耗时、原始响应体，便于后续处理。
- 🚀 **轻量易用**：基于 Flask 构建，开箱即用；提供示例脚本、Postman 集合和 Docker 支持。
- 🔁 **会话生命周期管理**：创建、查询、删除全流程 API，方便集成到现有系统。
- 🧩 **易扩展**：清晰的架构拆分，可扩展存储、认证、日志等能力。

## 2. 典型使用场景

### 2.1 联系表单 API 化
将网站上的“联系我们”表单转成 API，供移动端、小程序或自动化流程调用。

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: your-master-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "联系表单代理",
    "target": {
      "url": "https://example.com/contact",
      "method": "POST"
    },
    "input_mappings": [
      { "input_key": "name", "target_field": "full_name", "transport": "form" },
      { "input_key": "email", "target_field": "email_address", "transport": "form" },
      { "input_key": "message", "target_field": "message", "transport": "form" }
    ]
  }'
```

### 2.2 搜索/查询自动化
将搜索页或筛选页封装为 API，向内部系统暴露统一的数据查询能力。

```json
{
  "name": "搜索 API",
  "target": {
    "url": "https://example.com/search",
    "method": "GET"
  },
  "input_mappings": [
    { "input_key": "keyword", "target_field": "q", "transport": "query" },
    { "input_key": "page", "target_field": "page", "transport": "query" }
  ]
}
```

### 2.3 包装现有 API 或内部系统
对复杂或历史遗留 API 进行二次封装，隐藏复杂细节，输出干净易用的接口。

```json
{
  "name": "内部系统包装",
  "target": {
    "url": "https://api.legacy-system.local/v1/data",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer static-token"
    },
    "use_json": true
  },
  "input_mappings": [
    { "input_key": "payload", "target_field": "data", "transport": "json" },
    { "input_key": "user_token", "target_field": "X-User-Token", "transport": "header" }
  ]
}
```

## 3. 架构总览

### 3.1 架构图
```
┌──────────────────────────────────────────────────────────────────┐
│                         客户端应用（API调用方）                   │
│                  （Web、移动端、自动化脚本等）                   │
└───────────────────────────┬──────────────────────────────────────┘
                            │ REST API 请求
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                       Web Reverse Proxy API                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   Flask 应用（app.py）                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │ 认证模块     │  │ 会话管理器   │  │ 代理客户端     │  │  │
│  │  │ (auth.py)    │  │ (session_...)│  │ (proxy_client) │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTP 请求
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                         目标网站/服务端                          │
│                 （任意 HTTP / HTTPS 终端）                       │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 核心组件说明
- **app.py**：Flask 主入口，定义路由、处理请求与错误。
- **auth.py**：主 API Key 与会话 API Key 校验逻辑。
- **session_manager.py**：会话创建、查询、删除与内存存储。
- **proxy_client.py**：字段映射、请求构造与实际 HTTP 调用。
- **models.py**：使用 Pydantic 定义请求与响应的数据模型。
- **config.py**：环境变量读取与基础配置校验。
- **utils.py**：通用工具函数，比如随机生成 API Key。

### 3.3 数据流与生命周期
**会话创建流程：**
1. 客户端携带主 API Key 调用 `POST /api/v1/sessions`。
2. 认证模块校验主 API Key。
3. Pydantic 校验请求体参数。
4. SessionManager 生成 `session_id` 与会话级 `api_key`。
5. 会话配置存储在内存中，返回给调用方。

**执行请求流程：**
1. 客户端携带会话 API Key 调用 `POST /api/v1/sessions/<session_id>/execute`。
2. 系统校验会话 API Key。
3. SessionManager 读取会话配置。
4. ProxyClient 根据输入映射转换数据并构造目标请求。
5. 发送请求到目标网站，收集响应信息。
6. 返回统一格式的响应给客户端。

## 4. 快速开始

### 4.1 环境要求
- Python 3.10 及以上版本。
- pip 或其他 Python 包管理工具。
- 推荐使用虚拟环境（`venv`、`conda` 等）。
- 可选：Docker / Docker Compose（用于容器化部署）。

### 4.2 本地运行步骤
1. **克隆仓库并进入项目目录**
   ```bash
   git clone <repository-url>
   cd web-reverse-proxy-api
   ```
2. **创建并激活虚拟环境**
   ```bash
   python -m venv venv
   # macOS/Linux
   source venv/bin/activate
   # Windows (PowerShell)
   venv\Scripts\Activate.ps1
   ```
3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env，至少设置 API_KEY
   ```
5. **启动服务**
   - 方式一：`python app.py`
   - 方式二：`flask --app app run --host=0.0.0.0 --port=5000`

应用默认监听 `http://0.0.0.0:5000`。

### 4.3 使用 Docker 运行
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```
> 在 Docker 模式下，同样需要通过环境变量或 `.env` 文件设置主 API Key。

### 4.4 基础验证
1. **健康检查**
   ```bash
   curl http://localhost:5000/health
   ```
   期望输出：
   ```json
   { "status": "healthy", "base_url": "http://localhost:5000" }
   ```

2. **获取 API 信息**
   ```bash
   curl http://localhost:5000/api/v1/info \
     -H "X-API-Key: your-master-api-key"
   ```

3. **创建首个会话**
   ```bash
   curl -X POST http://localhost:5000/api/v1/sessions \
     -H "X-API-Key: your-master-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Hello Session",
       "target": { "url": "https://httpbin.org/post", "method": "POST" },
       "input_mappings": [
         { "input_key": "message", "target_field": "message", "transport": "form" }
       ]
     }'
   ```
   返回结果中包含 `session_id` 与 `api_key`，请妥善保存。

## 5. 核心概念

### 5.1 会话（Session）模型
每个会话描述一次目标网站的请求配置以及字段映射，结构如下：

```python
Session {
    session_id: str,
    api_key: str,
    request_model: {
        name: str,
        description: str | None,
        target: {
            url: HttpUrl,
            method: str,
            headers: dict,
            query_parameters: dict,
            use_json: bool
        },
        input_mappings: [
            {
                input_key: str,
                target_field: str,
                transport: str
            }
        ]
    },
    created_at: datetime,
    updated_at: datetime
}
```

- `session_id`：会话唯一标识。
- `api_key`：用于执行会话的密钥，仅在创建会话时返回一次。
- `target`：定义目标网站地址、HTTP 方法及静态 Header/Query 参数。
- `input_mappings`：描述输入数据如何转换至目标请求。
- `created_at / updated_at`：会话的时间戳，便于追踪与审计。

### 5.2 输入映射（Input Mapping）
| `transport` 值 | 描述 | 常见场景 |
| --- | --- | --- |
| `form` | 作为 `application/x-www-form-urlencoded` 提交 | 普通 HTML 表单 |
| `json` | 放入 JSON 请求体 | 现代 REST API |
| `query` | 添加到 URL 查询参数 | 搜索、分页、筛选 |
| `header` | 设置为 HTTP 请求头 | 认证信息、追踪 ID |

> 可以在同一个会话中混合多种传输方式，例如同时传递表单字段与自定义 Header。

### 5.3 安全与认证机制
- **主 API Key**：用于会话管理（创建、查询、删除）。在 `.env` 中设置 `API_KEY`。
- **会话 API Key**：每个会话独有，用于执行 `execute` 请求。
- **认证方式**：支持 `X-API-Key` Header、`Authorization: Bearer`、URL `api_key` 查询参数。
- **最佳实践**：
  - 生产环境必须使用 HTTPS。
  - 定期轮换主 API Key。
  - 不要将 `.env` 文件提交到版本控制。
  - 如需更高安全性，可在 `auth.py` 中扩展 IP 白名单、限流等策略。

## 6. API 使用指南

### 6.1 认证方式
1. Header：`X-API-Key: <your-api-key>`
2. Authorization Header：`Authorization: Bearer <your-api-key>`
3. 查询参数：`?api_key=<your-api-key>`

### 6.2 Endpoint 速查表
| HTTP 方法 | 路径 | 说明 | 认证 |
| --- | --- | --- | --- |
| GET | `/health` | 健康检查 | 不需要 |
| GET | `/api/v1/info` | 获取 API 基本信息 | 主 API Key |
| POST | `/api/v1/sessions` | 创建会话 | 主 API Key |
| GET | `/api/v1/sessions` | 列出所有会话 | 主 API Key |
| GET | `/api/v1/sessions/<session_id>` | 查看会话详情 | 主 API Key |
| POST | `/api/v1/sessions/<session_id>/execute` | 执行会话请求 | 会话 API Key |
| DELETE | `/api/v1/sessions/<session_id>` | 删除会话 | 主 API Key |

所有成功响应包含 `success: true`，失败时返回 `success: false` 和错误信息。

### 6.3 完整工作流示例
**步骤 1：创建会话**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: your-master-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Session",
    "description": "代理到 httpbin.org",
    "target": {
      "url": "https://httpbin.org/post",
      "method": "POST"
    },
    "input_mappings": [
      { "input_key": "text", "target_field": "input", "transport": "form" }
    ]
  }'
```

**步骤 2：执行会话**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session-id>/execute \
  -H "X-API-Key: <session-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "text": "Hello World"
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
      "Content-Type": "application/json"
    },
    "url": "https://httpbin.org/post",
    "elapsed_ms": 123.45,
    "body": "{...目标网站的响应...}"
  }
}
```

### 6.4 扩展参数与响应格式
- `payload`：与 `input_mappings.input_key` 对应的键值对。
- `extra_headers`：在执行时额外追加的请求头，会与会话配置合并。
- `query_parameters`：在执行时追加的查询参数。
- **错误响应格式：**
  ```json
  {
    "success": false,
    "error": "错误类型",
    "message": "可选的详细描述",
    "details": {}  // Pydantic 校验错误时包含详细信息
  }
  ```

## 7. 配置与部署

### 7.1 环境变量
| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `API_KEY` | `default-api-key-please-change` | 主 API Key，请务必修改 |
| `BASE_URL` | `http://localhost:5000` | 对外暴露的服务基础地址 |
| `TARGET_WEB_URL` | `https://example.com` | 默认目标 URL（可选） |
| `PORT` | `5000` | Flask 监听端口 |
| `DEBUG` | `False` | 是否开启调试模式（`True` / `False`） |

> 修改 `.env` 后需要重启服务生效。

### 7.2 生产部署建议
- 使用 Gunicorn/UWSGI 等 WSGI 服务器托管 Flask 应用，结合 Nginx 提供反向代理与 HTTPS。
- 将环境变量配置在 CI/CD 或容器编排平台（如 Kubernetes、Docker Swarm）中。
- 启用集中式日志与监控（ELK、Prometheus、Sentry 等）。
- 若需要多实例水平扩展，建议将会话存储迁移到 Redis 等持久化介质。
- 根据目标站点的速率限制配置重试与限流策略，避免被封禁。

## 8. 项目结构
```
.
├── app.py                # Flask 应用入口与路由
├── auth.py               # 主/会话 API Key 认证逻辑
├── session_manager.py    # 会话生命周期与内存存储
├── proxy_client.py       # 字段映射与请求执行
├── models.py             # Pydantic 数据模型
├── config.py             # 环境变量与配置校验
├── utils.py              # 工具函数（API Key 生成等）
├── examples/              # Python 与 cURL 调用示例
├── postman_collection.json # Postman 集合
├── Dockerfile             # 单体容器配置
├── docker-compose.yml     # 本地 Docker 编排
├── requirements.txt       # Python 依赖列表
├── README*.md             # 多语言主文档（含 README_CN）
├── API_DOCUMENTATION*.md  # API 文档（中英文）
├── QUICKSTART*.md         # 快速上手指南（中英文）
├── ARCHITECTURE*.md       # 架构说明（中英文）
└── USAGE_GUIDE_CN.md      # 中文使用指南
```

## 9. 开发与测试指南
- 克隆项目后优先阅读本说明与 `API_DOCUMENTATION.md` 获取接口详情。
- 使用虚拟环境隔离依赖，确保与生产环境一致的 Python 版本。
- 运行 `python app.py` 或 `flask --app app run` 启动本地服务。
- 利用 `examples/example_usage.py` 快速验证端到端流程：
  ```bash
  python examples/example_usage.py
  ```
- 若新增功能，建议配套编写单元测试或集成测试，可自行扩展 `tests/` 目录并使用 `pytest`。
- 调试时可以启用 `DEBUG=True`，但生产环境务必关闭。
- 修改 `proxy_client.py` 可添加自定义请求转换、重试策略等高级能力。

## 10. 常见问题（FAQ）
- **如何更改主 API Key？**  
  在 `.env` 中设置 `API_KEY`，重启服务即可生效。

- **会话数据会持久化吗？**  
  目前存储在内存中，重启服务会清空。可在 `SessionManager` 中接入 Redis/数据库实现持久化。

- **如何传递 Cookie 或自定义 Header？**  
  在会话的 `target.headers` 中配置静态 Header，或在执行请求时通过 `extra_headers` 动态传入。

- **为什么收到 “Unauthorized”？**  
  确认使用了正确的 API Key；执行会话时需要会话 API Key，而非主 API Key。

- **是否支持 HTTPS 目标站点？**  
  支持，项目基于 `requests` 库，会自动处理 HTTPS。

- **如何处理复杂的表单（含文件上传）？**  
  当前版本聚焦文本字段；如需文件上传，可在 `proxy_client.py` 中扩展 multipart/form-data 支持。

- **如何排查目标站点的响应？**  
  `response.body` 字段会返回目标站点原始响应，可配合日志或调试工具查看详细信息。

## 11. 未来规划（Roadmap）
- **阶段 1（当前）**：基础会话管理、字段映射、双层认证。
- **阶段 2**：持久化存储、限流、使用统计、可视化后台。
- **阶段 3**：异步请求、缓存策略、Webhook 回调。
- **阶段 4**：插件化架构、自定义中间件、更多认证方式。

若您有新的需求或想法，欢迎通过 Issue 反馈。

## 12. 贡献指南与许可证

### 12.1 贡献流程
1. Fork 本仓库并创建功能分支：`git checkout -b feature/your-feature`。
2. 完成本地开发与测试，确保符合代码风格与文档规范。
3. 提交 Pull Request，并在描述中说明问题背景、解决方案与测试情况。
4. 维护者会进行代码审查并给出反馈，必要时请根据意见进行修改。

欢迎提供文档翻译、功能增强、Bug 修复等各类贡献。

### 12.2 许可证
本项目基于 **MIT License** 开源，详情参阅仓库中的 `LICENSE` 文件。

## 13. 相关资源

### 中文文档
- **[快速上手指南（中文）](QUICKSTART_CN.md)** - 5分钟内启动和测试 API
- **[API 文档（中文）](API_DOCUMENTATION_CN.md)** - 完整的 API 接口说明与示例
- **[架构文档（中文）](ARCHITECTURE_CN.md)** - 深入了解系统设计与组件
- **[使用指南（中文）](USAGE_GUIDE_CN.md)** - 实战场景与高级用法
- **[项目主页（中文）](README_CN.md)** - 本文档

### 英文文档
- [英文 README](README.md)
- [API Documentation (English)](API_DOCUMENTATION.md)
- [Quickstart Guide (English)](QUICKSTART.md)
- [Architecture Documentation (English)](ARCHITECTURE.md)

### 其他资源
- [示例代码目录](examples/) - Python 和 cURL 示例脚本
- [Postman 集合](postman_collection.json) - 可直接导入 Postman 使用

### 推荐阅读顺序
1. 初学者：[快速上手指南](QUICKSTART_CN.md) → [使用指南](USAGE_GUIDE_CN.md)
2. 开发者：[API 文档](API_DOCUMENTATION_CN.md) → [架构文档](ARCHITECTURE_CN.md)
3. 运维人员：[本文档](#7-配置与部署) → [架构文档](ARCHITECTURE_CN.md)

> 若您在使用过程中遇到问题，欢迎提交 Issue 或 PR，一起完善这一工具。
