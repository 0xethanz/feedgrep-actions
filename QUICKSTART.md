# FeedGrep GitHub Actions 快速参考

## 📋 部署清单

- [ ] 复制所有文件到项目根目录
- [ ] 创建GitHub Personal Access Token
- [ ] 配置GitHub Secrets
- [ ] 启用GitHub Pages
- [ ] 编辑feedgrep.yaml配置
- [ ] 推送代码触发首次运行
- [ ] 验证GitHub Pages访问

## 🚀 3分钟快速部署

### 1. 复制文件
```bash
cd /path/to/feedgrep
cp -r github-actions-deploy/.github .github
cp github-actions-deploy/*.py .
cp github-actions-deploy/index.html index-github-pages.html
```

### 2. 创建令牌
访问 https://github.com/settings/tokens/new

**选择权限:**
- ✅ repo (完整控制)
- ✅ workflow (更新工作流)
- ✅ issues (创建issues)
- ✅ pages (Pages部署)

复制令牌值

### 3. 配置Secrets
进入仓库 Settings → Secrets and variables → Actions

**创建以下Secrets:**

| Key | Value |
|-----|-------|
| GH_TOKEN | [你复制的令牌] |
| GITHUB_REPO_OWNER | [你的GitHub用户名] |
| GITHUB_REPO_NAME | feedgrep |

### 4. 启用Pages
Settings → Pages → 选择 "GitHub Actions"

### 5. 提交推送
```bash
git add .
git commit -m "feat: GitHub Actions部署"
git push origin main
```

### 6. 完成！
访问: `https://YOUR_USERNAME.github.io/feedgrep/`

## 📖 API 文档

### 获取所有分类
```bash
GET /feedgrep/api/categories.json
```
返回: `["tech", "news", "finance"]`

### 获取按分类组织的RSS
```bash
GET /feedgrep/api/feeds.json
```
返回:
```json
{
  "tech": {
    "count": 50,
    "items": [...]
  }
}
```

### 获取所有项目
```bash
GET /feedgrep/api/items.json
```
返回:
```json
{
  "items": [...],
  "count": 150
}
```

### 项目数据格式
```json
{
  "id": 123,
  "title": "文章标题",
  "link": "https://example.com",
  "description": "内容预览",
  "published": "2024-12-10T10:00:00Z",
  "category": "tech",
  "source_name": "来源",
  "url": "GitHub Issue链接"
}
```

## ⚙️ 工作流调度

### 默认运行时间
- **时间**: 每天 UTC 02:00 (北京时间 10:00)
- **位置**: `.github/workflows/rss-feed.yml` 第13行

### 修改运行时间
编辑 `.github/workflows/rss-feed.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # 改成你想要的时间
```

Cron格式: `分 小时 日期 月份 星期`

常用例子:
```yaml
'0 */6 * * *'      # 每6小时运行一次
'0 12 * * *'       # 每天中午12点运行
'0 0 * * 1'        # 每周一凌晨运行
'*/30 * * * *'     # 每30分钟运行一次
```

## 🔧 常见配置

### 增加并发处理
在 `rss-feed.yml` 中添加矩阵策略:

```yaml
strategy:
  matrix:
    category: [news, tech, finance]
```

### 限制RSS项数
编辑 `fetch_feeds_github.py` 第63行:

```python
entries = feed.get('entries', [])[:10]  # 改为你想要的数字
```

### 修改主题颜色
编辑 `index.html` 中的Tailwind颜色:

```javascript
// 将 indigo-600 改为其他颜色
// 可用: red, blue, green, purple, pink 等
```

## 🐛 故障排除

### GitHub Pages显示404
- [ ] 检查仓库Settings → Pages
- [ ] 确保Source选择了 "GitHub Actions"
- [ ] 检查build-pages.yml是否运行成功

### 工作流执行失败
- [ ] 查看Actions日志详细错误信息
- [ ] 检查GH_TOKEN是否有效
- [ ] 验证feedgrep.yaml格式

### 数据未更新
- [ ] 手动触发工作流: Actions → rss-feed → Run workflow
- [ ] 检查RSS源URL是否可访问
- [ ] 查看GitHub API速率限制

### 导入/导出Issues不显示
- [ ] 刷新浏览器 (Ctrl+F5)
- [ ] 清除浏览器缓存
- [ ] 检查Pages部署日志

## 📊 监控和维护

### 查看工作流运行
Actions标签页 → 选择工作流 → 查看运行详情

### 查看生成的Issues
Issues标签页 → 按标签过滤 (rss-item) → 查看数据

### 查看Pages部署日志
Settings → Pages → 查看部署历史

## 💡 进阶用法

### 添加自定义推送
在 `fetch_feeds_github.py` 中修改 `create_item_issue` 方法:

```python
# 添加Webhook推送
import requests
requests.post(
    "https://hooks.discord.com/...",
    json={"content": f"新文章: {title}"}
)
```

### 集成其他服务
- **Discord**: 添加Webhook通知
- **Telegram**: 调用Bot API发送消息
- **Email**: 集成邮件服务

### 导出数据
从 `/api/items.json` 导出所有数据进行二次分析。

## 📈 成本分析

每月免费额度：
- GitHub Actions: **2000分钟**
- 工作流运行: 每天1次 = ~150分钟/月
- 可用额度: **1850分钟** ✅

安全范围：保持每日运行≤13次

## 🔗 相关链接

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [GitHub Pages文档](https://docs.github.com/en/pages)
- [GitHub API文档](https://docs.github.com/en/rest)
- [Cron表达式](https://crontab.guru/)

## 💬 需要帮助?

1. 查看完整文档: `README.md`
2. 检查部署指南: `DEPLOYMENT.md`
3. 查看工作流日志: Actions标签页
4. 提交Issue: GitHub Issues

---

**提示**: 将此文件存为便签或书签，便于快速查阅！

