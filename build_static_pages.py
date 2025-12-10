#!/usr/bin/env python3
"""
FeedGrep GitHub Actions - 静态页面生成脚本
从GitHub Issues读取数据，生成静态JSON和HTML文件
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime
from typing import List, Dict
from collections import defaultdict
from urllib.parse import quote


class GitHubIssuesReader:
    """从GitHub Issues读取数据"""
    
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
    
    def get_all_issues(self, state: str = "open") -> List[Dict]:
        """获取所有Issues"""
        issues = []
        page = 1
        
        while True:
            try:
                url = f"{self.base_url}/issues?state={state}&per_page=100&page={page}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code != 200:
                    break
                
                batch = response.json()
                if not batch:
                    break
                
                issues.extend(batch)
                page += 1
                
            except Exception as e:
                print(f"⚠️  获取Issues时出错 (第{page}页): {e}")
                break
        
        return issues
    
    def parse_issue_to_item(self, issue: Dict) -> Dict:
        """将GitHub Issue转换为RSS项目"""
        body = issue.get('body', '')
        labels = [label['name'] for label in issue.get('labels', [])]
        
        # 提取分类和源信息
        category = labels[0] if labels else 'uncategorized'
        source_name = 'Unknown'
        
        for label in labels:
            if label.startswith('source:'):
                source_name = label.replace('source:', '').replace('-', ' ')
                break
        
        # 提取链接（从body中）
        link = ''
        if '[' in body and '](' in body:
            start = body.find('[')
            end = body.find(']', start)
            link_start = body.find('](', end)
            link_end = body.find(')', link_start)
            if link_start != -1 and link_end != -1:
                link = body[link_start+2:link_end]
        
        return {
            'id': issue.get('id'),
            'title': issue.get('title', ''),
            'link': link,
            'description': body[:200] + '...' if len(body) > 200 else body,
            'published': issue.get('created_at', ''),
            'category': category,
            'source_name': source_name,
            'url': issue.get('html_url', '')
        }


class StaticPageBuilder:
    """构建静态页面"""
    
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/api", exist_ok=True)
    
    def build_feeds_json(self, items: List[Dict]) -> Dict:
        """构建feeds.json"""
        feeds = defaultdict(lambda: {
            'count': 0,
            'items': []
        })
        
        for item in items:
            category = item.get('category', 'uncategorized')
            feeds[category]['count'] += 1
            feeds[category]['items'].append(item)
        
        return dict(feeds)
    
    def build_categories_json(self, items: List[Dict]) -> List[str]:
        """构建categories.json"""
        categories = set()
        for item in items:
            categories.add(item.get('category', 'uncategorized'))
        return sorted(list(categories))
    
    def save_json(self, filename: str, data: Dict):
        """保存JSON文件"""
        try:
            filepath = f"{self.output_dir}/api/{filename}"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 生成: {filepath}")
        except Exception as e:
            print(f"❌ 保存JSON失败: {e}")
    
    def save_html(self, filename: str, content: str):
        """保存HTML文件"""
        try:
            filepath = f"{self.output_dir}/{filename}"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 生成: {filepath}")
        except Exception as e:
            print(f"❌ 保存HTML失败: {e}")
    
    def build_index_html(self) -> str:
        """生成首页HTML"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FeedGrep - 免费RSS阅读器</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.js"></script>
</head>
<body class="bg-gray-50">
    <div id="app" class="min-h-screen">
        <nav class="bg-white shadow">
            <div class="max-w-7xl mx-auto px-4 py-4">
                <h1 class="text-2xl font-bold text-indigo-600">
                    <i class="fas fa-rss"></i> FeedGrep
                </h1>
                <p class="text-gray-600 text-sm mt-1">通过GitHub Actions + GitHub Pages 0成本运行</p>
            </div>
        </nav>
        
        <main class="max-w-7xl mx-auto px-4 py-8">
            <!-- 统计信息 -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="text-3xl font-bold text-indigo-600">{{ totalItems }}</div>
                    <div class="text-gray-600">条RSS内容</div>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="text-3xl font-bold text-green-600">{{ categories.length }}</div>
                    <div class="text-gray-600">分类</div>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="text-3xl font-bold text-blue-600">{{ updateTime }}</div>
                    <div class="text-gray-600">最后更新</div>
                </div>
            </div>
            
            <!-- 分类列表 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div v-for="category in categories" :key="category" class="bg-white rounded-lg shadow overflow-hidden">
                    <div class="bg-indigo-100 px-6 py-3">
                        <h2 class="text-lg font-bold text-indigo-900">{{ category }}</h2>
                        <p class="text-sm text-indigo-700">{{ feeds[category]?.count || 0 }} 条内容</p>
                    </div>
                    <div class="p-6">
                        <div v-for="item in feeds[category]?.items?.slice(0, 3)" :key="item.id" class="mb-4 pb-4 border-b last:border-b-0">
                            <a :href="item.link" target="_blank" class="text-indigo-600 hover:underline font-semibold">
                                {{ item.title }}
                            </a>
                            <p class="text-sm text-gray-600 mt-1">{{ item.source_name }}</p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
        
        <footer class="bg-gray-800 text-white mt-12 py-8">
            <div class="max-w-7xl mx-auto px-4 text-center">
                <p>完全免费的RSS聚合器 | <a href="https://github.com/0xethanz/feedgrep" class="underline">GitHub</a></p>
                <p class="text-sm text-gray-400 mt-2">由 GitHub Actions + GitHub Pages 自动生成</p>
            </div>
        </footer>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6/js/all.js"></script>
    <script>
        const { createApp } = Vue;
        
        createApp({
            data() {
                return {
                    feeds: {},
                    categories: [],
                    updateTime: '加载中...'
                };
            },
            computed: {
                totalItems() {
                    return Object.values(this.feeds).reduce((sum, cat) => sum + (cat.count || 0), 0);
                }
            },
            async mounted() {
                try {
                    const response = await fetch('./api/feeds.json');
                    this.feeds = await response.json();
                    
                    const catResponse = await fetch('./api/categories.json');
                    this.categories = await catResponse.json();
                    
                    this.updateTime = new Date().toLocaleString('zh-CN');
                } catch (e) {
                    console.error('加载数据失败:', e);
                }
            }
        }).mount('#app');
    </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description='FeedGrep 静态页面生成器')
    parser.add_argument('--token', required=True, help='GitHub访问令牌')
    parser.add_argument('--owner', required=True, help='仓库所有者')
    parser.add_argument('--repo', required=True, help='仓库名称')
    parser.add_argument('--output', default='docs', help='输出目录')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📄 开始构建静态页面")
    print("=" * 60)
    
    # 读取Issues数据
    reader = GitHubIssuesReader(args.token, args.owner, args.repo)
    print("⏳ 从GitHub读取数据...")
    issues = reader.get_all_issues()
    
    if not issues:
        print("❌ 没有找到任何Issues")
        return
    
    # 转换数据
    items = [reader.parse_issue_to_item(issue) for issue in issues]
    print(f"✅ 读取了 {len(items)} 条内容")
    
    # 生成静态页面
    builder = StaticPageBuilder(args.output)
    
    # 生成JSON数据
    feeds = builder.build_feeds_json(items)
    categories = builder.build_categories_json(items)
    
    builder.save_json('feeds.json', feeds)
    builder.save_json('categories.json', categories)
    builder.save_json('items.json', {'items': items, 'count': len(items)})
    
    # 生成HTML
    builder.save_html('index.html', builder.build_index_html())
    
    print("\n" + "=" * 60)
    print("✅ 页面构建完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
