FROM python:3.9-slim

WORKDIR /app

# 设置Python不缓存pyc文件
ENV PYTHONDONTWRITEBYTECODE=1
# 设置Python不缓冲输出
ENV PYTHONUNBUFFERED=1
# 设置时区
ENV TZ=Asia/Shanghai

# 配置清华大学镜像源并安装依赖
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        python3-dev \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制项目依赖文件
COPY requirements.txt .

# 先安装numpy/pandas等大型包，加快后续安装
# 使用阿里云的pip镜像源安装依赖
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip install --no-cache-dir numpy pandas matplotlib \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf ~/.cache/pip

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p uploads static/images

# 端口暴露
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]