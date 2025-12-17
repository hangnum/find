@echo off
REM Everything CLI 安装脚本 (Windows)
REM 用于安装 Everything 搜索工具和命令行接口

echo ================================================
echo   NL-Find - Everything CLI 安装脚本
echo ================================================
echo.

REM 检查是否已安装
where es >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo [√] Everything CLI ^(es.exe^) 已安装
    es -version
    echo.
    echo 无需重复安装。
    goto :end
)

echo [!] Everything CLI 未找到，开始安装...
echo.

REM 方式1: 使用 winget (推荐)
where winget >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo 正在使用 winget 安装 Everything...
    winget install voidtools.Everything --accept-package-agreements --accept-source-agreements
    if %ERRORLEVEL% == 0 (
        echo.
        echo [√] Everything 安装成功！
        echo [!] 请重启终端后再使用。
        goto :end
    )
)

REM 方式2: 使用 Chocolatey
where choco >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo 正在使用 Chocolatey 安装 Everything...
    choco install everything -y
    if %ERRORLEVEL% == 0 (
        echo.
        echo [√] Everything 安装成功！
        goto :end
    )
)

REM 方式3: 手动下载
echo.
echo [!] 未找到包管理器，请手动安装 Everything：
echo.
echo    1. 访问 https://www.voidtools.com/downloads/
echo    2. 下载并安装 Everything
echo    3. 下载 Everything Command-line Interface (es.exe)
echo    4. 将 es.exe 添加到 PATH 环境变量
echo.

:end
echo.
echo ================================================
echo   安装完成后，NL-Find 将自动检测并使用 Everything
echo   作为高速搜索后端（毫秒级搜索）
echo ================================================
pause
