import requests
from datetime import datetime, timezone
from supabase import create_client

# === 設定 ===
SUPABASE_URL = "https://lvtqanjloslkwapvgdpw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2dHFhbmpsb3Nsa3dhcHZnZHB3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2MTA1NjgsImV4cCI6MjA5NDE4NjU2OH0.2cCNqCeIugWsvO7Eatdz2t7KCYcENss3z83U_7Udp1Q"

API_URL = "https://api.nextmarket.games/l9asia/v1/sale/c2c"

TARGETS = [
    {
        "rarity": "レア",
        "presetIdList": ["36", "49"],
        "realmCode": "OLD_REALM",
        "sort": "PRICE_ASC",
    },
    {
        "rarity": "エピック",
        "presetIdList": ["36", "50"],
        "realmCode": "OLD_REALM",
        "sort": "PRICE_ASC",
    },
]


def get_usd_jpy_rate():
    """現在のUSD/JPY為替レートを取得"""
    resp = requests.get(
        "https://api.frankfurter.app/latest?from=USD&to=JPY",
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["rates"]["JPY"]


def fetch_all_pages(preset_id_list, realm_code, sort):
    """全ページのデータを取得して返す"""
    all_items = []
    page = 0
    total_elements = 0

    while True:
        payload = {
            "presetIdList": preset_id_list,
            "realmCode": realm_code,
            "sort": sort,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ja-JP,ja;q=0.9",
        }
        resp = requests.post(
            f"{API_URL}?page={page}",
            json=payload,
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        content = data.get("content", [])
        all_items.extend(content)
        total_elements = data.get("totalElements", 0)

        if data.get("last", True):
            break
        page += 1

    return all_items, total_elements


def analyze(items, usd_jpy_rate):
    """最安値・上位5件平均を計算（USD・円両方）"""
    prices_usd = sorted([
        item["fiatPriceInfo"]["price"]
        for item in items
        if item.get("fiatPriceInfo")
    ])

    if not prices_usd:
        return None, None, None, None

    min_usd = prices_usd[0]
    top5_avg_usd = round(sum(prices_usd[:5]) / len(prices_usd[:5]), 4)
    min_jpy = round(min_usd * usd_jpy_rate, 1)
    top5_avg_jpy = round(top5_avg_usd * usd_jpy_rate, 1)

    return min_usd, top5_avg_usd, min_jpy, top5_avg_jpy


def main():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    fetched_at = datetime.now(timezone.utc).isoformat()

    # 為替レート取得
    usd_jpy_rate = get_usd_jpy_rate()
    print(f"USD/JPY: {usd_jpy_rate}")

    for target in TARGETS:
        print(f"取得中: {target['rarity']}...")
        try:
            items, total_count = fetch_all_pages(
                target["presetIdList"],
                target["realmCode"],
                target["sort"],
            )
            min_usd, top5_avg_usd, min_jpy, top5_avg_jpy = analyze(items, usd_jpy_rate)

            record = {
                "fetched_at": fetched_at,
                "rarity": target["rarity"],
                "total_count": total_count,
                "min_price": min_jpy,
                "top5_avg_price": top5_avg_jpy,
                "min_price_usd": min_usd,
                "top5_avg_price_usd": top5_avg_usd,
                "usd_jpy_rate": usd_jpy_rate,
                "min_price_rare_equiv": round(min_jpy / 5, 1) if target["rarity"] == "エピック" else None,
                "top5_avg_rare_equiv": round(top5_avg_jpy / 5, 1) if target["rarity"] == "エピック" else None,
            }

            print(f"  件数: {total_count}, 最安値: ¥{min_jpy}(${min_usd}), 上位5平均: ¥{top5_avg_jpy}(${top5_avg_usd})")

            supabase.table("price_snapshots").insert(record).execute()
            print(f"  → Supabase保存完了")

        except Exception as e:
            print(f"  エラー: {e}")

    print("完了")


if __name__ == "__main__":
    main()