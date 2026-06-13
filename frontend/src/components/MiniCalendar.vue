<template>
  <div class="minical">
    <div class="weekdays">
      <span v-for="w in weekdays" :key="w" class="weekday">{{ w }}</span>
    </div>
    <div class="days">
      <div
        v-for="(day, idx) in days"
        :key="idx"
        class="day"
        :class="day.classes"
        :title="day.title"
      >
        <span v-if="day.date" class="day-num">{{ day.num }}</span>
        <span v-if="day.count" class="day-dot" :style="{ background: getColor(day.count) }"></span>
      </div>
    </div>
    <div class="legend">
      <span class="legend-item"><span class="legend-dot l0"></span> 无</span>
      <span class="legend-item"><span class="legend-dot l1"></span> 少</span>
      <span class="legend-item"><span class="legend-dot l2"></span> 中</span>
      <span class="legend-item"><span class="legend-dot l3"></span> 多</span>
      <span class="legend-item"><span class="legend-dot l4"></span> 很多</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  records: { type: Object, default: () => ({}) },
  months: { type: Number, default: 3 }
})

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

const getColor = (count) => {
  if (count <= 0) return 'transparent'
  if (count <= 5) return '#c7d2fe'
  if (count <= 15) return '#818cf8'
  if (count <= 30) return '#6366f1'
  return '#4338ca'
}

const days = computed(() => {
  const result = []
  const today = new Date()
  const startDate = new Date(today)
  startDate.setDate(today.getDate() - (props.months * 30 - 1))

  const firstDay = new Date(startDate.getFullYear(), startDate.getMonth(), 1)
  const paddingStart = firstDay.getDay()
  for (let i = 0; i < paddingStart; i++) {
    result.push({ date: null, num: '', classes: '', count: 0, title: '' })
  }

  const d = new Date(startDate)
  while (d <= today) {
    const dateStr = d.toISOString().split('T')[0]
    const record = props.records[dateStr]
    const count = record ? record.total : 0
    const isToday = dateStr === today.toISOString().split('T')[0]
    result.push({
      date: dateStr,
      num: d.getDate(),
      count,
      classes: isToday ? 'is-today' : '',
      title: count > 0 ? `${dateStr}: ${count}个单词` : dateStr
    })
    d.setDate(d.getDate() + 1)
  }
  return result
})
</script>

<style scoped>
.minical { padding: 8px 0; }
.weekdays { display: grid; grid-template-columns: repeat(7, 1fr); margin-bottom: 8px; }
.weekday { text-align: center; font-size: 12px; color: var(--text-secondary); font-weight: 500; }
.days { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; }
.day {
  aspect-ratio: 1;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: #f3f4f6;
  font-size: 11px;
  color: var(--text-secondary);
}
.day.is-today { border: 2px solid var(--primary); }
.day-num { font-weight: 500; }
.day-dot {
  position: absolute;
  bottom: 3px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.legend { display: flex; justify-content: flex-end; gap: 14px; margin-top: 16px; font-size: 12px; color: var(--text-secondary); align-items: center; }
.legend-item { display: flex; align-items: center; gap: 4px; }
.legend-dot { width: 12px; height: 12px; border-radius: 3px; }
.l0 { background: #f3f4f6; }
.l1 { background: #c7d2fe; }
.l2 { background: #818cf8; }
.l3 { background: #6366f1; }
.l4 { background: #4338ca; }
</style>
