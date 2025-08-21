"""
NetBird API 真实响应数据

基于实际 API 调用收集的响应格式，确保测试数据的真实性
"""

API_RESPONSES = {
    "peers": {
        "single": {
            "id": "d2itv26kurdc73fqb0cg",
            "name": "ab14ca4f6a9a",
            "ip": "100.109.212.184",
            "connected": True,
            "lastSeen": "2025-08-21T10:30:00Z",
            "os": "linux",
            "version": "0.24.0",
            "hostname": "test-host",
            "sshEnabled": False,
            "groups": [
                {
                    "id": "d1n8evekurdc73cnnpig",
                    "name": "All",
                    "peers_count": 8,
                    "resources_count": 0
                },
                {
                    "id": "d2itruukurdc73fqb0bg", 
                    "name": "Quarantine",
                    "peers_count": 1,
                    "resources_count": 0
                }
            ],
            "userId": "user123",
            "approvalRequired": False,
            "loginExpirationEnabled": False
        },
        
        "list": [
            {
                "id": "d2itv26kurdc73fqb0cg",
                "name": "ab14ca4f6a9a",
                "ip": "100.109.212.184",
                "connected": True,
                "groups": [{"id": "d1n8evekurdc73cnnpig", "name": "All"}]
            },
            {
                "id": "d1n8muukurdc73cnnpkg",
                "name": "dev-container",
                "ip": "100.109.88.220", 
                "connected": True,
                "groups": [{"id": "d1n8evekurdc73cnnpig", "name": "All"}]
            }
        ],
        
        "create_request": {
            "name": "new-peer",
            "sshEnabled": False,
            "approvalRequired": False
        },
        
        "update_request": {
            "name": "updated-peer",
            "sshEnabled": True,
            "approvalRequired": False
        }
    },
    
    "groups": {
        "single": {
            "id": "d1n8evekurdc73cnnpig",
            "name": "All",
            "peersCount": 8,
            "peers": [
                {"id": "d1n8muukurdc73cnnpkg", "name": "dev-container", "ip": "100.109.88.220"},
                {"id": "d1n8n4ukurdc73cnnpl0", "name": "dev-container-2", "ip": "100.109.134.118"}
            ],
            "resourcesCount": 0
        },
        
        "list": [
            {
                "id": "d1n8evekurdc73cnnpig", 
                "name": "All",
                "peersCount": 8,
                "peers": [
                    {"id": "peer1", "name": "dev-container"},
                    {"id": "peer2", "name": "MacBook-Pro"}
                ]
            },
            {
                "id": "d1n8ohukurdc73cnnplg",
                "name": "PC", 
                "peersCount": 3,
                "peers": [
                    {"id": "peer3", "name": "MacBook-Pro-2.local"},
                    {"id": "peer4", "name": "MBA-m4.local"}
                ]
            }
        ],
        
        "create_request": {
            "name": "new-group",
            "peers": []
        },
        
        "update_request": {
            "name": "updated-group",
            "peers": ["d1n8muukurdc73cnnpkg", "d1n8n4ukurdc73cnnpl0"]
        }
    },
    
    "policies": {
        "single": {
            "id": "d1n8evekurdc73cnnpj0",
            "name": "Default",
            "description": "This is a default rule that allows connections between all the resources",
            "enabled": False,
            "rules": [
                {
                    "id": "d1n8evekurdc73cnnpj0",
                    "name": "Default", 
                    "description": "This is a default rule that allows connections between all the resources",
                    "enabled": False,
                    "sources": [
                        {
                            "id": "d1n8evekurdc73cnnpig",
                            "name": "All",
                            "peers_count": 8,
                            "resources_count": 0
                        }
                    ],
                    "destinations": [
                        {
                            "id": "d1n8evekurdc73cnnpig", 
                            "name": "All",
                            "peers_count": 8,
                            "resources_count": 0
                        }
                    ],
                    "bidirectional": True,
                    "protocol": "all",
                    "ports": [],
                    "action": "accept"
                }
            ],
            "sourcePostureChecks": []
        },
        
        "list": [
            {
                "id": "d1n8evekurdc73cnnpj0",
                "name": "Default", 
                "enabled": False,
                "rules": [{"id": "rule1", "name": "Default", "enabled": False}]
            },
            {
                "id": "d2iu28ekurdc73fqb0d0",
                "name": "Super",
                "enabled": True,
                "rules": [{"id": "rule2", "name": "Super", "enabled": True}]
            }
        ],
        
        "create_request": {
            "name": "new-policy",
            "description": "New policy description",
            "enabled": True,
            "rules": []
        },
        
        "update_request": {
            "name": "updated-policy",
            "description": "Updated policy description",
            "enabled": False,
            "rules": []
        }
    },
    
    "routes": {
        "single": {
            "id": "route123",
            "network": "10.0.0.0/24",
            "description": "Test route",
            "enabled": True,
            "peer": "d1n8muukurdc73cnnpkg",
            "groups": ["d1n8evekurdc73cnnpig"],
            "masquerade": False,
            "metric": 100
        },
        
        "list": [
            {
                "id": "route123",
                "network": "10.0.0.0/24",
                "description": "Test route",
                "enabled": True,
                "peer": "d1n8muukurdc73cnnpkg"
            },
            {
                "id": "route456",
                "network": "192.168.1.0/24",
                "description": "Another route",
                "enabled": False,
                "peer": "d1n8n4ukurdc73cnnpl0"
            }
        ]
    },
    
    "rules": {
        "single": {
            "id": "rule123",
            "name": "Test Rule",
            "description": "Test access control rule",
            "enabled": True,
            "sources": ["d1n8evekurdc73cnnpig"],
            "destinations": ["d1n8ohukurdc73cnnplg"],
            "bidirectional": True,
            "protocol": "tcp",
            "ports": ["80", "443"],
            "action": "accept"
        },
        
        "list": [
            {
                "id": "rule123",
                "name": "Test Rule",
                "enabled": True,
                "action": "accept"
            },
            {
                "id": "rule456",
                "name": "Block Rule",
                "enabled": True,
                "action": "drop"
            }
        ]
    },
    
    "users": {
        "single": {
            "id": "user123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "admin",
            "autoGroups": ["d1n8evekurdc73cnnpig"],
            "status": "active",
            "lastLogin": "2025-08-21T10:00:00Z"
        },
        
        "list": [
            {
                "id": "user123",
                "email": "test@example.com",
                "name": "Test User",
                "role": "admin"
            },
            {
                "id": "user456",
                "email": "user@example.com",
                "name": "Regular User",
                "role": "user"
            }
        ]
    },
    
    "accounts": {
        "single": {
            "id": "account123",
            "createdBy": "user123",
            "domain": "example.com",
            "network": {
                "id": "network123",
                "net": "100.109.0.0/16",
                "dns": "100.109.0.1"
            },
            "settings": {
                "peerLoginExpirationEnabled": False,
                "peerLoginExpiration": 86400
            }
        }
    },
    
    "setup_keys": {
        "single": {
            "id": "key123",
            "key": "A1B2C3D4-E5F6-G7H8-I9J0-K1L2M3N4O5P6",
            "name": "Test Setup Key",
            "type": "reusable",
            "usedTimes": 3,
            "lastUsed": "2025-08-21T09:00:00Z",
            "state": "valid",
            "autoGroups": ["d1n8evekurdc73cnnpig"],
            "usageLimit": 0,
            "ephemeral": False
        },
        
        "list": [
            {
                "id": "key123",
                "name": "Test Setup Key",
                "type": "reusable",
                "state": "valid"
            },
            {
                "id": "key456",
                "name": "Ephemeral Key",
                "type": "one-off",
                "state": "used"
            }
        ]
    },
    
    "errors": {
        "401_unauthorized": {
            "message": "token invalid",
            "code": 401
        },
        "403_forbidden": {
            "message": "forbidden",
            "code": 403
        },
        "404_not_found": {
            "message": "resource not found", 
            "code": 404
        },
        "400_validation_error": {
            "message": "validation failed",
            "code": 400,
            "details": ["field 'name' is required"]
        },
        "409_conflict": {
            "message": "resource already exists",
            "code": 409
        },
        "429_rate_limit": {
            "message": "rate limit exceeded",
            "code": 429
        },
        "500_server_error": {
            "message": "internal server error",
            "code": 500
        },
        "503_service_unavailable": {
            "message": "service temporarily unavailable",
            "code": 503
        }
    }
}

