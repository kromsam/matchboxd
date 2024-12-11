import { createRouter, createWebHistory } from 'vue-router';
import AppContent from './components/AppContent.vue';

const routes = [
  {
    path: '/:listPath',
    name: 'watchlist',
    component: AppContent,
    props: (route) => ({
      listPath: route.params.listPath,
      sortMode: route.query.sort || 'film',
      city: route.query.city || ''
    })
  },
];

export default createRouter({
  history: createWebHistory(),
  routes
});