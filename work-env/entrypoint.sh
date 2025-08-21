#!/bin/bash
set -e

# NetBird 自动注册和连接
if [ -n "${NETBIRD_KEY}" ]; then
    netbird service start
    echo "NetBird setup key detected, checking connection status..."
    
    # 检查 NetBird 是否已经连接
    if netbird status 2>/dev/null | grep -q "Daemon status: Connected"; then
        echo "NetBird is already connected"
    else
        echo "Connecting to NetBird network..."
        # 使用 setup key 连接
        netbird up --setup-key "${NETBIRD_KEY}" --daemon-off &
        NETBIRD_PID=$!
        
        # 等待连接建立
        sleep 5
        
        # 检查连接状态
        if netbird status 2>/dev/null | grep -q "Daemon status: Connected"; then
            echo "NetBird connected successfully"
        else
            echo "NetBird connection failed, but continuing..."
        fi
    fi
else
    echo "No NETBIRD_KEY provided, skipping NetBird setup"
fi

# 执行原始命令
exec "$@"