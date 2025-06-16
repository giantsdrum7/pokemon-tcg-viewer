import { defineFunction } from '@aws-amplify/backend';

export const updatePokemonCards = defineFunction({
  entry: './amplify/functions/updatePokemonCards/index.ts',
  runtime: 'nodejs18.x',
  environment: {
    TABLE_NAME: 'Pokedex',
  },
});
