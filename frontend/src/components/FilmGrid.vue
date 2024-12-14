<template>
  <div class="columns is-multiline">
    <div
      v-for="(film, index) in sortedFilms"
      :key="film.id"
      class="column is-3-desktop is-4-tablet is-6-mobile"
    >
      <film-card :film="film" :index="index" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import FilmCard from './FilmCard.vue';

const props = defineProps({
  films: {
    type: Array,
    required: true
  },
  selectedCity: {
    type: String,
    required: true
  }
});

const filteredFilms = computed(() => {
  return props.films.filter(film =>
    film.cities.some(city => city.city_slug === props.selectedCity)
  );
});

const sortedFilms = computed(() => {
  return [...filteredFilms.value].sort((a, b) => {
    const dateA = new Date(a.showings[0]?.start_date || '');
    const dateB = new Date(b.showings[0]?.start_date || '');
    return dateA - dateB;
  });
});
</script>