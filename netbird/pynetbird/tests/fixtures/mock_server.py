"""
NetBird API Mock 服务器

使用 respx 模拟 NetBird API 响应
"""
import re
from typing import Dict, Any, Optional, Callable
import respx
from httpx import Response
import json

from .api_responses import API_RESPONSES, HTTP_RESPONSES

def setup_mock_server(mock: respx.MockRouter) -> respx.MockRouter:
    """设置 NetBird API Mock 服务器"""
    
    base_url = "https://api.test.netbird.io/api"
    
    # Peers endpoints
    mock.get(f"{base_url}/peers").mock(
        return_value=Response(200, json=API_RESPONSES["peers"]["list"])
    )
    
    mock.get(re.compile(f"{base_url}/peers/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["peers"]["single"])
    )
    
    mock.post(f"{base_url}/peers").mock(
        return_value=Response(201, json=API_RESPONSES["peers"]["single"])
    )
    
    mock.put(re.compile(f"{base_url}/peers/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["peers"]["single"])
    )
    
    mock.patch(re.compile(f"{base_url}/peers/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["peers"]["single"])
    )
    
    mock.delete(re.compile(f"{base_url}/peers/[^/]+$")).mock(
        return_value=Response(204)
    )
    
    # Groups endpoints
    mock.get(f"{base_url}/groups").mock(
        return_value=Response(200, json=API_RESPONSES["groups"]["list"])
    )
    
    mock.get(re.compile(f"{base_url}/groups/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["groups"]["single"])
    )
    
    mock.post(f"{base_url}/groups").mock(
        return_value=Response(201, json=API_RESPONSES["groups"]["single"])
    )
    
    mock.put(re.compile(f"{base_url}/groups/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["groups"]["single"])
    )
    
    mock.patch(re.compile(f"{base_url}/groups/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["groups"]["single"])
    )
    
    mock.delete(re.compile(f"{base_url}/groups/[^/]+$")).mock(
        return_value=Response(204)
    )
    
    # Policies endpoints  
    mock.get(f"{base_url}/policies").mock(
        return_value=Response(200, json=API_RESPONSES["policies"]["list"])
    )
    
    mock.get(re.compile(f"{base_url}/policies/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["policies"]["single"])
    )
    
    mock.post(f"{base_url}/policies").mock(
        return_value=Response(201, json=API_RESPONSES["policies"]["single"])
    )
    
    mock.put(re.compile(f"{base_url}/policies/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["policies"]["single"])
    )
    
    mock.patch(re.compile(f"{base_url}/policies/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["policies"]["single"])
    )
    
    mock.delete(re.compile(f"{base_url}/policies/[^/]+$")).mock(
        return_value=Response(204)
    )
    
    # Routes endpoints
    mock.get(f"{base_url}/routes").mock(
        return_value=Response(200, json=API_RESPONSES["routes"]["list"])
    )
    
    mock.get(re.compile(f"{base_url}/routes/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["routes"]["single"])
    )
    
    mock.post(f"{base_url}/routes").mock(
        return_value=Response(201, json=API_RESPONSES["routes"]["single"])
    )
    
    mock.put(re.compile(f"{base_url}/routes/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["routes"]["single"])
    )
    
    mock.delete(re.compile(f"{base_url}/routes/[^/]+$")).mock(
        return_value=Response(204)
    )
    
    # Rules endpoints
    mock.get(f"{base_url}/rules").mock(
        return_value=Response(200, json=API_RESPONSES["rules"]["list"])
    )
    
    mock.get(re.compile(f"{base_url}/rules/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["rules"]["single"])
    )
    
    # Users endpoints
    mock.get(f"{base_url}/users").mock(
        return_value=Response(200, json=API_RESPONSES["users"]["list"])
    )
    
    mock.get(re.compile(f"{base_url}/users/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["users"]["single"])
    )
    
    # Accounts endpoints
    mock.get(f"{base_url}/accounts/me").mock(
        return_value=Response(200, json=API_RESPONSES["accounts"]["single"])
    )
    
    # Setup Keys endpoints
    mock.get(f"{base_url}/setup-keys").mock(
        return_value=Response(200, json=API_RESPONSES["setup_keys"]["list"])
    )
    
    mock.get(re.compile(f"{base_url}/setup-keys/[^/]+$")).mock(
        return_value=Response(200, json=API_RESPONSES["setup_keys"]["single"])
    )
    
    mock.post(f"{base_url}/setup-keys").mock(
        return_value=Response(201, json=API_RESPONSES["setup_keys"]["single"])
    )
    
    # Error scenarios
    setup_error_scenarios(mock, base_url)
    
    return mock

def setup_error_scenarios(mock: respx.MockRouter, base_url: str):
    """设置错误场景模拟"""
    
    # 401 Unauthorized
    mock.get(f"{base_url}/unauthorized").mock(
        return_value=Response(401, json=HTTP_RESPONSES[401])
    )
    
    # 403 Forbidden
    mock.get(f"{base_url}/forbidden").mock(
        return_value=Response(403, json=HTTP_RESPONSES[403])
    )
    
    # 404 Not Found
    mock.get(f"{base_url}/not-found").mock(
        return_value=Response(404, json=HTTP_RESPONSES[404])
    )
    
    # 400 Validation Error
    mock.post(f"{base_url}/validation-error").mock(
        return_value=Response(400, json=HTTP_RESPONSES[400])
    )
    
    # 409 Conflict
    mock.post(f"{base_url}/conflict").mock(
        return_value=Response(409, json=HTTP_RESPONSES[409])
    )
    
    # 429 Rate Limit
    mock.get(f"{base_url}/rate-limit").mock(
        return_value=Response(429, json=HTTP_RESPONSES[429])
    )
    
    # 500 Server Error
    mock.get(f"{base_url}/server-error").mock(
        return_value=Response(500, json=HTTP_RESPONSES[500])
    )
    
    # 503 Service Unavailable
    mock.get(f"{base_url}/service-unavailable").mock(
        return_value=Response(503, json=HTTP_RESPONSES[503])
    )
    
    # Network timeout simulation
    mock.get(f"{base_url}/timeout").mock(
        side_effect=Exception("Timeout")
    )

def setup_dynamic_mock_server(
    mock: respx.MockRouter,
    responses: Dict[str, Any]
) -> respx.MockRouter:
    """设置动态 Mock 服务器，支持自定义响应"""
    
    base_url = "https://api.test.netbird.io/api"
    
    for endpoint, response_data in responses.items():
        status_code = response_data.get("status", 200)
        json_data = response_data.get("json", {})
        headers = response_data.get("headers", {})
        
        # 支持不同的 HTTP 方法
        method = response_data.get("method", "GET").upper()
        
        if method == "GET":
            mock.get(f"{base_url}/{endpoint}").mock(
                return_value=Response(status_code, json=json_data, headers=headers)
            )
        elif method == "POST":
            mock.post(f"{base_url}/{endpoint}").mock(
                return_value=Response(status_code, json=json_data, headers=headers)
            )
        elif method == "PUT":
            mock.put(f"{base_url}/{endpoint}").mock(
                return_value=Response(status_code, json=json_data, headers=headers)
            )
        elif method == "DELETE":
            mock.delete(f"{base_url}/{endpoint}").mock(
                return_value=Response(status_code, json=json_data, headers=headers)
            )
        elif method == "PATCH":
            mock.patch(f"{base_url}/{endpoint}").mock(
                return_value=Response(status_code, json=json_data, headers=headers)
            )
    
    return mock

def setup_stateful_mock_server(mock: respx.MockRouter) -> Dict[str, Any]:
    """
    设置有状态的 Mock 服务器
    
    返回一个状态字典，可以在测试中修改服务器行为
    """
    base_url = "https://api.test.netbird.io/api"
    
    # 内部状态存储
    state = {
        "peers": dict(API_RESPONSES["peers"]["list"]),
        "groups": dict(API_RESPONSES["groups"]["list"]),
        "policies": dict(API_RESPONSES["policies"]["list"]),
        "routes": dict(API_RESPONSES["routes"]["list"]),
        "call_count": {},
        "last_request": None
    }
    
    def track_request(endpoint: str, method: str = "GET"):
        """追踪请求"""
        key = f"{method}:{endpoint}"
        state["call_count"][key] = state["call_count"].get(key, 0) + 1
        state["last_request"] = {"endpoint": endpoint, "method": method}
    
    # Peers endpoints with state tracking
    @mock.get(f"{base_url}/peers")
    def get_peers(request):
        track_request("/peers", "GET")
        return Response(200, json=state["peers"])
    
    @mock.post(f"{base_url}/peers")
    def create_peer(request):
        track_request("/peers", "POST")
        new_peer = json.loads(request.content)
        new_peer["id"] = f"peer_{len(state['peers']) + 1}"
        state["peers"].append(new_peer)
        return Response(201, json=new_peer)
    
    # Groups endpoints with state tracking
    @mock.get(f"{base_url}/groups")
    def get_groups(request):
        track_request("/groups", "GET")
        return Response(200, json=state["groups"])
    
    @mock.post(f"{base_url}/groups")
    def create_group(request):
        track_request("/groups", "POST")
        new_group = json.loads(request.content)
        new_group["id"] = f"group_{len(state['groups']) + 1}"
        state["groups"].append(new_group)
        return Response(201, json=new_group)
    
    return state

class MockServerBuilder:
    """Mock 服务器构建器"""
    
    def __init__(self, base_url: str = "https://api.test.netbird.io/api"):
        self.base_url = base_url
        self.routes = {}
        self.error_routes = {}
        
    def add_route(
        self,
        method: str,
        endpoint: str,
        response_data: Any,
        status_code: int = 200,
        headers: Optional[Dict] = None
    ) -> "MockServerBuilder":
        """添加路由"""
        key = f"{method.upper()}:{endpoint}"
        self.routes[key] = {
            "data": response_data,
            "status": status_code,
            "headers": headers or {}
        }
        return self
    
    def add_error_route(
        self,
        endpoint: str,
        error_code: int,
        error_message: str
    ) -> "MockServerBuilder":
        """添加错误路由"""
        self.error_routes[endpoint] = {
            "code": error_code,
            "message": error_message
        }
        return self
    
    def build(self, mock: respx.MockRouter) -> respx.MockRouter:
        """构建 Mock 服务器"""
        # 添加正常路由
        for route_key, route_config in self.routes.items():
            method, endpoint = route_key.split(":", 1)
            url = f"{self.base_url}/{endpoint}"
            
            response = Response(
                route_config["status"],
                json=route_config["data"],
                headers=route_config["headers"]
            )
            
            if method == "GET":
                mock.get(url).mock(return_value=response)
            elif method == "POST":
                mock.post(url).mock(return_value=response)
            elif method == "PUT":
                mock.put(url).mock(return_value=response)
            elif method == "DELETE":
                mock.delete(url).mock(return_value=response)
            elif method == "PATCH":
                mock.patch(url).mock(return_value=response)
        
        # 添加错误路由
        for endpoint, error_config in self.error_routes.items():
            url = f"{self.base_url}/{endpoint}"
            response = Response(
                error_config["code"],
                json={"message": error_config["message"], "code": error_config["code"]}
            )
            mock.get(url).mock(return_value=response)
        
        return mock

def create_test_server_with_latency(
    mock: respx.MockRouter,
    latency_ms: int = 100
) -> respx.MockRouter:
    """创建带延迟的测试服务器"""
    import asyncio
    import time
    
    base_url = "https://api.test.netbird.io/api"
    
    async def delayed_response(request):
        """延迟响应"""
        await asyncio.sleep(latency_ms / 1000)
        return Response(200, json={"message": "delayed response"})
    
    mock.get(f"{base_url}/slow").mock(side_effect=delayed_response)
    
    return mock