# GitHub Actions + GitHub Pages 部署方案

完全免费的FeedGrep部署架构，零成本运行，自动化处理RSS源。

## 📁 文件结构

```
github-actions-deploy/
├── README.md                      # 详细部署文档
├── DEPLOYMENT.md                  # 部署配置说明
├── QUICKSTART.md                  # 快速参考指南
├── setup.sh                       # 自动部署脚本
├── index.html                     # 前端页面（可选）
│
├── fetch_feeds_github.py          # RSS处理脚本
├── build_static_pages.py          # 页面生成脚本
├── migrate_to_github_issues.py    # 数据迁移脚本
│
└── .github/workflows/
    ├── rss-feed.yml              # RSS定时处理工作流
    └── build-pages.yml           # 页面构建工作流
```

## 🚀 快速部署 (5分钟)

### 方式1: 自动部署脚本 (推荐)

```bash
# 进入项目目录
cd /path/to/feedgrep

# 运行自动部署脚本
bash github-actions-deploy/setup.sh
```

### 方式2: 手动复制

```bash
# 复制工作流文件
cp -r github-actions-deploy/.github/workflows .github/

# 复制Python脚本
cp github-actions-deploy/*.py .

# 复制前端文件
cp github-actions-deploy/index.html .
```

### 方式3: 一行命令

```bash
cp -r github-actions-deploy/.github . && \
cp github-actions-deploy/*.py . && \
cp github-actions-deploy/index.html . && \
git add . && \
git commit -m "feat: GitHub Actions部署" && \
git push origin main
```

## 🔑 配置步骤

### 1. 创建GitHub令牌
https://github.com/settings/tokens → Generate new token (classic)

**必需权限:**
- ✅ repo
- ✅ workflow
- ✅ issues
- ✅ pages

### 2. 添加仓库Secrets
Settings → Secrets and variables → Actions

```
GH_TOKEN = 你的令牌
GITHUB_REPO_OWNER = 你的用户名
GITHUB_REPO_NAME = feedgrep
```

### 3. 启用GitHub Pages
Settings → Pages → Source: GitHub Actions

### 4. 推送代码
```bash
git add .
git commit -m "部署GitHub Actions"
git push origin main
```

## 📊 架构设计

```
每天UTC 02:00
    ↓
rss-feed.yml 工作流
    ↓
fetch_feeds_github.py 脚本
    ↓
检查所有RSS源 → 创建GitHub Issues
    ↓
build-pages.yml 工作流
    ↓
build_static_pages.py 脚本
    ↓
从Issues读取数据 → 生成JSON API
    ↓
GitHub Pages 自动部署
    ↓
访问: https://YOUR_USERNAME.github.io/feedgrep
```

## 📚 文档指南

| 文档 | 用途 | 阅读时间 |
|-----|-----|---------|
| **README.md** | 完整功能介绍和配置 | 15分钟 |
| **QUICKSTART.md** | 快速参考和常见问题 | 5分钟 |
| **DEPLOYMENT.md** | 深入部署和优化指南 | 10分钟 |
| **setup.sh** | 一键自动部署 | 1分钟 |

## 🎯 特点

✅ **完全免费** - 零成本运行  
✅ **自动化** - GitHub Actions定时处理  
✅ **易部署** - 一条命令启动  
✅ **高可靠** - 依赖GitHub基础设施  
✅ **易维护** - 配置管理完全在GitHub  
✅ **无限制** - Issues存储无限制  

## 📈 性能指标

| 指标 | 值 |
|-----|-----|
| 免费额度 (月) | 2000分钟 |
| 典型消耗 | 150分钟 |
| 剩余额度 | 1850分钟 ✅ |
| 并发任务 | 20个 |
| 运行频率 | 建议1-3小时 |
| API请求 | 无限制 |

## 🔧 常用命令

### 部署
```bash
bash github-actions-deploy/setup.sh
```

### 手动触发工作流
```bash
gh workflow run rss-feed.yml -r main
```

### 数据迁移 (从SQLite)
```bash
python migrate_to_github_issues.py \
  --db feedgrep.db \
  --token YOUR_TOKEN \
  --owner YOUR_USERNAME \
  --repo feedgrep
```

### 本地测试RSS处理
```bash
python fetch_feeds_github.py \
  --config feedgrep.yaml \
  --token YOUR_TOKEN \
  --owner YOUR_USERNAME \
  --repo feedgrep
```

### 本地生成页面
```bash
python build_static_pages.py \
  --token YOUR_TOKEN \
  --owner YOUR_USERNAME \
  --repo feedgrep \
  --output docs
```

## 🐛 常见问题

**Q: GitHub Pages访问404?**  
A: 检查Settings → Pages，确保Source选择GitHub Actions

**Q: RSS数据未更新?**  
A: 手动触发rss-feed.yml工作流或检查Action日志

**Q: 如何增加运行频率?**  
A: 编辑.github/workflows/rss-feed.yml中的cron表达式

**Q: 能否添加推送通知?**  
A: 可以在fetch_feeds_github.py中集成Discord/Telegram等服务

**Q: 如何删除旧的Issue?**  
A: 使用GitHub Issues的批量操作或脚本

## 📦 依赖项

### Python依赖
```
feedparser==6.0.10
pyyaml==6.0.3
requests==2.31.0
```

### GitHub功能
- GitHub API v3
- GitHub Actions
- GitHub Pages
- GitHub Issues

## 🎓 学习资源

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [GitHub Pages文档](https://docs.github.com/en/pages)
- [REST API文档](https://docs.github.com/en/rest)
- [Cron表达式生成器](https://crontab.guru/)

## 💡 扩展建议

1. **集成Discord通知** - 新RSS更新时发送Discord消息
2. **Email推送** - 添加定期邮件摘要
3. **搜索功能** - 前端集成Lunr.js实现全文搜索
4. **分析面板** - 统计阅读数据和趋势
5. **订阅管理** - 允许用户自定义订阅源

## 🔒 安全考虑

- ✅ 使用GitHub Token保护API调用
- ✅ Token存储在Secrets中，不暴露
- ✅ 支持私有仓库（数据完全私有）
- ✅ 所有通信都是HTTPS加密
- ✅ GitHub的DDoS防护和安全认证

## 📞 支持

- 📖 查看完整文档
- 🐛 提交Issue报告问题
- 💬 讨论功能建议
- 🔗 分享改进方案

## 📄 许可证

与主项目相同

---

**准备好了？** 运行 `bash github-actions-deploy/setup.sh` 开始部署！

