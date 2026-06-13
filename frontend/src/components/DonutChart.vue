<template>
  <div class="donut">
    <svg :viewBox="`0 0 ${size} ${size}`" :width="size" :height="size">
      <circle :cx="cx" :cy="cy" :r="r" fill="none" stroke="#f3f4f6" :stroke-width="strokeW" />
      <g v-for="(seg, i) in segments" :key="i">
        <circle
          :cx="cx"
          :cy="cy"
          :r="r"
          fill="none"
          :stroke="seg.color"
          :stroke-width="strokeW"
          :stroke-dasharray="seg.dash"
          :stroke-dashoffset="seg.offset"
          transform="rotate(-90 120 120)"
          stroke-linecap="butt"
        />
      </g>
      <text :x="cx" :y="cy - 4" text-anchor="middle" font-size="22" font-weight="800" fill="#1f2937">{{ total }}</text>
      <text :x="cx" :y="cy + 18" text-anchor="middle" font-size="11" fill="#6b7280">单词总数</text>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, default: () => [] },
  size: { type: Number, default: 240 }
})

const strokeW = 30
const cx = props.size / 2
const cy = props.size / 2
const r = (props.size - strokeW) / 2
const circumference = 2 * Math.PI * r

const total = computed(() => props.data.reduce((s, d) => s + (d.value || 0), 0))

const segments = computed(() => {
  if (!total.value) return []
  let offset = 0
  return props.data.map(d => {
    const portion = (d.value || 0) / total.value
    const dash = `${portion * circumference} ${circumference}`
    const seg = { color: d.color, dash, offset }
    offset += portion * circumference
    return seg
  })
})
</script>

<style scoped>
.donut { display: flex; justify-content: center; }
svg { display: block; }
</style>
