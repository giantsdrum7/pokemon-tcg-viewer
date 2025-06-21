import boto3
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('Pokedex')

def normalize_cardtype():
    print("🔍 Scanning for cardtype = 'pokémon'…")
    response = table.scan(
        FilterExpression=Attr('cardtype').eq('pokémon')
    )
    items = response.get('Items', [])
    print(f"Found {len(items)} items to update.")

    updated = 0
    for item in items:
        key = {
            'pokemon': item['pokemon'],
            'set': item['set']
        }

        # Rewrite cardtype to ASCII version
        item['cardtype'] = 'pokemon'

        # Convert Decimal values for DynamoDB compatibility
        for k, v in item.items():
            if isinstance(v, float):
                item[k] = Decimal(str(v))

        table.put_item(Item=item)
        updated += 1
        if updated % 50 == 0:
            print(f"⏳ Updated {updated} items...")

    print(f"✅ Done! Updated {updated} items.")

if __name__ == '__main__':
    normalize_cardtype()
