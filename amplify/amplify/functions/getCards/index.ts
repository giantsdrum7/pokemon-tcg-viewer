import { DynamoDBClient, ScanCommand } from "@aws-sdk/client-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";

// Initialize DynamoDB client
const client = new DynamoDBClient({ region: "us-east-2" });

export const handler = async (event: any) => {
  const query = event.queryStringParameters || {};

  // Define filter type and build filter array
  const filters: { key: string; op: string; value: any }[] = [];

  for (const key in query) {
    const val = query[key];
    if (val.startsWith("<")) {
      filters.push({ key, op: "<", value: parseFloat(val.slice(1)) });
    } else if (val.startsWith(">")) {
      filters.push({ key, op: ">", value: parseFloat(val.slice(1)) });
    } else {
      filters.push({ key, op: "=", value: val });
    }
  }

  // Scan entire Pokedex table
  const scan = await client.send(new ScanCommand({ TableName: "Pokedex" }));
  const items = scan.Items?.map(item => unmarshall(item) as Record<string, any>) || [];

  // Apply filters in Lambda
  const filtered = items.filter((item: Record<string, any>) =>
    filters.every(({ key, op, value }) => {
      const fieldVal = item[key];
      if (fieldVal === undefined) return false;
      if (op === "=") return fieldVal == value;
      if (op === "<") return fieldVal < value;
      if (op === ">") return fieldVal > value;
      return false;
    })
  );

  // Return matching results
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(filtered),
  };
};
