# Lordnine Market Price Tracker

ロードナインのマーケット価格を5分ごとに自動取得・蓄積するシステム。

## 構成

```
GitHub Actions (5分ごと cron)
  → scripts/fetch_prices.py
  → Supabase (price_snapshots テーブル)
```

## セットアップ手順

### 1. Supabase テーブル作成

Supabase ダッシュボード → SQL Editor を開き、
`scripts/create_table.sql` の内容を貼り付けて実行。

### 2. GitHub リポジトリ作成

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/japan-phoenix/lordnine-market.git
git push -u origin main
```

### 3. GitHub Actions 有効化

リポジトリの **Actions タブ** を開き、ワークフローを有効化。

### 4. 動作確認

Actions タブ → 「Fetch Lordnine Market Prices」→ 「Run workflow」で手動実行して確認。

## 取得データ

| カラム | 内容 |
|--------|------|
| fetched_at | 取得日時 |
| rarity | レア / エピック |
| total_count | 登録件数 |
| min_price | 最安値（円） |
| top5_avg_price | 上位5件平均（円） |

## チャート表示

Supabase → Google Looker Studio で接続してチャート作成。

接続方法：
1. Looker Studio (https://lookerstudio.google.com) を開く
2. 「データソースを追加」→「PostgreSQL」
3. Supabase の接続情報を入力
