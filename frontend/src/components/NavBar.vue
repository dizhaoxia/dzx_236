<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="nav-logo">
        <span class="logo-icon">📚</span>
        <span class="logo-text">Vocab Master</span>
      </router-link>
      <div class="nav-menu">
        <router-link to="/" class="nav-link" active-class="active" :exact="true">
          <span>🏠</span> 首页
        </router-link>
        <router-link to="/study" class="nav-link" active-class="active">
          <span>📖</span> 学习
        </router-link>
        <router-link to="/stats" class="nav-link" active-class="active">
          <span>📊</span> 统计
        </router-link>
        <router-link to="/vocab" class="nav-link" active-class="active">
          <span>📚</span> 词库
        </router-link>
        <router-link to="/custom" class="nav-link" active-class="active">
          <span>⭐</span> 生词本
        </router-link>
      </div>
      <div class="nav-user">
        <router-link to="/profile" class="user-info">
          <span class="avatar">{{ avatarText }}</span>
          <span class="nickname">{{ userStore.nickname }}</span>
        </router-link>
        <button class="logout-btn" @click="handleLogout" title="退出登录">
          🚪
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useToastStore } from '@/stores/toast'

const userStore = useUserStore()
const router = useRouter()
const toast = useToastStore()

const avatarText = computed(() => {
  const name = userStore.nickname || 'U'
  return name.charAt(0).toUpperCase()
})

const handleLogout = () => {
  userStore.logout()
  toast.success('已退出登录')
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: white;
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow);
  z-index: 100;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  display: flex;
  gap: 4px;
  flex: 1;
  justify-content: center;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.2s;
  font-size: 14px;
}

.nav-link:hover {
  background: #f3f4f6;
  color: var(--text);
}

.nav-link.active {
  background: #eef2ff;
  color: var(--primary);
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text);
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.nickname {
  font-size: 14px;
  font-weight: 500;
}

.logout-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: transparent;
  font-size: 18px;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn:hover {
  background: #fee2e2;
}

@media (max-width: 768px) {
  .nav-menu { display: none; }
  .nickname { display: none; }
}
</style>
