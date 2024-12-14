<template>
  <div class="columns is-multiline">
    <div v-for="(showingsForDate, date) in groupedShowings" :key="date"
      class="column is-3-desktop is-4-tablet is-6-mobile">
      <date-card :date="formatDate(date)" :showings="showingsForDate" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import DateCard from './DateCard.vue';

const props = defineProps({
  films: Array,
  selectedCity: String
});

const filteredFilms = computed(() => {
  return props.films.filter(film =>
    film.cities.some(city => city.city_slug === props.selectedCity)
  );
});

const groupedShowings = computed(() => {
  const groups = {};

  filteredFilms.value.forEach(film => {
    film.showings.forEach(showing => {
      const startDateTime = new Date(showing.start_date);
      const endDateTime = new Date(showing.end_date);

      // Format date as YYYY-MM-DD for grouping
      const date = startDateTime.toISOString().split('T')[0];

      if (!groups[date]) {
        groups[date] = [];
      }

      groups[date].push({
        id: showing.id,
        film: {
          title: film.title,
          tmdb_id: film.tmdb_id
        },
        theater: showing.location_name,
        startTime: startDateTime.toLocaleTimeString('nl-NL', {
          hour: '2-digit',
          minute: '2-digit'
        }),
        endTime: endDateTime.toLocaleTimeString('nl-NL', {
          hour: '2-digit',
          minute: '2-digit'
        }),
        ticketUrl: showing.ticket_url,
        startDateTime // Add startDateTime for sorting
      });
    });
  });

  // Sort each group by start time
  Object.keys(groups).forEach(date => {
    groups[date].sort((a, b) => a.startDateTime - b.startDateTime);
  });

  // Sort groups by date
  const sortedGroups = Object.keys(groups).sort((a, b) => new Date(a) - new Date(b)).reduce((acc, date) => {
    acc[date] = groups[date];
    return acc;
  }, {});

  return sortedGroups;
});

function formatDate(date) {
  return new Date(date).toLocaleDateString('nl-NL', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}
</script>

<style scoped>
.card {
  margin-bottom: 1rem;
}

.table {
  margin-top: 1rem;
}
</style>