"""
Tests for PyNetBird data models.

Validates model creation, validation, serialization, and API compatibility.
"""

import pytest
from datetime import datetime
from ipaddress import IPv4Address

from pynetbird.models import (
    Peer, PeerStatus, PeerOS, PeerUpdate, PeerList,
    Group, GroupType, GroupCreate, GroupUpdate, GroupList,
    Policy, PolicyRule, PolicyAction, PolicyProtocol, PolicyCreate, PolicyUpdate, PolicyList,
    PeerRef, GroupRef,
)


class TestPeerModels:
    """Test Peer-related models."""
    
    def test_peer_basic_creation(self):
        """Test basic Peer model creation."""
        peer_data = {
            "id": "peer123",
            "name": "test-peer",
            "ip": "192.168.1.100",
            "connected": True,
            "os": "linux",
            "groups": [{"id": "group1", "name": "dev"}]
        }
        
        peer = Peer.model_validate(peer_data)
        assert peer.id == "peer123"
        assert peer.name == "test-peer"
        assert peer.ip == IPv4Address("192.168.1.100")
        assert peer.connected is True
        assert peer.os == PeerOS.LINUX
        assert len(peer.groups) == 1
        assert peer.groups[0].name == "dev"
    
    def test_peer_with_timestamps(self):
        """Test Peer model with timestamp fields."""
        peer_data = {
            "id": "peer456",
            "name": "timestamp-peer",
            "ip": "10.0.0.1",
            "connected": False,
            "createdAt": "2024-01-15T10:30:00Z",
            "updatedAt": "2024-01-16T15:45:00Z",
            "lastSeen": "2024-01-16T14:00:00Z"
        }
        
        peer = Peer.model_validate(peer_data)
        assert isinstance(peer.created_at, datetime)
        assert isinstance(peer.updated_at, datetime)
        assert isinstance(peer.last_seen, datetime)
    
    def test_peer_status_property(self):
        """Test Peer status property."""
        connected_peer = Peer(id="p1", name="connected", ip="10.0.0.1", connected=True)
        assert connected_peer.status == PeerStatus.CONNECTED
        
        disconnected_peer = Peer(id="p2", name="disconnected", ip="10.0.0.2", connected=False)
        assert disconnected_peer.status == PeerStatus.DISCONNECTED
    
    def test_peer_group_methods(self):
        """Test Peer group-related methods."""
        peer = Peer(
            id="peer789",
            name="grouped-peer",
            ip="10.0.0.3",
            groups=[
                GroupRef(id="g1", name="developers"),
                GroupRef(id="g2", name="production")
            ]
        )
        
        assert peer.is_in_group("developers")
        assert peer.is_in_group("production")
        assert not peer.is_in_group("staging")
        assert peer.group_names == ["developers", "production"]
        assert peer.group_ids == ["g1", "g2"]
    
    def test_peer_list_operations(self):
        """Test PeerList model operations."""
        peer_list = PeerList(
            peers=[
                Peer(id="p1", name="peer1", ip="10.0.0.1", connected=True),
                Peer(id="p2", name="peer2", ip="10.0.0.2", connected=False),
                Peer(id="p3", name="peer3", ip="10.0.0.3", connected=True)
            ],
            total=3
        )
        
        assert len(peer_list) == 3
        assert peer_list[0].name == "peer1"
        
        # Test find methods
        found = peer_list.find_by_name("peer2")
        assert found is not None
        assert found.id == "p2"
        
        found_ip = peer_list.find_by_ip("10.0.0.3")
        assert found_ip is not None
        assert found_ip.name == "peer3"
        
        # Test property methods
        connected = peer_list.connected_peers
        assert len(connected) == 2
        
        disconnected = peer_list.disconnected_peers
        assert len(disconnected) == 1
    
    def test_peer_update_model(self):
        """Test PeerUpdate model."""
        update = PeerUpdate(
            name="new-name",
            sshEnabled=True,
            loginExpirationEnabled=False
        )
        
        update_dict = update.to_dict()
        assert update_dict["name"] == "new-name"
        assert update_dict["sshEnabled"] is True
        assert update_dict["loginExpirationEnabled"] is False


