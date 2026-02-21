# Dockerfile for Discord Bot
FROM python:3.10-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なシステムパッケージのインストール（必要に応じて）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードのコピー
COPY . .

# ボットの起動
CMD ["python", "main.py"]
