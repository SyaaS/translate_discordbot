# 🌍 Discord Translation Bot (Multi-Language & Auto-Translate Support)

[![Discord.py](https://img.shields.io/badge/discord.py-v2.3.0+-blue.svg)](https://discordpy.readthedocs.io/en/stable/)
[![DeepL](https://img.shields.io/badge/Main_Engine-DeepL_API-002E3B.svg)](https://www.deepl.com/)
[![MyMemory](https://img.shields.io/badge/Fallback-MyMemory_API-red.svg)](https://mymemory.translated.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

国旗絵文字・カスタム絵文字リアクションによる即時スレッド翻訳機能に加え、**チャンネル間全自動翻訳・スレッド自動生成翻訳・特定ユーザー＆絵文字トリガー翻訳・元言語制限フィルター・過去ログ一括バックフィル**を備えた高機能な Discord 翻訳ボットです。

---

## ✨ 主な機能

### 1. 🚩 リアクション即時翻訳
- **国旗＆カスタム絵文字対応**: メッセージに国旗（🇺🇸 🇯🇵 🇫🇷 等）やカスタム絵文字でリアクションするだけで、指定言語へ即座に翻訳。
- 💬 **スレッド管理**: 翻訳結果は専用スレッドに集約。元メッセージを汚さず、会話の邪魔をしません。
- 🔒 **自動クローズ＆再開**: 翻訳投稿後はスレッドを自動アーカイブ。追加リアクション時は自動で再開して追記します。
- ⚙️ **カスタム絵文字マッピング (`/emoji` コマンド)**: サーバーごとに独自のカスタム絵文字を任意の言語にマッピング可能。

### 2. 🤖 自動翻訳＆スレッド自動生成 (`!auto_translate`)
- 🔄 **全自動翻訳モード (`all`)**: 指定チャンネルに投稿されたメッセージを別のチャンネルへ自動で翻訳・転送。
- 🧵 **スレッド自動翻訳モード (`thread`)**: 発言の直下に自動でスレッド（例: `🌐 翻訳 (Chinese Simplified)`）を作成し、その中に翻訳を投稿。
- 🎯 **トリガー限定翻訳モード (`trigger`)**: 特定ユーザーの発言かつ指定スタンプが押された場合のみ翻訳転送。
- 🔍 **元言語制限フィルター (`source_lang`)**: 日本語（`ja`）など特定言語で投稿されたメッセージのみを処理対象とし、英語や中国語などの発言は自動スキップ（`add_thread` はデフォルトで `ja` 限定）。
- 👤 **対象ユーザー・絵文字絞り込み**: 全体設定またはペア個別設定で対象ユーザー（例: `user1`）やスタンプを自由に変更可能。
- 📚 **過去ログ一括バックフィル (`backfill`)**: 過去メッセージを古い順から一括翻訳・転送（重複メッセージの自動検出スキップ付き）。

### 3. 🤖 デュアル翻訳エンジン＆最適化
- **DeepL API Free**: 高精度な標準翻訳（月50万文字無料枠）。
- **MyMemory API**: DeepL非対応言語やフォールバック時に自動切り替え（メール登録で5万文字/日無料）。
- ⚡ **重複判定＆言語自動判定**: 同一言語翻訳の自動回避、同一メッセージの重複投稿防止。

---

## 📖 使い方・コマンド一覧

### リアクション翻訳
1. 翻訳したいメッセージに国旗絵文字（例: 🇺🇸 🇯🇵 🇨🇳）やカスタム絵文字でリアクションします。
2. ボットが自動的にスレッドを作成し、翻訳を投稿してアーカイブします。

### 絵文字マッピング管理（スラッシュコマンド）
| コマンド | 説明 |
|---|---|
| `/emoji add <emoji> <language>` | カスタム絵文字を特定の翻訳言語にマッピング追加 |
| `/emoji remove <emoji>` | カスタム絵文字マッピングを削除 |
| `/emoji list` | 現在登録されている絵文字マッピング一覧を表示 |
| `/emoji default_flags <enabled>` | デフォルト国旗絵文字の有効/無効切り替え |

### 自動翻訳ペア管理コマンド (`!auto_translate` / `!at`)
| コマンド | 説明 |
|---|---|
| `!at add <#転送元> <#転送先> <言語コード> [ユーザー] [元言語制限]` | 全自動翻訳ペアを追加（転送元＝転送先の場合はスレッド翻訳） |
| `!at add_thread <#対象チャンネル> <言語コード> [ユーザー] [元言語制限]` | スレッド自動翻訳ペアを追加（[元言語制限]省略時は `ja` 限定） |
| `!at add_trigger <#転送元> <#転送先> <言語コード> [スタンプ] [ユーザー] [元言語制限]` | 特定スタンプ・ユーザー指定のトリガー翻訳ペアを追加 |
| `!at list` | 現在設定されている自動翻訳ペア一覧を表示 |
| `!at remove <#転送元> [#転送先]` | 自動翻訳ペアを削除 |
| `!at trigger_user add/remove/list <ユーザー名/ID>` | トリガー対象ユーザーの管理 |
| `!at trigger_emoji add/remove/list <絵文字>` | トリガースタンプの管理 |
| `!at trigger_info` | トリガー設定の総合情報を表示 |
| `!at backfill <#転送元> <#転送先> <言語コード> [件数] [開始ID]` | 過去メッセージの一括翻訳・転送 |
| `!at env_export` | 現在の設定を環境変数 (`AUTO_TRANSLATE_PAIRS` 等) 形式で出力 |

---

## 🔒 永続化（環境変数形式）

`!auto_translate env_export` で出力された設定を `.env` や GCP Secret Manager / Fly.io Secrets に設定することで、再起動後も永久に設定が保持されます。

### 設定フォーマット (`AUTO_TRANSLATE_PAIRS`)
`SOURCE_ID:TARGET_ID:LANG_CODE:MODE:EMOJI:TARGET_USERS:SOURCE_LANG_LIMIT`

```env
AUTO_TRANSLATE_PAIRS="111111111111111111:222222222222222222:ja:all:::,111111111111111111:111111111111111111:zh:thread::user1:ja,333333333333333333:111111111111111111:zh:trigger:<:translate_zhcn:999999999999999999>:user1:,333333333333333333:444444444444444444:en:trigger:<:translate_en:888888888888888888>:user1:"
TRIGGER_USERS="user1"
TRIGGER_EMOJIS="🌐"
```

---

## 🛠 プロジェクト構成

```text
.
├── main.py                # ボット起動エントリポイント（ヘルスチェックサーバー含む）
├── cogs/
│   ├── translator.py      # リアクション制御・即時スレッド翻訳ロジック
│   ├── auto_translator.py # 全自動・スレッド自動・トリガー限定自動翻訳コグ
│   └── emoji_manager.py   # スラッシュコマンド(/emoji)によるカスタム絵文字マッピング
├── utils/
│   ├── flag_map.py        # 絵文字と言語コードの定義
│   ├── emoji_config.py    # サーバーごとのカスタム絵文字設定永続化
│   └── translator.py      # 翻訳エンジン統合API (DeepL/MyMemory & 元言語判定)
├── Dockerfile             # Docker ビルド設定
├── deploy_cloudrun.sh     # GCP Cloud Run デプロイスクリプト
├── set_gcp_secrets.sh     # GCP Secret Manager 登録スクリプト
├── set_fly_secrets.sh     # Fly.io シークレット登録スクリプト
└── requirements.txt       # Python依存パッケージ
```

---

## 🚀 デプロイ

### 1. 準備
```bash
git clone https://github.com/Syaas/translate_discordbot.git
cd translate_discordbot
pip install -r requirements.txt
```

### 2. GCP Cloud Run へのデプロイ
```bash
# GCP シークレットの登録・更新
chmod +x set_gcp_secrets.sh
./set_gcp_secrets.sh --prefix translate_discordbot_

# ビルド＆デプロイ
chmod +x deploy_cloudrun.sh
./deploy_cloudrun.sh --prefix translate_discordbot_
```

---

## 📄 ライセンス
[MIT License](LICENSE)
