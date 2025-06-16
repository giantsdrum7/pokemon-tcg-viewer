import { defineBackend, api } from '@aws-amplify/backend';
import { data } from '@aws-amplify/backend-data';
import { lambda } from '@aws-amplify/backend-function';
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

  // 🔹 Lambda function to serve API queries (NEW)
  getCards: lambda({
    runtime: 'nodejs18.x',
    entry: './functions/getCards/index.ts',
  }),

  // 🔹 REST API routes (updated to include /cards)
  api: api.rest({
    routes: {
      'GET /update-cards': {
        function: backend.updatePokemonCards,
      },
      'GET /cards': {
        function: backend.getCards,
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
