# 🌍 Discord Translation Bot (Multi-Language & Auto-Translate Support)

[![Discord.py](https://img.shields.io/badge/discord.py-v2.3.0+-blue.svg)](https://discordpy.readthedocs.io/en/stable/)
[![DeepL](https://img.shields.io/badge/Main_Engine-DeepL_API-002E3B.svg)](https://www.deepl.com/)
[![MyMemory](https://img.shields.io/badge/Fallback-MyMemory_API-red.svg)](https://mymemory.translated.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

国旗絵文字・カスタム絵文字リアクションによる即時スレッド翻訳機能に加え、**チャンネル間全自動翻訳・スレッド自動生成翻訳・特定ユーザー＆絵文字トリガー翻訳・元言語制限フィルター・過去ログ一括バックフィル**を備えた高機能な Discord 翻訳ボットです。

---

## ✨ 主な機能

### 1. 🚩 リアクション即時翻訳
- **国旗＆文字・カスタム絵文字対応**: メッセージに国旗（🇺🇸 🇯🇵 🇫🇷 等）やアルファベット記号（🇯 ➔ 日本語、🇪 ➔ 英語、🇨 ➔ 簡体字中国語、🇰 ➔ 韓国語 等）、カスタム絵文字でリアクションするだけで、指定言語へ即座に翻訳。
- 💬 **スレッド管理**: 翻訳結果は専用スレッドに集約。元メッセージを汚さず、会話の邪魔をしません。
- 🔒 **自動クローズ＆再開**: 翻訳投稿後はスレッドを自動アーカイブ。追加リアクション時は自動で再開して追記します。
- ⚙️ **カスタム絵文字マッピング (`/emoji` コマンド)**: サーバーごとに独自のカスタム絵文字を任意の言語にマッピング可能。

### 2. 🤖 自動翻訳＆スレッド自動生成 (`!auto_translate`)
- 🔄 **全自動翻訳モード (`all`)**: 指定チャンネルに投稿されたメッセージを別のチャンネルへ自動で翻訳・転送。
- 🧵 **スレッド自動翻訳モード (`thread`)**: 発言の直下に自動でスレッド（例: `🌐 翻訳 (Chinese Simplified)`）を作成し、その中に翻訳を投稿。
- 💬 **モード1 相互レスポンス自動スレッド翻訳 (`1`)**: 基準言語A（例: `ja`）を設定。他言語の投稿には常に言語Aの翻訳スレッドを付与し、言語A話者が他言語投稿に返信した場合は相手の投稿言語に翻訳したスレッドを自動作成。
- 🎯 **トリガー限定翻訳モード (`trigger`)**: 特定ユーザーの発言かつ指定スタンプが押された場合のみ翻訳転送。
- 🔍 **元言語制限フィルター (`source_lang`)**: 日本語（`ja`）など特定言語で投稿されたメッセージのみを処理対象とし、英語や中国語などの発言は自動スキップ（`add_thread` はデフォルトで `ja` 限定）。
- 👤 **対象ユーザー・絵文字絞り込み**: 全体設定またはペア個別設定で対象ユーザーやスタンプを自由に変更可能。
- 📚 **過去ログ一括バックフィル (`backfill`)**: 過去メッセージを古い順から一括翻訳・転送（重複メッセージの自動検出スキップ付き）。

### 3. 🤖 デュアル翻訳エンジン＆最適化
- **DeepL API Free**: 高精度な標準翻訳（月50万文字無料枠）。
- **MyMemory API**: DeepL非対応言語やフォールバック時に自動切り替え（メール登録で5万文字/日無料）。
- ⚡ **重複判定＆言語自動判定**: 同一言語翻訳の自動回避、同一メッセージの重複投稿防止。

---

## 📖 使い方・コマンド一覧

### リアクション翻訳
1. 翻訳したいメッセージに国旗絵文字（例: 🇺🇸 🇯🇵 🇨🇳）やアルファベット記号（🇯 ➔ 日本語、🇪 ➔ 英語 等）でリアクションします。
2. ボットが自動的にスレッドを作成し、翻訳を投稿してアーカイブします。

**アルファベット（Regional Indicator）対応表:**
- 🇯 (`:regional_indicator_j:`) ➔ **日本語 (`ja`)**
- 🇪 (`:regional_indicator_e:`) ➔ **英語 (`en`)**
- 🇨 (`:regional_indicator_c:`) ➔ **簡体字中国語 (`zh`)**
- 🇰 (`:regional_indicator_k:`) ➔ **韓国語 (`ko`)**
- 🇫 (`:regional_indicator_f:`) ➔ **フランス語 (`fr`)**
- 🇩 (`:regional_indicator_d:`) ➔ **ドイツ語 (`de`)**
- 🇸 (`:regional_indicator_s:`) ➔ **スペイン語 (`es`)**

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
| `!at add_mode <モード番号> <#対象チャンネル> <基準言語コード>` | モード指定自動翻訳を設定（例: `!at add_mode 1 #交流チャネル ja`） |
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

#### 💡 モード1 (`Mode 1`) の動作仕様
多言語交流チャンネルで特定の言語（例: 日本語 `ja`）をメインとする場合に最適化された双方向スレッド自動翻訳です。
- **コマンド**: `!at add_mode 1 <#対象チャンネル> <基準言語コード>`（例: `!at add_mode 1 #交流チャネル ja`）
- **通常発言の翻訳**: 基準言語以外の発言（英語、中国語等）があると、自動でスレッドを作成し **基準言語（`ja`）** 翻訳を投稿。
- **基準言語での返信**: 基準言語以外の投稿に基準言語で返信（リプライ）すると、返信元の投稿言語（英語や中国語）を自動判定し、その言語に翻訳したスレッドを投稿。
- **他言語での返信**: チャンネル参加者全員が読めるよう、自動で **基準言語（`ja`）** 翻訳スレッドを投稿。
- **重複・不要翻訳のスキップ**: 同一言語同士の発言や返信（例: 英語➔英語、日本語➔日本語）は自動スキップ。

---

---

## 🔒 設定の永続化

### 1. 🔥 Firebase (Cloud Firestore) による全自動永続化（推奨）
Discord 上でコマンド（`!at add_mode`, `!at remove`, `/emoji add` 等）を実行した瞬間に、**Firebase Firestore にリアルタイムで自動保存**され、Bot 起動時に自動復元されます。ターミナルでの設定反映作業が一切不要になります。

- **保存単位**: Bot の Discord ID ごとにドキュメント（コレクション: `bot_configs`）を自動作成して保存するため、複数サーバーや複数 Bot（Cloud Run と Fly.io 等）で同じ Firebase プロジェクトを共有しても設定が混ざりません。
- **環境変数の設定**:
  - `FIREBASE_PROJECT_ID`: Firebase / GCP プロジェクトID
  - `FIREBASE_CREDENTIALS_JSON`: （Fly.io や別プロジェクトの場合）Firebase サービスアカウント秘密鍵の JSON 文字列
    ※ Cloud Run で同一 GCP プロジェクト内の Firestore を利用する場合は、キー不要（自動認証）で `FIREBASE_PROJECT_ID` だけで接続可能です。

### 2. 環境変数形式による永続化（フォールバック）
Firebase 未設定時は、従来通り `!auto_translate env_export` で出力された設定を `.env` や GCP Secret Manager / Fly.io Secrets に設定することで設定を保持できます。

#### 設定フォーマット (`AUTO_TRANSLATE_PAIRS`)
`SOURCE_ID:TARGET_ID:LANG_CODE:MODE:EMOJI:TARGET_USERS:SOURCE_LANG_LIMIT`

```env
AUTO_TRANSLATE_PAIRS="111111111111111111:111111111111111111:ja:1:::,111111111111111111:222222222222222222:ja:all:::,111111111111111111:111111111111111111:zh:thread::user1:ja,333333333333333333:111111111111111111:zh:trigger:<:translate_zhcn:999999999>:user1:"
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

### 3. Fly.io へのデプロイ
```bash
# ログイン（初回のみ）
fly auth login

# 初回シークレット設定（必要な場合）
fly secrets set DISCORD_TOKEN="xxxx" DEEPL_API_KEY="xxxx" -a translate-discordbot

# デプロイ
fly deploy
```

---

## 📄 ライセンス
[MIT License](LICENSE)
