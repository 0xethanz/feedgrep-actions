# 如何清空去重记忆

## 去重机制说明

FeedGrep使用GitHub Issues作为数据存储，去重检查通过查询GitHub Issues API实现：

- **去重逻辑**: 在创建新Issue前，通过标题搜索已存在的Issues
- **默认行为**: 检查所有状态的Issues (`state=all`)，包括打开和已关闭的Issues
- **存储位置**: 没有本地缓存或数据库，所有数据存储在GitHub Issues中

## 清空去重记忆的方法

### 方法1：关闭所有RSS相关的Issues（推荐）

使用提供的 `clear_issues.py` 脚本关闭所有RSS相关的Issues，然后配合 `--ignore-closed` 参数重新处理RSS。

#### 步骤：

1. **列出所有RSS相关的Issues（预览模式）**
```bash
python clear_issues.py \
  --token YOUR_GITHUB_TOKEN \
  --owner YOUR_USERNAME \
  --repo YOUR_REPO \
  --action list
```

2. **关闭所有RSS相关的Issues**
```bash
python clear_issues.py \
  --token YOUR_GITHUB_TOKEN \
  --owner YOUR_USERNAME \
  --repo YOUR_REPO \
  --action close \
  --confirm
```

3. **重新处理RSS（忽略已关闭的Issues）**
```bash
python fetch_feeds_github.py \
  --config feedgrep.yaml \
  --token YOUR_GITHUB_TOKEN \
  --owner YOUR_USERNAME \
  --repo YOUR_REPO \
  --ignore-closed
```

### 方法2：手动删除GitHub Issues

通过GitHub网页界面手动删除所有RSS相关的Issues：

1. 访问仓库的Issues页面
2. 使用标签过滤: `label:rss-item`
3. 批量选择并关闭Issues
4. 注意：GitHub不支持批量删除，只能关闭

### 方法3：使用GitHub CLI批量关闭

如果你安装了GitHub CLI (gh)：

```bash
# 获取所有打开的rss-item标签的issue编号并关闭
gh issue list --label rss-item --state open --json number --jq '.[].number' | \
while read issue_number; do
  gh issue close $issue_number
done
```

## 使用 `--ignore-closed` 参数

在 `fetch_feeds_github.py` 中新增了 `--ignore-closed` 参数：

- **不使用** (默认): 去重时检查所有Issues（包括已关闭的）
- **使用**: 去重时只检查打开的Issues，忽略已关闭的

### 示例用法

**正常模式（检查所有Issues）**
```bash
python fetch_feeds_github.py \
  --config feedgrep.yaml \
  --token $GH_TOKEN \
  --owner username \
  --repo feedgrep
```

**清空后重新处理（忽略已关闭的Issues）**
```bash
python fetch_feeds_github.py \
  --config feedgrep.yaml \
  --token $GH_TOKEN \
  --owner username \
  --repo feedgrep \
  --ignore-closed
```

## 在GitHub Actions中使用

修改 `.github/workflows/rss-feed.yml`：

```yaml
- name: 📡 处理RSS源
  run: |
    python fetch_feeds_github.py \
      --config feedgrep.yaml \
      --token ${{ secrets.GH_TOKEN }} \
      --owner ${{ github.repository_owner }} \
      --repo ${{ github.event.repository.name }} \
      --ignore-closed  # 添加这个参数来忽略已关闭的issues
```

## 完整清空工作流程

如果你想完全清空去重记忆并重新开始：

### 步骤1: 关闭所有现有Issues
```bash
python clear_issues.py \
  --token YOUR_GITHUB_TOKEN \
  --owner YOUR_USERNAME \
  --repo YOUR_REPO \
  --action close \
  --confirm
```

### 步骤2: 修改工作流（可选）
如果想在工作流中忽略已关闭的issues，编辑 `.github/workflows/rss-feed.yml`，添加 `--ignore-closed` 参数。

### 步骤3: 手动触发RSS处理
在GitHub Actions页面手动触发 `rss-feed` 工作流。

### 步骤4: 检查结果
查看Issues页面，应该会看到新创建的Issues（旧的已关闭）。

## 注意事项

1. **GitHub API限制**: GitHub不支持通过API直接删除Issues，只能关闭
2. **去重仍然有效**: 即使关闭Issues，使用默认模式仍会检测到重复（因为检查 `state=all`）
3. **使用场景**: 
   - 想要重新抓取历史数据: 使用 `--ignore-closed`
   - 想要保持去重: 不使用 `--ignore-closed`（默认）
4. **存储空间**: 关闭的Issues仍占用仓库空间，如需彻底清理，需手动删除

## 脚本选项说明

### clear_issues.py 参数

| 参数 | 说明 |
|------|------|
| `--token` | GitHub访问令牌（必需） |
| `--owner` | 仓库所有者（必需） |
| `--repo` | 仓库名称（必需） |
| `--action` | 操作类型: `list`, `close`, `mark-deleted` |
| `--confirm` | 确认执行操作（否则仅预览） |

### fetch_feeds_github.py 新参数

| 参数 | 说明 |
|------|------|
| `--ignore-closed` | 去重时忽略已关闭的Issues |

## 常见问题

**Q: 为什么关闭Issues后仍然显示重复？**
A: 默认情况下，去重检查包括已关闭的Issues。使用 `--ignore-closed` 参数来忽略它们。

**Q: 可以永久删除Issues吗？**
A: GitHub API不支持删除Issues，只能通过网页界面手动删除。

**Q: 清空后会丢失数据吗？**
A: 关闭Issues不会删除数据，只是改变状态。如果需要，可以重新打开。

**Q: 多久执行一次清空？**
A: 根据需要。一般不需要清空，除非需要重新抓取历史数据或测试。
