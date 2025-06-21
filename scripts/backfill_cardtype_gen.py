import boto3
import time
import requests

# AWS setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('Pokedex')

# PokéTCG API setup
API_URL = "https://api.pokemontcg.io/v2/cards/"
HEADERS = {
    "X-Api-Key": "37816893-cb51-4a0c-9d99-d5b49d65bffa"  # ⬅️ INSERT YOUR KEY HERE
}

def get_generation(dex):
    if 1 <= dex <= 151:
        return 1
    elif 152 <= dex <= 251:
        return 2
    elif 252 <= dex <= 386:
        return 3
    elif 387 <= dex <= 493:
        return 4
    elif 494 <= dex <= 649:
        return 5
    elif 650 <= dex <= 721:
        return 6
    elif 722 <= dex <= 809:
        return 7
    elif 810 <= dex <= 905:
        return 8
    else:
        return 9

def backfill_data():
    print("🔄 Scanning DynamoDB for card updates...")
    response = table.scan()
    items = response['Items']
    updated, skipped, errored = 0, 0, 0

    while True:
        for item in items:
            card_id = item.get('card_id')
            if not card_id:
                skipped += 1
                continue

            key = {
                'pokemon': item['pokemon'],
                'set': item['set']
            }

            try:
                # Fetch card info from API
                res = requests.get(f"{API_URL}{card_id}", headers=HEADERS)
                if res.status_code != 200:
                    print(f"❌ Error fetching {card_id}: {res.status_code}")
                    errored += 1
                    continue

                data = res.json().get('data', {})
                supertype = data.get('supertype', '').strip()
                pokedex_numbers = data.get('nationalPokedexNumbers', [])
                dex = pokedex_numbers[0] if pokedex_numbers else None

                update_expr = "SET cardtype = :ct"
                expr_vals = {":ct": supertype.lower() if supertype else "unknown"}

                if supertype == "Pokémon" and dex:
                    gen = get_generation(dex)
                    update_expr += ", dex_number = :dex, gen = :gen"
                    expr_vals[":dex"] = dex
                    expr_vals[":gen"] = gen

                table.update_item(
                    Key=key,
                    UpdateExpression=update_expr,
                    ExpressionAttributeValues=expr_vals
                )

                print(f"✅ {card_id} → cardtype: {expr_vals[':ct']}" +
                        (f", dex: {expr_vals.get(':dex')}, gen: {expr_vals.get(':gen')}" if ':dex' in expr_vals else ""))
                updated += 1
                if updated % 100 == 0:
                    print(f"⏳ {updated} cards updated so far...")



            except Exception as e:
                print(f"⚠️ Error updating {card_id}: {e}")
                errored += 1
                continue

            time.sleep(0.04)  # Respect API limits

        if 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items = response['Items']
        else:
            break

    print(f"\n🎉 Done! {updated} cards updated, {skipped} skipped (no card_id), {errored} errored.")

if __name__ == '__main__':
    backfill_data()
