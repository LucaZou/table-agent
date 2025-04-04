# 设置控制台输出使用UTF-8编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "开始部署Docker环境..." -ForegroundColor Green

# 1. 构建前端
Write-Host "正在构建前端..." -ForegroundColor Cyan
Set-Location -Path .\frontend
npm install
npm run build
Set-Location -Path ..

# 2. 确保目录存在
if (-not (Test-Path -Path ".\backend\uploads")) {
    New-Item -ItemType Directory -Path ".\backend\uploads" -Force
}
if (-not (Test-Path -Path ".\backend\static\images")) {
    New-Item -ItemType Directory -Path ".\backend\static\images" -Force
}

# 3. 停止和删除旧容器
Write-Host "停止和删除旧容器..." -ForegroundColor Cyan
docker-compose -f docker-compose-prod.yml down

# 4. 启动新容器
Write-Host "启动新容器..." -ForegroundColor Cyan
docker-compose -f docker-compose-prod.yml up -d

# 5. 显示容器状态
Write-Host "容器状态:" -ForegroundColor Green
docker-compose -f docker-compose-prod.yml ps

Write-Host "部署完成!" -ForegroundColor Green
Write-Host "前端访问地址: http://localhost" -ForegroundColor Yellow
Write-Host "后端API地址: http://localhost:8000" -ForegroundColor Yellow 