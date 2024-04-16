import { createRouter, createWebHashHistory } from 'vue-router';
import DateDetailed from './components/DateDetailed.vue';
import DateGrid from './components/DateGrid.vue';
import FilmDetailed from './components/FilmDetailed.vue';
import FilmGrid from './components/FilmGrid.vue';
import { apiData } from './mockData';

// Import your components

const routes = [
    { path: '/', component: FilmGrid, props: { films: apiData.films_with_showings } },
    { path: '/films/:tmdb_id', name: 'film-details', component: FilmDetailed, props: true },
    { path: '/dates', component: DateGrid, props: { dates: extractDates(apiData.films_with_showings) } },
    { path: '/dates/:date', component: DateDetailed, props: getScreeningsByDate(apiData.films_with_showings) },
];

// Create the router instance
const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

// Export the router instance
export default router;


// Helper functions to extract dates and screenings
function extractDates(films) {
    const datesSet = new Set();
    films.forEach((film) => {
        film.showings.forEach((showing) => {
            datesSet.add(showing.start_date.split('T')[0]);
        });
    });
    return Array.from(datesSet);
}

function getScreeningsByDate(films) {
    return function (route) {
        const date = route.params.date;
        const screenings = films.reduce((acc, film) => {
            const filmScreenings = film.showings.filter((showing) => showing.start_date.split('T')[0] === date);
            if (filmScreenings.length > 0) {
                acc.push({
                    title: film.title,
                    screenings: filmScreenings,
                });
            }
            return acc;
        }, []);
        return {
            date,
            screenings,
        };
    };
}