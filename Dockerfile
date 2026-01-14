# 1. 基础镜像：找一个装好了 Python 3.9 的 Linux 系统
FROM python:3.11-slim

# 2. 设置工作目录：在容器里创建一个叫 /app 的文件夹
WORKDIR /app

# 3. 复制依赖清单：把电脑上的 requirements.txt 拷进去
COPY requirements.txt .

# 4. 安装依赖：在容器里运行 pip install
# 使用清华源加速，否则会非常慢
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 5. 复制代码：把当前目录下所有代码都拷进去
COPY . .

# 6. 暴露端口：告诉外界，我会在 5000 端口提供服务
EXPOSE 5000

# 7. 启动命令：容器启动时，自动运行 python run.py
CMD ["python", "run.py"]