<template>
  <div class="block has-text-centered">
    <h1 class="title is-2">
      Films in
      <div class="select is-medium is-primary is-inline-block">
        <select
          v-model="currentCity"
          @change="$emit('updateCity', $event.target.value)"
        >
          <option
            v-for="city in cities"
            :key="city.city_slug"
            :value="city.city_slug"
          >
            {{ city.city_name }}
          </option>
        </select>
      </div>
      van
      <a :href="letterboxdUrl" class="has-text-primary" target="_blank">
        {{ letterboxdList }}
      </a>
      <button
        class="button is-ghost is-medium"
        @click.prevent="$emit('toggleSort')"
      >
        {{ sortMode === 'film' ? 'per film' : 'op datum' }}
      </button>
    </h1>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  letterboxdList: String,
  selectedCity: String,
  cities: Array,
  sortMode: String
});

const emit = defineEmits(['updateCity', 'toggleSort']);

const letterboxdUrl = computed(() => `https://letterboxd.com/${props.letterboxdList}`);

const currentCity = computed({
  get: () => props.selectedCity,
  set: value => emit('updateCity', value)
});
</script>