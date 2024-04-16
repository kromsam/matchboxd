<template>
    <div class="columns">
        <div class="column is-one-third">
            <film-card :film="filmData" />
        </div>
        <div class="column">
            <div class="box ">
                <film-table :showings="filmData.showings" :film="filmData" />
            </div>
        </div>
    </div>
</template>
  
<script>
// Import the apiData from your mockData file
import { apiData } from '../mockData'; // Update the path accordingly
import FilmCard from './FilmCard.vue'; // Update the path accordingly
import FilmTable from './FilmTable.vue';

// Mocked function to fetch film data by ID
function fetchFilmData(filmId) {
    // Use the films_with_showings data from apiData
    const films = apiData.films_with_showings;

    // Find the film with the given ID
    const film = films.find((f) => f.tmdb_id === parseInt(filmId, 10));

    return film || null; // Return the found film or null if not found
}

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
    created() {
        // If film prop is not provided, fetch film data using the route parameter
        if (!this.film) {
            const filmId = this.$route.params.tmdb_id;
            this.filmData = fetchFilmData(filmId);
        } else {
            // If film prop is provided, use it directly
            this.filmData = this.film;
        }
    },
    // Rest of your component logic
};
</script>
  
<style scoped>
/* Your component styles */
</style>