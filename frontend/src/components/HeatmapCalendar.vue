<template>
  <div class="heatmap">
    <div class="months-row">
      <div v-for="(m, idx) in monthLabels" :key="idx" class="month-label" :style="{ left: m.left + 'px' }">
        {{ m.name }}
      </div>
    </div>
    <div class="heatmap-body">
      <div class="weekday-col">
        <div class="wd-label" style="height: 13px"></div>
        <div class="wd-label">一</div>
        <div class="wd-label" style="height: 13px"></div>
        <div class="wd-label">三</div>
        <div class="wd-label" style="height: 13px"></div>
        <div class="wd-label">五</div>
        <div class="wd-label" style="height: 13px"></div>
      </div>
      <div class="weeks-grid">
        <div v-for="(week, wi) in weeks" :key="wi" class="week-col">
          <div
            v-for="(day, di) in week"
            :key="di"
            class="day-cell"
            :class="{ 'day-today': day.isToday }"
            :style="{ background: getColor(day.count) }"
            :title="getTitle(day)"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ records: { type: Object, default: () => ({}) } })

const CELL = 12
const GAP = 3

const today = new Date()
const startDate = new Date(today)
startDate.setDate(today.getDate() - 364)
while (startDate.getDay() !== 0) startDate.setDate(startDate.getDate() - 1)

const getColor = (count) => {
  if (!count) return '#f3f4f6'
  if (count <= 5) return '#c7d2fe'
  if (count <= 15) return '#818cf8'
  if (count <= 30) return '#6366f1'
  return '#4338ca'
}

const getTitle = (d) => {
  if (!d.date) return ''
  return d.count > 0 ? `${d.date}: 学习了 ${d.count} 个单词` : d.date
}

const weeks = computed(() => {
  const result = []
  const cursor = new Date(startDate)
  const todayStr = today.toISOString().split('T')[0]
  let week = []
  while (cursor <= today) {
    const dateStr = cursor.toISOString().split('T')[0]
    const rec = props.records[dateStr]
    week.push({
      date: dateStr,
      count: rec ? rec.total : 0,
      isToday: dateStr === todayStr
    })
    if (week.length === 7) {
      result.push(week)
      week = []
    }
    cursor.setDate(cursor.getDate() + 1)
  }
  if (week.length) {
    while (week.length < 7) week.push({ date: null, count: 0 })
    result.push(week)
  }
  return result
})

const monthLabels = computed(() => {
  const labels = []
  const cursor = new Date(startDate)
  const endDate = new Date(today)
  let currentMonth = -1
  let colIdx = 0
  const names = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  while (cursor <= endDate) {
    const m = cursor.getMonth()
    if (m !== currentMonth) {
      const colPos = Math.floor(colIdx / 7)
      labels.push({ name: names[m], left: colPos * (CELL + GAP) + 4 })
      currentMonth = m
    }
    colIdx++
    cursor.setDate(cursor.getDate() + 1)
  }
  return labels
})
</script>

<style scoped>
.heatmap { overflow-x: auto; padding-bottom: 4px; }
.months-row { position: relative; height: 20px; padding-left: 28px; margin-bottom: 4px; }
.month-label { position: absolute; font-size: 11px; color: var(--text-secondary); }
.heatmap-body { display: flex; }
.weekday-col { display: flex; flex-direction: column; padding-right: 6px; }
.wd-label { font-size: 10px; color: var(--text-secondary); line-height: 12px; text-align: right; padding: 0 4px; height: 15px; }
.weeks-grid { display: flex; gap: 3px; }
.week-col { display: flex; flex-direction: column; gap: 3px; }
.day-cell {
  width: 12px; height: 12px; border-radius: 3px;
  cursor: pointer; transition: transform 0.15s;
}
.day-cell:hover { transform: scale(1.3); outline: 2px solid var(--primary); z-index: 1; }
.day-today { outline: 2px solid var(--primary-dark); }
</style>