class TestGroupModels:
    """Test Group-related models."""
    
    def test_group_basic_creation(self):
        """Test basic Group model creation."""
        group_data = {
            "id": "group123",
            "name": "Development",
            "description": "Development environment",
            "peersCount": 5,
            "peers": [
                {"id": "p1", "name": "dev1"},
                {"id": "p2", "name": "dev2"}
            ]
        }
        
        group = Group.model_validate(group_data)
        assert group.id == "group123"
        assert group.name == "Development"
        assert group.description == "Development environment"
        assert group.peers_count == 5
        assert len(group.peers) == 2
    
    def test_group_type_parsing(self):
        """Test Group type parsing."""
        all_group = Group(
            id="g1",
            name="All",
            type="all"
        )
        assert all_group.group_type == GroupType.ALL
        assert all_group.is_all_group
        
        standard_group = Group(
            id="g2",
            name="Standard"
        )
        assert standard_group.group_type is None
        assert not standard_group.is_all_group
    
    def test_group_peer_operations(self):
        """Test Group peer manipulation methods."""
        group = Group(
            id="g1",
            name="Test Group",
            peers=[
                PeerRef(id="p1", name="peer1"),
                PeerRef(id="p2", name="peer2")
            ],
            peersCount=2
        )
        
        assert group.has_peer("p1")
        assert group.has_peer_by_name("peer2")
        assert not group.has_peer("p3")
        
        # Test add peer
        group.add_peer(PeerRef(id="p3", name="peer3"))
        assert group.has_peer("p3")
        assert group.peers_count == 3
        
        # Test remove peer
        removed = group.remove_peer("p1")
        assert removed is True
        assert not group.has_peer("p1")
        assert group.peers_count == 2
    
    def test_group_list_operations(self):
        """Test GroupList model operations."""
        group_list = GroupList(
            groups=[
                Group(id="g1", name="All", type="all", peersCount=10),
                Group(id="g2", name="Production", peersCount=5),
                Group(id="g3", name="Empty", peersCount=0)
            ]
        )
        
        assert len(group_list) == 3
        
        # Test find methods
        found = group_list.find_by_name("Production")
        assert found is not None
        assert found.id == "g2"
        
        all_group = group_list.all_group
        assert all_group is not None
        assert all_group.name == "All"
        
        # Test property methods
        non_empty = group_list.non_empty_groups
        assert len(non_empty) == 2
    
    def test_group_create_model(self):
        """Test GroupCreate model."""
        create = GroupCreate(
            name="New Group",
            description="Test description",
            peers=["p1", "p2", "p3"]
        )
        
        assert create.name == "New Group"
        assert len(create.peers) == 3
    
    def test_group_validation(self):
        """Test Group validation."""
        with pytest.raises(ValueError, match="cannot be empty"):
            GroupCreate(name="")
        
        with pytest.raises(ValueError, match="too long"):
            GroupCreate(name="a" * 101)


