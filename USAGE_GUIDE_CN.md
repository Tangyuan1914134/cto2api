# 使用指南（中文版）

> 通过真实场景和详细示例，快速掌握 Web Reverse Proxy API 的使用方法。

## 目录
- [1. 核心概念](#1-核心概念)
- [2. 基本用法](#2-基本用法)
  - [2.1 认证方式](#21-认证方式)
  - [2.2 创建第一个会话](#22-创建第一个会话)
  - [2.3 执行请求](#23-执行请求)
- [3. 真实场景示例](#3-真实场景示例)
  - [3.1 联系表单代理](#31-联系表单代理)
  - [3.2 电商搜索接口](#32-电商搜索接口)
  - [3.3 API 包装与转换](#33-api-包装与转换)
  - [3.4 多步骤表单](#34-多步骤表单)
- [4. 高级用法](#4-高级用法)
  - [4.1 动态 Header 注入](#41-动态-header-注入)
  - [4.2 处理分页数据](#42-处理分页数据)
  - [4.3 混合传输方式](#43-混合传输方式)
  - [4.4 错误处理与重试](#44-错误处理与重试)
- [5. 实战技巧](#5-实战技巧)
  - [5.1 Cookie 管理](#51-cookie-管理)
  - [5.2 User-Agent 伪装](#52-user-agent-伪装)
  - [5.3 响应解析](#53-响应解析)
  - [5.4 会话管理最佳实践](#54-会话管理最佳实践)
- [6. Python 客户端示例](#6-python-客户端示例)
- [7. 故障排除](#7-故障排除)
- [8. 性能优化建议](#8-性能优化建议)

---

## 1. 核心概念

### 会话（Session）
会话是一个配置单元，描述如何将你的 API 请求转换为目标网站的 HTTP 请求。每个会话包含：
- **目标 URL**：要访问的网站地址
- **HTTP 方法**：GET、POST、PUT、DELETE 等
- **字段映射**：定义输入数据如何传递给目标网站
- **认证信息**：会话专用的 API Key

### 输入映射（Input Mapping）
描述如何将你的 API 输入转换为目标网站的参数：
- `input_key`：你在 API 中使用的字段名
- `target_field`：目标网站期望的字段名
- `transport`：数据传输方式（form、json、query、header）

### 双重认证
- **主 API Key**：管理会话的权限
- **会话 API Key**：执行特定会话的权限

---

## 2. 基本用法

### 2.1 认证方式

#### 方式 1：X-API-Key Header（推荐）
```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/v1/sessions
```

#### 方式 2：Authorization Bearer
```bash
curl -H "Authorization: Bearer your-api-key" http://localhost:5000/api/v1/sessions
```

#### 方式 3：查询参数
```bash
curl "http://localhost:5000/api/v1/sessions?api_key=your-api-key"
```

---

### 2.2 创建第一个会话

**请求：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试会话",
    "description": "用于测试 httpbin.org",
    "target": {
      "url": "https://httpbin.org/post",
      "method": "POST"
    },
    "input_mappings": [
      {
        "input_key": "message",
        "target_field": "text",
        "transport": "form"
      }
    ]
  }'
```

**响应：**
```json
{
  "success": true,
  "session": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "api_key": "sk_session_abc123xyz789",
    "base_url": "http://localhost:5000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000",
    "target_url": "https://httpbin.org/post",
    "fields": [...]
  }
}
```

**重要：** 保存 `session_id` 和 `api_key` 用于后续请求！

---

### 2.3 执行请求

**请求：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/execute \
  -H "X-API-Key: sk_session_abc123xyz789" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "message": "你好，世界！"
    }
  }'
```

**响应：**
```json
{
  "success": true,
  "response": {
    "status_code": 200,
    "headers": {
      "Content-Type": "application/json"
    },
    "url": "https://httpbin.org/post",
    "elapsed_ms": 156.78,
    "body": "{\"form\": {\"text\": \"你好，世界！\"}, ...}"
  }
}
```

---

## 3. 真实场景示例

### 3.1 联系表单代理

**场景：** 网站有一个联系表单，需要通过移动端 App 提交用户反馈。

**目标网站表单：**
```html
<form action="https://example.com/contact" method="POST">
  <input name="fullname" />
  <input name="email_address" />
  <textarea name="user_message"></textarea>
  <button type="submit">提交</button>
</form>
```

**创建会话：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "联系表单 API",
    "description": "将网站联系表单转换为 API",
    "target": {
      "url": "https://example.com/contact",
      "method": "POST",
      "headers": {
        "User-Agent": "Mozilla/5.0 (compatible; ContactBot/1.0)"
      }
    },
    "input_mappings": [
      {
        "input_key": "name",
        "target_field": "fullname",
        "transport": "form"
      },
      {
        "input_key": "email",
        "target_field": "email_address",
        "transport": "form"
      },
      {
        "input_key": "message",
        "target_field": "user_message",
        "transport": "form"
      }
    ]
  }'
```

**执行提交：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session_id>/execute \
  -H "X-API-Key: <session_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "name": "张三",
      "email": "zhangsan@example.com",
      "message": "我对你们的产品很感兴趣，请联系我。"
    }
  }'
```

---

### 3.2 电商搜索接口

**场景：** 将电商网站的搜索功能包装为 API，供内部系统调用。

**目标 URL：** `https://shop.example.com/search?q=关键词&category=分类&sort=price&page=1`

**创建会话：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "商品搜索 API",
    "description": "电商网站搜索接口代理",
    "target": {
      "url": "https://shop.example.com/search",
      "method": "GET"
    },
    "input_mappings": [
      {
        "input_key": "keyword",
        "target_field": "q",
        "transport": "query"
      },
      {
        "input_key": "category",
        "target_field": "category",
        "transport": "query"
      },
      {
        "input_key": "sort_by",
        "target_field": "sort",
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
      "keyword": "笔记本电脑",
      "category": "electronics",
      "sort_by": "price",
      "page": "1"
    }
  }'
```

**实际请求 URL：**
```
https://shop.example.com/search?q=笔记本电脑&category=electronics&sort=price&page=1
```

---

### 3.3 API 包装与转换

**场景：** 旧系统 API 接口复杂，需要简化供前端使用。

**旧系统 API：**
- URL: `https://legacy-api.internal/v1/user/data`
- Method: POST
- 需要认证 Header: `X-Legacy-Token`
- 需要特定格式的 JSON Body

**创建会话：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "用户数据 API 包装",
    "description": "简化旧系统的复杂 API",
    "target": {
      "url": "https://legacy-api.internal/v1/user/data",
      "method": "POST",
      "headers": {
        "X-Legacy-Token": "static-token-abc123"
      },
      "use_json": true
    },
    "input_mappings": [
      {
        "input_key": "user_id",
        "target_field": "userId",
        "transport": "json"
      },
      {
        "input_key": "action",
        "target_field": "actionType",
        "transport": "json"
      },
      {
        "input_key": "request_id",
        "target_field": "X-Request-ID",
        "transport": "header"
      }
    ]
  }'
```

**简化后的调用：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session_id>/execute \
  -H "X-API-Key: <session_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "user_id": 12345,
      "action": "get_profile",
      "request_id": "req-001"
    }
  }'
```

**实际发送到旧系统：**
- Headers: 
  - `X-Legacy-Token: static-token-abc123`
  - `X-Request-ID: req-001`
  - `Content-Type: application/json`
- Body:
  ```json
  {
    "userId": 12345,
    "actionType": "get_profile"
  }
  ```

---

### 3.4 多步骤表单

**场景：** 模拟登录后提交数据（需要 Cookie 或 Token）。

**步骤 1：登录获取 Token**
```bash
# 先通过其他方式获取登录 Token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**步骤 2：创建带认证的会话**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "需要登录的操作",
    "target": {
      "url": "https://app.example.com/api/submit",
      "method": "POST",
      "headers": {
        "Authorization": "Bearer '$TOKEN'"
      },
      "use_json": true
    },
    "input_mappings": [
      {
        "input_key": "data",
        "target_field": "content",
        "transport": "json"
      }
    ]
  }'
```

**步骤 3：提交数据**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session_id>/execute \
  -H "X-API-Key: <session_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "data": "重要数据"
    }
  }'
```

---

## 4. 高级用法

### 4.1 动态 Header 注入

**场景：** 每次请求需要不同的认证信息。

**创建会话时使用 Header 映射：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "动态认证 API",
    "target": {
      "url": "https://api.example.com/data",
      "method": "POST",
      "use_json": true
    },
    "input_mappings": [
      {
        "input_key": "auth_token",
        "target_field": "Authorization",
        "transport": "header"
      },
      {
        "input_key": "data",
        "target_field": "payload",
        "transport": "json"
      }
    ]
  }'
```

**执行时传入不同的 Token：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/<session_id>/execute \
  -H "X-API-Key: <session_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "auth_token": "Bearer user-token-123",
      "data": "用户数据"
    }
  }'
```

---

### 4.2 处理分页数据

**创建支持分页的会话：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "分页数据查询",
    "target": {
      "url": "https://api.example.com/items",
      "method": "GET"
    },
    "input_mappings": [
      {
        "input_key": "page",
        "target_field": "page",
        "transport": "query"
      },
      {
        "input_key": "per_page",
        "target_field": "limit",
        "transport": "query"
      }
    ]
  }'
```

**循环获取所有页面（Python 示例）：**
```python
import requests

session_id = "your-session-id"
api_key = "your-session-api-key"
base_url = f"http://localhost:5000/api/v1/sessions/{session_id}/execute"

all_items = []
page = 1

while True:
    response = requests.post(
        base_url,
        headers={"X-API-Key": api_key},
        json={
            "payload": {
                "page": page,
                "per_page": 50
            }
        }
    )
    
    data = response.json()
    # 需要自行实现 parse_items_from_response 用于解析目标站点返回的数据
    items = parse_items_from_response(data['response']['body'])
    
    if not items:
        break
    
    all_items.extend(items)
    page += 1

print(f"总共获取 {len(all_items)} 条数据")
```

---

### 4.3 混合传输方式

**场景：** 同时使用表单、查询参数和 Header。

```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "混合传输示例",
    "target": {
      "url": "https://complex-api.example.com/endpoint",
      "method": "POST"
    },
    "input_mappings": [
      {
        "input_key": "username",
        "target_field": "user",
        "transport": "form"
      },
      {
        "input_key": "api_version",
        "target_field": "version",
        "transport": "query"
      },
      {
        "input_key": "client_id",
        "target_field": "X-Client-ID",
        "transport": "header"
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
      "username": "alice",
      "api_version": "2.0",
      "client_id": "mobile-app-ios"
    }
  }'
```

**实际请求：**
- URL: `https://complex-api.example.com/endpoint?version=2.0`
- Method: POST
- Headers: `X-Client-ID: mobile-app-ios`
- Body: `user=alice`

---

### 4.4 错误处理与重试

**Python 客户端示例（带重试）：**
```python
import requests
from time import sleep

def execute_with_retry(session_id, api_key, payload, max_retries=3):
    url = f"http://localhost:5000/api/v1/sessions/{session_id}/execute"
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                headers={
                    "X-API-Key": api_key,
                    "Content-Type": "application/json"
                },
                json={"payload": payload},
                timeout=10
            )
            
            result = response.json()
            
            if result.get("success"):
                return result
            else:
                print(f"请求失败: {result.get('error')}")
                
        except requests.exceptions.RequestException as e:
            print(f"第 {attempt + 1} 次尝试失败: {e}")
            if attempt < max_retries - 1:
                sleep(2 ** attempt)  # 指数退避
    
    raise Exception("所有重试都失败了")

# 使用
result = execute_with_retry(
    session_id="your-session-id",
    api_key="your-api-key",
    payload={"message": "测试"}
)
```

---

## 5. 实战技巧

### 5.1 Cookie 管理

**方法 1：在 Header 中设置 Cookie**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "带 Cookie 的请求",
    "target": {
      "url": "https://example.com/api",
      "method": "POST",
      "headers": {
        "Cookie": "session_id=abc123; user_pref=dark_mode"
      }
    },
    "input_mappings": [...]
  }'
```

**方法 2：动态传递 Cookie**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "动态 Cookie",
    "target": {
      "url": "https://example.com/api",
      "method": "POST"
    },
    "input_mappings": [
      {
        "input_key": "cookie_value",
        "target_field": "Cookie",
        "transport": "header"
      }
    ]
  }'
```

---

### 5.2 User-Agent 伪装

**避免被目标网站识别为机器人：**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "伪装浏览器",
    "target": {
      "url": "https://example.com/api",
      "method": "GET",
      "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
      }
    },
    "input_mappings": [...]
  }'
```

---

### 5.3 响应解析

**Python 示例：解析 JSON 响应**
```python
import requests
import json

response = requests.post(
    f"http://localhost:5000/api/v1/sessions/{session_id}/execute",
    headers={"X-API-Key": api_key},
    json={"payload": {"query": "test"}}
)

result = response.json()

if result['success']:
    # 解析目标网站返回的 body
    target_response = json.loads(result['response']['body'])
    print(f"状态码: {result['response']['status_code']}")
    print(f"耗时: {result['response']['elapsed_ms']}ms")
    print(f"数据: {target_response}")
else:
    print(f"错误: {result.get('error')}")
```

---

### 5.4 会话管理最佳实践

**1. 为不同用途创建独立会话**
```python
# 好的做法
contact_form_session = create_session("联系表单")
search_api_session = create_session("搜索 API")
user_api_session = create_session("用户 API")

# 不好的做法（混用一个会话）
generic_session = create_session("通用会话")
```

**2. 定期清理不用的会话**
```bash
# 列出所有会话
curl http://localhost:5000/api/v1/sessions \
  -H "X-API-Key: my-master-key"

# 删除旧会话
curl -X DELETE http://localhost:5000/api/v1/sessions/<old_session_id> \
  -H "X-API-Key: my-master-key"
```

**3. 安全存储会话凭证**
```python
# 使用环境变量
import os

SESSION_ID = os.getenv('CONTACT_FORM_SESSION_ID')
SESSION_API_KEY = os.getenv('CONTACT_FORM_API_KEY')

# 或使用配置文件（加密存储）
from cryptography.fernet import Fernet

def load_encrypted_credentials():
    with open('credentials.enc', 'rb') as f:
        encrypted = f.read()
    return decrypt(encrypted)
```

---

## 6. Python 客户端示例

**完整的 Python 封装类：**
```python
import requests
from typing import Dict, Any, Optional

class ProxyAPIClient:
    def __init__(self, base_url: str, master_api_key: str):
        self.base_url = base_url.rstrip('/')
        self.master_api_key = master_api_key
        self.sessions = {}
    
    def create_session(self, name: str, target_url: str, 
                      method: str, input_mappings: list,
                      headers: Optional[Dict] = None) -> Dict:
        """创建会话"""
        url = f"{self.base_url}/api/v1/sessions"
        
        payload = {
            "name": name,
            "target": {
                "url": target_url,
                "method": method,
                "headers": headers or {}
            },
            "input_mappings": input_mappings
        }
        
        response = requests.post(
            url,
            headers={
                "X-API-Key": self.master_api_key,
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        result = response.json()
        
        if result.get('success'):
            session = result['session']
            self.sessions[name] = {
                'id': session['session_id'],
                'api_key': session['api_key']
            }
            return session
        else:
            raise Exception(f"创建会话失败: {result.get('error')}")
    
    def execute(self, session_name: str, payload: Dict) -> Dict:
        """执行会话"""
        if session_name not in self.sessions:
            raise ValueError(f"会话 '{session_name}' 不存在")
        
        session = self.sessions[session_name]
        url = f"{self.base_url}/api/v1/sessions/{session['id']}/execute"
        
        response = requests.post(
            url,
            headers={
                "X-API-Key": session['api_key'],
                "Content-Type": "application/json"
            },
            json={"payload": payload}
        )
        
        return response.json()
    
    def list_sessions(self) -> list:
        """列出所有会话"""
        url = f"{self.base_url}/api/v1/sessions"
        
        response = requests.get(
            url,
            headers={"X-API-Key": self.master_api_key}
        )
        
        result = response.json()
        return result.get('sessions', [])
    
    def delete_session(self, session_name: str) -> bool:
        """删除会话"""
        if session_name not in self.sessions:
            return False
        
        session = self.sessions[session_name]
        url = f"{self.base_url}/api/v1/sessions/{session['id']}"
        
        response = requests.delete(
            url,
            headers={"X-API-Key": self.master_api_key}
        )
        
        if response.json().get('success'):
            del self.sessions[session_name]
            return True
        
        return False

# 使用示例
if __name__ == "__main__":
    client = ProxyAPIClient(
        base_url="http://localhost:5000",
        master_api_key="my-master-key"
    )
    
    # 创建联系表单会话
    client.create_session(
        name="contact_form",
        target_url="https://example.com/contact",
        method="POST",
        input_mappings=[
            {"input_key": "name", "target_field": "fullname", "transport": "form"},
            {"input_key": "email", "target_field": "email", "transport": "form"}
        ]
    )
    
    # 执行请求
    result = client.execute(
        session_name="contact_form",
        payload={
            "name": "张三",
            "email": "zhangsan@example.com"
        }
    )
    
    print(f"状态: {result['success']}")
    print(f"响应: {result['response']}")
```

---

## 7. 故障排除

### 问题 1：401 Unauthorized
**原因：**
- API Key 错误或未提供
- 使用了错误的 API Key 类型（主 API Key vs 会话 API Key）

**解决方法：**
```bash
# 检查环境变量
echo $API_KEY

# 确认使用正确的 Key
# 管理会话用主 API Key
# 执行请求用会话 API Key
```

### 问题 2：目标网站返回 403
**原因：**
- 缺少必要的 Header（如 User-Agent）
- 目标网站有反爬虫机制
- IP 被封禁

**解决方法：**
```bash
# 添加完整的浏览器 Header
"headers": {
  "User-Agent": "Mozilla/5.0...",
  "Accept": "text/html,application/xhtml+xml...",
  "Accept-Language": "zh-CN,zh;q=0.9",
  "Referer": "https://example.com/"
}
```

### 问题 3：中文乱码
**原因：**
- 编码问题

**解决方法：**
```bash
# 使用 --data-raw 而不是 -d
curl -X POST ... \
  --data-raw '{"payload": {"message": "中文测试"}}'

# 或指定编码
curl -X POST ... \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"payload": {"message": "中文测试"}}'
```

### 问题 4：超时
**原因：**
- 目标网站响应慢
- 网络问题

**解决方法：**
```python
# 在客户端设置更长的超时
response = requests.post(
    url,
    json=payload,
    timeout=30  # 30秒超时
)
```

---

## 8. 性能优化建议

### 1. 复用会话
```python
# 好的做法：创建一次，多次使用
session_id = create_session(...)
for item in items:
    execute_session(session_id, item)

# 不好的做法：每次都创建新会话
for item in items:
    session_id = create_session(...)
    execute_session(session_id, item)
    delete_session(session_id)
```

### 2. 批量请求
```python
import concurrent.futures

def execute_batch(session_id, api_key, payloads):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(execute_request, session_id, api_key, payload)
            for payload in payloads
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    return results
```

### 3. 监控性能
```python
import time

start_time = time.time()
result = execute_session(session_id, payload)
elapsed = time.time() - start_time

print(f"代理耗时: {elapsed:.2f}s")
print(f"目标耗时: {result['response']['elapsed_ms']}ms")
print(f"总耗时: {elapsed:.2f}s")
```

---

如有更多问题，请参阅：
- [API 文档](API_DOCUMENTATION_CN.md)
- [快速开始](QUICKSTART_CN.md)
- [项目 README](README_CN.md)
