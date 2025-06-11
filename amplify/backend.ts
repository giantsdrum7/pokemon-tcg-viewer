import { defineBackend } from '@aws-amplify/backend';
import { data } from '@aws-amplify/backend-data';
import { lambda } from '@aws-amplify/backend-function';
import { api } from '@aws-amplify/backend-api';
import { storage } from '@aws-amplify/backend-storage';

const backend = defineBackend({
  // 🔹 DynamoDB table for your card data
  data: {
    pokemonCards: data.table({
      partitionKey: { name: 'id', type: 'string' }, // match your CSV structure
    }),
  },

  // 🔹 Lambda function to sync S3 → DynamoDB
  updatePokemonCards: lambda({
    runtime: 'nodejs18.x',
    entry: './functions/updatePokemonCards/index.ts',
    environment: {
      TABLE_NAME: backend.data.pokemonCards.name,
    },
    timeoutSeconds: 30,
  }),

  // 🔹 REST API endpoint to trigger the Lambda
  api: api.rest({
    routes: {
      'GET /update-cards': {
        function: backend.updatePokemonCards,
      },
    },
  }),

  // 🔹 S3 bucket for CSV backup
  storage: {
    pokeAssets: storage.bucket({
      name: 'poke-num',
    }),
  },
});

export default backend;
