#!/bin/bash
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 显示帮助信息
show_help() {
  echo -e "${BLUE}AI表格处理工具 - Docker部署脚本${NC}"
  echo -e "用法: $0 [选项]"
  echo -e "选项:"
  echo -e "  -e, --env ENV     指定环境: dev (开发环境) 或 prod (生产环境), 默认是dev"
  echo -e "  -h, --help        显示帮助信息"
  echo ""
}

# 默认环境
ENV="dev"

# 解析参数
while [[ $# -gt 0 ]]; do
  case "$1" in
    -e|--env)
      ENV="$2"
      shift 2
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo -e "${RED}错误: 未知参数 $1${NC}"
      show_help
      exit 1
      ;;
  esac
done

# 验证环境参数
if [[ "$ENV" != "dev" && "$ENV" != "prod" ]]; then
  echo -e "${RED}错误: 环境必须是 'dev' 或 'prod'${NC}"
  show_help
  exit 1
fi

echo -e "${GREEN}开始部署Docker ${ENV} 环境...${NC}"

# 设置Docker Compose文件
if [[ "$ENV" == "dev" ]]; then
  COMPOSE_FILE="docker-compose-dev.yml"
  echo -e "${GREEN}使用开发环境配置...${NC}"
else
  COMPOSE_FILE="docker-compose-prod.yml"
  echo -e "${GREEN}使用生产环境配置...${NC}"
fi

# 确保目录存在
mkdir -p backend/uploads backend/static/images

echo -e "${CYAN}停止和删除旧容器...${NC}"
docker-compose -f $COMPOSE_FILE down

echo -e "${CYAN}启动新容器...${NC}"
docker-compose -f $COMPOSE_FILE up -d --build || { echo -e "${RED}容器启动失败${NC}"; exit 1; }

echo -e "${GREEN}容器状态:${NC}"
docker-compose -f $COMPOSE_FILE ps

echo -e "${GREEN}部署完成!${NC}"
echo -e "${YELLOW}前端访问地址: http://localhost${NC}"
echo -e "${YELLOW}后端API地址: http://localhost:8000${NC}"