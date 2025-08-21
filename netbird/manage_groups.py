#!/usr/bin/env python3
"""
NetBird Groups and Peers Management Script

管理 NetBird Peers 和 Groups 的 Python 脚本
"""

import os
import sys
import json
import argparse
import requests
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class NetBirdManager:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or os.getenv("NETBIRD_API_URL", "https://api.netbird.io")
        self.api_key = api_key or os.getenv("NETBIRD_API_KEY")
        
        if not self.api_key:
            print("错误: 请设置环境变量 NETBIRD_API_KEY")
            print("获取 API Key: https://app.netbird.io/settings/personal-access-token")
            sys.exit(1)
        
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make API request to NetBird"""
        url = f"{self.api_url}/api{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            print(f"API 请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"响应内容: {e.response.text}")
            sys.exit(1)
    
    def list_peers(self) -> List[Dict]:
        """List all peers"""
        print("获取 Peers 列表...")
        peers = self._make_request("GET", "/peers")
        
        if not peers:
            print("没有找到 peers")
            return []
        
        print(f"找到 {len(peers)} 个 peers:")
        for peer in peers:
            # Handle groups - they might be dicts with id and name
            groups_data = peer.get("groups", [])
            if groups_data and isinstance(groups_data[0], dict):
                groups = ", ".join([g.get("name", g.get("id", "Unknown")) for g in groups_data])
            else:
                groups = ", ".join(groups_data) if groups_data else "None"
            
            print(f"ID: {peer['id']}")
            print(f"Name: {peer.get('name', 'N/A')}")
            print(f"IP: {peer['ip']}")
            print(f"Status: {'已连接' if peer.get('connected') else '已断开'}")
            print(f"Groups: {groups}")
            print("---")
        
        return peers
    
    def list_groups(self) -> List[Dict]:
        """List all groups"""
        print("获取 Groups 列表...")
        groups = self._make_request("GET", "/groups")
        
        if not groups:
            print("没有找到 groups")
            return []
        
        print(f"找到 {len(groups)} 个 groups:")
        for group in groups:
            # Handle peers - they might be dicts, strings, or None
            peers_data = group.get("peers")
            if peers_data is None:
                peers_data = []
            
            if peers_data and isinstance(peers_data[0], dict):
                peers = ", ".join([p.get("name", p.get("id", "Unknown")) for p in peers_data])
            else:
                peers = ", ".join(peers_data) if peers_data else "None"
            
            print(f"ID: {group['id']}")
            print(f"Name: {group['name']}")
            print(f"Peers Count: {len(peers_data)}")
            print(f"Peers: {peers}")
            print("---")
        
        return groups
    
    def list_policies(self) -> List[Dict]:
        """List all policies"""
        print("获取 Policies 列表...")
        policies = self._make_request("GET", "/policies")
        
        if not policies:
            print("没有找到 policies")
            return []
        
        print(f"找到 {len(policies)} 个 policies:")
        for policy in policies:
            # Policies have a rules array, need to extract sources/destinations from rules
            rules = policy.get("rules", [])
            
            # Collect all unique sources and destinations from all rules
            all_sources = []
            all_destinations = []
            bidirectional = False
            
            for rule in rules:
                sources = rule.get("sources", [])
                destinations = rule.get("destinations", [])
                bidirectional = bidirectional or rule.get("bidirectional", False)
                
                for src in sources:
                    name = src.get("name", src.get("id", "Unknown"))
                    if name not in all_sources:
                        all_sources.append(name)
                
                for dest in destinations:
                    name = dest.get("name", dest.get("id", "Unknown"))
                    if name not in all_destinations:
                        all_destinations.append(name)
            
            source_groups = ", ".join(all_sources) if all_sources else "None"
            dest_groups = ", ".join(all_destinations) if all_destinations else "None"
            
            print(f"ID: {policy['id']}")
            print(f"Name: {policy['name']}")
            print(f"Description: {policy.get('description', 'N/A')}")
            print(f"Enabled: {'是' if policy.get('enabled') else '否'}")
            print(f"Source Groups: {source_groups}")
            print(f"Destination Groups: {dest_groups}")
            print(f"Bidirectional: {'是' if bidirectional else '否'}")
            print(f"Rules Count: {len(rules)}")
            print("---")
        
        return policies
    
    def create_group(self, name: str, description: str = "") -> Dict:
        """Create a new group"""
        print(f"创建 Group: {name}")
        
        data = {
            "name": name,
            "description": description,
            "peers": []
        }
        
        group = self._make_request("POST", "/groups", data)
        print(f"Group 创建成功: {group['id']}")
        return group
    
    def get_group_by_name(self, name: str) -> Optional[Dict]:
        """Get group by name"""
        groups = self._make_request("GET", "/groups")
        
        for group in groups:
            if group["name"] == name:
                return group
        
        return None
    
    def add_peers_to_group(self, peer_ids: List[str], group_name: str, create_group_if_missing: bool = False) -> Dict:
        """Add peers to a group"""
        print(f"将 Peers {peer_ids} 添加到 Group '{group_name}'")
        
        # Get or create group
        group = self.get_group_by_name(group_name)
        
        if not group:
            if create_group_if_missing:
                print(f"Group '{group_name}' 不存在，正在创建...")
                group = self.create_group(group_name, "Auto-created group")
            else:
                print(f"错误: Group '{group_name}' 不存在。使用 --create-group 自动创建。")
                sys.exit(1)
        
        # Add new peers to existing peers list
        existing_peers = set(group.get("peers", []))
        all_peers = list(existing_peers.union(set(peer_ids)))
        
        # Update group
        data = {
            "name": group_name,
            "peers": all_peers
        }
        
        updated_group = self._make_request("PUT", f"/groups/{group['id']}", data)
        print(f"Peers 成功添加到 Group。当前 Peers: {updated_group['peers']}")
        
        return updated_group
    
    def create_policy(self, group_name: str, policy_name: str, description: str = "", bidirectional: bool = True) -> Dict:
        """Create or update policy for group internal communication"""
        print(f"为 Group '{group_name}' 创建 Policy: {policy_name}")
        
        # Get group
        group = self.get_group_by_name(group_name)
        if not group:
            print(f"错误: Group '{group_name}' 不存在")
            sys.exit(1)
        
        group_id = group["id"]
        
        # Check if policy already exists
        policies = self._make_request("GET", "/policies")
        existing_policy = None
        
        for policy in policies:
            if policy["name"] == policy_name:
                existing_policy = policy
                break
        
        # Prepare policy data with the correct structure (using rules array)
        data = {
            "name": policy_name,
            "description": description,
            "enabled": True,
            "rules": [
                {
                    "name": policy_name,
                    "description": description,
                    "enabled": True,
                    "sources": [group_id],  # Just use group IDs
                    "destinations": [group_id],
                    "bidirectional": bidirectional,
                    "protocol": "all",
                    "ports": [],
                    "action": "accept"
                }
            ]
        }
        
        if existing_policy:
            print("Policy 已存在，正在更新...")
            policy = self._make_request("PUT", f"/policies/{existing_policy['id']}", data)
        else:
            policy = self._make_request("POST", "/policies", data)
        
        print(f"Policy 创建/更新成功: {policy['id']}")
        return policy


def main():
    parser = argparse.ArgumentParser(description="NetBird Groups and Peers Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List commands
    subparsers.add_parser("list-peers", help="列出所有 peers")
    subparsers.add_parser("list-groups", help="列出所有 groups")
    subparsers.add_parser("list-policies", help="列出所有 policies")
    
    # Create group command
    create_group_parser = subparsers.add_parser("create-group", help="创建新的 group")
    create_group_parser.add_argument("-n", "--name", required=True, help="Group 名称")
    create_group_parser.add_argument("-d", "--description", default="", help="Group 描述")
    
    # Add peers to group command
    add_peers_parser = subparsers.add_parser("add-peers-to-group", help="将 peers 添加到 group")
    add_peers_parser.add_argument("-p", "--peer-ids", required=True, help="Peer IDs (逗号分隔)")
    add_peers_parser.add_argument("-g", "--group-name", required=True, help="Group 名称")
    add_peers_parser.add_argument("-c", "--create-group", action="store_true", help="如果 group 不存在则创建")
    
    # Create policy command
    create_policy_parser = subparsers.add_parser("create-policy", help="创建 policy 使 group 内部互通")
    create_policy_parser.add_argument("-g", "--group-name", required=True, help="Group 名称")
    create_policy_parser.add_argument("-n", "--policy-name", required=True, help="Policy 名称")
    create_policy_parser.add_argument("-d", "--description", default="", help="Policy 描述")
    create_policy_parser.add_argument("-b", "--bidirectional", type=bool, default=True, help="双向通信")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = NetBirdManager()
    
    try:
        if args.command == "list-peers":
            manager.list_peers()
        
        elif args.command == "list-groups":
            manager.list_groups()
        
        elif args.command == "list-policies":
            manager.list_policies()
        
        elif args.command == "create-group":
            manager.create_group(args.name, args.description)
        
        elif args.command == "add-peers-to-group":
            peer_ids = [p.strip() for p in args.peer_ids.split(",")]
            manager.add_peers_to_group(peer_ids, args.group_name, args.create_group)
        
        elif args.command == "create-policy":
            manager.create_policy(args.group_name, args.policy_name, args.description, args.bidirectional)
        
        else:
            print(f"未知命令: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()