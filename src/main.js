import './assets/main.css'
import './style.css'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import LandingView from './views/LandingView.vue'
import LoginView from './views/LoginView.vue'
import HomeView from './views/HomeView.vue'

const routes = [
  { path: '/', component: LandingView },
  { path: '/login', component: LoginView },
  { path: '/home', component: HomeView },
  { path: '/callback', redirect: '/home' } // Add callback route that redirects to home
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

createApp(App).use(router).mount('#app')
