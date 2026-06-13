<template>
  <div class="container">
    <div class="page-header">
      <div>
        <h1 class="page-title">📊 学习统计</h1>
        <p class="page-subtitle">数据可视化，记录每一个进步的足迹</p>
      </div>
    </div>

    <div class="grid grid-4 stats-overview" style="margin-bottom: 24px">
      <div class="card stat-block">
        <div class="stat-icon s1">📚</div>
        <div>
          <div class="stat-num">{{ summary.total_words || 0 }}</div>
          <div class="stat-lbl">已学习单词</div>
        </div>
      </div>
      <div class="card stat-block">
        <div class="stat-icon s2">✅</div>
        <div>
          <div class="stat-num">{{ summary.mastered || 0 }}</div>
          <div class="stat-lbl">已掌握</div>
        </div>
      </div>
      <div class="card stat-block">
        <div class="stat-icon s3">📅</div>
        <div>
          <div class="stat-num">{{ summary.study_days || 0 }}</div>
          <div class="stat-lbl">学习天数</div>
        </div>
      </div>
      <div class="card stat-block">
        <div class="stat-icon s4">🔥</div>
        <div>
          <div class="stat-num">{{ summary.streak || 0 }}</div>
          <div class="stat-lbl">连续打卡</div>
        </div>
      </div>
    </div>

    <div class="card heatmap-card">
      <div class="card-header">
        <h3 class="card-title">📅 学习热力图（近一年）</h3>
        <div class="legend-row">
          <span>少</span>
          <span class="legend-box l0"></span>
          <span class="legend-box l1"></span>
          <span class="legend-box l2"></span>
          <span class="legend-box l3"></span>
          <span class="legend-box l4"></span>
          <span>多</span>
        </div>
      </div>
      <HeatmapCalendar :records="calendarRecords" />
    </div>

    <div class="grid grid-2" style="margin-top: 24px">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">📈 学习趋势</h3>
          <div class="trend-tabs">
            <button :class="{ active: trendDays === 7 }" @click="trendDays = 7">7天</button>
            <button :class="{ active: trendDays === 30 }" @click="trendDays = 30">30天</button>
            <button :class="{ active: trendDays === 90 }" @click="trendDays = 90">90天</button>
          </div>
        </div>
        <TrendChart :data="trendData" :days="trendDays" />
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">🥧 单词掌握分布</h3>
        </div>
        <div class="pie-wrap">
          <DonutChart
            :data="[
              { label: '新词', value: summary.new || 0, color: '#f59e0b' },
              { label: '学习中', value: summary.learning || 0, color: '#3b82f6' },
              { label: '已掌握', value: summary.mastered || 0, color: '#10b981' }
            ]"
          />
          <div class="pie-legend">
            <div v-for="item in pieItems" :key="item.label" class="pie-item">
              <span class="pie-dot" :style="{ background: item.color }"></span>
              <span class="pie-label">{{ item.label }}</span>
              <span class="pie-value">{{ item.value }}</span>
              <span class="pie-pct">{{ item.pct }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card" style="margin-top: 24px">
      <div class="card-header">
        <h3 class="card-title">🏆 累计数据</h3>
      </div>
      <div class="grid grid-4">
        <div class="cum-item">
          <div class="cum-num cum-new">{{ summary.total_new || 0 }}</div>
          <div class="cum-lbl">累计新学</div>
        </div>
        <div class="cum-item">
          <div class="cum-num cum-review">{{ summary.total_review || 0 }}</div>
          <div class="cum-lbl">累计复习</div>
        </div>
        <div class="cum-item">
          <div class="cum-num cum-master">{{ summary.total_mastered || 0 }}</div>
          <div class="cum-lbl">累计掌握</div>
        </div>
        <div class="cum-item">
          <div class="cum-num cum-avg">{{ avgPerDay }}</div>
          <div class="cum-lbl">日均学习</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToastStore } from '@/stores/toast'
import api from '@/utils/api'
import HeatmapCalendar from '@/components/HeatmapCalendar.vue'
import TrendChart from '@/components/TrendChart.vue'
import DonutChart from '@/components/DonutChart.vue'

