<template>
  <div class="card">
    <div class="card-content">
      <p class="title is-4">{{ date }}</p>
      <div class="content">
        <table class="table is-fullwidth">
          <thead>
            <tr>
              <th>Film</th>
              <th>Theater</th>
              <th>Time</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="showing in showings" :key="showing.id">
              <td>
                <a :href="`/films/${showing.film.tmdb_id}`">
                  {{ showing.film.title }}
                </a>
              </td>
              <td>{{ showing.theater }}</td>
              <td>{{ showing.startTime }} - {{ showing.endTime }}</td>
              <td>
                <a v-if="showing.ticketUrl" 
                   :href="showing.ticketUrl" 
                   class="button is-small is-primary"
                   target="_blank">
                  Tickets
                </a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['date', 'showings']
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