class TestPolicyModels:
    """Test Policy-related models."""
    
    def test_policy_rule_creation(self):
        """Test PolicyRule model creation."""
        rule_data = {
            "id": "rule123",
            "name": "Allow HTTP",
            "enabled": True,
            "sources": [{"id": "g1", "name": "Web Servers"}],
            "destinations": [{"id": "g2", "name": "Database"}],
            "protocol": "tcp",
            "ports": ["80", "443"],
            "bidirectional": False,
            "action": "accept"
        }
        
        rule = PolicyRule.model_validate(rule_data)
        assert rule.id == "rule123"
        assert rule.name == "Allow HTTP"
        assert rule.protocol == PolicyProtocol.TCP
        assert len(rule.ports) == 2
        assert rule.action == PolicyAction.ACCEPT
        assert not rule.bidirectional
    
    def test_policy_rule_properties(self):
        """Test PolicyRule properties."""
        rule = PolicyRule(
            id="r1",
            name="Test Rule",
            sources=[GroupRef(id="g1", name="Source")],
            destinations=[GroupRef(id="g2", name="Dest")],
            action="drop"
        )
        
        assert rule.is_deny_rule
        assert not rule.is_allow_rule
        assert rule.source_group_names == ["Source"]
        assert rule.destination_group_names == ["Dest"]
        assert rule.port_summary == "all ports"
    
    def test_policy_creation(self):
        """Test Policy model creation."""
        policy_data = {
            "id": "policy123",
            "name": "Default Policy",
            "description": "Default access policy",
            "enabled": True,
            "rules": [
                {
                    "id": "r1",
                    "name": "Rule 1",
                    "enabled": True,
                    "sources": [{"id": "g1", "name": "All"}],
                    "destinations": [{"id": "g1", "name": "All"}],
                    "protocol": "all",
                    "action": "accept"
                }
            ],
            "createdAt": "2024-01-15T10:00:00Z"
        }
        
        policy = Policy.model_validate(policy_data)
        assert policy.id == "policy123"
        assert policy.name == "Default Policy"
        assert len(policy.rules) == 1
        assert isinstance(policy.created_at, datetime)
    
    def test_policy_rule_methods(self):
        """Test Policy rule-related methods."""
        policy = Policy(
            id="p1",
            name="Test Policy",
            rules=[
                PolicyRule(
                    id="r1",
                    name="Rule 1",
                    enabled=True,
                    sources=[GroupRef(id="g1", name="Group1")],
                    destinations=[GroupRef(id="g2", name="Group2")]
                ),
                PolicyRule(
                    id="r2",
                    name="Rule 2",
                    enabled=False,
                    sources=[GroupRef(id="g2", name="Group2")],
                    destinations=[GroupRef(id="g3", name="Group3")]
                )
            ]
        )
        
        assert policy.rule_count == 2
        assert len(policy.enabled_rules) == 1
        assert len(policy.disabled_rules) == 1
        
        # Test get rule methods
        rule = policy.get_rule_by_id("r1")
        assert rule is not None
        assert rule.name == "Rule 1"
        
        rule_by_name = policy.get_rule_by_name("Rule 2")
        assert rule_by_name is not None
        assert not rule_by_name.enabled
    
    def test_policy_group_methods(self):
        """Test Policy group-related methods."""
        policy = Policy(
            id="p1",
            name="Test Policy",
            rules=[
                PolicyRule(
                    id="r1",
                    name="Rule 1",
                    sources=[GroupRef(id="g1", name="Group1")],
                    destinations=[GroupRef(id="g2", name="Group2")]
                ),
                PolicyRule(
                    id="r2",
                    name="Rule 2",
                    sources=[GroupRef(id="g2", name="Group2")],
                    destinations=[GroupRef(id="g3", name="Group3")]
                )
            ]
        )
        
        assert "Group1" in policy.all_source_groups
        assert "Group2" in policy.all_source_groups
        assert "Group3" in policy.all_destination_groups
        
        rules_for_g1 = policy.rules_for_source_group("g1")
        assert len(rules_for_g1) == 1
        assert rules_for_g1[0].id == "r1"
    
    def test_policy_list_operations(self):
        """Test PolicyList model operations."""
        policy_list = PolicyList(
            policies=[
                Policy(id="p1", name="Policy 1", enabled=True, rules=[]),
                Policy(id="p2", name="Policy 2", enabled=False, rules=[])
            ]
        )
        
        assert len(policy_list) == 2
        
        found = policy_list.find_by_name("Policy 1")
        assert found is not None
        assert found.enabled
        
        enabled = policy_list.enabled_policies
        assert len(enabled) == 1
        
        disabled = policy_list.disabled_policies
        assert len(disabled) == 1


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_peer_serialization(self):
        """Test Peer model serialization."""
        peer = Peer(
            id="p1",
            name="test",
            ip="10.0.0.1",
            connected=True,
            sshEnabled=True
        )
        
        # Test to_dict
        peer_dict = peer.to_dict()
        assert peer_dict["id"] == "p1"
        assert peer_dict["sshEnabled"] is True
        assert "connected" in peer_dict
        
        # Test from_api_response
        api_data = {
            "id": "p2",
            "name": "api-peer",
            "ip": "10.0.0.2",
            "connected": "true",  # String should be parsed
            "os": "Linux"  # Case should be handled
        }
        
        peer2 = Peer.from_api_response(api_data)
        assert peer2.connected is True
        assert peer2.os == PeerOS.LINUX
    
    def test_group_serialization(self):
        """Test Group model serialization."""
        group = Group(
            id="g1",
            name="Test",
            peersCount=5,
            type="all"
        )
        
        group_dict = group.to_dict()
        assert group_dict["peersCount"] == 5
        assert group_dict["type"] == "all"
    
    def test_policy_serialization(self):
        """Test Policy model serialization."""
        policy = Policy(
            id="pol1",
            name="Test Policy",
            enabled=True,
            rules=[
                PolicyRule(
                    id="r1",
                    name="Rule",
                    protocol="tcp",
                    action="accept",
                    sources=[],
                    destinations=[]
                )
            ]
        )
        
        policy_dict = policy.to_dict()
        assert policy_dict["name"] == "Test Policy"
        assert len(policy_dict["rules"]) == 1
        assert policy_dict["rules"][0]["protocol"] == "tcp"


