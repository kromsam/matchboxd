<template>
    <div>
      <div class="buttons has-addons mb-4">
        <button 
          class="button" 
          :class="{ 'is-primary': activeView === 'films' }"
          @click="$emit('toggle-view', 'films')">
          Film View
        </button>
        <button 
          class="button"
          :class="{ 'is-primary': activeView === 'dates' }"
          @click="$emit('toggle-view', 'dates')">
          Date View
        </button>
      </div>
  
      <film-grid v-if="activeView === 'films'" :films="films" />
      <date-grid v-else :dates="dates" />
    </div>
  </template>
  
  <script>
  import FilmGrid from './FilmGrid.vue';
  import DateGrid from './DateGrid.vue';
  
  export default {
    components: {
      FilmGrid,
      DateGrid
    },
    props: {
      films: Array,
      dates: Array,
      activeView: String
    },
    emits: ['toggle-view']
  };
  </script>