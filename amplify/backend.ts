import { defineBackend } from '@aws-amplify/backend';

export const backend = defineBackend({
  data: {
    Pokedex: {
      partitionKey: { name: 'id', type: 'string' },
    },
  },
  updatePokemonCards: {
    entry: './functions/updatePokemonCards/index.ts',
    runtime: 'nodejs18.x',
    environment: {
      TABLE_NAME: 'Pokedex', // Make sure this matches exactly with the table name
    },
  },
  api: {
    rest: {
      routes: {
        'GET /update-cards': {
          function: 'updatePokemonCards',
        },
      },
    },
  },
  storage: {
    pokeAssets: {}, // This defines an S3 bucket, if needed for CSV or images
  },
});
