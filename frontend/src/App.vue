<template>
  <div class="app-wrapper">
    <NavBar v-if="userStore.isLoggedIn" />
    <main class="main-content" :class="{ 'with-nav': userStore.isLoggedIn }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <Toast />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import Toast from '@/components/Toast.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
  if (userStore.isLoggedIn) {
    userStore.fetchProfile().catch(() => {})
  }
})
</script>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
}

.with-nav {
  padding-top: 64px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
