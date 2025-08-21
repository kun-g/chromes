"""
测试数据工厂

使用 Factory Boy 模式生成测试数据，支持灵活的数据创建
"""
import random
from datetime import datetime, timedelta
from ipaddress import IPv4Address
from typing import List, Dict, Any, Optional
from faker import Faker

# 初始化 Faker
fake = Faker()

class PeerFactory:
    """Peer 数据工厂"""
    
    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """创建 Peer 数据"""
        defaults = {
            "id": f"peer_{fake.uuid4()}",
            "name": fake.hostname(),
            "ip": str(IPv4Address(f"100.109.{random.randint(1, 255)}.{random.randint(1, 255)}")),
            "connected": fake.boolean(),
            "lastSeen": datetime.utcnow().isoformat() + "Z",
            "os": random.choice(['linux', 'windows', 'darwin']),
            "version": f"0.{random.randint(20, 25)}.{random.randint(0, 10)}",
            "hostname": fake.hostname(),
            "sshEnabled": False,
            "groups": [],
            "userId": f"user_{fake.uuid4()}",
            "approvalRequired": False,
            "loginExpirationEnabled": False
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_list(count: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """创建 Peer 列表"""
        return [PeerFactory.create(**kwargs) for _ in range(count)]
    
    @staticmethod
    def create_connected(**kwargs) -> Dict[str, Any]:
        """创建已连接的 Peer"""
        return PeerFactory.create(
            connected=True,
            lastSeen=datetime.utcnow().isoformat() + "Z",
            **kwargs
        )
    
    @staticmethod
    def create_disconnected(**kwargs) -> Dict[str, Any]:
        """创建未连接的 Peer"""
        last_seen = datetime.utcnow() - timedelta(hours=random.randint(1, 72))
        return PeerFactory.create(
            connected=False,
            lastSeen=last_seen.isoformat() + "Z",
            **kwargs
        )
    
    @staticmethod
    def create_with_groups(group_refs: List[Dict], **kwargs) -> Dict[str, Any]:
        """创建带组的 Peer"""
        return PeerFactory.create(groups=group_refs, **kwargs)
    
    @staticmethod
    def create_linux_peer(**kwargs) -> Dict[str, Any]:
        """创建 Linux Peer"""
        return PeerFactory.create(os="linux", **kwargs)
    
    @staticmethod
    def create_windows_peer(**kwargs) -> Dict[str, Any]:
        """创建 Windows Peer"""
        return PeerFactory.create(os="windows", **kwargs)
    
    @staticmethod
    def create_darwin_peer(**kwargs) -> Dict[str, Any]:
        """创建 macOS Peer"""
        return PeerFactory.create(os="darwin", **kwargs)

class GroupFactory:
    """Group 数据工厂"""
    
    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """创建 Group 数据"""
        defaults = {
            "id": f"group_{fake.uuid4()}",
            "name": fake.company(),
            "peersCount": 0,
            "peers": [],
            "resourcesCount": 0
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_list(count: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """创建 Group 列表"""
        return [GroupFactory.create(**kwargs) for _ in range(count)]
    
    @staticmethod  
    def create_with_peers(peer_refs: List[Dict], **kwargs) -> Dict[str, Any]:
        """创建带成员的 Group"""
        return GroupFactory.create(
            peers=peer_refs,
            peersCount=len(peer_refs),
            **kwargs
        )
    
    @staticmethod
    def create_all_group(**kwargs) -> Dict[str, Any]:
        """创建 'All' 特殊组"""
        return GroupFactory.create(
            id="all_group",
            name="All",
            **kwargs
        )
    
    @staticmethod
    def create_empty_group(**kwargs) -> Dict[str, Any]:
        """创建空组"""
        return GroupFactory.create(
            peers=[],
            peersCount=0,
            **kwargs
        )

class PolicyFactory:
    """Policy 数据工厂"""
    
    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """创建 Policy 数据"""
        defaults = {
            "id": f"policy_{fake.uuid4()}",
            "name": fake.company(),
            "description": fake.sentence(),
            "enabled": True,
            "rules": [],
            "sourcePostureChecks": []
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_list(count: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """创建 Policy 列表"""
        return [PolicyFactory.create(**kwargs) for _ in range(count)]
    
    @staticmethod
    def create_rule(**kwargs) -> Dict[str, Any]:
        """创建 Policy Rule 数据"""
        defaults = {
            "id": f"rule_{fake.uuid4()}",
            "name": fake.word().capitalize(),
            "description": fake.sentence(),
            "enabled": True,
            "sources": [],
            "destinations": [],
            "bidirectional": True,
            "protocol": "all",
            "ports": [],
            "action": "accept"
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_with_rules(rules: List[Dict], **kwargs) -> Dict[str, Any]:
        """创建带规则的 Policy"""
        return PolicyFactory.create(rules=rules, **kwargs)
    
    @staticmethod
    def create_tcp_rule(ports: List[str], **kwargs) -> Dict[str, Any]:
        """创建 TCP 规则"""
        return PolicyFactory.create_rule(
            protocol="tcp",
            ports=ports,
            **kwargs
        )
    
    @staticmethod
    def create_udp_rule(ports: List[str], **kwargs) -> Dict[str, Any]:
        """创建 UDP 规则"""
        return PolicyFactory.create_rule(
            protocol="udp",
            ports=ports,
            **kwargs
        )
    
    @staticmethod
    def create_deny_rule(**kwargs) -> Dict[str, Any]:
        """创建拒绝规则"""
        return PolicyFactory.create_rule(
            action="drop",
            **kwargs
        )

class RouteFactory:
    """Route 数据工厂"""
    
    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """创建 Route 数据"""
        # 生成随机 IP 网段
        network_base = f"{random.randint(10, 192)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        defaults = {
            "id": f"route_{fake.uuid4()}",
            "network": f"{network_base}.0/24",
            "description": fake.sentence(),
            "enabled": True,
            "peer": f"peer_{fake.uuid4()}",
            "groups": [],
            "masquerade": False,
            "metric": random.randint(1, 1000)
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_list(count: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """创建 Route 列表"""
        return [RouteFactory.create(**kwargs) for _ in range(count)]

class UserFactory:
    """User 数据工厂"""
    
    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """创建 User 数据"""
        defaults = {
            "id": f"user_{fake.uuid4()}",
            "email": fake.email(),
            "name": fake.name(),
            "role": random.choice(["admin", "user", "viewer"]),
            "autoGroups": [],
            "status": "active",
            "lastLogin": datetime.utcnow().isoformat() + "Z"
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_admin(**kwargs) -> Dict[str, Any]:
        """创建管理员用户"""
        return UserFactory.create(role="admin", **kwargs)
    
    @staticmethod
    def create_regular_user(**kwargs) -> Dict[str, Any]:
        """创建普通用户"""
        return UserFactory.create(role="user", **kwargs)

class SetupKeyFactory:
    """SetupKey 数据工厂"""
    
    @staticmethod
    def create(**kwargs) -> Dict[str, Any]:
        """创建 SetupKey 数据"""
        # 生成类似真实的 key
        key_parts = [fake.lexify(text='????').upper() for _ in range(8)]
        key = '-'.join(key_parts)
        
        defaults = {
            "id": f"key_{fake.uuid4()}",
            "key": key,
            "name": fake.company() + " Key",
            "type": random.choice(["reusable", "one-off"]),
            "usedTimes": random.randint(0, 10),
            "lastUsed": datetime.utcnow().isoformat() + "Z",
            "state": "valid",
            "autoGroups": [],
            "usageLimit": 0,
            "ephemeral": False
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_reusable(**kwargs) -> Dict[str, Any]:
        """创建可重复使用的 Key"""
        return SetupKeyFactory.create(
            type="reusable",
            usageLimit=0,
            **kwargs
        )
    
    @staticmethod
    def create_one_off(**kwargs) -> Dict[str, Any]:
        """创建一次性 Key"""
        return SetupKeyFactory.create(
            type="one-off",
            usageLimit=1,
            usedTimes=0,
            **kwargs
        )

# 工厂助手函数
def create_peer_group_relationship(
    peer_count: int = 3,
    group_name: str = "All"
) -> Dict[str, Any]:
    """创建 Peer 和 Group 的关联关系"""
    group = GroupFactory.create(name=group_name)
    peers = PeerFactory.create_list(peer_count)
    
    # 为 peers 添加 group 引用
    group_ref = {
        "id": group["id"],
        "name": group["name"],
        "peers_count": peer_count,
        "resources_count": 0
    }
    for peer in peers:
        peer["groups"] = [group_ref]
    
    # 为 group 添加 peer 引用
    peer_refs = [
        {"id": p["id"], "name": p["name"], "ip": p["ip"]}
        for p in peers
    ]
    group["peers"] = peer_refs
    group["peersCount"] = len(peers)
    
    return {"group": group, "peers": peers}

def create_policy_with_groups(
    source_groups: List[Dict],
    dest_groups: List[Dict],
    rule_name: str = "Test Rule"
) -> Dict[str, Any]:
    """创建带组引用的策略"""
    rule = PolicyFactory.create_rule(
        name=rule_name,
        sources=source_groups,
        destinations=dest_groups
    )
    return PolicyFactory.create_with_rules([rule])

def create_network_topology(
    group_count: int = 3,
    peers_per_group: int = 2
) -> Dict[str, Any]:
    """创建网络拓扑结构"""
    groups = []
    all_peers = []
    
    for i in range(group_count):
        group_name = f"Group-{i+1}"
        relationship = create_peer_group_relationship(
            peer_count=peers_per_group,
            group_name=group_name
        )
        groups.append(relationship["group"])
        all_peers.extend(relationship["peers"])
    
    # 创建策略连接组
    policies = []
    for i in range(len(groups) - 1):
        policy = create_policy_with_groups(
            source_groups=[groups[i]],
            dest_groups=[groups[i + 1]],
            rule_name=f"Policy-{i+1}"
        )
        policies.append(policy)
    
    return {
        "groups": groups,
        "peers": all_peers,
        "policies": policies
    }

def create_test_environment() -> Dict[str, Any]:
    """创建完整的测试环境数据"""
    topology = create_network_topology()
    
    # 添加路由
    routes = []
    for peer in topology["peers"][:2]:  # 只为前两个 peer 创建路由
        route = RouteFactory.create(peer=peer["id"])
        routes.append(route)
    
    # 添加用户
    users = [
        UserFactory.create_admin(),
        UserFactory.create_regular_user(),
        UserFactory.create_regular_user()
    ]
    
    # 添加 Setup Keys
    setup_keys = [
        SetupKeyFactory.create_reusable(),
        SetupKeyFactory.create_one_off()
    ]
    
    return {
        "groups": topology["groups"],
        "peers": topology["peers"],
        "policies": topology["policies"],
        "routes": routes,
        "users": users,
        "setup_keys": setup_keys
    }