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
          <button class="button is-loading is-large is-primary">
            Loading
          </button>
          <p class="mt-4">Loading films...</p>
        </div>
        <div v-else>
          <div v-if="sortMode === 'film'">
            <film-grid :films="films" :selectedCity="selectedCity" />
          </div>
          <div v-else>
            <date-grid :films="films" :selectedCity="selectedCity" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import AppHeader from './components/AppHeader.vue';
import FilmGrid from './components/FilmGrid.vue';
import DateGrid from './components/DateGrid.vue';

const letterboxdList = ref('');
const films = ref([]);
const cities = ref([]);
const selectedCity = ref('');
const sortMode = ref('film');
const apiUrl = import.meta.env.VITE_API_URL;
const isLoading = ref(false);

function initFromURL() {
  const params = new URLSearchParams(window.location.search);
  sortMode.value = params.get('sort') || 'film';
  selectedCity.value = params.get('city') || '';
}

async function fetchCities() {
  try {
    const response = await axios.get(`${apiUrl}/cities`);
    cities.value = response.data;
  } catch (error) {
    console.error('Error fetching cities:', error);
  }
}

async function loadData() {
  isLoading.value = true;
  try {
    const path = window.location.pathname;
    const response = await axios.get(`${apiUrl}/list/${path}`, {
      params: {
        city: selectedCity.value,
        sort: sortMode.value
      }
    });
    const data = response.data;
    films.value = data.films_with_showings;
    letterboxdList.value = data.path;
  } catch (error) {
    console.error('Error loading data:', error);
  } finally {
    isLoading.value = false;
  }
}

function updateCity(city) {
  selectedCity.value = city;
  const params = new URLSearchParams(window.location.search);
  params.set('city', city);
  params.set('sort', sortMode.value); // Preserve sort mode
  window.history.replaceState({}, '', `?${params.toString()}`);
}

function toggleSort() {
  sortMode.value = sortMode.value === 'film' ? 'date' : 'film';
  const params = new URLSearchParams(window.location.search);
  params.set('sort', sortMode.value);
  if (selectedCity.value) params.set('city', selectedCity.value); // Preserve city
  window.history.replaceState({}, '', `?${params.toString()}`);
}

onMounted(() => {
  initFromURL();
  fetchCities();
  loadData();
});
</script>

<style>
/* Removed styles moved to main.css */
</style>