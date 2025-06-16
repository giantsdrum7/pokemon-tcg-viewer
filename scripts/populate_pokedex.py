import boto3
import requests
import time
from decimal import Decimal

# --------- CONFIG ---------
API_KEY = '37816893-cb51-4a0c-9d99-d5b49d65bffa'
HEADERS = {"X-Api-Key": API_KEY}
REGION = 'us-east-2'
TABLE_NAME = 'Pokedex'

# --------- AWS INIT ---------
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

# --------- FETCH ALL CARDS ---------
def fetch_all_cards():
    url = "https://api.pokemontcg.io/v2/cards"
    page = 1
    page_size = 250
    cards = []

    while True:
        print(f"📦 Fetching page {page}...")
        response = requests.get(f"{url}?page={page}&pageSize={page_size}", headers=HEADERS)

        if response.status_code != 200:
            print(f"❌ API error: {response.status_code}")
            break

        data = response.json().get("data", [])
        if not data:
            break

        cards.extend(data)
        page += 1
        time.sleep(0.3)  # Prevent throttling

    print(f"✅ Fetched {len(cards)} cards total.")
    return cards

# --------- CLEAN PRICE ---------
def clean_price(price):
    try:
        return Decimal(str(round(float(price), 2)))
    except:
        return Decimal("0.00")

# --------- UPLOAD CARD VARIANTS ---------
def upload_variant(card, variant_name, price_obj):
    try:
        set_name = card["set"]["name"]
        item = {
            "pokemon": card["name"],                 # Partition Key
            "set": set_name,                         # Sort Key
            "card_id": card["id"],
            "set_code": card["set"]["id"],
            "collector_number": card.get("number", ""),
            "image_url": card["images"]["large"],
            "rarity": card.get("rarity", "Unknown"),
            "variant": variant_name,
            "types": card.get("types", []),
            "subtypes": card.get("subtypes", []),
            "prices": {
                "low": clean_price(price_obj.get("low")),
                "mid": clean_price(price_obj.get("mid")),
                "market": clean_price(price_obj.get("market")),
            }
        }

        table.put_item(Item=item)
        print(f"✅ Uploaded {card['name']} ({variant_name}) — {set_name}")
    except Exception as e:
        print(f"⚠️ Failed to upload variant {variant_name} for card {card.get('id')}: {str(e)}")

# --------- MAIN ---------
if __name__ == "__main__":
    all_cards = fetch_all_cards()

    for card in all_cards:
        prices = card.get("tcgplayer", {}).get("prices", {})

        # Upload each available variant
        for variant_name in ["normal", "holofoil", "reverseHolofoil"]:
            if variant_name in prices:
                upload_variant(card, variant_name, prices[variant_name])

    print("🎉 All cards and variants uploaded to DynamoDB: Pokedex")
