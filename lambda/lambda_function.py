import boto3
import json
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('PokemonSummary')

# JSON encoder to convert Decimal to float
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    try:
        # Read the ?generation=1 query parameter
        params = event.get('queryStringParameters') or {}
        gen_filter = params.get('generation')

        if gen_filter:
            try:
                gen_value = int(gen_filter)
                response = table.scan(
                    FilterExpression=Attr("generation").eq(gen_value)
                )
            except ValueError:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid generation value"})
                }
        else:
            # fallback: return all generations if no filter is passed
            response = table.scan()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response["Items"], cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
