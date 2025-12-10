# FeedGrep GitHub Actions 部署配置文件

## 快速复制文件

将以下命令在项目根目录运行，快速部署GitHub Actions工作流：

```bash
# 1. 复制工作流文件
cp -r github-actions-deploy/.github/workflows .github/

# 2. 复制脚本
cp github-actions-deploy/fetch_feeds_github.py .
cp github-actions-deploy/build_static_pages.py .

# 3. 提交到GitHub
git add .
git commit -m "feat: 添加GitHub Actions自动化部署"
git push origin main
```

## 文件说明

### 工作流文件 (.github/workflows/)

#### `rss-feed.yml`
**功能**: 定时处理RSS源，将内容存储到GitHub Issues

**触发条件**:
- 每天UTC 02:00自动运行（北京时间10:00）
- 可手动通过Actions页面触发
- 修改feedgrep.yaml时自动运行

**执行流程**:
1. 检出代码
2. 设置Python 3.11环境
3. 安装依赖: feedparser, pyyaml, requests
4. 运行RSS处理脚本
5. 触发页面构建工作流
6. 发送完成通知

**关键环境变量**:
- `GH_TOKEN`: GitHub访问令牌（从Secrets读取）
- `github.repository_owner`: 仓库所有者
- `github.event.repository.name`: 仓库名称

#### `build-pages.yml`
**功能**: 从GitHub Issues生成静态页面并部署到GitHub Pages

**触发条件**:
- 由rss-feed.yml手动触发
- 可通过Actions页面手动触发
- 修改build-pages.yml时自动运行

**执行流程**:
1. 检出代码
2. 设置Python 3.11环境
3. 安装依赖
4. 从GitHub Issues读取数据
5. 生成JSON格式的API
6. 复制前端文件
7. 部署到GitHub Pages
8. 生成部署摘要

### Python脚本

#### `fetch_feeds_github.py`
处理RSS源，存储到GitHub Issues。

```bash
python fetch_feeds_github.py \
  --config feedgrep.yaml \
  --token YOUR_GITHUB_TOKEN \
  --owner YOUR_USERNAME \
  --repo feedgrep
```

**主要类**:
- `GitHubIssuesDataStore`: 操作GitHub Issues API
- `FeedGrepGitHubActions`: 处理RSS源的主逻辑

**输出**:
- 在GitHub Issues中为每个新RSS项创建Issue
- 自动标记分类和来源标签
- 去重处理

#### `build_static_pages.py`
从GitHub Issues生成静态页面。

```bash
python build_static_pages.py \
  --token YOUR_GITHUB_TOKEN \
  --owner YOUR_USERNAME \
  --repo feedgrep \
  --output docs
```

**主要类**:
- `GitHubIssuesReader`: 读取GitHub Issues
- `StaticPageBuilder`: 生成静态页面

**生成文件**:
- `docs/index.html`: 首页
- `docs/api/feeds.json`: 按分类的RSS内容
- `docs/api/categories.json`: 分类列表
- `docs/api/items.json`: 所有项目

## 部署步骤

### 1. 准备GitHub令牌
```bash
# 在 https://github.com/settings/tokens 创建PAT
# 选择权限: repo, workflow, issues, pages
# 复制令牌
```

### 2. 配置Secrets
在GitHub仓库设置中添加以下Secrets:

```
GH_TOKEN = 你的令牌值
GITHUB_REPO_OWNER = 你的用户名
GITHUB_REPO_NAME = feedgrep
```

### 3. 启用GitHub Pages
1. 仓库Settings → Pages
2. Source选择: GitHub Actions
3. 保存

### 4. 配置feedgrep.yaml
根据需求编辑RSS源和规则。

### 5. 推送代码
```bash
git add .
git commit -m "部署GitHub Actions"
git push origin main
```

### 6. 检查运行
访问Actions标签页查看工作流运行情况。

## 环境变量和Secrets

### Secrets (必需)
| 名称 | 说明 | 获取方法 |
|-----|-----|--------|
| GH_TOKEN | GitHub访问令牌 | https://github.com/settings/tokens |

### 环境变量 (自动)
| 名称 | 说明 |
|-----|-----|
| github.repository_owner | 仓库所有者 |
| github.event.repository.name | 仓库名称 |
| github.ref | 当前分支 |

## 工作流执行顺序

```
rss-feed.yml (定时运行)
    ↓
检查RSS源 → 创建GitHub Issues
    ↓
触发 build-pages.yml
    ↓
读取GitHub Issues → 生成静态页面
    ↓
部署到GitHub Pages
    ↓
完成! 访问 github_pages_url
```

## 故障排除

### 工作流运行失败
1. 检查Actions日志
2. 验证GH_TOKEN是否有效
3. 检查feedgrep.yaml格式

### GitHub Pages未更新
1. 检查build-pages.yml是否完成
2. 查看Pages设置中的Source
3. 清除浏览器缓存

### RSS内容未更新
1. 检查RSS源URL是否有效
2. 查看rss-feed.yml的执行日志
3. 手动触发工作流测试

## 性能优化

### 并发处理RSS
编辑`rss-feed.yml`使用矩阵：

```yaml
strategy:
  matrix:
    category: [news, tech, finance]
```

### 限制Issue数量
编辑`fetch_feeds_github.py`中的条目限制：

```python
entries = feed.get('entries', [])[:10]  # 改为其他数字
```

### 缓存依赖
工作流已配置pip缓存，提升速度。

## 成本分析

### 免费额度 (每月)
- GitHub Actions: 2000分钟
- 并发任务: 20个
- GitHub Pages: 1GB存储
- API调用: 无限制

### 典型使用
- 每天运行1次: 5分钟 × 30天 = 150分钟/月
- 剩余: 1850分钟 (充足)

## 扩展功能

### 添加新的推送方式
在`fetch_feeds_github.py`中修改`create_item_issue`方法：

```python
# 添加Discord webhook推送
webhook_url = "你的discord webhook"
requests.post(webhook_url, json={...})
```

### 自定义HTML主题
编辑`build_static_pages.py`中的`build_index_html`方法。

### 添加搜索功能
在生成的index.html中集成搜索库（如Lunr.js）。

