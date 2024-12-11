<template>
    <div v-for="date in sortedDates" :key="date">
        <div class="box">
            <h2 class="title">{{ date }}</h2>
            <table class="table is-fullwidth">
                <tbody>
                    <tr v-for="showing in groupedShowings[date]" :key="showing.id">
                        <td>
                            <a :href="showing.information_url" target="_blank" v-if="showing.information_url">{{
                                showing.location_name }}</a>
                        </td>
                        <td>{{ showing.start_date }}</td>
                        <td>{{ showing.end_date }}</td>

                        <td>{{ showing.location_city }}</td>
                        <td>
                            <a :href="showing.ticket_url" target="_blank" v-if="showing.ticket_url">Tickets</a>
                        </td>

                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        showings: Array,
        film: Object,
    },
    computed: {
        sortedDates() {
            const uniqueDates = [...new Set(this.showings.map(showing => new Date(showing.start_date).toLocaleDateString()))];
            return uniqueDates.sort((a, b) => new Date(a) - new Date(b));
        },
        groupedShowings() {
            const grouped = {};
            this.showings.forEach(showing => {
                const date = new Date(showing.start_date).toLocaleDateString();
                if (!grouped[date]) {
                    grouped[date] = [];
                }
                grouped[date].push(showing);
            });
            return grouped;
        },
    },
};
</script>

<style>
/* Add Bulma styling or your custom styles here */
.block:not(:last-child) {
    margin-bottom: 1.5rem;
}
</style>