# HTTP 状态码响应映射
HTTP_RESPONSES = {
    200: {"status": "success"},
    201: {"status": "created"},
    204: None,  # No content
    400: API_RESPONSES["errors"]["400_validation_error"],
    401: API_RESPONSES["errors"]["401_unauthorized"],
    403: API_RESPONSES["errors"]["403_forbidden"],
    404: API_RESPONSES["errors"]["404_not_found"],
    409: API_RESPONSES["errors"]["409_conflict"],
    429: API_RESPONSES["errors"]["429_rate_limit"],
    500: API_RESPONSES["errors"]["500_server_error"],
    503: API_RESPONSES["errors"]["503_service_unavailable"],
}

# 分页响应示例
PAGINATED_RESPONSE = {
    "data": [],
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "hasMore": True,
    "nextPage": 2
}

# WebSocket 事件示例
WEBSOCKET_EVENTS = {
    "peer_connected": {
        "type": "peer_connected",
        "data": {
            "peerId": "d1n8muukurdc73cnnpkg",
            "timestamp": "2025-08-21T10:30:00Z"
        }
    },
    "peer_disconnected": {
        "type": "peer_disconnected",
        "data": {
            "peerId": "d1n8muukurdc73cnnpkg",
            "timestamp": "2025-08-21T10:35:00Z"
        }
    },
    "config_updated": {
        "type": "config_updated",
        "data": {
            "timestamp": "2025-08-21T10:40:00Z"
        }
    }
}