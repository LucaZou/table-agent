#!/bin/bash

# 设置输出颜色
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始部署Docker环境...${NC}"

# 1. 构建前端
echo -e "${CYAN}正在构建前端...${NC}"
cd frontend
npm install
npm run build
cd ..

# 2. 确保目录存在
mkdir -p backend/uploads
mkdir -p backend/static/images

# 3. 停止和删除旧容器
echo -e "${CYAN}停止和删除旧容器...${NC}"
docker-compose -f docker-compose-prod.yml down

# 4. 启动新容器
echo -e "${CYAN}启动新容器...${NC}"
docker-compose -f docker-compose-prod.yml up -d

# 5. 显示容器状态
echo -e "${GREEN}容器状态:${NC}"
docker-compose -f docker-compose-prod.yml ps

echo -e "${GREEN}部署完成!${NC}"
echo -e "${YELLOW}前端访问地址: http://localhost${NC}"
echo -e "${YELLOW}后端API地址: http://localhost:8000${NC}" 