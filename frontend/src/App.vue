<script>
import axios from 'axios';

export default {
  data() {
    return {
      activeGrid: 'films', // Default to Film Grid
      selectedFilm: null,
      selectedDate: null,
      selectedScreenings: null,
      films: [],
      dates: [],
    };
  },
  watch: {
    '$route': {
      immediate: true,
      handler: 'fetchData'
    }
  },
  methods: {
    async fetchData() {
      const apiUrl = import.meta.env.VITE_API_URL;
      console.log('API URL:', apiUrl);
      const path = this.$route.path || '';
      const city = this.$route.query.city || '';
      console.log(`Path: ${path}, City: ${city}`);
      if (!path) {
        console.error('Path is undefined');
        return;
      }
      try {
        console.log(`Fetching data from: ${apiUrl}${path}?city=${city}`);
        const response = await axios.get(`${apiUrl}${path}`, { params: { city } });
        console.log('API response:', response.data);
        this.films = response.data.films_with_showings;
        this.dates = this.extractDates(this.films);
        console.log('Films:', this.films);
        console.log('Dates:', this.dates);
      } catch (error) {
        console.error('Failed to fetch data from API:', error);
      }
    },
    toggleGrid(grid) {
      this.activeGrid = grid;
    },
    extractDates(films) {
      const datesSet = new Set();
      films.forEach((film) => {
        film.showings.forEach((showing) => {
          datesSet.add(showing.start_date.split('T')[0]);
        });
      });
      return Array.from(datesSet);
    },
  },
};
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