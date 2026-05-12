-- Supabase の SQL Editor で実行してください

CREATE TABLE price_snapshots (
  id            BIGSERIAL PRIMARY KEY,
  fetched_at    TIMESTAMPTZ NOT NULL,
  rarity        TEXT NOT NULL,         -- 'レア' or 'エピック'
  total_count   INTEGER,               -- 登録件数
  min_price     NUMERIC(10, 1),        -- 最安値（円）
  top5_avg_price NUMERIC(10, 1),       -- 上位5件平均（円）
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス（チャート表示を高速化）
CREATE INDEX idx_price_snapshots_fetched_at ON price_snapshots (fetched_at DESC);
CREATE INDEX idx_price_snapshots_rarity     ON price_snapshots (rarity);
