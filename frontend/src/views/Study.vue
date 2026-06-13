<template>
  <div class="container">
    <div class="page-header">
      <div>
        <h1 class="page-title">📖 学习中心</h1>
        <p class="page-subtitle">混合新词 + 复习词，科学记忆更高效</p>
      </div>
    </div>

    <div v-if="!queue.length && !loading" class="card empty-study">
      <div class="empty">
        <div class="empty-icon">🎉</div>
        <div class="empty-text">今日学习任务已完成！</div>
        <div class="empty-subtext">休息一下，明天继续加油哦～</div>
        <button class="btn btn-primary btn-lg" style="margin-top: 20px" @click="loadQueue">
          🔄 刷新学习队列
        </button>
      </div>
    </div>

    <div v-if="loading" class="card">
      <div class="empty">
        <div class="empty-icon">⏳</div>
        <div class="empty-text">正在加载学习队列...</div>
      </div>
    </div>

    <div v-if="queue.length && !loading" class="study-layout">
      <div class="study-sidebar">
        <div class="card sidebar-card">
          <h3 class="sidebar-title">📊 今日进度</h3>
          <div class="sidebar-stat">
            <span>剩余</span>
            <strong class="text-primary">{{ queue.length }}</strong>
          </div>
          <div class="sidebar-stat">
            <span>新词</span>
            <strong class="text-warning">{{ newCount }}</strong>
          </div>
          <div class="sidebar-stat">
            <span>复习</span>
            <strong class="text-info">{{ reviewCount }}</strong>
          </div>
          <div class="sidebar-stat">
            <span>目标</span>
            <strong>{{ dailyGoal }} 词/天</strong>
          </div>
          <div class="sidebar-stat">
            <span>今日已完成</span>
            <strong class="text-success">{{ completedCount }}</strong>
          </div>
          <div class="queue-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
            <div class="progress-label">{{ progress }}%</div>
          </div>
        </div>

        <div class="card sidebar-card">
          <h3 class="sidebar-title">📋 学习队列</h3>
          <div class="queue-list">
            <div
              v-for="(w, idx) in queue"
              :key="w.user_word_id"
              class="queue-item"
              :class="{ active: idx === currentIndex, done: idx < currentIndex }"
            >
              <span class="queue-idx">{{ idx + 1 }}</span>
              <span class="queue-word">{{ idx < currentIndex ? '✓' : w.word }}</span>
              <span v-if="!w.is_review && idx >= currentIndex" class="badge badge-warning" style="margin-left:auto">新</span>
              <span v-if="w.is_review && idx >= currentIndex" class="badge badge-info" style="margin-left:auto">复</span>
            </div>
          </div>
        </div>
      </div>

      <div class="study-main">
        <div class="word-card" :class="{ flipped: showAnswer }">
          <div class="word-front">
            <div class="word-tag" :class="currentWord?.is_review ? 'tag-review' : 'tag-new'">
              {{ currentWord?.is_review ? '🔄 复习' : '🆕 新词' }}
            </div>
            <div class="word-title">{{ currentWord?.word }}</div>
            <div v-if="currentWord?.phonetic" class="word-phonetic">
              {{ currentWord.phonetic }}
              <button class="speak-btn" @click="speakWord" title="朗读">🔊</button>
            </div>
            <button class="btn btn-outline btn-lg reveal-btn" @click="showAnswer = true">
              查看释义
            </button>
          </div>
          <div class="word-back">
            <div class="word-tag" :class="currentWord?.is_review ? 'tag-review' : 'tag-new'">
              {{ currentWord?.is_review ? '🔄 复习' : '🆕 新词' }}
            </div>
            <div class="word-title">{{ currentWord?.word }}</div>
            <div v-if="currentWord?.phonetic" class="word-phonetic">
              {{ currentWord.phonetic }}
              <button class="speak-btn" @click="speakWord" title="朗读">🔊</button>
            </div>
            <div class="word-section">
              <div class="section-label">📝 释义</div>
              <div class="section-content meaning">{{ currentWord?.meaning }}</div>
            </div>
            <div v-if="currentWord?.example" class="word-section">
              <div class="section-label">💬 例句</div>
              <div class="section-content example">{{ currentWord?.example }}</div>
              <div v-if="currentWord?.example_trans" class="section-content example-trans">
                {{ currentWord.example_trans }}
              </div>
            </div>
          </div>
        </div>

        <div class="action-buttons" v-if="showAnswer">
          <button class="action-btn btn-unknown" @click="handleReview(0)">
            <span class="action-icon">❌</span>
            <span class="action-text">不认识</span>
            <span class="action-hint">重新学习</span>
          </button>
          <button class="action-btn btn-vague" @click="handleReview(1)">
            <span class="action-icon">🤔</span>
            <span class="action-text">模糊</span>
            <span class="action-hint">适当延后</span>
          </button>
          <button class="action-btn btn-know" @click="handleReview(2)">
            <span class="action-icon">✅</span>
            <span class="action-text">认识</span>
            <span class="action-hint">按算法延后</span>
          </button>
        </div>

        <div v-if="!showAnswer" class="hint-text">
          💡 请尝试回忆单词含义，然后点击查看释义
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useToastStore } from '@/stores/toast'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

