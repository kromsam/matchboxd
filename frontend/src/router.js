import { createRouter, createWebHistory } from 'vue-router';
import DateDetailed from './components/DateDetailed.vue';
import DateGrid from './components/DateGrid.vue';
import FilmDetailed from './components/FilmDetailed.vue';
import FilmGrid from './components/FilmGrid.vue';

const routes = [
  // Specific routes
  { path: '/films/:tmdb_id', name: 'film-details', component: FilmDetailed, props: true },
  { path: '/dates', component: DateGrid, props: true },
  { path: '/dates/:date', component: DateDetailed, props: true },
  
  // Generic catch-all route
  { path: '/:catchAll(.*)', component: FilmGrid, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

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