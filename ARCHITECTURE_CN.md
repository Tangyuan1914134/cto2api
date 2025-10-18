# 架构文档（中文版）

> 了解 Web Reverse Proxy API 的整体设计、组件职责与扩展思路，帮助你快速掌握项目工作原理。

## 目录
- [1. 概览](#1-概览)
- [2. 架构图](#2-架构图)
- [3. 核心组件](#3-核心组件)
  - [3.1 应用层（app.py）](#31-应用层apppy)
  - [3.2 认证层（auth.py）](#32-认证层authpy)
  - [3.3 会话管理（session_manager.py）](#33-会话管理session_managerpy)
  - [3.4 代理客户端（proxy_client.py）](#34-代理客户端proxy_clientpy)
  - [3.5 数据模型（models.py）](#35-数据模型modelspy)
  - [3.6 配置模块（config.py）](#36-配置模块configpy)
  - [3.7 工具函数（utils.py）](#37-工具函数utilspy)
- [4. 数据流](#4-数据流)
  - [4.1 会话创建流程](#41-会话创建流程)
  - [4.2 请求执行流程](#42-请求执行流程)
- [5. 会话数据结构](#5-会话数据结构)
- [6. 传输类型（Transport）](#6-传输类型transport)
- [7. 安全模型](#7-安全模型)
  - [7.1 双层认证](#71-双层认证)
  - [7.2 安全最佳实践](#72-安全最佳实践)
- [8. 存储策略](#8-存储策略)
  - [8.1 当前实现](#81-当前实现)
  - [8.2 未来增强](#82-未来增强)
- [9. 可扩展性设计](#9-可扩展性设计)
  - [9.1 水平扩展](#91-水平扩展)
  - [9.2 垂直扩展](#92-垂直扩展)
- [10. 错误处理与返回格式](#10-错误处理与返回格式)
- [11. 扩展点](#11-扩展点)
- [12. 性能指标](#12-性能指标)
- [13. 部署架构](#13-部署架构)
  - [13.1 开发环境](#131-开发环境)
  - [13.2 生产环境](#132-生产环境)
  - [13.3 Docker 部署](#133-docker-部署)
- [14. API 版本管理](#14-api-版本管理)
- [15. 日志与监控](#15-日志与监控)
- [16. 依赖管理](#16-依赖管理)
- [17. 未来路线图](#17-未来路线图)

---

## 1. 概览

Web Reverse Proxy API 基于 Flask 构建，提供一个通用的反向代理层，将传统网页表单或 HTTP 接口转化为结构化的 RESTful API。项目强调以下几点：

- 清晰的模块划分，便于维护和扩展。
- 通过会话（Session）描述目标网站配置，实现高度可定制化。
- 使用双重 API Key 认证保障安全性。
- 使用 Pydantic 进行数据验证，减少错误输入。
- 利用 `requests` 库执行实际的 HTTP 请求，兼容大多数网站。

---

## 2. 架构图
```
┌──────────────────────────────────────────────────────────────────┐
│                         客户端应用（API调用方）                   │
│           （Web、移动端、后端服务、自动化脚本等）               │
└───────────────────────────┬──────────────────────────────────────┘
                            │ REST/HTTP 请求
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                       Web Reverse Proxy API                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      Flask 应用层                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │ 认证模块     │  │ 会话管理器   │  │ 代理客户端     │  │  │
│  │  │ (auth.py)    │  │ (session_...)│  │ (proxy_client) │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTP 请求
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                         目标网站 / 服务端                        │
│                    （任意 HTTP/HTTPS 终端）                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. 核心组件

### 3.1 应用层（app.py）
- Flask 应用入口，注册所有路由。
- 处理请求和响应的序列化。
- 集成跨域（CORS）支持、错误处理。
- 调用 SessionManager、ProxyClient 等核心服务。

### 3.2 认证层（auth.py）
- 验证主 API Key（Master）与会话 API Key（Session）。
- 提供装饰器 `@require_api_key` 保护需要主 API Key 的路由。
- 提供函数 `validate_session_api_key` 验证会话 API Key。
- 支持 `X-API-Key` 和 `Authorization: Bearer` 两种认证方式。

### 3.3 会话管理（session_manager.py）
- 使用内存（字典）存储所有会话。
- 负责创建、读取、删除会话。
- 生成唯一的 `session_id` 和会话级 `api_key`。
- 暴露列表接口供查询所有会话。

### 3.4 代理客户端（proxy_client.py）
- 构造发往目标网站的 HTTP 请求。
- 根据 `input_mappings` 将输入数据映射到对应的 transport。
- 支持表单、查询参数、请求头、JSON 四种传输方式。
- 使用 `requests` 库发送请求并格式化响应。
- 捕获请求异常并抛出适当的错误信息。

### 3.5 数据模型（models.py）
- 使用 Pydantic 定义请求与响应的数据结构。
- 提供输入验证和类型提示，确保 API 调用安全可靠。
- 包含创建会话所需的 `SessionCreateRequest`、执行会话的 `ExecuteRequest` 等模型。

### 3.6 配置模块（config.py）
- 通过 `python-dotenv` 读取 `.env` 中的配置。
- 暴露 Config 类，统一管理 `API_KEY`、`BASE_URL`、`PORT` 等设置。
- 在启动时执行校验，提醒开发者更新默认的 API Key。

### 3.7 工具函数（utils.py）
- 提供通用工具，如生成随机 API Key 的函数。
- 可扩展添加更多公共逻辑（如日志格式化、时间处理等）。

---

## 4. 数据流

### 4.1 会话创建流程
1. 客户端携带主 API Key 调用 `POST /api/v1/sessions`
2. `auth.require_api_key` 校验主 API Key
3. 使用 Pydantic 对请求体进行验证
4. `SessionManager.create_session` 创建会话配置，生成 ID 和 API Key
5. 会话信息存储在内存中，返回给客户端

### 4.2 请求执行流程
1. 客户端携带会话 API Key 调用 `POST /api/v1/sessions/<id>/execute`
2. 系统校验会话 API Key，仅允许对应会话使用
3. `SessionManager` 读取会话配置
4. `ProxyClient` 根据 `input_mappings` 构造目标请求
5. 发送请求至目标网站，接收响应
6. 格式化返回数据（状态码、Header、Body、耗时等）并返回给客户端

---

## 5. 会话数据结构
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
                transport: Literal['form', 'json', 'query', 'header']
            }
        ]
    },
    created_at: datetime,
    updated_at: datetime
}
```
- `session_id`：唯一标识
- `api_key`：执行会话的密钥，创建时生成
- `target`：目标网站配置
- `input_mappings`：描述字段映射与传输方式
- `created_at / updated_at`：时间戳，便于审计

---

## 6. 传输类型（Transport）

| transport | 描述 | 常见场景 | Content-Type |
| --- | --- | --- | --- |
| `form` | 表单字段提交 | 传统 HTML 表单 | `application/x-www-form-urlencoded` |
| `json` | JSON 请求体 | 现代 REST API | `application/json` |
| `query` | URL 查询参数 | 搜索、分页、过滤 | - |
| `header` | HTTP 请求头 | 认证、追踪、用户信息 | - |

可在同一会话中混合使用多种传输方式，以满足复杂业务需求。

---

## 7. 安全模型

### 7.1 双层认证
1. **主 API Key**（Master API Key）：
   - 用于会话管理（创建、查询、删除）
   - 配置在 `.env` 的 `API_KEY`
   - 应放置在安全的环境变量中

2. **会话 API Key**（Session API Key）：
   - 每个会话独立生成，用于执行请求
   - 仅在会话创建时返回一次
   - 适合分发给调用方或其他服务

### 7.2 安全最佳实践
- 强制使用 HTTPS 访问本服务与目标网站
- 定期轮换主 API Key 和会话 API Key
- 将 API Key 存储在安全的密钥管理系统（如 Vault）
- 在 `auth.py` 中添加 IP 白名单或速率限制
- 使用日志和审计功能监控 API 调用

---

## 8. 存储策略

### 8.1 当前实现
- 使用内存字典存储所有会话
- 适合开发、测试或单节点部署
- 重启服务会丢失所有会话

### 8.2 未来增强
- 将会话存储迁移到 Redis，实现持久化与共享
- 使用关系型数据库（PostgreSQL、MySQL）保存历史记录
- 增加会话过期策略（TTL）
- 收集会话访问统计与分析数据

---

## 9. 可扩展性设计

### 9.1 水平扩展
- 应用层无状态，可通过负载均衡水平扩展
- 会话信息需共享，推荐使用外部存储（Redis、数据库）
- 配合 API 网关或反向代理实现多实例部署

### 9.2 垂直扩展
- 增加单机资源（CPU、内存）以提升处理能力
- 在 ProxyClient 中实现连接池、重试策略
- 引入异步请求（aiohttp/asyncio）提升吞吐量

---

## 10. 错误处理与返回格式

- 所有 API 返回统一的 JSON 格式：
  ```json
  {
    "success": false,
    "error": "错误类型",
    "message": "详细描述",
    "details": {}
  }
  ```
- 常见错误类型：
  - `400 Bad Request`：请求参数错误
  - `401 Unauthorized`：认证失败
  - `404 Not Found`：会话不存在
  - `500 Internal Server Error`：内部错误
- Flask 提供默认的 404、500 错误处理器，返回结构化信息。

---

## 11. 扩展点

- **自定义认证**：在 `auth.py` 中添加更多认证方式（OAuth、JWT 等）。
- **会话存储**：在 `SessionManager` 中替换为 Redis、数据库或云存储。
- **请求转换**：扩展 `proxy_client.py` 支持文件上传、多部分表单等。
- **中间件**：在 Flask 中加入日志、性能监控、限流等通用中间件。
- **Webhook**：在请求完成后触发回调或事件通知。

---

## 12. 性能指标

建议监控的核心指标：
- 请求总量与成功率
- 会话数量与增长趋势
- 目标网站响应时间与代理耗时（`elapsed_ms`）
- 错误率（按类型分类）
- 最耗时/失败最多的目标 URL

可结合 Prometheus、Grafana、Datadog 等工具进行可视化。

---

## 13. 部署架构

### 13.1 开发环境
```
本地机器 → Flask 开发服务器（端口 5000）
```

### 13.2 生产环境
```
客户端 → 负载均衡（Nginx/ALB） → WSGI（Gunicorn/uWSGI） → Flask App → 目标网站
             │                     └→ 多个 Worker 进程
             └→ HTTPS/TLS
```

### 13.3 Docker 部署
```
客户端 → Docker 容器（Flask + Gunicorn）
           └→ 使用环境变量注入配置
           └→ 可挂载卷存放日志或证书
```

---

## 14. API 版本管理
- 当前版本：`v1`
- API 路径格式：`/api/v1/...`
- 未来版本迭代将确保向后兼容或提供迁移指南。

---

## 15. 日志与监控

### 15.1 当前实现
- 使用 Flask 默认日志输出（stdout）
- 推荐结合 Docker、系统日志进行收集

### 15.2 建议方案
- 采用结构化日志（JSON）
- 集成 ELK、Splunk、CloudWatch 等日志平台
- 配置 Sentry、Rollbar 进行异常追踪
- 使用 APM（如 New Relic、Datadog）监控性能

---

## 16. 依赖管理

### 核心依赖
- **Flask 3.0.0**：Web 框架
- **requests 2.31.0**：HTTP 客户端
- **pydantic 2.5.0**：数据验证
- **python-dotenv 1.0.0**：环境变量加载

### 可选/开发依赖
- **flask-cors**：跨域支持
- **gunicorn**：生产环境 WSGI 服务器

依赖通过 `requirements.txt` 管理，可根据需要锁定或升级版本。

---

## 17. 未来路线图

1. **阶段 1 - 当前**
   - 基础会话管理
   - 多种字段传输方式
   - 双层 API Key 认证

2. **阶段 2**
   - 会话持久化存储
   - 限流与速率控制
   - API 使用统计与可视化

3. **阶段 3**
   - 异步请求与批量处理
   - 缓存机制与后端熔断
   - Webhook/回调通知

4. **阶段 4**
   - 插件系统
   - 自定义中间件
   - 更多认证协议（OAuth2、SAML 等）

欢迎通过 Issue 或 Pull Request 分享你的想法，共同完善该项目。
