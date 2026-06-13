<template>
  <div class="trend-chart" ref="chartRef">
    <div class="chart-area">
      <svg :viewBox="`0 0 ${viewW} ${viewH}`" preserveAspectRatio="none" width="100%" :height="chartH">
        <defs>
          <linearGradient id="gradNew" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.3" />
            <stop offset="100%" stop-color="#f59e0b" stop-opacity="0" />
          </linearGradient>
          <linearGradient id="gradReview" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.3" />
            <stop offset="100%" stop-color="#3b82f6" stop-opacity="0" />
          </linearGradient>
        </defs>
        <g class="grid-lines">
          <line v-for="n in 4" :key="'h'+n" :x1="padL" :x2="viewW - padR" :y1="getY(maxVal * n / 4)" :y2="getY(maxVal * n / 4)" stroke="#e5e7eb" stroke-dasharray="3,3" />
        </g>
        <path :d="reviewAreaPath" fill="url(#gradReview)" />
        <path :d="newAreaPath" fill="url(#gradNew)" />
        <polyline :points="reviewPointsStr" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        <polyline :points="newPointsStr" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        <g v-for="(p, i) in newPoints" :key="'np'+i">
          <circle :cx="p.x" :cy="p.y" r="3" fill="#f59e0b" />
        </g>
        <g v-for="(p, i) in reviewPoints" :key="'rp'+i">
          <circle :cx="p.x" :cy="p.y" r="3" fill="#3b82f6" />
        </g>
        <g v-for="n in 5" :key="'ylb'+n">
          <text :x="padL - 8" :y="getY(maxVal * (n-1) / 4) + 4" text-anchor="end" font-size="10" fill="#9ca3af">{{ Math.round(maxVal * (n-1) / 4) }}</text>
        </g>
      </svg>
    </div>
    <div class="x-labels">
      <span v-for="(lbl, i) in xLabels" :key="'xl'+i" class="x-label" :style="{ width: (100 / xLabels.length) + '%' }">
        {{ lbl }}
      </span>
    </div>
    <div class="chart-legend">
      <span class="legend-item"><span class="legend-dot" style="background:#f59e0b"></span>新学</span>
      <span class="legend-item"><span class="legend-dot" style="background:#3b82f6"></span>复习</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
  days: { type: Number, default: 30 }
})

const padL = 36, padR = 12, padT = 8, padB = 0
const chartH = 220
const viewW = 600
const viewH = chartH

const dates = computed(() => props.data.dates || [])
const newArr = computed(() => props.data.new || [])
const reviewArr = computed(() => props.data.review || [])

const maxVal = computed(() => {
  const all = [...newArr.value, ...reviewArr.value, 5]
  return Math.ceil(Math.max(...all) / 5) * 5
})

const innerW = viewW - padL - padR
const innerH = viewH - padT - padB

const getX = (i) => {
  const n = dates.value.length || 1
  return padL + (innerW * i) / (n - 1 || 1)
}
const getY = (v) => padT + innerH - (innerH * v) / (maxVal.value || 1)

const newPoints = computed(() => newArr.value.map((v, i) => ({ x: getX(i), y: getY(v) })))
const reviewPoints = computed(() => reviewArr.value.map((v, i) => ({ x: getX(i), y: getY(v) })))
const newPointsStr = computed(() => newPoints.value.map(p => `${p.x},${p.y}`).join(' '))
const reviewPointsStr = computed(() => reviewPoints.value.map(p => `${p.x},${p.y}`).join(' '))

const newAreaPath = computed(() => {
  if (!newPoints.value.length) return ''
  const first = newPoints.value[0]
  const last = newPoints.value[newPoints.value.length - 1]
  const y0 = getY(0)
  return `M ${first.x},${y0} L ${newPointsStr.value.split(' ').join(' L ')} L ${last.x},${y0} Z`
})
const reviewAreaPath = computed(() => {
  if (!reviewPoints.value.length) return ''
  const first = reviewPoints.value[0]
  const last = reviewPoints.value[reviewPoints.value.length - 1]
  const y0 = getY(0)
  return `M ${first.x},${y0} L ${reviewPointsStr.value.split(' ').join(' L ')} L ${last.x},${y0} Z`
})

const xLabels = computed(() => {
  const ds = dates.value
  if (!ds.length) return []
  const step = Math.max(1, Math.ceil(ds.length / 6))
  const result = []
  for (let i = 0; i < ds.length; i += step) {
    const d = ds[i]
    const parts = d.split('-')
    result.push(`${parts[1]}/${parts[2]}`)
  }
  return result
})
</script>

<style scoped>
.trend-chart { width: 100%; }
.chart-area { width: 100%; }
.x-labels { display: flex; margin-top: 8px; padding-left: 36px; padding-right: 12px; }
.x-label { text-align: center; font-size: 10px; color: #9ca3af; overflow: hidden; }
.chart-legend { display: flex; justify-content: center; gap: 20px; margin-top: 12px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-secondary); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; }
</style>
