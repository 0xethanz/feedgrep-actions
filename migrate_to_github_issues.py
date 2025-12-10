#!/usr/bin/env python3
"""
FeedGrep 数据迁移脚本
将SQLite数据库中的数据迁移到GitHub Issues
"""

import sqlite3
import requests
import argparse
import sys
from datetime import datetime
from typing import List, Dict
from urllib.parse import quote


class GitHubIssuesDataStore:
    """使用GitHub Issues作为数据存储"""
    
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
    
    def create_issue_for_item(self, item: Dict) -> bool:
        """为数据库项目创建GitHub Issue"""
        try:
            title = item.get('title', 'Untitled')[:200]
            link = item.get('link', '')
            description = item.get('description', '')
            category = item.get('category', 'uncategorized')
            source_name = item.get('source_name', 'Unknown')
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
_从SQLite数据库迁移于 {datetime.now().isoformat()}_
"""
            
            # 构建标签
            labels = [
                category,
                "rss-item",
                "migrated",
                f"source:{source_name.replace(' ', '-')}"
            ]
            
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
                print(f"✅ 迁移: {title[:50]}")
                return True
            else:
                print(f"❌ 失败: {response.status_code} - {response.text[:100]}")
                return False
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False


class SQLiteReader:
    """从SQLite读取数据"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def get_all_items(self) -> List[Dict]:
        """获取数据库中的所有项目"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询所有项目
            cursor.execute('''
                SELECT id, title, link, description, category, source_name, published
                FROM feedgrep_items
                ORDER BY created_at DESC
            ''')
            
            items = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return items
            
        except Exception as e:
            print(f"❌ 读取数据库失败: {e}")
            return []
    
    def get_items_by_category(self, category: str) -> List[Dict]:
        """按分类获取项目"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, title, link, description, category, source_name, published
                FROM feedgrep_items
                WHERE category = ?
                ORDER BY created_at DESC
            ''', (category,))
            
            items = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return items
            
        except Exception as e:
            print(f"❌ 查询分类数据失败: {e}")
            return []


def main():
    parser = argparse.ArgumentParser(description='FeedGrep SQLite到GitHub Issues数据迁移工具')
    parser.add_argument('--db', required=True, help='SQLite数据库文件路径')
    parser.add_argument('--token', required=True, help='GitHub访问令牌')
    parser.add_argument('--owner', required=True, help='GitHub用户名')
    parser.add_argument('--repo', default='feedgrep', help='仓库名称')
    parser.add_argument('--category', help='只迁移指定分类（可选）')
    parser.add_argument('--limit', type=int, help='限制迁移数量（可选）')
    parser.add_argument('--dry-run', action='store_true', help='干运行模式，不真正迁移')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📦 FeedGrep 数据迁移工具")
    print("=" * 60)
    
    # 读取SQLite数据
    reader = SQLiteReader(args.db)
    
    if args.category:
        print(f"⏳ 读取分类 '{args.category}' 的数据...")
        items = reader.get_items_by_category(args.category)
    else:
        print("⏳ 读取所有数据...")
        items = reader.get_all_items()
    
    if not items:
        print("❌ 没有找到任何数据")
        return
    
    print(f"✅ 找到 {len(items)} 条数据\n")
    
    # 应用限制
    if args.limit:
        items = items[:args.limit]
        print(f"📌 应用限制: 只迁移前 {args.limit} 条\n")
    
    # 干运行模式
    if args.dry_run:
        print("🔍 干运行模式 - 显示将迁移的数据:\n")
        for i, item in enumerate(items[:5], 1):
            print(f"{i}. [{item['category']}] {item['title']}")
        if len(items) > 5:
            print(f"   ... 还有 {len(items) - 5} 条")
        return
    
    # 确认迁移
    print(f"⚠️  将迁移 {len(items)} 条数据到GitHub Issues")
    confirm = input("继续？(y/n): ")
    if confirm.lower() != 'y':
        print("❌ 取消迁移")
        return
    
    # 执行迁移
    store = GitHubIssuesDataStore(args.token, args.owner, args.repo)
    
    print("\n" + "=" * 60)
    print("🚀 开始迁移...")
    print("=" * 60)
    
    success_count = 0
    failed_count = 0
    
    for i, item in enumerate(items, 1):
        if store.create_issue_for_item(item):
            success_count += 1
        else:
            failed_count += 1
        
        # 进度显示
        if i % 10 == 0:
            print(f"   进度: {i}/{len(items)}")
    
    print("\n" + "=" * 60)
    print("✅ 迁移完成!")
    print(f"   成功: {success_count}")
    print(f"   失败: {failed_count}")
    print("=" * 60)
    
    if failed_count > 0:
        print("\n⚠️  部分数据迁移失败，请检查GitHub API限制")
        print("   GitHub API限制: 60个请求/小时 (未认证)")
        print("   需要等待1小时后重试，或使用有效令牌")


if __name__ == '__main__':
    main()
