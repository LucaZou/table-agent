#!/usr/bin/env pwsh
# PowerShell部署脚本

# 参数定义
param (
    [string]$Env = "dev",
    [switch]$Help,
    [switch]$Prune
)

# 显示帮助信息
function Show-Help {
    Write-Host "AI表格处理工具 - Docker部署脚本" -ForegroundColor Blue
    Write-Host "用法: ./deploy-docker.ps1 [选项]"
    Write-Host "选项:"
    Write-Host "  -Env <env>   指定环境: dev (开发环境) 或 prod (生产环境), 默认是dev"
    Write-Host "  -Prune       清理未使用的Docker资源"
    Write-Host "  -Help        显示帮助信息"
    Write-Host ""
}

# 如果需要帮助，显示帮助信息并退出
if ($Help) {
    Show-Help
    exit 0
}

# 验证环境参数
if ($Env -ne "dev" -and $Env -ne "prod") {
    Write-Host "错误: 环境必须是 'dev' 或 'prod'" -ForegroundColor Red
    Show-Help
    exit 1
}

# 检查Docker是否已安装
try {
    $dockerVersion = docker --version
    Write-Host "检测到Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未检测到Docker，请先安装Docker" -ForegroundColor Red
    exit 1
}

# 检查docker-compose是否已安装
try {
    $composeVersion = docker-compose --version
    Write-Host "检测到Docker Compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未检测到Docker Compose，请先安装Docker Compose" -ForegroundColor Red
    exit 1
}

Write-Host "开始部署Docker $Env 环境..." -ForegroundColor Green

# 设置Docker Compose文件
if ($Env -eq "dev") {
    $ComposeFile = "docker-compose-dev.yml"
    Write-Host "使用开发环境配置..." -ForegroundColor Green
}
else {
    $ComposeFile = "docker-compose-prod.yml"
    Write-Host "使用生产环境配置..." -ForegroundColor Green
}

# 确保目录存在
if (-not (Test-Path -Path "backend/uploads")) {
    Write-Host "创建目录: backend/uploads" -ForegroundColor Cyan
    New-Item -Path "backend/uploads" -ItemType Directory -Force | Out-Null
}
if (-not (Test-Path -Path "backend/static/images")) {
    Write-Host "创建目录: backend/static/images" -ForegroundColor Cyan
    New-Item -Path "backend/static/images" -ItemType Directory -Force | Out-Null
}

# 生产环境检查证书文件
if ($Env -eq "prod") {
    Write-Host "检查证书文件..." -ForegroundColor Cyan
    if (-not (Test-Path -Path "uagent.top.pem") -or -not (Test-Path -Path "uagent.top.key")) {
        Write-Host "警告: SSL证书文件不存在，请确保证书文件放置在正确位置" -ForegroundColor Yellow
        $continue = Read-Host "是否继续部署? (y/n)"
        if ($continue -ne "y") {
            Write-Host "部署已取消" -ForegroundColor Red
            exit 0
        }
    }
}

Write-Host "停止和删除旧容器..." -ForegroundColor Cyan
docker-compose -f $ComposeFile down

# 如果指定了清理选项
if ($Prune) {
    Write-Host "清理未使用的Docker资源..." -ForegroundColor Cyan
    docker system prune -f
}

Write-Host "启动新容器..." -ForegroundColor Cyan
docker-compose -f $ComposeFile up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "容器启动失败" -ForegroundColor Red
    exit 1
}

Write-Host "等待容器启动完成..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host "容器状态:" -ForegroundColor Green
docker-compose -f $ComposeFile ps

Write-Host "部署完成!" -ForegroundColor Green
if ($Env -eq "prod") {
    Write-Host "前端访问地址: https://localhost" -ForegroundColor Yellow
}
else {
    Write-Host "前端访问地址: http://localhost" -ForegroundColor Yellow
}
Write-Host "后端API地址: http://localhost:8000" -ForegroundColor Yellow   