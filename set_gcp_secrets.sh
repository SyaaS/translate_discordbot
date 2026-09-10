#!/bin/bash
# .env の内容を GCP Secret Manager に登録するスクリプト
#
# 前提: gcloud CLI がインストール・認証済みであること
# 使い方:
#   ./set_gcp_secrets.sh [PROJECT_ID] [SECRET_PREFIX]
#   ./set_gcp_secrets.sh --prefix SECRET_PREFIX
#   ./set_gcp_secrets.sh --project PROJECT_ID --prefix SECRET_PREFIX

set -euo pipefail

PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"
SECRET_PREFIX="translate_discordbot_"

usage() {
  echo "Usage: $0 [PROJECT_ID] [SECRET_PREFIX]"
  echo "       $0 --prefix SECRET_PREFIX"
  echo "       $0 --project PROJECT_ID --prefix SECRET_PREFIX"
}

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--project)
      PROJECT_ID="$2"
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
  SECRET_PREFIX="${POSITIONAL_ARGS[1]}"
fi

if [ -z "$PROJECT_ID" ]; then
  usage
  echo "または gcloud config set project <PROJECT_ID> を実行してください"
  exit 1
fi

if [ ! -f .env ]; then
  echo ".env file not found!"
  exit 1
fi

echo "GCP Secret Manager にシークレットを登録します (project: $PROJECT_ID, prefix: $SECRET_PREFIX)..."

# コメント行と空行を除去して処理
while IFS='=' read -r key value; do
  # 空行やコメントをスキップ
  [[ -z "$key" || "$key" =~ ^# ]] && continue
  # 値の前後のダブルクォート・シングルクォートを除去
  value="${value#\"}"
  value="${value%\"}"
  value="${value#\'}"
  value="${value%\'}"

  secret_name="${SECRET_PREFIX}${key}"

  # シークレットが存在しなければ作成
  if ! gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
    echo "  作成: $secret_name"
    echo -n "$value" | gcloud secrets create "$secret_name" \
      --project="$PROJECT_ID" \
      --data-file=- \
      --replication-policy="automatic"

    # Cloud Run デフォルト サービスアカウントへのアクセス権限付与
    project_num="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)' 2>/dev/null || true)"
    if [ -n "$project_num" ]; then
      gcloud secrets add-iam-policy-binding "$secret_name" \
        --member="serviceAccount:${project_num}-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor" \
        --project="$PROJECT_ID" &>/dev/null || true
    fi
  else
    echo "  更新: $secret_name"
    echo -n "$value" | gcloud secrets versions add "$secret_name" \
      --project="$PROJECT_ID" \
      --data-file=-
  fi
done < <(grep -v '^#' .env | grep -v '^$')

echo "Done!"
