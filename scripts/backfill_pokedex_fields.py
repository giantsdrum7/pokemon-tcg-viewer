import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('Pokedex')

def backfill_table():
    scan_kwargs = {}
    done = False
    start_key = None

    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key

        response = table.scan(**scan_kwargs)
        for item in response.get('Items', []):
            update_fields = []
            expression_values = {}

            # Promote prices.market → market_price
            prices = item.get("prices", {})
            market_price = prices.get("market")
            if market_price is not None:
                update_fields.append("market_price = :mp")
                expression_values[":mp"] = market_price

            # Set supertype
            if "supertype" in item:
                update_fields.append("supertype = :st")
                expression_values[":st"] = item["supertype"]

            # Set primary_subtype
            subtypes = item.get("subtypes")
            if subtypes and isinstance(subtypes, list) and len(subtypes) > 0:
                update_fields.append("primary_subtype = :ps")
                expression_values[":ps"] = subtypes[0]

            # Only update if something changed
            if update_fields:
                update_expr = "SET " + ", ".join(update_fields)
                table.update_item(
                    Key={"pokemon": item["pokemon"], "set": item["set"]},
                    UpdateExpression=update_expr,
                    ExpressionAttributeValues=expression_values
                )

        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None

if __name__ == "__main__":
    backfill_table()
