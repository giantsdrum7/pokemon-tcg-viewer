import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { Readable } from "stream";
import { parse } from "csv-parse";

export const handler = async (): Promise<any> => {
  const s3 = new S3Client({});
  const ddb = new DynamoDBClient({});
  const bucket = "poke-num";
  const key = "cards.csv";
  const tableName = process.env.TABLE_NAME!;

  const response = await s3.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
  const stream = response.Body as Readable;

  const parser = stream.pipe(parse({ columns: true, skip_empty_lines: true }));

  for await (const record of parser) {
    await ddb.send(new PutItemCommand({
      TableName: tableName,
      Item: Object.entries(record).reduce((acc, [key, val]) => {
        acc[key] = { S: val };
        return acc;
      }, {} as Record<string, { S: string }>),
    }));
  }

  return {
    statusCode: 200,
    body: JSON.stringify("Success"),
  };
};
