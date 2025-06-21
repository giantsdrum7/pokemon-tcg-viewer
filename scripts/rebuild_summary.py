import boto3
from collections import defaultdict

# Initialize DynamoDB tables
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
pokedex_table = dynamodb.Table('Pokedex')
summary_table = dynamodb.Table('PokemonSummary')

# Step 1: Clear existing summary table
def clear_summary_table():
    print("🧹 Wiping PokemonSummary table...")
    response = summary_table.scan()
    items = response.get('Items', [])

    while True:
        for item in items:
            summary_table.delete_item(Key={'pokemon': item['pokemon']})
            print(f"Deleted: {item['pokemon']}")

        if 'LastEvaluatedKey' in response:
            response = summary_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items = response['Items']
        else:
            break

    print("✅ PokemonSummary table cleared.\n")

# Step 2: Rebuild summary only for Pokémon
def build_summary():
    print("🔍 Scanning Pokedex for Pokémon cards...")
    response = pokedex_table.scan()
    items = response['Items']
    summary_data = defaultdict(list)

    while True:
        for item in items:
            if item.get('supertype') != 'Pokémon':
                continue

            base_name = item['pokemon']
            summary_data[base_name].append(item)

        if 'LastEvaluatedKey' in response:
            response = pokedex_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items = response['Items']
        else:
            break

    print("📊 Building new summary entries...")
    for base_name, cards in summary_data.items():
        if not cards:
            continue

        top_card = max(cards, key=lambda x: x.get('market_price', 0))
        summary_item = {
            'pokemon': base_name,
            'card_count': len(cards),
            'market_price': top_card.get('market_price', 0),
            'top_card_image': top_card.get('image_url', ''),
            'pokemon_image': cards[0].get('pokemon_image', '')
        }

        summary_table.put_item(Item=summary_item)
        print(f"✅ Added summary for: {base_name}")

    print("\n🎉 Summary rebuild complete. Only Pokémon included.")

# Run both steps
if __name__ == '__main__':
    clear_summary_table()
    build_summary()
