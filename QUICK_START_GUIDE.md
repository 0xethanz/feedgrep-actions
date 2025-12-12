# Quick Start Guide - 修复后的使用指南

## 问题已修复 ✅

两个主要问题已经解决：

1. ✅ **构建错误已修复** - 即使没有Issues也能成功创建docs目录
2. ✅ **去重记忆清空** - 提供了完整的清空和重置方案

---

## 🚀 立即开始使用

### 正常使用（推荐）

不需要做任何改变，工作流现在会正常工作：

```bash
# GitHub Actions 会自动运行
# 如果没有Issues，会生成空的静态页面，不再报错
```

---

## 🔄 清空去重记忆（如需要）

### 方法1: 使用提供的脚本（最简单）

#### 步骤1: 列出所有RSS Issues
```bash
python clear_issues.py \
  --token YOUR_GITHUB_TOKEN \
  --owner 0xethanz \
  --repo feedgrep-actions \
  --action list
```

#### 步骤2: 关闭所有RSS Issues
```bash
python clear_issues.py \
  --token YOUR_GITHUB_TOKEN \
  --owner 0xethanz \
  --repo feedgrep-actions \
  --action close \
  --confirm
```

#### 步骤3: 重新处理RSS（忽略已关闭的）
```bash
python fetch_feeds_github.py \
  --config feedgrep.yaml \
  --token YOUR_GITHUB_TOKEN \
  --owner 0xethanz \
  --repo feedgrep-actions \
  --ignore-closed
```

### 方法2: 在GitHub Actions中使用

修改 `.github/workflows/rss-feed.yml`，添加 `--ignore-closed` 参数：

```yaml
- name: 📡 处理RSS源
  run: |
    python fetch_feeds_github.py \
      --config feedgrep.yaml \
      --token ${{ secrets.GH_TOKEN }} \
      --owner ${{ github.repository_owner }} \
      --repo ${{ github.event.repository.name }} \
      --ignore-closed
```

---

## 📖 详细文档

查看完整文档了解更多：
- **清空去重记忆**: 查看 `CLEAR_DEDUP_MEMORY.md`
- **部署配置**: 查看 `DEPLOYMENT.md`

---

## ⚙️ 工作原理

### 去重机制
- 使用GitHub Issues作为数据存储（无本地缓存）
- 通过标题搜索检查重复项
- 默认检查所有状态的Issues（包括已关闭的）

### 清空过程
1. 关闭所有RSS相关的Issues
2. 使用 `--ignore-closed` 参数重新运行
3. 只检查打开的Issues，已关闭的会被忽略

---

## 🎯 常见使用场景

### 场景1: 首次使用（无需清空）
```bash
# 直接运行即可，工作流会自动处理
git push origin main
```

### 场景2: 重新抓取所有历史数据
```bash
# 1. 关闭所有旧Issues
python clear_issues.py --token TOKEN --owner USER --repo REPO --action close --confirm

# 2. 重新处理RSS（带--ignore-closed参数）
python fetch_feeds_github.py --config feedgrep.yaml --token TOKEN --owner USER --repo REPO --ignore-closed
```

### 场景3: 继续正常使用
```bash
# 不需要任何额外参数，保持默认即可
# 这样会防止真正的重复内容
```

---

## 💡 重要提示

1. **默认行为是最佳实践** - 不需要清空去重记忆
2. **只在特殊情况下清空** - 比如需要重新抓取历史数据
3. **GitHub不支持删除Issues** - 只能关闭它们
4. **使用 `--ignore-closed` 谨慎** - 可能导致重复内容

---

## 🆘 需要帮助？

如果遇到问题：
1. 检查GitHub Actions日志
2. 查看 `CLEAR_DEDUP_MEMORY.md` 获取详细说明
3. 确保GitHub Token有正确的权限

---

## ✅ 验证修复

运行以下命令验证修复是否成功：

```bash
# 测试build_static_pages（即使没有issues）
python build_static_pages.py \
  --token dummy \
  --owner test \
  --repo test \
  --output /tmp/test

# 应该看到：
# ⚠️  没有找到任何Issues，将生成空的静态页面
# ✅ 生成: /tmp/test/api/feeds.json
# ✅ 页面构建完成!
```

成功！现在可以正常使用了。🎉
