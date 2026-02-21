# translate_discordbot

国旗絵文字リアクションをトリガーに、Discordチャンネルの発言を翻訳してスレッドに投稿するBotです。

## 機能

- チャンネルの投稿に国旗絵文字（🇺🇸 🇯🇵 🇫🇷 等）でリアクションすると、その言語へ自動翻訳
- 翻訳結果は元メッセージのスレッドに投稿（スレッドがなければ自動作成）
- 同じ言語への重複翻訳はスキップ
- 翻訳エンジン: **DeepL API Free**（月50万字・無料）→ 失敗時 **Google Translate**（非公式）にフォールバック

## 対応国旗（主要なもの）

🇯🇵 日本語 / 🇺🇸 英語(US) / 🇬🇧 英語(UK) / 🇨🇳 中国語(簡体) / 🇹🇼 中国語(繁体) / 🇰🇷 韓国語  
🇫🇷 フランス語 / 🇩🇪 ドイツ語 / 🇪🇸 スペイン語 / 🇧🇷 ポルトガル語(BR) / 🇮🇹 イタリア語  
🇷🇺 ロシア語 / 🇺🇦 ウクライナ語 / 🇵🇱 ポーランド語 / 🇹🇷 トルコ語 / 🇸🇦 アラビア語  
その他50カ国以上（`utils/flag_map.py` 参照）

## セットアップ

### 1. リポジトリのクローン・移動

```bash
git clone <repository_url>
cd translate_discordbot
```

### 2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 3. Discord Bot の準備

1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリケーションを作成
2. **Bot** ページでトークンをコピー
3. **Privileged Gateway Intents** で以下を有効化:
   - `SERVER MEMBERS INTENT`（任意）
   - `MESSAGE CONTENT INTENT` ✅（必須）
4. OAuth2 URL を生成してサーバーに招待  
   - Scopes: `bot`
   - Bot Permissions: `Read Messages/View Channels`, `Send Messages`, `Read Message History`, `Create Public Threads`, `Send Messages in Threads`

### 4. DeepL API キーの取得（推奨・無料）

1. [DeepL API Free](https://www.deepl.com/ja/pro-api) で無料アカウントを作成
2. API キー（`DeepL-Auth-Key`）をコピー

> **注意**: DeepL キー未設定でも Google Translate（非公式）でフォールバック動作しますが、安定性が低下します。

### 5. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集:

```env
DISCORD_TOKEN=your_discord_bot_token_here
DEEPL_API_KEY=your_deepl_api_key_here   # 省略可（フォールバック使用）
```

### 6. 起動

```bash
python main.py
```

## 使い方

1. Discordのチャンネルで任意のメッセージに国旗絵文字でリアクションする
2. ボットがそのメッセージのスレッドに翻訳を投稿する

```
🇺🇸 English (US) Translation (via DeepL):
Hello, this is a translated message.
```

## プロジェクト構成

```
translate_discordbot/
├── main.py              # エントリポイント
├── cogs/
│   └── translator.py    # リアクションイベント処理
├── utils/
│   ├── flag_map.py      # 国旗絵文字→言語コードマッピング
│   └── translator.py    # 翻訳処理（DeepL / Google Translate）
├── .env.example         # 環境変数テンプレート
├── requirements.txt     # 依存ライブラリ
└── README.md
```

## コスト

| エンジン | 費用 | 上限 |
|---|---|---|
| DeepL API Free | **無料** | 月50万文字 |
| Google Translate (フォールバック) | **無料** | 実質無制限（非公式・不安定） |
