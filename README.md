# translate_discordbot

国旗絵文字リアクションをトリガーに、Discordチャンネルの発言を翻訳してスレッドに投稿するBotです。

## 機能

- チャンネルの投稿に国旗絵文字（🇺🇸 🇯🇵 🇫🇷 等）でリアクションすると、その言語へ自動翻訳
- 翻訳結果は元メッセージのスレッドに投稿（スレッドがなければ自動作成）、投稿後はスレッドを自動クローズ
- 同じ言語への重複翻訳はスキップ
- 翻訳エンジン: **DeepL API Free**（月50万字・無料）→ 非対応言語または失敗時は **MyMemory API**（公式・無料）にフォールバック
- DeepL が非対応の言語（タガログ語等）は最初から MyMemory に直行

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

### 3. Discord Bot の準備（Developer Portal）

#### 3-1. アプリケーションの作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセスしてログイン
2. 右上の **「New Application」** をクリック
3. アプリ名（例: `TranslateBot`）を入力して **「Create」**

#### 3-2. Botの作成とトークン取得

1. 左サイドバーの **「Bot」** を選択
2. **「Add Bot」→「Yes, do it!」** でBotを作成（すでにBotタブがある場合はスキップ）
3. **「Reset Token」** → **「Yes, do it!」** をクリックしてトークンを表示
4. 表示されたトークンをコピーして `.env` の `DISCORD_TOKEN` に貼り付ける

   > ⚠️ トークンは一度しか表示されません。必ず安全な場所に保管してください。

#### 3-3. Privileged Gateway Intents の有効化

「Bot」ページの下部 **「Privileged Gateway Intents」** セクションで以下をオンにして **「Save Changes」**:

| Intent | 要否 | 用途 |
|---|---|---|
| `MESSAGE CONTENT INTENT` | **必須** ✅ | メッセージ本文の読み取り |
| `SERVER MEMBERS INTENT` | 任意 | メンバー情報の取得 |
| `PRESENCE INTENT` | 不要 | — |

#### 3-4. サーバーへの招待（OAuth2 URL の生成）

1. 左サイドバーの **「OAuth2」→「URL Generator」** を選択
2. **Scopes** で `bot` にチェック
3. 表示される **Bot Permissions** で以下にチェック:

   | 権限 | カテゴリ |
   |---|---|
   | `Read Messages / View Channels` | General |
   | `Manage Threads` | General | ← **スレッドクローズに必須** ✅ |
   | `Send Messages` | Text |
   | `Send Messages in Threads` | Text |
   | `Create Public Threads` | Text |
   | `Read Message History` | Text |

4. ページ下部に生成された URL をコピーしてブラウザで開く
5. 招待先のサーバーを選択して **「認証」** → ✅ 完了

### 4. 翻訳 API の準備

#### DeepL API Free（推奨・無料）

1. [DeepL API Free](https://www.deepl.com/ja/pro-api) で無料アカウントを作成
2. API キー（`DeepL-Auth-Key`）をコピー

> DeepL キー未設定でも MyMemory API（公式・無料）でフォールバック動作します。

#### MyMemory API（フォールバック・クレカ不要）

| 設定 | 日次上限 |
|---|---|
| `MYMEMORY_EMAIL` 未設定 | 5,000 文字/日 |
| `MYMEMORY_EMAIL` 設定あり | 50,000 文字/日 |

上限を増やしたい場合は [mymemory.translated.net](https://mymemory.translated.net/) で無料アカウント登録後、メールアドレスを `.env` に設定してください。

### 5. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集:

```env
DISCORD_TOKEN=your_discord_bot_token_here
DEEPL_API_KEY=your_deepl_api_key_here      # 省略可。未設定時は MyMemory にフォールバック
MYMEMORY_EMAIL=your_email@example.com      # 省略可。設定すると日次上限が 5千→5万字に拡張
```

### 6. 起動

```bash
python main.py
```

## 使い方

1. Discordのチャンネルで任意のメッセージに国旗絵文字でリアクションする
2. ボットがそのメッセージのスレッドに翻訳を投稿する
3. 投稿後、スレッドは自動的にクローズ（アーカイブ）される

```
🇺🇸 English (US) Translation (via DeepL):
Hello, this is a translated message.
```

> 同じメッセージに別の国旗をリアクションすると、クローズされたスレッドが自動的に再開されて追加翻訳が投稿され、再びクローズされます。

## プロジェクト構成

```
translate_discordbot/
├── main.py              # エントリポイント
├── cogs/
│   └── translator.py    # リアクションイベント処理
├── utils/
│   ├── flag_map.py      # 国旗絵文字→言語コードマッピング
│   └── translator.py    # 翻訳処理（DeepL / MyMemory フォールバック）
├── .env.example         # 環境変数テンプレート
├── requirements.txt     # 依存ライブラリ
└── README.md
```

## コスト

| エンジン | 費用 | 上限 | クレカ | 安定性 |
|---|---|---|---|---|
| DeepL API Free | **無料** | 月50万文字 | 不要 | ◎ |
| MyMemory API（フォールバック） | **無料** | 5千〜5万文字/日 | 不要 | ○ |
