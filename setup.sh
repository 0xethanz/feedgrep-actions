#!/bin/bash
# FeedGrep GitHub Actions 快速部署脚本
# 一键部署GitHub Actions工作流和所有配置文件

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     FeedGrep GitHub Actions 自动部署脚本                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 检查必要的工具
if ! command -v git &> /dev/null; then
    echo "❌ 错误: 未找到 git 命令"
    echo "请先安装 Git: https://git-scm.com/"
    exit 1
fi

# 检查是否在Git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误: 当前目录不是Git仓库"
    echo "请先运行: git init"
    exit 1
fi

# 显示当前仓库信息
REPO_URL=$(git remote get-url origin 2>/dev/null || echo "未配置")
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "📌 当前仓库信息:"
echo "   URL: $REPO_URL"
echo "   分支: $BRANCH"
echo ""

# 复制文件
echo "📁 复制文件..."

# 复制工作流文件
mkdir -p .github/workflows
cp github-actions-deploy/.github/workflows/*.yml .github/workflows/
echo "   ✅ 工作流文件 (.github/workflows/)"

# 复制脚本文件
cp github-actions-deploy/*.py .
echo "   ✅ Python脚本"

# 复制前端文件（如果不存在）
if [ ! -f index-github-pages.html ]; then
    cp github-actions-deploy/index.html index-github-pages.html
    echo "   ✅ 前端文件 (index-github-pages.html)"
fi

echo ""
echo "✅ 文件复制完成"
echo ""

# 显示后续步骤
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              后续配置步骤                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "1️⃣  创建GitHub令牌:"
echo "   访问: https://github.com/settings/tokens"
echo "   选择 'Generate new token (classic)'"
echo "   权限: repo, workflow, issues, pages"
echo ""
echo "2️⃣  添加Secrets (仓库 Settings → Secrets):"
echo "   GH_TOKEN = 你的令牌"
echo "   GITHUB_REPO_OWNER = 你的GitHub用户名"
echo "   GITHUB_REPO_NAME = 仓库名称"
echo ""
echo "3️⃣  启用GitHub Pages:"
echo "   Settings → Pages → Source 选择 'GitHub Actions'"
echo ""
echo "4️⃣  提交并推送:"
echo "   git add ."
echo "   git commit -m 'feat: 添加GitHub Actions自动化'"
echo "   git push origin main"
echo ""
echo "5️⃣  查看运行:"
echo "   在仓库 Actions 标签页查看工作流运行"
echo ""

# 询问是否继续
read -p "是否立即提交并推送这些文件? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 正在提交..."
    git add .github/workflows/ *.py *.html 2>/dev/null || true
    git commit -m "feat: 添加 GitHub Actions 自动化部署配置"
    
    echo "📤 正在推送..."
    git push origin "$BRANCH"
    
    echo ""
    echo "✅ 推送完成!"
    echo "💡 检查仓库的 Actions 标签页查看工作流运行情况"
else
    echo ""
    echo "📝 请手动执行以下命令:"
    echo "   git add ."
    echo "   git commit -m 'feat: 添加 GitHub Actions 自动化'"
    echo "   git push origin main"
fi

echo ""
echo "📚 查看文档: github-actions-deploy/README.md"
echo ""
