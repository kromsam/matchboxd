<template>
  <div class="detailed-date-view">
    <div class="date-details">
      <h2>{{ formatDate(date) }}</h2>
      <!-- Add more date details as needed -->
    </div>

    <div class="screenings-table">
      <h3>Screenings</h3>
      <table>
        <!-- Add table headers -->
        <thead>
          <tr>
            <th>Film Title</th>
            <th>Start Date</th>
            <th>End Date</th>
            <th>Location</th>
            <!-- Add more columns as needed -->
          </tr>
        </thead>
        <tbody>
          <!-- Iterate through screenings and display rows -->
          <tr v-for="screening in screenings" :key="screening.id">
            <td>{{ screening.title }}</td>
            <td>{{ screening.start_date }}</td>
            <td>{{ screening.end_date }}</td>
            <td>{{ screening.location_name }}</td>
            <!-- Add more columns as needed -->
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  props: ['date', 'screenings'],
  methods: {
    formatDate(date) {
      // Format the date as per your requirements
      // You can use a library like moment.js for this
      return date;
    },
  },
};
</script>

<style scoped>
/* Add your styling for detailed date view here */
</style>
