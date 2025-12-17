#!/bin/bash
# fd 安装脚本 (Linux/macOS)
# fd 是一个快速的 find 替代工具

echo "================================================"
echo "  NL-Find - fd 安装脚本"
echo "================================================"
echo

# 检查是否已安装
if command -v fd &> /dev/null || command -v fdfind &> /dev/null; then
    echo "[√] fd 已安装"
    fd --version 2>/dev/null || fdfind --version 2>/dev/null
    echo
    echo "无需重复安装。"
    exit 0
fi

echo "[!] fd 未找到，开始安装..."
echo

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        echo "正在使用 Homebrew 安装 fd..."
        brew install fd
    else
        echo "[!] 请先安装 Homebrew: https://brew.sh"
        exit 1
    fi
elif [[ -f /etc/debian_version ]]; then
    # Debian/Ubuntu
    echo "正在使用 apt 安装 fd..."
    sudo apt update && sudo apt install -y fd-find
    # 创建别名
    if [ -f /usr/bin/fdfind ]; then
        echo "创建 fd 别名..."
        mkdir -p ~/.local/bin
        ln -sf /usr/bin/fdfind ~/.local/bin/fd
        echo "请将 ~/.local/bin 添加到 PATH"
    fi
elif [[ -f /etc/fedora-release ]]; then
    # Fedora
    echo "正在使用 dnf 安装 fd..."
    sudo dnf install -y fd-find
elif [[ -f /etc/arch-release ]]; then
    # Arch Linux
    echo "正在使用 pacman 安装 fd..."
    sudo pacman -S fd
else
    echo "[!] 未识别的 Linux 发行版，请手动安装 fd："
    echo "    https://github.com/sharkdp/fd#installation"
    exit 1
fi

echo
echo "[√] fd 安装完成！"
echo
echo "================================================"
echo "  NL-Find 将自动使用 fd 作为高速搜索后端"
echo "================================================"
