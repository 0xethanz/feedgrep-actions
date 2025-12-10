#!/usr/bin/env python3
"""
FeedGrep GitHub Actions 版本 - RSS处理脚本
将RSS内容存储到GitHub Issues中
"""

import os
import sys
import json
import yaml
import feedparser
import argparse
from datetime import datetime
import requests
from typing import List, Dict, Optional
from urllib.parse import quote

class GitHubIssuesDataStore:
    """使用GitHub Issues作为数据存储的实现"""
    
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
    
    def create_item_issue(self, item: Dict, category: str, source_name: str, keyword: str = None) -> bool:
        """
        在GitHub Issues中创建一个新的RSS项目记录
        
        Args:
            item: RSS项目数据
            category: 分类
            source_name: RSS源名称
            keyword: 匹配的关键词（如果有）
        
        Returns:
            是否创建成功
        """
        try:
            title = item.get('title', 'Untitled')[:200]  # GitHub title限制
            link = item.get('link', '')
            description = item.get('description', '')
            published = item.get('published', '')
            
            # 构建Issue body
            body = f"""
## 源信息
- **分类**: {category}
- **来源**: {source_name}
- **链接**: [{link}]({link})
- **发布时间**: {published}

## 内容
{description[:1000]}

---
_自动创建于 {datetime.now().isoformat()}_
"""
            
            # 构建标签
            labels = [
                category,
                "rss-item",
                f"source:{source_name.replace(' ', '-')}",
            ]
            if keyword:
                labels.append(f"keyword:{keyword}")
            
            # 创建Issue
            data = {
                "title": title,
                "body": body,
                "labels": labels
            }
            
            response = requests.post(
                f"{self.base_url}/issues",
                json=data,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"✅ 创建Issue成功: {title}")
                return True
            else:
                print(f"❌ 创建Issue失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 创建Issue时出错: {e}")
            return False
    
    def get_items_by_label(self, label: str, state: str = "open") -> List[Dict]:
        """
        通过标签获取Issues
        
        Args:
            label: 标签名称
            state: 状态 (open/closed/all)
        
        Returns:
            Issues列表
        """
        try:
            url = f"{self.base_url}/issues?labels={quote(label)}&state={state}&per_page=100"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 获取Issues失败: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 获取Issues时出错: {e}")
            return []
    
    def check_item_exists(self, title: str) -> bool:
        """检查该标题的Issue是否已存在"""
        try:
            url = f"{self.base_url}/issues?q=title:{quote(title)}&state=all"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                issues = response.json()
                return len(issues) > 0
            return False
                
        except Exception as e:
            print(f"⚠️  检查Issue时出错: {e}")
            return False


class FeedGrepGitHubActions:
    """GitHub Actions环境下的FeedGrep处理器"""
    
    def __init__(self, config_path: str, token: str, owner: str, repo: str):
        """初始化处理器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.store = GitHubIssuesDataStore(token, owner, repo)
        self.processed_items = 0
        self.skipped_items = 0
    
    def fetch_feed(self, feed_url: str) -> Optional[feedparser.FeedParserDict]:
        """获取RSS源"""
        try:
            print(f"⏳ 获取RSS: {feed_url}")
            result = feedparser.parse(feed_url)
            
            if result.status == 200 or hasattr(result, 'entries'):
                return result
            else:
                print(f"❌ 获取失败 (Status: {result.status})")
                return None
                
        except Exception as e:
            print(f"❌ 获取RSS时出错: {e}")
            return None
    
    def process_feed(self, feed_url: str, category: str, source_name: str):
        """处理单个RSS源"""
        print(f"\n📌 处理 {source_name} ({category})")
        
        feed = self.fetch_feed(feed_url)
        if not feed:
            return
        
        entries = feed.get('entries', [])[:10]  # 只处理最新10条
        
        for entry in entries:
            # 去重检查
            if self.store.check_item_exists(entry.get('title', 'Untitled')):
                print(f"⏭️  已存在: {entry.get('title', 'Untitled')[:50]}")
                self.skipped_items += 1
                continue
            
            # 创建Issue记录
            if self.store.create_item_issue(entry, category, source_name):
                self.processed_items += 1
    
    def process_all_feeds(self):
        """处理所有RSS源"""
        print("=" * 60)
        print("🚀 开始处理RSS源")
        print("=" * 60)
        
        categories = self.config.get('categories', {})
        
        for category, sources in categories.items():
            print(f"\n📂 分类: {category}")
            
            for source in sources:
                source_name = source.get('name', 'Unknown')
                source_url = source.get('url', '')
                
                if source_url:
                    self.process_feed(source_url, category, source_name)
        
        print("\n" + "=" * 60)
        print(f"✅ 处理完成")
        print(f"   新增: {self.processed_items}")
        print(f"   重复跳过: {self.skipped_items}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='FeedGrep GitHub Actions RSS处理器')
    parser.add_argument('--config', default='feedgrep.yaml', help='配置文件路径')
    parser.add_argument('--token', required=True, help='GitHub访问令牌')
    parser.add_argument('--owner', required=True, help='仓库所有者')
    parser.add_argument('--repo', required=True, help='仓库名称')
    
    args = parser.parse_args()
    
    # 验证配置文件
    if not os.path.exists(args.config):
        print(f"❌ 配置文件不存在: {args.config}")
        sys.exit(1)
    
    # 创建处理器并处理RSS
    processor = FeedGrepGitHubActions(
        args.config,
        args.token,
        args.owner,
        args.repo
    )
    
    processor.process_all_feeds()


if __name__ == '__main__':
    main()
