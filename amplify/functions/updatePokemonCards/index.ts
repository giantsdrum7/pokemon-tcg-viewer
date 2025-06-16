import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";
import { marshall } from "@aws-sdk/util-dynamodb";

const ddb = new DynamoDBClient({});

export const handler = async (event: any) => {
  try {
    const tableName = process.env.TABLE_NAME;
    if (!tableName) throw new Error("Missing TABLE_NAME environment variable");

    const body = typeof event.body === "string" ? JSON.parse(event.body) : event.body;

    const item = marshall({
      id: body.id,
      pokemon: body.pokemon,
      set: body.set,
      rarity: body.rarity,
      market_price: body.market_price,
      types: body.types,
      subtypes: body.subtypes,
    });

    await ddb.send(
      new PutItemCommand({
        TableName: tableName,
        Item: item,
      })
    );

    return {
      statusCode: 200,
      body: JSON.stringify({ message: "Card inserted/updated", id: body.id }),
    };
  } catch (error: any) {
    console.error("Error in Lambda:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
