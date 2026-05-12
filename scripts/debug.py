import requests

API_URL = "https://api.nextmarket.games/l9asia/v1/sale/c2c"

TARGETS = [
    {"rarity": "レア", "presetIdList": ["36", "49"]},
    {"rarity": "エピック", "presetIdList": ["36", "50"]},
]

def fetch_all_pages(preset_id_list):
    all_items = []
    page = 0
    while True:
        payload = {
            "presetIdList": preset_id_list,
            "realmCode": "OLD_REALM",
            "sort": "PRICE_ASC",
        }
        resp = requests.post(
            f"{API_URL}?page={page}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        data = resp.json()
        all_items.extend(data.get("content", []))
        if data.get("last", True):
            break
        page += 1
    return all_items, data.get("totalElements", 0)

for target in TARGETS:
    items, total = fetch_all_pages(target["presetIdList"])
    prices = sorted([
        i["fiatPriceInfo"]["price"]
        for i in items
        if i.get("fiatPriceInfo") and i["fiatPriceInfo"]["currencyType"] == "JPY"
    ])
    min_price = prices[0] if prices else None
    top5_avg = round(sum(prices[:5]) / len(prices[:5]), 1) if prices else None
    print(f"{target['rarity']}: 件数={total}, 最安値=¥{min_price}, 上位5平均=¥{top5_avg}")