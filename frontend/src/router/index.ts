import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../stores/auth'

const routes = [
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/', component: () => import('../views/Dashboard.vue'), meta: { auth: true } },
  { path: '/cases', component: () => import('../views/Cases.vue'), meta: { auth: true } },
  { path: '/cases/:id', component: () => import('../views/CaseDetail.vue'), meta: { auth: true } },
  { path: '/guides', component: () => import('../views/Guides.vue'), meta: { auth: true } },
  { path: '/public-demo', component: () => import('../views/PublicDemo.vue') },
]

const router = createRouter({ history: createWebHistory(), routes })
router.beforeEach((to) => {
  const auth = useAuth()
  if (to.meta.auth && !auth.isAuthed) return '/login'
})
export default router
