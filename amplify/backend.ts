import { defineBackend } from '@aws-amplify/backend';
import { data } from './data/resource';
import { updatePokemonCards } from './functions/updatePokemonCards/resource';

export const backend = defineBackend({
  data,
  updatePokemonCards,
});
