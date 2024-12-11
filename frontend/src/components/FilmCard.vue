<template>
  <div class="card">
    <div class="card-image">
      <figure class="image is-2by3">
        <a :href="film.clean_title" target="_blank">
          <img :src="film.img_url" :alt="film.title">
        </a>
      </figure>
    </div>
    
    <div class="card-content">
      <p class="title is-5">{{ film.title }}</p>
      <p class="subtitle is-6">{{ film.oneliner }}</p>
      
      <div class="buttons are-small">
        <a v-for="link in links" 
           :key="link.url" 
           :href="link.url"
           class="button is-primary is-light"
           target="_blank">
          {{ link.text }}
        </a>
      </div>
    </div>

    <footer class="card-footer">
      <div class="card-footer-item">
        <button class="button is-ghost" 
                @click="toggleShowings"
                :aria-expanded="showShowings">
          {{ film.showings.length }} 
          {{ film.showings.length === 1 ? 'Voorstelling' : 'Voorstellingen' }}
        </button>
      </div>
    </footer>
    
    <div v-show="showShowings" class="card-content pt-0">
      <div class="menu">
        <ul class="menu-list">
          <li v-for="showing in groupedShowings" 
              :key="showing.date">
            <p class="menu-label">{{ showing.date }}</p>
            <ul>
              <li v-for="time in showing.times" :key="time.id">
                <a :href="time.url" target="_blank">
                  {{ time.theater }} - {{ time.time }}
                </a>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['film', 'index'],
  computed: {
    links() {
      return [
        { url: this.film.clean_title, text: 'Cineville' },
        { url: `https://letterboxd.com/film/${this.film.slug}`, text: 'Letterboxd' },
        { url: `https://www.imdb.com/title/${this.film.imdb_id}`, text: 'IMDb' },
        { url: `https://www.themoviedb.org/movie/${this.film.tmdb_id}`, text: 'TMDB' }
      ]
    },
    groupedShowings() {
      const groups = {};
      
      this.film.showings.forEach(showing => {
        const showingDate = new Date(showing.start_date);
        const date = showingDate.toLocaleDateString('nl-NL', {
          weekday: 'long',
          month: 'long',
          day: 'numeric'
        });
        
        if (!groups[date]) {
          groups[date] = {
            date,
            times: []
          };
        }
        
        groups[date].times.push({
          id: showing.id,
          url: showing.ticket_url,
          theater: showing.location_name,
          time: new Date(showing.start_date).toLocaleTimeString('nl-NL', {
            hour: '2-digit',
            minute: '2-digit'
          })
        });
      });

      return Object.values(groups).sort((a, b) => {
        const dateA = new Date(this.film.showings.find(s => 
          new Date(s.start_date).toLocaleDateString('nl-NL', {
            weekday: 'long',
            month: 'long',
            day: 'numeric'
          }) === a.date
        ).start_date);
        const dateB = new Date(this.film.showings.find(s => 
          new Date(s.start_date).toLocaleDateString('nl-NL', {
            weekday: 'long',
            month: 'long',
            day: 'numeric'
          }) === b.date
        ).start_date);
        return dateA - dateB;
      });
    }
  },
  data() {
    return {
      showShowings: false
    }
  },
  methods: {
    toggleShowings() {
      this.showShowings = !this.showShowings
    }
  }
}
</script>

<style scoped>
.menu-label {
  font-weight: bold;
  margin-bottom: 0.5em;
  text-transform: capitalize;
}
</style>