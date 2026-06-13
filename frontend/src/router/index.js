import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { auth: true }
  },
  {
    path: '/study',
    name: 'Study',
    component: () => import('@/views/Study.vue'),
    meta: { auth: true }
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('@/views/Stats.vue'),
    meta: { auth: true }
  },
  {
    path: '/vocab',
    name: 'Vocab',
    component: () => import('@/views/Vocab.vue'),
    meta: { auth: true }
  },
  {
    path: '/vocab/:id',
    name: 'VocabDetail',
    component: () => import('@/views/VocabDetail.vue'),
    meta: { auth: true }
  },
  {
    path: '/custom',
    name: 'Custom',
    component: () => import('@/views/Custom.vue'),
    meta: { auth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { auth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('vocab_token')
  if (to.meta.auth && !token) {
    next({ name: 'Login' })
  } else if (to.meta.guest && token) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
