#!/bin/bash
# Cloud Run へデプロイするスクリプト
#
# 前提:
#   - gcloud CLI がインストール・認証済み
#   - Cloud Build API が有効化済み
#   - set_gcp_secrets.sh でシークレットが登録済み
#
# 使い方:
#   ./deploy_cloudrun.sh [PROJECT_ID] [REGION] [SECRET_PREFIX]
#   ./deploy_cloudrun.sh --prefix SECRET_PREFIX
#   ./deploy_cloudrun.sh --project PROJECT_ID --region REGION --prefix SECRET_PREFIX

set -euo pipefail

PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"
REGION="asia-northeast1"
SECRET_PREFIX="translate_discordbot_"
SERVICE_NAME="translate-discordbot"

usage() {
  echo "Usage: $0 [PROJECT_ID] [REGION] [SECRET_PREFIX]"
  echo "       $0 --prefix SECRET_PREFIX"
  echo "       $0 --project PROJECT_ID --region REGION --prefix SECRET_PREFIX"
}

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--project)
      PROJECT_ID="$2"
      shift 2
      ;;
    -r|--region)
      REGION="$2"
      shift 2
      ;;
    -x|--prefix)
      SECRET_PREFIX="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done

if [ "${#POSITIONAL_ARGS[@]}" -ge 1 ]; then
  PROJECT_ID="${POSITIONAL_ARGS[0]}"
fi
if [ "${#POSITIONAL_ARGS[@]}" -ge 2 ]; then
  REGION="${POSITIONAL_ARGS[1]}"
fi
if [ "${#POSITIONAL_ARGS[@]}" -ge 3 ]; then
  SECRET_PREFIX="${POSITIONAL_ARGS[2]}"
fi

IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$SERVICE_NAME/$SERVICE_NAME"

if [ -z "$PROJECT_ID" ]; then
  usage
  echo "または gcloud config set project <PROJECT_ID> を実行してください"
  exit 1
fi

echo "=== Cloud Run デプロイ ==="
echo "  Project : $PROJECT_ID"
echo "  Region  : $REGION"
echo "  Prefix  : $SECRET_PREFIX"
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

# ── 2. Cloud Build でイメージをビルド＆プッシュ ──
echo "▶ Cloud Build でイメージをビルド＆プッシュ..."
gcloud builds submit . \
  --project="$PROJECT_ID" \
  --tag "$IMAGE"

# ── 3. Cloud Run へデプロイ ──
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
  --set-secrets="DISCORD_TOKEN=${SECRET_PREFIX}DISCORD_TOKEN:latest,DEEPL_API_KEY=${SECRET_PREFIX}DEEPL_API_KEY:latest" \
  --set-env-vars="MYMEMORY_EMAIL=$(grep '^MYMEMORY_EMAIL=' .env 2>/dev/null | cut -d'=' -f2- || echo '')"

echo ""
echo "✅ デプロイ完了！"
echo "   ログ確認: gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