const userStore = useUserStore()
const toast = useToastStore()
const loading = ref(false)
const queue = ref([])
const currentIndex = ref(0)
const showAnswer = ref(false)
const completedCount = ref(0)
const queueInfo = ref({})

const currentWord = computed(() => queue.value[currentIndex.value] || null)
const newCount = computed(() => queue.value.filter(w => !w.is_review).length)
const reviewCount = computed(() => queue.value.filter(w => w.is_review).length)
const dailyGoal = computed(() => userStore.dailyGoal || 20)
const totalCount = computed(() => queue.value.length + completedCount.value)
const progress = computed(() => totalCount.value ? Math.round((completedCount.value / totalCount.value) * 100) : 0)

const loadQueue = async () => {
  loading.value = true
  try {
    const res = await api.get('/study/queue')
    if (res.code === 200) {
      queue.value = res.data.queue || []
      queueInfo.value = res.data
      currentIndex.value = 0
      showAnswer.value = false
    } else {
      toast.error(res.message || '加载失败')
    }
  } catch (e) {
    toast.error('加载学习队列失败')
  } finally {
    loading.value = false
  }
}

const speakWord = () => {
  if ('speechSynthesis' in window && currentWord.value) {
    const utter = new SpeechSynthesisUtterance(currentWord.value.word)
    utter.lang = 'en-US'
    speechSynthesis.speak(utter)
  }
}

const handleReview = async (quality) => {
  if (!currentWord.value) return
  try {
    const res = await api.post('/study/review', {
      user_word_id: currentWord.value.user_word_id,
      quality
    })
    if (res.code === 200) {
      const labels = ['重新学习', '延后复习', '安排下次复习']
      toast.success(`已${labels[quality]}：${currentWord.value.word}`)
      completedCount.value++
      currentIndex.value++
      showAnswer.value = false
      await nextTick()
      if (currentIndex.value >= queue.value.length) {
        setTimeout(() => {
          toast.success('🎉 太棒了！本轮学习完成！')
        }, 300)
      }
    }
  } catch (e) {
    toast.error('操作失败，请重试')
  }
}

onMounted(loadQueue)
</script>

