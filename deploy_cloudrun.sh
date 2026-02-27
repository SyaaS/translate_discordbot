#!/bin/bash
# Cloud Run へデプロイするスクリプト
#
# 前提:
#   - gcloud CLI がインストール・認証済み
#   - Docker が利用可能（Artifact Registry にプッシュするため）
#   - set_gcp_secrets.sh でシークレットが登録済み
#
# 使い方: ./deploy_cloudrun.sh [PROJECT_ID] [REGION]

set -euo pipefail

PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${2:-asia-northeast1}"
SERVICE_NAME="translate-discordbot"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME"

if [ -z "$PROJECT_ID" ]; then
  echo "Usage: $0 <PROJECT_ID> [REGION]"
  echo "または gcloud config set project <PROJECT_ID> を実行してください"
  exit 1
fi

echo "=== Cloud Run デプロイ ==="
echo "  Project : $PROJECT_ID"
echo "  Region  : $REGION"
echo "  Service : $SERVICE_NAME"
echo "  Image   : $IMAGE"
echo ""

# ── 1. Artifact Registry リポジトリ作成（初回のみ） ──
echo "▶ Artifact Registry リポジトリを確認..."
if ! gcloud artifacts repositories describe "$SERVICE_NAME" \
  --project="$PROJECT_ID" \
  --location="$REGION" &>/dev/null; then
  echo "  リポジトリを作成します..."
  gcloud artifacts repositories create "$SERVICE_NAME" \
    --project="$PROJECT_ID" \
    --location="$REGION" \
    --repository-format=docker
fi

# ── 2. Docker 認証設定 ──
echo "▶ Docker 認証を設定..."
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet

# ── 3. Docker イメージをビルド＆プッシュ ──
echo "▶ Docker イメージをビルド..."
docker build -t "$IMAGE" .

echo "▶ Docker イメージをプッシュ..."
docker push "$IMAGE"

# ── 4. Cloud Run へデプロイ ──
echo "▶ Cloud Run へデプロイ..."
gcloud run deploy "$SERVICE_NAME" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --image="$IMAGE" \
  --platform=managed \
  --no-allow-unauthenticated \
  --port=8080 \
  --min-instances=1 \
  --max-instances=1 \
  --no-cpu-throttling \
  --cpu=1 \
  --memory=512Mi \
  --timeout=3600 \
  --set-secrets="DISCORD_TOKEN=DISCORD_TOKEN:latest,DEEPL_API_KEY=DEEPL_API_KEY:latest" \
  --set-env-vars="MYMEMORY_EMAIL=$(grep '^MYMEMORY_EMAIL=' .env 2>/dev/null | cut -d'=' -f2- || echo '')"

echo ""
echo "✅ デプロイ完了！"
echo "   ログ確認: gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
