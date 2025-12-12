#!/usr/bin/env python3
"""
清空所有RSS相关的GitHub Issues
用于重置去重记忆
"""

import os
import sys
import argparse
import requests
from typing import List, Dict


class IssuesCleaner:
    """清理GitHub Issues的工具类"""
    
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def get_all_rss_issues(self) -> List[Dict]:
        """获取所有带有rss-item标签的Issues"""
        issues = []
        page = 1
        
        print("⏳ 正在获取所有RSS相关的Issues...")
        
        while True:
            try:
                # 获取带有rss-item标签的issues
                url = f"{self.base_url}/issues?labels=rss-item&state=all&per_page=100&page={page}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    print(f"❌ 获取Issues失败: {response.status_code}")
                    break
                
                batch = response.json()
                if not batch:
                    break
                
                issues.extend(batch)
                print(f"   已获取 {len(issues)} 条...")
                page += 1
                
            except Exception as e:
                print(f"⚠️  获取Issues时出错 (第{page}页): {e}")
                break
        
        return issues
    
    def close_issue(self, issue_number: int) -> bool:
        """关闭一个Issue"""
        try:
            url = f"{self.base_url}/issues/{issue_number}"
            data = {"state": "closed"}
            response = requests.patch(url, json=data, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ 关闭Issue #{issue_number}失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 关闭Issue #{issue_number}时出错: {e}")
            return False
    
    def delete_issue(self, issue_number: int) -> bool:
        """
        删除一个Issue（注意：GitHub API不支持直接删除Issue）
        只能关闭Issue，然后添加"deleted"标签
        """
        # 先关闭Issue
        issue_closed = self.close_issue(issue_number)
        if not issue_closed:
            return False
        
        try:
            # 添加"deleted"标签（使用正确的格式）
            url = f"{self.base_url}/issues/{issue_number}/labels"
            # 注意：这里会创建标签如果它不存在
            response = requests.post(url, json=["deleted"], headers=self.headers, timeout=10)
            
            if response.status_code in [200, 201]:
                return True
            else:
                # 如果失败（可能是标签已存在等），只要Issue已关闭就认为成功
                print(f"⚠️  添加标签返回 {response.status_code}，但Issue已关闭")
                return True
                
        except Exception as e:
            print(f"⚠️  添加标签时出错: {e}")
            # Issue已经关闭，即使添加标签失败也认为操作成功
            return True


def main():
    parser = argparse.ArgumentParser(
        description='清空所有RSS相关的GitHub Issues',
        epilog='注意：GitHub API不支持直接删除Issues，只能关闭它们'
    )
    parser.add_argument('--token', required=True, help='GitHub访问令牌')
    parser.add_argument('--owner', required=True, help='仓库所有者')
    parser.add_argument('--repo', required=True, help='仓库名称')
    parser.add_argument('--action', 
                       choices=['close', 'mark-deleted', 'list'],
                       default='list',
                       help='执行的操作: list(列出), close(关闭), mark-deleted(关闭并标记删除)')
    parser.add_argument('--confirm', 
                       action='store_true',
                       help='确认执行操作（不加此参数将只显示预览）')
    
    args = parser.parse_args()
    
    cleaner = IssuesCleaner(args.token, args.owner, args.repo)
    
    # 获取所有RSS相关的Issues
    issues = cleaner.get_all_rss_issues()
    
    if not issues:
        print("✅ 没有找到任何RSS相关的Issues")
        return
    
    print(f"\n找到 {len(issues)} 个RSS相关的Issues:")
    print("=" * 60)
    
    # 列出所有issues
    for issue in issues[:10]:  # 只显示前10个
        state = "✓ 已关闭" if issue['state'] == 'closed' else "○ 打开"
        print(f"{state} #{issue['number']}: {issue['title'][:60]}")
    
    if len(issues) > 10:
        print(f"... 还有 {len(issues) - 10} 个")
    
    print("=" * 60)
    
    # 执行操作
    if args.action == 'list':
        print("\n💡 仅列出模式。使用 --action close 或 --action mark-deleted 来执行操作")
        print("💡 添加 --confirm 参数来确认执行")
        return
    
    if not args.confirm:
        print(f"\n⚠️  预览模式：将会对 {len(issues)} 个Issues执行 '{args.action}' 操作")
        print("⚠️  添加 --confirm 参数来真正执行操作")
        return
    
    # 确认执行
    print(f"\n🚀 开始执行 '{args.action}' 操作...")
    
    success_count = 0
    fail_count = 0
    
    for issue in issues:
        issue_number = issue['number']
        
        if args.action == 'close':
            if cleaner.close_issue(issue_number):
                print(f"✅ 已关闭 #{issue_number}: {issue['title'][:60]}")
                success_count += 1
            else:
                fail_count += 1
        
        elif args.action == 'mark-deleted':
            if cleaner.delete_issue(issue_number):
                print(f"✅ 已标记删除 #{issue_number}: {issue['title'][:60]}")
                success_count += 1
            else:
                fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 操作完成!")
    print(f"   成功: {success_count}")
    print(f"   失败: {fail_count}")
    print("=" * 60)
    
    print("\n📝 说明:")
    print("- GitHub API不支持直接删除Issues")
    print("- 去重检查使用 state=all 查询，包括已关闭的Issues")
    print("- 如需重新处理相同内容，建议使用手动删除或等待Issues被自动归档")


if __name__ == '__main__':
    main()
