import boto3
import csv
import os
import requests
from io import StringIO
from decimal import Decimal, InvalidOperation

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

table_name = os.environ['cards_table']
bucket = os.environ['bucket']
csv_file = os.environ['pokedex_file']
api_key = os.environ['api_key']

headers = {'X-Api-Key': api_key}
table = dynamodb.Table(table_name)

def safe_decimal(val):
    try:
        return Decimal(str(val))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")

def handler(event, context):
    print("Starting update...")

    response = s3.get_object(Bucket=bucket, Key=csv_file)
    content = response['Body'].read().decode('utf-8')
    reader = csv.DictReader(StringIO(content))
    pokemon_names = [row['pokemon'].strip() for row in reader][:25]

    all_items = []

    for name in pokemon_names:
        print(f"Fetching cards for: {name}")
        url = f'https://api.pokemontcg.io/v2/cards?q=name:{name.lower()}'

        try:
            api_response = requests.get(url, headers=headers, timeout=10)
            data = api_response.json().get('data', [])
        except Exception as e:
            print(f"Failed to fetch cards for {name}: {e}")
            continue

        with table.batch_writer() as batch:
            for card in data:
                card_id = card.get('id', 'unknown')
                image_url = card.get('images', {}).get('small', 'n/a')
                rarity = card.get('rarity', 'n/a')
                set_info = card.get('set', {})
                set_name = set_info.get('name', 'n/a')
                release_date = set_info.get('releaseDate', 'unknown')

                prices = card.get('tcgplayer', {}).get('prices', {})

                item = {
                    'pokemon': name,
                    'card_id': card_id,
                    'image_url': image_url,
                    'rarity': rarity,
                    'set_name': set_name,
                    'release_date': release_date,
                    'price_low': safe_decimal(prices.get('normal', {}).get('low')),
                    'price_mid': safe_decimal(prices.get('normal', {}).get('mid')),
                    'price_market': safe_decimal(prices.get('normal', {}).get('market'))
                }

                batch.put_item(Item=item)
                all_items.append(item)

        print(f"✅ Synced {len(data)} cards for {name}")

    # Generate cards.csv
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(['pokemon', 'card_id', 'image_url', 'rarity', 'set_name', 'release_date', 'price_low', 'price_mid', 'price_market'])

    for item in all_items:
        writer.writerow([
            item['pokemon'],
            item['card_id'],
            item['image_url'],
            item['rarity'],
            item['set_name'],
            item['release_date'],
            str(item['price_low']),
            str(item['price_mid']),
            str(item['price_market']),
        ])

    # Save to S3
    s3.put_object(
        Bucket=bucket,
        Key='cards.csv',
        Body=csv_buffer.getvalue()
    )

    return {
        'statusCode': 200,
        'body': f'Successfully updated cards for {len(pokemon_names)} Pokémon and saved to cards.csv.'
    }
