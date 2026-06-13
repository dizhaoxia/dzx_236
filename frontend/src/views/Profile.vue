<template>
  <div class="container">
    <div class="page-header">
      <div>
        <h1 class="page-title">👤 个人中心</h1>
        <p class="page-subtitle">管理账户信息与学习设置</p>
      </div>
    </div>

    <div class="grid grid-2 profile-grid">
      <div class="card profile-card">
        <div class="avatar-section">
          <div class="avatar-large">{{ avatarText }}</div>
          <div class="user-basic">
            <div class="user-nickname">{{ userStore.nickname }}</div>
            <div class="user-email">{{ userStore.user?.email }}</div>
            <div class="user-created">📅 加入于 {{ userStore.user?.created_at }}</div>
          </div>
        </div>

        <div class="stats-summary">
          <div class="summary-row">
            <div class="summary-item">
              <div class="s-num">{{ userStore.stats?.total_words || 0 }}</div>
              <div class="s-lbl">已学单词</div>
            </div>
            <div class="summary-item">
              <div class="s-num">{{ userStore.stats?.mastered_words || 0 }}</div>
              <div class="s-lbl">已掌握</div>
            </div>
            <div class="summary-item">
              <div class="s-num">{{ userStore.stats?.study_days || 0 }}</div>
              <div class="s-lbl">学习天数</div>
            </div>
            <div class="summary-item">
              <div class="s-num">{{ userStore.stats?.streak || 0 }}</div>
              <div class="s-lbl">连续打卡</div>
            </div>
          </div>
        </div>

        <div class="today-panel">
          <div class="panel-title">📊 今日学习</div>
          <div class="today-row">
            <div class="today-item">
              <span class="today-label">📖 新学</span>
              <span class="today-val">{{ userStore.stats?.today_new || 0 }}</span>
            </div>
            <div class="today-item">
              <span class="today-label">🔄 复习</span>
              <span class="today-val">{{ userStore.stats?.today_review || 0 }}</span>
            </div>
            <div class="today-item">
              <span class="today-label">📝 总计</span>
              <span class="today-val">{{ userStore.stats?.today_total || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card settings-card">
        <h3 class="settings-title">⚙️ 账户设置</h3>

        <div class="settings-section">
          <div class="section-label">个人资料</div>
          <div class="form-group">
            <label class="form-label">昵称</label>
            <input v-model="form.nickname" type="text" class="form-input" placeholder="请输入昵称" />
          </div>
          <button class="btn btn-primary" @click="saveProfile" :disabled="saving">
            {{ saving ? '保存中...' : '保存昵称' }}
          </button>
        </div>

        <div class="settings-section">
          <div class="section-label">每日学习目标</div>
          <div class="goal-options">
            <div
              v-for="g in goalOptions"
              :key="g.value"
              class="goal-option"
              :class="{ active: form.daily_goal === g.value }"
              @click="form.daily_goal = g.value"
            >
              <div class="goal-value">{{ g.value }}</div>
              <div class="goal-desc">{{ g.desc }}</div>
              <div class="goal-check" v-if="form.daily_goal === g.value">✓</div>
            </div>
          </div>
          <button class="btn btn-primary" style="margin-top: 12px" @click="saveGoal" :disabled="savingGoal">
            {{ savingGoal ? '保存中...' : '保存目标' }}
          </button>
        </div>

        <div class="settings-section">
          <div class="section-label">学习模式</div>
          <div class="mode-options">
            <div
              v-for="m in modeOptions"
              :key="m.value"
              class="mode-option"
              :class="{ active: form.study_mode === m.value }"
              @click="form.study_mode = m.value"
            >
              <div class="mode-icon">{{ m.icon }}</div>
              <div class="mode-name">{{ m.name }}</div>
              <div class="mode-desc">{{ m.desc }}</div>
              <div class="mode-check" v-if="form.study_mode === m.value">✓</div>
            </div>
          </div>
          <button class="btn btn-primary" style="margin-top: 12px" @click="saveStudyMode" :disabled="savingMode">
            {{ savingMode ? '保存中...' : '保存模式' }}
          </button>
        </div>

        <div class="settings-section">
          <div class="section-label">修改密码</div>
          <div class="form-group">
            <label class="form-label">新密码（至少6位）</label>
            <input v-model="form.password" type="password" class="form-input" placeholder="留空则不修改" />
          </div>
          <div class="form-group">
            <label class="form-label">确认新密码</label>
            <input v-model="form.confirmPassword" type="password" class="form-input" placeholder="再次输入新密码" />
          </div>
          <button class="btn btn-primary" @click="savePassword" :disabled="savingPwd">
            {{ savingPwd ? '修改中...' : '修改密码' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useToastStore } from '@/stores/toast'

const userStore = useUserStore()
const toast = useToastStore()

const form = reactive({
  nickname: userStore.nickname,
  daily_goal: userStore.dailyGoal,
  study_mode: userStore.studyMode,
  password: '',
  confirmPassword: ''
})

const saving = ref(false)
const savingGoal = ref(false)
const savingMode = ref(false)
const savingPwd = ref(false)

const goalOptions = [
  { value: 10, desc: '轻松入门，适合碎片化学习' },
  { value: 20, desc: '适中节奏，稳步提升' },
  { value: 50, desc: '高强度备考，快速突破' }
]

const modeOptions = [
  { value: 'card', name: '卡片模式', icon: '🃏', desc: '看英文回忆中文释义' },
  { value: 'spelling', name: '拼写模式', icon: '⌨️', desc: '看中文拼写英文单词' }
]

const avatarText = computed(() => {
  const name = userStore.nickname || 'U'
  return name.charAt(0).toUpperCase()
})

const saveProfile = async () => {
  if (!form.nickname === userStore.nickname) {
    toast.info('昵称没有变化')
    return
  }
  saving.value = true
  try {
    const res = await userStore.updateProfile({ nickname: form.nickname })
    if (res.code === 200) {
      toast.success('昵称修改成功')
    } else {
      toast.error(res.message || '修改失败')
    }
  } catch (e) {
    toast.error(e?.message || '修改失败')
  } finally {
    saving.value = false
  }
}

const saveGoal = async () => {
  savingGoal.value = true
  try {
    const res = await userStore.updateProfile({ daily_goal: form.daily_goal })
    if (res.code === 200) {
      toast.success(`每日目标已设为 ${form.daily_goal} 个单词`)
    } else {
      toast.error(res.message || '修改失败')
    }
  } catch (e) {
    toast.error(e?.message || '修改失败')
  } finally {
    savingGoal.value = false
  }
}

const saveStudyMode = async () => {
  savingMode.value = true
  try {
    const res = await userStore.updateProfile({ study_mode: form.study_mode })
    if (res.code === 200) {
      const modeLabel = modeOptions.find(m => m.value === form.study_mode)?.name || form.study_mode
      toast.success(`学习模式已切换为 ${modeLabel}`)
    } else {
      toast.error(res.message || '修改失败')
    }
  } catch (e) {
    toast.error(e?.message || '修改失败')
  } finally {
    savingMode.value = false
  }
}

const savePassword = async () => {
  if (!form.password) {
    toast.warning('请输入新密码')
    return
  }
  if (form.password.length < 6) {
    toast.warning('密码至少6位')
    return
  }
  if (form.password !== form.confirmPassword) {
    toast.error('两次密码输入不一致')
    return
  }
  savingPwd.value = true
  try {
    const res = await userStore.updateProfile({ password: form.password })
    if (res.code === 200) {
      toast.success('密码修改成功')
      form.password = ''
      form.confirmPassword = ''
    } else {
      toast.error(res.message || '修改失败')
    }
  } catch (e) {
    toast.error(e?.message || '修改失败')
  } finally {
    savingPwd.value = false
  }
}

onMounted(() => {
  if (!userStore.stats) {
    userStore.fetchProfile().catch(() => {})
  }
})
</script>

<style scoped>
.profile-grid { align-items: start; }
.profile-card { padding: 32px; }

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 24px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border);
}
.avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: var(--shadow);
}
.user-basic { flex: 1; min-width: 0; }
.user-nickname { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
.user-email { font-size: 14px; color: var(--text-secondary); margin-bottom: 6px; word-break: break-all; }
.user-created { font-size: 12px; color: var(--text-secondary); }

.stats-summary { margin-bottom: 24px; }
.summary-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.summary-item {
  text-align: center;
  padding: 16px 8px;
  background: #f9fafb;
  border-radius: 12px;
}
.s-num { font-size: 24px; font-weight: 800; color: var(--primary); margin-bottom: 4px; }
.s-lbl { font-size: 12px; color: var(--text-secondary); }

.today-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px;
  color: white;
}
.panel-title { font-size: 15px; font-weight: 600; margin-bottom: 14px; opacity: 0.95; }
.today-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.today-item {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  padding: 12px;
  text-align: center;
}
.today-label { display: block; font-size: 12px; opacity: 0.9; margin-bottom: 4px; }
.today-val { display: block; font-size: 22px; font-weight: 700; }

