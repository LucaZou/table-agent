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
  echo -e "  -p, --prune       清理未使用的Docker资源"
  echo -e "  -h, --help        显示帮助信息"
  echo ""
}

# 默认环境
ENV="dev"
PRUNE=false

# 解析参数
while [[ $# -gt 0 ]]; do
  case "$1" in
    -e|--env)
      ENV="$2"
      shift 2
      ;;
    -p|--prune)
      PRUNE=true
      shift
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

# 检查Docker是否已安装
if ! command -v docker &> /dev/null; then
  echo -e "${RED}错误: Docker未安装，请先安装Docker${NC}"
  exit 1
fi

# 检查docker-compose是否已安装
if ! command -v docker-compose &> /dev/null; then
  echo -e "${RED}错误: Docker Compose未安装，请先安装Docker Compose${NC}"
  exit 1
fi

echo -e "${GREEN}检测到Docker: $(docker --version)${NC}"
echo -e "${GREEN}检测到Docker Compose: $(docker-compose --version)${NC}"

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

# 生产环境检查前端构建
if [[ "$ENV" == "prod" ]]; then
  echo -e "${CYAN}检查证书文件...${NC}"
  if [ ! -f "uagent.top.pem" ] || [ ! -f "uagent.top.key" ]; then
    echo -e "${YELLOW}警告: SSL证书文件不存在，请确保证书文件放置在正确位置${NC}"
    echo -n "是否继续部署? (y/n): "
    read -r continue
    if [[ "$continue" != "y" ]]; then
      echo -e "${RED}部署已取消${NC}"
      exit 0
    fi
  fi
fi

echo -e "${CYAN}停止和删除旧容器...${NC}"
docker-compose -f $COMPOSE_FILE down

# 如果指定了清理选项
if [[ "$PRUNE" == true ]]; then
  echo -e "${CYAN}清理未使用的Docker资源...${NC}"
  docker system prune -f
fi

echo -e "${CYAN}启动新容器...${NC}"
docker-compose -f $COMPOSE_FILE up -d --build || { echo -e "${RED}容器启动失败${NC}"; exit 1; }

echo -e "${CYAN}等待容器启动完成...${NC}"
sleep 5

echo -e "${GREEN}容器状态:${NC}"
docker-compose -f $COMPOSE_FILE ps

echo -e "${GREEN}检查容器健康状态...${NC}"
if [[ "$ENV" == "prod" ]]; then
  # 检查前端容器健康状态
  if [[ "$(docker inspect --format='{{.State.Health.Status}}' u_agent_frontend 2>/dev/null)" != "healthy" ]]; then
    echo -e "${YELLOW}警告: 前端容器还未达到健康状态，可能需要更多时间启动${NC}"
  else
    echo -e "${GREEN}前端容器状态正常${NC}"
  fi

  # 检查后端容器健康状态
  if [[ "$(docker inspect --format='{{.State.Health.Status}}' u_agent_backend 2>/dev/null)" != "healthy" ]]; then
    echo -e "${YELLOW}警告: 后端容器还未达到健康状态，可能需要更多时间启动${NC}"
  else
    echo -e "${GREEN}后端容器状态正常${NC}"
  fi
fi

echo -e "${GREEN}部署完成!${NC}"
if [[ "$ENV" == "prod" ]]; then
  echo -e "${YELLOW}前端访问地址: https://localhost${NC}"
else
  echo -e "${YELLOW}前端访问地址: http://localhost${NC}"
fi
echo -e "${YELLOW}后端API地址: http://localhost:8000${NC}"