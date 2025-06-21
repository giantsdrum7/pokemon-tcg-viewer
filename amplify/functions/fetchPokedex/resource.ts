import { function as defineFunction } from '@aws-amplify/backend/function';

export const updatePokemonCards = defineFunction({
  name: 'fetchPokedex',
  entry: './index.ts',
  runtime: 'nodejs18.x',
  permissions: {
    'dynamodb:*': ['*'],
  },
});
