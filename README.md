# SNS分析ツール

Twitter/X・Instagram対応のマーケティング分析Webアプリケーション

## 概要

個人ユーザー向けのSNS分析ツールです。マーケティング戦略立案と競合分析を支援し、データをスプレッドシート形式で保存・出力できます。

## 主な機能

### 対応SNS
- Twitter/X
- Instagram

### 分析機能
- 📝 **投稿内容・テキスト分析**
  - キーワード分析
  - 感情分析
  - トレンド分析

- 📊 **エンゲージメント分析**
  - いいね数の推移
  - コメント数の分析
  - シェア数の分析
  - エンゲージメント率の計算

- 👥 **フォロワー分析**
  - フォロワー数の推移
  - フォロワーの属性分析

- 🏷️ **ハッシュタグ分析**
  - 人気ハッシュタグの特定
  - ハッシュタグの効果分析

- ⏰ **投稿時間・頻度分析**
  - 最適な投稿時間の特定
  - 投稿頻度の分析

- 🔍 **競合分析**
  - 競合アカウントとの比較
  - 競合のエンゲージメント分析

### データ保存
- スプレッドシート形式での保存
- CSVエクスポート機能

## 技術スタック

- **フロントエンド**: HTML/CSS/JavaScript + Chart.js
- **バックエンド**: Python Flask
- **データ処理**: pandas, requests
- **外部API**: Twitter API v2, Instagram API
- **データ保存**: Google Sheets API, CSV

## セットアップ

### 前提条件
- Python 3.8以上
- Twitter Developer Account
- Instagram Developer Account（オプション）

### インストール

1. リポジトリをクローン
```bash
git clone https://github.com/Yuuta12-maker/sns-analysis-tool.git
cd sns-analysis-tool
```

2. 仮想環境を作成・有効化
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 依存関係をインストール
```bash
pip install -r requirements.txt
```

4. 環境変数を設定
```bash
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

### 設定

#### Twitter API設定
1. [Twitter Developer Portal](https://developer.twitter.com/)でアプリを作成
2. APIキーとトークンを取得
3. `.env`ファイルに設定

```env
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### 実行

```bash
python backend/app.py
```

ブラウザで `http://localhost:5000` にアクセス

## プロジェクト構成

```
sns-analysis-tool/
├── backend/           # Pythonバックエンド
│   ├── app.py        # メインアプリケーション
│   ├── twitter_api.py # Twitter API連携
│   └── data_processor.py # データ処理
├── templates/         # HTMLテンプレート
├── static/           
│   ├── css/          # スタイルシート
│   └── js/           # JavaScript
├── requirements.txt   # Python依存関係
├── .env.example      # 環境変数テンプレート
└── README.md
```

## 使用方法

1. トップページでアカウント名を入力
2. 分析したいSNSプラットフォームを選択
3. 分析期間を設定
4. 「分析開始」ボタンをクリック
5. 結果をダッシュボードで確認
6. スプレッドシートまたはCSVでデータをダウンロード

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。

## サポート

質問や問題がある場合は、GitHubのIssuesを使用してください。