class TestRealAPIResponses:
    """Test with real API response structures from manage_groups.py."""
    
    def test_real_peer_response(self):
        """Test parsing real peer API response."""
        peer_response = {
            "id": "d2itv26kurdc73fqb0cg",
            "name": "ab14ca4f6a9a",
            "ip": "100.109.212.184",
            "connected": True,
            "groups": [
                {"id": "d1n8evekurdc73cnnpig", "name": "All"},
                {"id": "d2itruukurdc73fqb0bg", "name": "Quarantine"}
            ],
            "os": "linux",
            "version": "0.24.3",
            "kernelVersion": "6.5.0-14-generic",
            "osVersion": "Ubuntu 23.10",
            "hostname": "container-host",
            "uiVersion": "",
            "dnsLabel": "ab14ca4f6a9a",
            "loginExpirationEnabled": False,
            "loginExpired": False,
            "approvalRequired": False,
            "sshEnabled": False,
            "accessiblePeersCount": 2,
            "createdAt": "2024-11-17T17:07:38.556Z",
            "lastSeen": "2024-11-17T17:08:15.423Z"
        }
        
        peer = Peer.model_validate(peer_response)
        assert peer.id == "d2itv26kurdc73fqb0cg"
        assert peer.name == "ab14ca4f6a9a"
        assert str(peer.ip) == "100.109.212.184"
        assert peer.connected is True
        assert len(peer.groups) == 2
        assert peer.is_in_group("All")
        assert peer.is_in_group("Quarantine")
        assert peer.os == PeerOS.LINUX
        assert peer.version == "0.24.3"
        assert peer.hostname == "container-host"
        assert peer.accessible_peers_count == 2
    
    def test_real_group_response(self):
        """Test parsing real group API response."""
        group_response = {
            "id": "d1n8evekurdc73cnnpig",
            "name": "All",
            "issued": "api",
            "peersCount": 3,
            "peers": [
                {"id": "d2itv26kurdc73fqb0cg", "name": "ab14ca4f6a9a"},
                {"id": "d2itvbekurdc73fqb0d0", "name": "dev-container"},
                {"id": "d2iu0rukurdc73fqb0dg", "name": "MacBook-Pro"}
            ]
        }
        
        group = Group.model_validate(group_response)
        assert group.id == "d1n8evekurdc73cnnpig"
        assert group.name == "All"
        assert group.peers_count == 3
        assert len(group.peers) == 3
        assert group.has_peer("d2itv26kurdc73fqb0cg")
        assert group.is_all_group
    
    def test_real_policy_response(self):
        """Test parsing real policy API response."""
        policy_response = {
            "id": "d1n8evekurdc73cnnpj0",
            "name": "Default",
            "description": "This is a default rule that allows connections between all the resources",
            "enabled": False,
            "rules": [
                {
                    "id": "d1n8evekurdc73cnnpj0",
                    "name": "Default",
                    "description": "",
                    "enabled": False,
                    "sources": [
                        {"id": "d1n8evekurdc73cnnpig", "name": "All", "peersCount": 3}
                    ],
                    "destinations": [
                        {"id": "d1n8evekurdc73cnnpig", "name": "All", "peersCount": 3}
                    ],
                    "bidirectional": True,
                    "protocol": "all",
                    "ports": [],
                    "action": "accept"
                }
            ],
            "sourcePostureChecks": []
        }
        
        policy = Policy.model_validate(policy_response)
        assert policy.id == "d1n8evekurdc73cnnpj0"
        assert policy.name == "Default"
        assert policy.enabled is False
        assert len(policy.rules) == 1
        
        rule = policy.rules[0]
        assert rule.name == "Default"
        assert rule.protocol == PolicyProtocol.ALL
        assert rule.action == PolicyAction.ACCEPT
        assert rule.bidirectional is True
        assert len(rule.sources) == 1
        assert rule.sources[0].name == "All"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])