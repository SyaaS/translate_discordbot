#!/bin/bash
# .env の内容を GCP Secret Manager に登録するスクリプト
#
# 前提: gcloud CLI がインストール・認証済みであること
# 使い方: ./set_gcp_secrets.sh [PROJECT_ID]

set -euo pipefail

PROJECT_ID="${1:-$(gcloud config get-value project 2>/dev/null)}"

if [ -z "$PROJECT_ID" ]; then
  echo "Usage: $0 <PROJECT_ID>"
  echo "または gcloud config set project <PROJECT_ID> を実行してください"
  exit 1
fi

if [ ! -f .env ]; then
  echo ".env file not found!"
  exit 1
fi

echo "GCP Secret Manager にシークレットを登録します (project: $PROJECT_ID)..."

# コメント行と空行を除去して処理
while IFS='=' read -r key value; do
  # 空行やコメントをスキップ
  [[ -z "$key" || "$key" =~ ^# ]] && continue
  # 値が空の場合はスキップ
  [[ -z "$value" ]] && continue

  secret_name="$key"

  # シークレットが存在しなければ作成
  if ! gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
    echo "  作成: $secret_name"
    echo -n "$value" | gcloud secrets create "$secret_name" \
      --project="$PROJECT_ID" \
      --data-file=- \
      --replication-policy="automatic"
  else
    echo "  更新: $secret_name"
    echo -n "$value" | gcloud secrets versions add "$secret_name" \
      --project="$PROJECT_ID" \
      --data-file=-
  fi
done < <(grep -v '^#' .env | grep -v '^$')

echo "Done!"
