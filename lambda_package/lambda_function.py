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

def handler(event, context):
    print("Starting update...")

    # Load pokedex from S3
    response = s3.get_object(Bucket=bucket, Key=csv_file)
    content = response['Body'].read().decode('utf-8')
    reader = csv.DictReader(StringIO(content))
    pokemon_names = [row['pokemon'].strip().lower() for row in reader][:25]

    all_items = []  # Collect items for CSV generation

    for name in pokemon_names:
        print(f"Fetching cards for: {name}")
        url = f'https://api.pokemontcg.io/v2/cards?q=name:{name}'

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
                set_info = card.get('set', {})
                set_name = set_info.get('name', 'n/a')
                release_date = set_info.get('releaseDate', 'unknown')

                # Pull lowest market price from TCGPlayer (if available)
                price = Decimal("0")
                prices = card.get('tcgplayer', {}).get('prices', {})

                for variant in ['normal', 'holofoil']:
                    try:
                        variant_price = prices.get(variant, {}).get('market', None)
                        if variant_price is not None:
                            price = Decimal(str(variant_price))
                            break
                    except (InvalidOperation, TypeError):
                        continue

                item = {
                    'pokemon': name,
                    'card_id': card_id,
                    'image_url': image_url,
                    'set_name': set_name,
                    'release_date': release_date,
                    'price_usd': price
                }

                batch.put_item(Item=item)
                all_items.append(item)  # Store item for CSV output

        print(f"✅ Synced {len(data)} cards for {name}")

    # Write to CSV
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(['pokemon', 'card_id', 'image_url', 'set_name', 'release_date', 'price_usd'])

    for item in all_items:
        writer.writerow([
            item['pokemon'],
            item['card_id'],
            item['image_url'],
            item['set_name'],
            item['release_date'],
            str(item['price_usd'])
        ])

    # Upload CSV to S3
    s3.put_object(
        Bucket=bucket,
        Key='cards.csv',
        Body=csv_buffer.getvalue()
    )

    return {
        'statusCode': 200,
        'body': f'Successfully updated cards for {len(pokemon_names)} Pokémon and saved to cards.csv.'
    }
