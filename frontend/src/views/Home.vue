<template>
  <div class="container">
    <div class="welcome-section">
      <div class="welcome-text">
        <h1 class="welcome-title">👋 欢迎回来，{{ userStore.nickname }}</h1>
        <p class="welcome-subtitle">今天也要继续加油哦！坚持就是胜利 💪</p>
      </div>
      <router-link to="/study" class="btn btn-primary btn-lg">
        🚀 开始学习
      </router-link>
    </div>

    <div class="grid grid-4 stats-grid">
      <div class="stat-card gradient-1">
        <div class="stat-label">今日学习</div>
        <div class="stat-value">{{ todaySummary.today_total || 0 }}</div>
        <div class="stat-detail">新学 {{ todaySummary.today_new || 0 }} / 复习 {{ todaySummary.today_review || 0 }}</div>
      </div>
      <div class="stat-card gradient-2">
        <div class="stat-label">每日目标</div>
        <div class="stat-value">{{ todaySummary.daily_goal || userStore.dailyGoal }} <span class="stat-unit">词</span></div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: goalProgress + '%' }"></div>
        </div>
        <div class="stat-detail">已完成 {{ goalProgress }}%</div>
      </div>
      <div class="stat-card gradient-3">
        <div class="stat-label">累计掌握</div>
        <div class="stat-value">{{ summary.mastered || 0 }} <span class="stat-unit">词</span></div>
        <div class="stat-detail">已学习 {{ summary.total_words || 0 }} 词</div>
      </div>
      <div class="stat-card gradient-4">
        <div class="stat-label">连续打卡</div>
        <div class="stat-value">{{ summary.streak || 0 }} <span class="stat-unit">天</span></div>
        <div class="stat-detail">累计学习 {{ summary.study_days || 0 }} 天</div>
      </div>
    </div>

    <div class="grid grid-2 main-grid">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">📚 今日学习进度</h3>
        </div>
        <div class="today-detail">
          <div class="today-item">
            <span class="today-label">📖 新学单词</span>
            <span class="today-value">{{ todaySummary.today_new || 0 }}</span>
          </div>
          <div class="today-item">
            <span class="today-label">🔄 复习单词</span>
            <span class="today-value">{{ todaySummary.today_review || 0 }}</span>
          </div>
          <div class="today-item">
            <span class="today-label">✨ 新掌握</span>
            <span class="today-value">{{ todaySummary.today_mastered || 0 }}</span>
          </div>
          <div class="today-item">
            <span class="today-label">⏰ 待复习</span>
            <span class="today-value">{{ todaySummary.review_due || 0 }}</span>
          </div>
        </div>
        <div class="card-actions">
          <router-link v-if="(todaySummary.review_due || 0) > 0" to="/study" class="btn btn-primary">
            立即复习 ({{ todaySummary.review_due }})
          </router-link>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">📊 学习概览</h3>
        </div>
        <div class="overview-list">
          <div class="overview-item">
            <div class="overview-header">
              <span class="overview-name">🆕 新词</span>
              <span class="overview-count">{{ summary.new || 0 }}</span>
            </div>
            <div class="progress-bar"><div class="progress-fill c1" :style="{ width: getPercent(summary.new, summary.total_words) + '%' }"></div></div>
          </div>
          <div class="overview-item">
            <div class="overview-header">
              <span class="overview-name">📖 学习中</span>
              <span class="overview-count">{{ summary.learning || 0 }}</span>
            </div>
            <div class="progress-bar"><div class="progress-fill c2" :style="{ width: getPercent(summary.learning, summary.total_words) + '%' }"></div></div>
          </div>
          <div class="overview-item">
            <div class="overview-header">
              <span class="overview-name">✅ 已掌握</span>
              <span class="overview-count">{{ summary.mastered || 0 }}</span>
            </div>
            <div class="progress-bar"><div class="progress-fill c3" :style="{ width: getPercent(summary.mastered, summary.total_words) + '%' }"></div></div>
          </div>
          <div class="overview-summary">
            <div>
              <span class="summary-label">累计新学</span>
              <span class="summary-value">{{ summary.total_new || 0 }}</span>
            </div>
            <div>
              <span class="summary-label">累计复习</span>
              <span class="summary-value">{{ summary.total_review || 0 }}</span>
            </div>
            <div>
              <span class="summary-label">累计掌握</span>
              <span class="summary-value">{{ summary.total_mastered || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card recent-calendar">
      <div class="card-header">
        <h3 class="card-title">📅 最近学习记录</h3>
      </div>
      <MiniCalendar :records="calendarRecords" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useToastStore } from '@/stores/toast'
import api from '@/utils/api'
import MiniCalendar from '@/components/MiniCalendar.vue'

const userStore = useUserStore()
const toast = useToastStore()
const todaySummary = ref({})
const summary = ref({})
const calendarRecords = ref({})

const goalProgress = computed(() => {
  const goal = todaySummary.value.daily_goal || userStore.dailyGoal || 20
  const done = todaySummary.value.today_new || 0
  return Math.min(100, Math.round((done / goal) * 100))
})

const getPercent = (val, total) => {
  if (!total) return 0
  return Math.round((val / total) * 100)
}

const loadData = async () => {
  try {
    const [s1, s2, cal] = await Promise.all([
      api.get('/study/today-summary'),
      api.get('/stats/summary'),
      api.get('/stats/calendar')
    ])
    if (s1.code === 200) todaySummary.value = s1.data
    if (s2.code === 200) summary.value = s2.data
    if (cal.code === 200) calendarRecords.value = cal.data.records || {}
  } catch (e) {
    toast.error('加载数据失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--radius);
  color: white;
  box-shadow: var(--shadow);
}
.welcome-title { font-size: 26px; font-weight: 700; margin-bottom: 6px; }
.welcome-subtitle { font-size: 14px; opacity: 0.9; }
.stats-grid { margin-bottom: 24px; }
.stat-card {
  padding: 24px;
  border-radius: var(--radius);
  color: white;
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}
.stat-card::before { content: ''; position: absolute; top: -30%; right: -10%; width: 120px; height: 120px; background: rgba(255,255,255,0.1); border-radius: 50%; }
.gradient-1 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.gradient-2 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.gradient-3 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
.gradient-4 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
.stat-label { font-size: 13px; opacity: 0.9; margin-bottom: 6px; position: relative; z-index: 1; }
.stat-value { font-size: 34px; font-weight: 800; line-height: 1.2; position: relative; z-index: 1; }
.stat-unit { font-size: 16px; font-weight: 500; opacity: 0.9; }
.stat-detail { font-size: 12px; opacity: 0.85; margin-top: 10px; position: relative; z-index: 1; }
.stat-card .progress-bar { margin: 12px 0 6px; background: rgba(255,255,255,0.3); }
.stat-card .progress-fill { background: white; }
.main-grid { margin-bottom: 24px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
.card-title { font-size: 18px; font-weight: 700; }
.today-detail { display: flex; flex-direction: column; gap: 14px; margin-bottom: 20px; }
.today-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; background: #f9fafb; border-radius: 10px; }
.today-label { font-size: 14px; color: var(--text-secondary); }
.today-value { font-size: 22px; font-weight: 700; color: var(--text); }
.card-actions { display: flex; gap: 12px; }
.overview-list { display: flex; flex-direction: column; gap: 16px; }
.overview-item { display: flex; flex-direction: column; gap: 8px; }
.overview-header { display: flex; justify-content: space-between; align-items: center; }
.overview-name { font-size: 14px; font-weight: 500; }
.overview-count { font-size: 16px; font-weight: 700; color: var(--text); }
.c1 { background: #f59e0b !important; }
.c2 { background: #3b82f6 !important; }
.c3 { background: #10b981 !important; }
.overview-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--border); }
.overview-summary > div { text-align: center; }
.summary-label { display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
.summary-value { font-size: 20px; font-weight: 700; color: var(--primary); }
.recent-calendar { margin-bottom: 24px; }
</style>
