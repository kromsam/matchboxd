<template>
  <div id="app">
    <div class="toggle-container">
      <button @click="toggleGrid('films')" :class="{ active: activeGrid === 'films' }">Film Grid</button>
      <button @click="toggleGrid('dates')" :class="{ active: activeGrid === 'dates' }">Date Grid</button>
    </div>

    <router-view :films="films" :dates="dates" :film="selectedFilm" :date="selectedDate"
      :screenings="selectedScreenings" />

  </div>
</template>

<script>
import { apiData } from './mockData'; // Import mock data

export default {
  data() {
    return {
      activeGrid: 'films', // Default to Film Grid
      selectedFilm: null,
      selectedDate: null,
      selectedScreenings: null,
    };
  },
  computed: {
    films() {
      return apiData.films_with_showings; // Use mock data
    },
    dates() {
      return extractDates(apiData.films_with_showings); // Use mock data
    },
  },
  methods: {
    toggleGrid(grid) {
      this.activeGrid = grid;
    },
  },
};

// Helper functions to extract dates and screenings
function extractDates(films) {
  const datesSet = new Set();
  films.forEach((film) => {
    film.showings.forEach((showing) => {
      datesSet.add(showing.start_date.split('T')[0]);
    });
  });
  return Array.from(datesSet);
}
</script>

<style>
/* Import Bulma styles */
@import "https://cdn.jsdelivr.net/npm/bulma@1.0.0/css/bulma.min.css";

/* Add your custom styles here */

.toggle-container {
  margin: 20px;
}

button {
  margin-right: 10px;
  cursor: pointer;
}

.active {
  font-weight: bold;
}
</style>