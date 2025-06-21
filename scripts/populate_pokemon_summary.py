import boto3
import re
import csv
from collections import defaultdict
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
source_table = dynamodb.Table('Pokedex')
target_table = dynamodb.Table('PokemonSummary')

# Load full name-to-dex dictionary from CSV
def load_dex_mapping(csv_path="scripts/poke-num-with-images.csv"):
    pokedex = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            dex, name, _ = row
            name_clean = name.strip().title()
            pokedex[name_clean] = int(dex.strip())
    return pokedex

def get_generation(dex):
    if dex <= 151: return 1
    if dex <= 251: return 2
    if dex <= 386: return 3
    if dex <= 493: return 4
    if dex <= 649: return 5
    if dex <= 721: return 6
    if dex <= 809: return 7
    if dex <= 905: return 8
    return 9

def extract_base_names(raw_name):
    clean = raw_name.lower()
    clean = re.sub(r"( ex| gx| vstar| vmax| lv\.x| δ| legend)", "", clean, flags=re.IGNORECASE)
    names = re.split(r"\s+and\s+|/| & ", clean)
    return [n.strip().title() for n in names if n.strip()]

def build_summary():
    POKEDEX_NUMBERS = load_dex_mapping()

    scan_kwargs = {}
    grouped = defaultdict(lambda: {
        "pokemon_image": None,
        "top_card_image": None,
        "market_price": Decimal("0.0"),
        "card_count": 0
    })

    print("🔄 Scanning Pokedex table...")
    while True:
        response = source_table.scan(**scan_kwargs)
        for item in response.get("Items", []):
            try:
                price = Decimal(str(item.get("market_price", 0)))
            except:
                price = Decimal("0.0")

            image_url = item.get("image_url", "")
            pokemon_image = item.get("pokemon_image", "")
            full_name = item.get("pokemon", "")

            for base in extract_base_names(full_name):
                group = grouped[base]
                group["card_count"] += 1

                if not group["pokemon_image"] and pokemon_image:
                    group["pokemon_image"] = pokemon_image

                if price > group["market_price"]:
                    group["market_price"] = price
                    group["top_card_image"] = image_url

        if 'LastEvaluatedKey' in response:
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        else:
            break

    print("📝 Writing to PokemonSummary table...")
    count_written = 0
    for base, data in grouped.items():
        dex = POKEDEX_NUMBERS.get(base)
        if dex is None:
            print(f"⚠️ Skipping {base} (not in dex mapping)")
            continue

        generation = get_generation(dex)

        target_table.put_item(Item={
            "pokemon": base,
            "pokemon_image": data["pokemon_image"],
            "top_card_image": data["top_card_image"],
            "market_price": data["market_price"],
            "card_count": data["card_count"],
            "generation": generation
        })
        print(f"✔️ {base} (Gen {generation}) written")
        count_written += 1

    print(f"✅ Done! {count_written} Pokémon summaries created.")

if __name__ == "__main__":
    build_summary()
