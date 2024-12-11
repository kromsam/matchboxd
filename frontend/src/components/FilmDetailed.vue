<template>
  <div class="columns">
    <div class="column is-one-third">
      <film-card :film="filmData" />
    </div>
    <div class="column">
      <div class="box">
        <film-table :showings="filmData.showings" :film="filmData" />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import FilmCard from './FilmCard.vue';
import FilmTable from './FilmTable.vue';

const apiUrl = import.meta.env.VITE_API_URL

export default {
  props: ['film'],
  components: {
    FilmCard,
    FilmTable,
  },
  data() {
    return {
      filmData: null,
    };
  },
  async created() {
    const filmId = this.$route.params.tmdb_id;
    try {
      const response = await axios.get(`${apiUrl}/films/${filmId}`);
      this.filmData = response.data;
    } catch (error) {
      console.error('Failed to fetch film data from API:', error);
    }
  },
};
</script>