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
    created() {
      console.log('Dates in DateGrid:', this.dates);
    },
    methods: {
        showDateScreenings(date) {
            console.log('Date clicked:', date);
            // Navigate to the detailed view for this date with its screenings
            this.$router.push(`/dates/${date}`);
        },
        formatDate(date) {
            // Format the date as per your requirements
            return date;
        }
    }
};
</script>