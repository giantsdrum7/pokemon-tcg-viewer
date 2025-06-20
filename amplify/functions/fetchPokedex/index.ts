import {
  DynamoDBClient,
  ScanCommand,
} from '@aws-sdk/client-dynamodb';
import { unmarshall } from '@aws-sdk/util-dynamodb';
import { APIGatewayProxyHandler } from 'aws-lambda';

const client = new DynamoDBClient({ region: 'us-east-2' });

export const handler: APIGatewayProxyHandler = async (event) => {
  try {
    const command = new ScanCommand({
      TableName: 'Pokedex',
      FilterExpression: '#type = :typeVal',
      ExpressionAttributeNames: {
        '#type': 'cardtype',
      },
      ExpressionAttributeValues: {
        ':typeVal': { S: 'pokemon' },
      },
    });

    const result = await client.send(command);
    const items = result.Items?.map((item) => unmarshall(item)) || [];

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
      },
      body: JSON.stringify(items),
    };
  } catch (error) {
    console.error('Error scanning Pokedex table:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to fetch pokedex data.' }),
    };
  }
};
