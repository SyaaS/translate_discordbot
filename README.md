# 🌍 Discord Translation Bot (Multi-Language Support)

[![Discord.py](https://img.shields.io/badge/discord.py-v2.3.0+-blue.svg)](https://discordpy.readthedocs.io/en/stable/)
[![DeepL](https://img.shields.io/badge/Main_Engine-DeepL_API-002E3B.svg)](https://www.deepl.com/)
[![MyMemory](https://img.shields.io/badge/Fallback-MyMemory_API-red.svg)](https://mymemory.translated.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

国旗絵文字（リアクション）をトリガーに、Discordチャンネルの発言を自動翻訳してスレッドに投稿する高精度・多機能な翻訳ボットです。

---

## ✨ 主な機能

- 🚩 **国旗リアクション翻訳**: メッセージに国旗（🇺🇸 🇯🇵 🇫🇷 等）でリアクションするだけで即座に翻訳
- 💬 **スレッド管理**: 翻訳結果は専用スレッドに集約。元メッセージを汚さず、会話の邪魔をしません
- 🔒 **自動クローズ**: 翻訳投稿後はスレッドを自動アーカイブし、チャンネルをスッキリ保ちます
- 🤖 **デュアルエンジン対応**: 
    - **DeepL API Free** (高品質・月50万文字まで無料) をメインに使用
    - 非対応言語や制限超過時は **MyMemory API** (公式・無料) に自動フォールバック
- 🔍 **言語自動検知**: メッセージのソース言語を自動判別。多国籍なサーバーでも設定不要で動作します
- ⚡ **重複防止**: 同じ言語への翻訳はスキップし、API消費と通知を最小限に抑えます

---

## 🚀 セットアップ

### 1. 準備
```bash
git clone https://github.com/Syaas/translate_discordbot.git
cd translate_discordbot
pip install -r requirements.txt
```

### 2. Discord Botの設定
1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリを作成。
2. **Bot** タブで `Privileged Gateway Intents` -> `MESSAGE CONTENT INTENT` をオン。
3. **Bot Token** を取得。

### 3. APIキーの準備
- **DeepL API**: [DeepL API Free](https://www.deepl.com/ja/pro-api) でキーを取得（無料）。
- **MyMemory API**: 設定なしでも動きますが、[公式サイト](https://mymemory.translated.net/)でメール登録すると無料枠が 5,000 → 50,000文字/日に増量されます。

### 4. 環境変数の設定
`.env.example` を `.env` にコピーして編集してください。
```env
DISCORD_TOKEN=your_discord_bot_token_here
DEEPL_API_KEY=your_deepl_api_key_here      # オプション
MYMEMORY_EMAIL=your_email@example.com      # オプション
```

---

## 📖 使い方

1. 翻訳したいメッセージに国旗絵文字でリアクション。
2. ボットがスレッドを作成し、翻訳内容を投稿します。
3. 投稿完了後、スレッドは自動的にアーカイブされます。

> **TIP**: 同じメッセージに別の国旗をリアクションすると、クローズされたスレッドが自動的に再開されて追加翻訳が投稿され、再びクローズされます。

---

## 🛠 プロジェクト構成

```text
.
├── main.py              # ボット起動エントリポイント
├── cogs/
│   └── translator.py    # リアクション制御・スレッド管理ロジック
├── utils/
│   ├── flag_map.py      # 絵文字と言語コードの定義
│   └── translator.py    # 翻訳エンジン統合API (DeepL/MyMemory)
└── requirements.txt     # Python依存パッケージ
```

---

## 💰 コスト・制限

| エンジン | 費用 | 実質上限 | 安定性 |
|---|---|---|---|
| DeepL API Free | **完全無料** | 500,000 文字 / 月 | ◎ |
| MyMemory API | **完全無料** | 5,000 ~ 50,000 文字 / 日 | ○ |

---

## デプロイ (Fly.io)

本ボットは [Fly.io](https://fly.io/) などの Docker 対応プラットフォームに簡単にデプロイできます。

### 1. Fly.io CLI のインストールとログイン
```bash
curl -L https://fly.io/install.sh | sh
fly auth login
```

### 2. アプリの作成と設定
初回のみ以下のコマンドを実行します。
```bash
fly launch
```
※ `fly.toml` が作成されます。既存のものを使う場合は `fly deploy` を実行してください。

### 3. シークレット（環境変数）の設定
`.env` の内容を Fly.io に登録します。**GitHub にプッシュしない機密情報です。**
```bash
fly secrets set DISCORD_TOKEN="your_token" DEEPL_API_KEY="your_key"
```

### 4. デプロイの実行
```bash
fly deploy
```

---

## 📄 ライセンス
[MIT License](LICENSE)
