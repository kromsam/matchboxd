<template>
  <div class="film-grid columns is-multiline">
    <div v-for="film in films" :key="film.tmdb_id" class="column is-one-third">
      <film-card @click="showFilmScreenings(film)" :film="film" />
    </div>
  </div>
</template>
<script>
import router from '@/router';
import FilmCard from './FilmCard.vue';

export default {
  components: {
    FilmCard
  },
  props: ['films'],
  created() {
    console.log('Films in FilmGrid:', this.films);
  },
  methods: {
    showFilmScreenings(film) {
      console.log('Film clicked:', film);
      // Navigate to the detailed view for this film with its screenings
      router.push({ name: 'film-details', params: { tmdb_id: film.tmdb_id }, props: { film } });
    }
  }
};
</script>