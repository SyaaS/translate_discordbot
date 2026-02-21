#!/bin/bash
# .env の内容を Fly.io のシークレットに設定するスクリプト

if [ ! -f .env ]; then
  echo ".env file not found!"
  exit 1
fi

echo "Setting secrets on Fly.io from .env..."

# コメント行と空行を除去して fly secrets set に渡す
grep -v '^#' .env | grep -v '^$' | xargs fly secrets set

echo "Done!"
