import { createRouter, createWebHistory } from 'vue-router'
import KioskView from '../views/KioskView.vue'
import AdminPanel from '../components/AdminPanel.vue'

const routes = [
  {
    path: '/',
    name: 'Kiosk',
    component: KioskView
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminPanel
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
