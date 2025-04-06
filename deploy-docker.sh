#!/bin/bash
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}开始部署Docker环境...${NC}"

# 确保目录存在
mkdir -p backend/uploads backend/static/images

echo -e "${CYAN}停止和删除旧容器...${NC}"
docker-compose -f docker-compose.yml down

echo -e "${CYAN}启动新容器...${NC}"
docker-compose -f docker-compose.yml up -d || { echo -e "${RED}容器启动失败${NC}"; exit 1; }

echo -e "${GREEN}容器状态:${NC}"
docker-compose -f docker-compose.yml ps

echo -e "${GREEN}部署完成!${NC}"
echo -e "${YELLOW}前端访问地址: http://localhost${NC}"
echo -e "${YELLOW}后端API地址: http://localhost:8000${NC}"