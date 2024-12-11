<template>
  <div class="section">
    <div class="container">
      <app-header 
        :letterboxdList="letterboxdList"
        :selectedCity="selectedCity"
        :cities="cities"
        :sortMode="sortMode"
        @updateCity="updateCity"
        @toggleSort="toggleSort"
      />
      
      <div class="content">
        <div v-if="isLoading" class="has-text-centered">
          <div class="button is-loading is-large is-primary">Loading</div>
          <p class="mt-4">Loading films...</p>
        </div>
        <div v-else>
          <div v-if="sortMode === 'film'">
            <film-grid :films="films" />
          </div>
          <div v-else>
            <date-grid :films="films" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import AppHeader from './components/AppHeader.vue'
import FilmGrid from './components/FilmGrid.vue'
import DateGrid from './components/DateGrid.vue'

export default {
  components: {
    AppHeader,
    FilmGrid,
    DateGrid
  },
  data() {
    return {
      letterboxdList: '',
      films: [],
      cities: [],
      selectedCity: '',
      sortMode: 'film',
      apiUrl: import.meta.env.VITE_API_URL,
      isLoading: false
    }
  },
  created() {
    this.initFromURL()
    this.loadData()
  },
  methods: {
    initFromURL() {
      const params = new URLSearchParams(window.location.search)
      this.sortMode = params.get('sort') || 'film'
      this.selectedCity = params.get('city') || ''
    },
    async loadData() {
      this.isLoading = true
      try {
        const path = window.location.pathname
        const response = await axios.get(`${this.apiUrl}${path}`, {
          params: { 
            city: this.selectedCity,
            sort: this.sortMode
          }
        })
        const data = response.data
        this.films = data.films_with_showings
        this.letterboxdList = data.path
        this.cities = [...new Set(data.films_with_showings.flatMap(f => 
          f.cities.map(c => c.city_name)
        ))]
      } catch (error) {
        console.error('Error loading data:', error)
      } finally {
        this.isLoading = false
      }
    },
    updateCity(city) {
      this.selectedCity = city
      const params = new URLSearchParams(window.location.search)
      params.set('city', city)
      params.set('sort', this.sortMode) // Preserve sort mode
      window.history.replaceState({}, '', `?${params.toString()}`)
      this.loadData()
    },
    toggleSort() {
      this.sortMode = this.sortMode === 'film' ? 'date' : 'film'
      const params = new URLSearchParams(window.location.search)
      params.set('sort', this.sortMode)
      if (this.selectedCity) params.set('city', this.selectedCity) // Preserve city
      window.history.replaceState({}, '', `?${params.toString()}`)
    }
  }
}
</script>

<style>
@import 'bulma/css/bulma.min.css';

:root {
  --primary-color: #3273dc;
  --card-height: 100%;
}

.section {
  padding: 3rem 1.5rem;
}

.card {
  height: var(--card-height);
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.image.is-2by3 {
  padding-top: 150%;
  position: relative;
  overflow: hidden;
}

.image.is-2by3 img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>