.settings-card { padding: 32px; }
.settings-title { font-size: 20px; font-weight: 700; margin-bottom: 24px; }
.settings-section {
  padding: 20px 0;
  border-bottom: 1px solid var(--border);
}
.settings-section:last-of-type { border-bottom: none; padding-bottom: 0; }
.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 14px;
}

.goal-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}
.goal-option {
  position: relative;
  padding: 16px 12px;
  background: #f9fafb;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
}
.goal-option:hover { background: #f3f4f6; }
.goal-option.active {
  background: #eef2ff;
  border-color: var(--primary);
}
.goal-value { font-size: 28px; font-weight: 800; color: var(--text); margin-bottom: 4px; }
.goal-option.active .goal-value { color: var(--primary); }
.goal-desc { font-size: 11px; color: var(--text-secondary); line-height: 1.4; }
.goal-check {
  position: absolute;
  top: 8px;
  right: 10px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.mode-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}
.mode-option {
  position: relative;
  padding: 20px 16px;
  background: #f9fafb;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
}
.mode-option:hover { background: #f3f4f6; }
.mode-option.active {
  background: #eef2ff;
  border-color: var(--primary);
}
.mode-icon { font-size: 32px; margin-bottom: 8px; }
.mode-name { font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.mode-option.active .mode-name { color: var(--primary); }
.mode-desc { font-size: 12px; color: var(--text-secondary); line-height: 1.4; }
.mode-check {
  position: absolute;
  top: 8px;
  right: 10px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

@media (max-width: 768px) {
  .profile-grid { grid-template-columns: 1fr; }
  .summary-row { grid-template-columns: repeat(2, 1fr); }
  .goal-options { grid-template-columns: 1fr; }
}
</style>
