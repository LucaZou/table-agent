# 设置PowerShell使用UTF-8编码
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# 设置输出颜色（使用ESC的ASCII码）
$ESC = [char]27
$Green = "$ESC[32m"
$Cyan = "$ESC[36m"
$Yellow = "$ESC[33m"
$NC = "$ESC[0m"

Write-Host "${Green}开始部署Docker环境...${NC}"
Write-Host "${Cyan}正在构建前端...${NC}"
Set-Location -Path "frontend"
npm install
npm run build
Set-Location -Path ".."

Write-Host "${Cyan}确保后端目录存在...${NC}"
New-Item -ItemType Directory -Path "backend/uploads" -Force
New-Item -ItemType Directory -Path "backend/static/images" -Force

Write-Host "${Cyan}停止和删除旧容器...${NC}"
docker-compose -f docker-compose.yml down

Write-Host "${Cyan}启动新容器...${NC}"
docker-compose -f docker-compose.yml up -d

Write-Host "${Green}容器状态:${NC}"
docker-compose -f docker-compose.yml ps

Write-Host "${Green}部署完成!${NC}"
Write-Host "${Yellow}前端访问地址: http://localhost${NC}"
Write-Host "${Yellow}后端API地址: http://localhost:8000${NC}"