# FeedGrep GitHub Actions + GitHub Pages 部署方案

这是FeedGrep的完全免费部署方案，使用：
- **GitHub Actions** 定时处理RSS任务
- **GitHub Pages** 托管前端网站
- **GitHub Issues** 存储数据（通过标签和标题组织）

## 完全免费的优势

✅ **0成本** - 完全免费，无限制  
✅ **自动化** - GitHub Actions定时任务自动运行  
✅ **无需服务器** - 无需支付任何主机费用  
✅ **简单部署** - 只需推送代码到GitHub  

## 架构设计

```
┌─────────────────┐
│ GitHub Actions  │ ← 定时触发 (每30分钟)
│  RSS处理任务    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Issues   │ ← 存储 RSS 数据
│  (数据库)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Pages    │ ← 前端展示
│   (网站)        │
└─────────────────┘
```

## 快速开始

### 1. 项目准备

```bash
# 1. Fork 或新建仓库
# 2. 克隆到本地
git clone https://github.com/YOUR_USERNAME/feedgrep.git
cd feedgrep

# 3. 复制部署文件到根目录
cp -r github-actions-deploy/* .

# 4. 推送到GitHub
git add .
git commit -m "feat: 添加 GitHub Actions 部署方案"
git push origin main
```

### 2. 配置GitHub

#### 2.1 启用GitHub Pages
1. 进入仓库 Settings
2. 找到 "Pages" 部分
3. 在 "Build and deployment" 中，选择：
   - Source: `GitHub Actions`

#### 2.2 创建个人访问令牌 (PAT)
1. 进入 [GitHub Personal Access Tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token"
3. 选择 "Generate new token (classic)"
4. 权限选择：
   - ✅ `repo` (完全控制私有仓库和公共仓库)
   - ✅ `workflow` (更新GitHub Action工作流)
   - ✅ `issues` (创建和编辑issues)
   - ✅ `pages` (部署到GitHub Pages)
5. 复制令牌值

#### 2.3 添加Secrets
1. 进入仓库 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加以下Secrets：

| Secret名称 | 值 | 说明 |
|-----------|-------|------|
| `GH_TOKEN` | 上面复制的PAT | GitHub操作令牌 |
| `GITHUB_REPO_OWNER` | 你的GitHub用户名 | 仓库所有者 |
| `GITHUB_REPO_NAME` | `feedgrep` | 仓库名称 |

### 3. 配置feedgrep.yaml

编辑根目录的 `feedgrep.yaml` 文件，配置：
- RSS源（可选）
- 关键词规则（可选）
- 推送渠道（可选）

在GitHub Actions环境下，**不支持外部推送**（飞书、企业微信等），所有数据将通过GitHub Issues存储。

### 4. 部署

```bash
# 将所有文件推送到GitHub
git add .
git commit -m "初始化部署"
git push origin main
```

GitHub Actions会自动：
1. ✅ 每天凌晨2点检查RSS源（UTC时间）
2. ✅ 更新GitHub Issues中的数据
3. ✅ 生成静态网页
4. ✅ 部署到GitHub Pages

## 工作流文件说明

### `.github/workflows/rss-feed.yml`
- 定时触发（每天UTC 2点）
- 处理所有RSS源
- 将新项目发送到GitHub Issues

### `.github/workflows/build-pages.yml`
- 在RSS数据更新后自动触发
- 从GitHub Issues读取数据
- 生成静态HTML页面
- 部署到GitHub Pages

## API端点 (静态生成)

部署后，你可以访问以下端点获取JSON数据：

```
https://YOUR_GITHUB_USERNAME.github.io/feedgrep/api/feeds.json
https://YOUR_GITHUB_USERNAME.github.io/feedgrep/api/items.json?category=tech
https://YOUR_GITHUB_USERNAME.github.io/feedgrep/api/categories.json
```

## 前端配置

编辑 `index.html` 中的API基URL：

```javascript
// 修改第500行左右
const API_BASE_URL = 'https://YOUR_GITHUB_USERNAME.github.io/feedgrep';
```

## 限制和考虑

| 限制项 | 值 | 说明 |
|-------|-----|------|
| 并发任务 | 20个 | GitHub Actions免费额度 |
| 月度分钟数 | 2000分钟 | 免费账户 |
| 工作流频率 | 建议1-3小时 | 避免超限 |
| Issues存储 | 无限制 | 适合小数据量 |
| 页面部署 | 1GB | 足够使用 |

## 迁移原有数据

如果有SQLite数据库，可以使用迁移工具：

```bash
python scripts/migrate_to_github_issues.py \
  --db feedgrep.db \
  --token YOUR_GITHUB_TOKEN \
  --repo YOUR_USERNAME/feedgrep
```

## 常见问题

### Q: 如何增加检查频率？
编辑 `.github/workflows/rss-feed.yml` 中的 `schedule` 部分。

### Q: 如何添加新的推送渠道？
由于是无服务器架构，推送渠道受限。建议使用GitHub Issues订阅或Email通知。

### Q: 数据安全吗？
- ✅ 如果仓库是私有的，数据完全私有
- ✅ GitHub Issues内容经过加密传输
- ✅ 建议敏感信息不公开仓库

### Q: 如何本地测试？

```bash
# 安装依赖
pip install -r requirements-github-actions.txt

# 运行RSS处理脚本
python scripts/fetch_feeds_github.py --config feedgrep.yaml --token YOUR_GITHUB_TOKEN

# 生成静态页面
python scripts/build_static_pages.py
```

## 高级配置

### 自定义检查时间
编辑 `.github/workflows/rss-feed.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # 每天UTC 2:00 (北京时间 10:00)
```

### 增加并发处理
编辑 `.github/workflows/rss-feed.yml`:
```yaml
jobs:
  rss-feed:
    strategy:
      matrix:
        category: [news, tech, finance]
```

## 成本对比

| 部署方案 | 月度成本 | 维护难度 |
|--------|---------|--------|
| **GitHub Actions + Pages** | **$0** | ⭐ 简单 |
| Railway | $5+ | ⭐⭐ 中等 |
| Vercel | $0-20+ | ⭐⭐ 中等 |
| 自建服务器 | $5+ | ⭐⭐⭐ 复杂 |
| AWS/Azure | $10+ | ⭐⭐⭐⭐ 很复杂 |

## 下一步

- [ ] 配置GitHub Secrets
- [ ] 启用GitHub Pages
- [ ] 推送代码触发首次运行
- [ ] 访问 GitHub Pages URL 查看结果
- [ ] 自定义 feedgrep.yaml
- [ ] 配置发送通知

## 支持

遇到问题？查看：
1. [GitHub Actions文档](https://docs.github.com/en/actions)
2. [GitHub Pages文档](https://docs.github.com/en/pages)
3. [项目Issues](https://github.com/0xethanz/feedgrep/issues)

