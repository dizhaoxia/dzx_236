<template>
  <div class="auth-page">
    <div class="auth-left">
      <div class="brand-area">
        <div class="logo">📚</div>
        <h1 class="brand-title">Vocab Master</h1>
        <p class="brand-slogan">科学记忆，高效背单词</p>
      </div>
      <div class="feature-list">
        <div class="feature-item"><span class="feature-icon">🧠</span>
          <div><div class="feature-title">SM-2 间隔重复算法</div><div class="feature-desc">科学安排复习，让记忆更持久</div></div>
        </div>
        <div class="feature-item"><span class="feature-icon">📈</span>
          <div><div class="feature-title">学习数据可视化</div><div class="feature-desc">日历热力图，记录每一次进步</div></div>
        </div>
        <div class="feature-item"><span class="feature-icon">📚</span>
          <div><div class="feature-title">多词库支持</div><div class="feature-desc">四级、六级、考研，总有适合你</div></div>
        </div>
      </div>
    </div>
    <div class="auth-right">
      <div class="auth-card">
        <div class="tabs">
          <router-link to="/login" class="tab active">登录</router-link>
          <router-link to="/register" class="tab">注册</router-link>
        </div>
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label class="form-label">邮箱</label>
            <input v-model="email" type="email" class="form-input" placeholder="请输入邮箱" required />
          </div>
          <div class="form-group">
            <label class="form-label">密码</label>
            <input v-model="password" type="password" class="form-input" placeholder="请输入密码" required />
          </div>
          <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="loading">
            {{ loading ? '登录中...' : '登 录' }}
          </button>
        </form>
        <p class="auth-tip">
          还没有账号？<router-link to="/register">立即注册</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useToastStore } from '@/stores/toast'

const email = ref('')
const password = ref('')
const loading = ref(false)
const router = useRouter()
const userStore = useUserStore()
const toast = useToastStore()

const handleLogin = async () => {
  loading.value = true
  try {
    const res = await userStore.login(email.value, password.value)
    if (res.code === 200) {
      toast.success('登录成功')
      router.push({ name: 'Home' })
    } else {
      toast.error(res.message || '登录失败')
    }
  } catch (e) {
    toast.error(e?.message || '登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; }
.auth-left {
  flex: 1; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; padding: 60px 48px; display: flex; flex-direction: column; justify-content: space-between;
}
.brand-area { display: flex; flex-direction: column; gap: 12px; }
.logo { font-size: 64px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2)); }
.brand-title { font-size: 42px; font-weight: 800; letter-spacing: -0.5px; }
.brand-slogan { font-size: 18px; opacity: 0.9; }
.feature-list { display: flex; flex-direction: column; gap: 28px; }
.feature-item { display: flex; align-items: flex-start; gap: 16px; }
.feature-icon { font-size: 32px; flex-shrink: 0; }
.feature-title { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.feature-desc { font-size: 13px; opacity: 0.85; }
.auth-right { width: 520px; background: white; display: flex; align-items: center; justify-content: center; padding: 40px; }
.auth-card { width: 100%; max-width: 400px; }
.tabs { display: flex; gap: 32px; margin-bottom: 32px; border-bottom: 2px solid var(--border); }
.tab {
  padding: 12px 0; font-size: 18px; font-weight: 600; color: var(--text-secondary);
  position: relative; margin-bottom: -2px; transition: color 0.2s;
}
.tab:hover { color: var(--text); }
.tab.active { color: var(--primary); }
.tab.active::after { content: ''; position: absolute; left: 0; right: 0; bottom: -2px; height: 2px; background: var(--primary); border-radius: 2px; }
.auth-tip { margin-top: 20px; text-align: center; font-size: 14px; color: var(--text-secondary); }
.auth-tip a { font-weight: 500; }
@media (max-width: 960px) {
  .auth-page { flex-direction: column; }
  .auth-left { padding: 40px 24px; }
  .auth-right { width: 100%; padding: 24px; }
  .brand-title { font-size: 32px; }
}
@media (max-width: 480px) {
  .feature-list { display: none; }
  .auth-left { padding: 32px 20px; }
}
</style>