<style scoped>
.empty-study { margin-top: 40px; }
.study-layout { display: grid; grid-template-columns: 280px 1fr; gap: 24px; align-items: start; }
.sidebar-card { margin-bottom: 20px; }
.sidebar-title { font-size: 16px; font-weight: 700; margin-bottom: 16px; }
.sidebar-stat {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; border-bottom: 1px dashed var(--border); font-size: 14px;
}
.sidebar-stat span { color: var(--text-secondary); }
.sidebar-stat strong { font-size: 16px; }
.text-primary { color: var(--primary); }
.text-warning { color: var(--warning); }
.text-info { color: var(--info); }
.text-success { color: var(--success); }
.queue-progress { margin-top: 16px; }
.progress-label { text-align: right; font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
.queue-list { max-height: 360px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
.queue-item {
  display: flex; align-items: center; gap: 8px; padding: 8px 10px;
  border-radius: 6px; font-size: 13px; cursor: pointer; transition: all 0.15s;
}
.queue-item:hover { background: #f3f4f6; }
.queue-item.active { background: #eef2ff; color: var(--primary); font-weight: 600; }
.queue-item.done { color: #9ca3af; text-decoration: line-through; }
.queue-idx { width: 22px; height: 22px; border-radius: 50%; background: #e5e7eb; display: flex; align-items: center; justify-content: center; font-size: 11px; }
.queue-item.active .queue-idx { background: var(--primary); color: white; }
.queue-item.done .queue-idx { background: #d1fae5; color: var(--success); }
.queue-word { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.study-main { }
.word-card {
  position: relative;
  min-height: 420px;
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 40px;
  perspective: 1000px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px solid transparent;
  transition: all 0.3s;
}
.word-card.flipped { border-color: var(--primary-light); background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%); }
.word-tag {
  position: absolute; top: 20px; right: 20px;
  padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;
}
.tag-new { background: #fef3c7; color: #92400e; }
.tag-review { background: #dbeafe; color: #1e40af; }

.word-front, .word-back { display: flex; flex-direction: column; align-items: center; text-align: center; width: 100%; max-width: 560px; }
.word-title { font-size: 48px; font-weight: 800; color: var(--text); margin: 20px 0 12px; letter-spacing: -0.5px; }
.word-phonetic { font-size: 18px; color: var(--text-secondary); margin-bottom: 30px; display: flex; align-items: center; gap: 10px; }
.speak-btn { background: #eef2ff; border: none; border-radius: 50%; width: 36px; height: 36px; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.speak-btn:hover { background: var(--primary); color: white; transform: scale(1.1); }
.reveal-btn { margin-top: 20px; padding: 14px 40px; font-size: 16px; }

.word-section { width: 100%; margin-top: 20px; text-align: left; }
.section-label { font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px; }
.section-content { font-size: 16px; line-height: 1.8; }
.meaning { color: var(--text); font-weight: 500; padding: 12px 16px; background: #f9fafb; border-radius: 10px; }
.example { color: #1f2937; font-style: italic; padding: 12px 16px; background: #eff6ff; border-radius: 10px 10px 0 0; }
.example-trans { color: var(--text-secondary); padding: 8px 16px 12px; background: #eff6ff; border-radius: 0 0 10px 10px; font-size: 14px; }

.action-buttons { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 24px; }
.action-btn {
  padding: 20px 16px;
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  color: white;
  font-weight: 600;
}
.action-btn:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.btn-unknown { background: linear-gradient(135deg, #f87171, #ef4444); }
.btn-vague { background: linear-gradient(135deg, #fbbf24, #f59e0b); }
.btn-know { background: linear-gradient(135deg, #34d399, #10b981); }
.action-icon { font-size: 28px; }
.action-text { font-size: 18px; }
.action-hint { font-size: 12px; opacity: 0.9; font-weight: 400; }

.hint-text { text-align: center; margin-top: 20px; color: var(--text-secondary); font-size: 14px; }

@media (max-width: 900px) {
  .study-layout { grid-template-columns: 1fr; }
  .sidebar-card:first-child { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .sidebar-card:first-child .sidebar-title { grid-column: 1/-1; margin-bottom: 4px; }
  .sidebar-stat { flex-direction: column; padding: 8px; background: #f9fafb; border-radius: 8px; border: none; gap: 4px; }
  .queue-list { max-height: 160px; }
  .word-card { min-height: 360px; padding: 24px; }
  .word-title { font-size: 36px; }
}
@media (max-width: 600px) {
  .action-buttons { grid-template-columns: 1fr; gap: 10px; }
  .action-btn { padding: 14px; flex-direction: row; justify-content: center; }
}
</style>
