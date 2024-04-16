<template>
    <div class="date-grid">
        <div v-for="date in dates" :key="date">
            <div class="date-card" @click="showDateScreenings(date)">
                <h3>{{ formatDate(date) }}</h3>
            </div>
        </div>
    </div>
</template>
  
<script>
export default {
    props: ['dates'],
    methods: {
        showDateScreenings(date) {
            // Navigate to the detailed view for this date with its screenings
            // You can use Vue Router or other navigation methods here
            this.$router.push(`/dates/${date}`);
        },
        formatDate(date) {
            // Format the date as per your requirements
            // You can use a library like moment.js for this
            return date;
        }
    }
};
</script>
  
<style scoped>
/* Add your styling for date cards here */
</style>