const toast = useToastStore()
const summary = ref({})
const calendarRecords = ref({})
const trendData = ref({})
const trendDays = ref(30)

const total = computed(() => (summary.value.new || 0) + (summary.value.learning || 0) + (summary.value.mastered || 0))
const pieItems = computed(() => {
  const items = [
    { label: '新词', value: summary.value.new || 0, color: '#f59e0b' },
    { label: '学习中', value: summary.value.learning || 0, color: '#3b82f6' },
    { label: '已掌握', value: summary.value.mastered || 0, color: '#10b981' }
  ]
  const t = total.value || 1
  return items.map(i => ({ ...i, pct: Math.round((i.value / t) * 100) }))
})
const avgPerDay = computed(() => {
  const days = summary.value.study_days || 0
  if (!days) return 0
  return Math.round(((summary.value.total_new || 0) + (summary.value.total_review || 0)) / days)
})

const loadAll = async () => {
  try {
    const [s, c] = await Promise.all([
      api.get('/stats/summary'),
      api.get('/stats/calendar')
    ])
    if (s.code === 200) summary.value = s.data
    if (c.code === 200) calendarRecords.value = c.data.records || {}
  } catch (e) {
    toast.error('加载统计数据失败')
  }
}

const loadTrend = async () => {
  try {
    const res = await api.get(`/stats/trend?days=${trendDays.value}`)
    if (res.code === 200) trendData.value = res.data
  } catch (e) {
    toast.error('加载趋势数据失败')
  }
}

watch(trendDays, loadTrend)
onMounted(() => { loadAll(); loadTrend() })
</script>

<style scoped>
.stats-overview .stat-block { display: flex; align-items: center; gap: 16px; }
.stat-icon {
  width: 56px; height: 56px; border-radius: 14px; display: flex;
  align-items: center; justify-content: center; font-size: 28px;
}
.s1 { background: #ede9fe; }
.s2 { background: #d1fae5; }
.s3 { background: #dbeafe; }
.s4 { background: #fee2e2; }
.stat-num { font-size: 28px; font-weight: 800; }
.stat-lbl { font-size: 13px; color: var(--text-secondary); }

.heatmap-card { padding: 28px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.card-title { font-size: 18px; font-weight: 700; }
.legend-row { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-secondary); }
.legend-box { width: 14px; height: 14px; border-radius: 3px; display: inline-block; }
.l0 { background: #f3f4f6; }
.l1 { background: #c7d2fe; }
.l2 { background: #818cf8; }
.l3 { background: #6366f1; }
.l4 { background: #4338ca; }

.trend-tabs { display: flex; gap: 4px; background: #f3f4f6; padding: 4px; border-radius: 8px; }
.trend-tabs button {
  border: none; background: transparent; padding: 6px 14px; border-radius: 6px;
  font-size: 13px; cursor: pointer; color: var(--text-secondary); font-weight: 500; transition: all 0.2s;
}
.trend-tabs button.active { background: white; color: var(--primary); box-shadow: var(--shadow); }

.pie-wrap { display: flex; align-items: center; gap: 32px; flex-wrap: wrap; justify-content: center; }
.pie-legend { display: flex; flex-direction: column; gap: 14px; flex: 1; min-width: 180px; }
.pie-item { display: flex; align-items: center; gap: 10px; font-size: 14px; }
.pie-dot { width: 12px; height: 12px; border-radius: 50%; }
.pie-label { flex: 1; }
.pie-value { font-weight: 700; min-width: 40px; text-align: right; }
.pie-pct { color: var(--text-secondary); min-width: 40px; text-align: right; }

.cum-item { text-align: center; padding: 20px; background: #f9fafb; border-radius: 12px; }
.cum-num { font-size: 30px; font-weight: 800; margin-bottom: 6px; }
.cum-lbl { font-size: 13px; color: var(--text-secondary); }
.cum-new { color: var(--warning); }
.cum-review { color: var(--info); }
.cum-master { color: var(--success); }
.cum-avg { color: var(--primary); }
</style>
