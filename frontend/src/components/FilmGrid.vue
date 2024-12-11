<template>
  <div class="columns is-multiline">
    <div v-for="(film, index) in sortedFilms" :key="film.id" class="column is-3-desktop is-4-tablet is-6-mobile">
      <film-card :film="film" :index="index" />
    </div>
  </div>
</template>

<script>
import FilmCard from './FilmCard.vue'

export default {
  components: { FilmCard },
  props: ['films'],
  computed: {
    sortedFilms() {
      return [...this.films].sort((a, b) => {
        const dateA = new Date(a.showings[0]?.start_date || '')
        const dateB = new Date(b.showings[0]?.start_date || '')
        return dateA - dateB
      })
    }
  }
}
</script>