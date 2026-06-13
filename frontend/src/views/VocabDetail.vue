<template>
  <div class="container">
    <div class="page-header">
      <div>
        <router-link to="/vocab" class="back-link">← 返回词库列表</router-link>
        <h1 class="page-title" style="margin-top: 8px">📖 {{ bookName }}</h1>
        <p class="page-subtitle">共 {{ total }} 个词汇</p>
      </div>
      <div class="page-actions">
        <div class="search-box">
          <input v-model="keyword" type="text" class="form-input" placeholder="🔍 搜索词库内单词..." @keyup.enter="page = 1; loadWords()" />
        </div>
      </div>
    </div>

    <div class="card">
      <div v-if="loading" class="empty">
        <div class="empty-icon">⏳</div>
        <div class="empty-text">加载中...</div>
      </div>
      <div v-else-if="!words.length" class="empty">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无词汇</div>
      </div>
      <div v-else class="word-list">
        <div v-for="w in words" :key="w.word_id" class="word-item" :class="{ learned: w.learned }">
          <div class="word-main">
            <div class="word-head">
              <span class="word-name">{{ w.word }}</span>
              <span v-if="w.phonetic" class="word-ipa">{{ w.phonetic }}</span>
              <span v-if="w.learned" class="word-status" :class="'status-' + w.status">
                {{ w.status === 'mastered' ? '已掌握' : w.status === 'learning' ? '学习中' : '新词' }}
              </span>
            </div>
            <div class="word-meaning">{{ w.meaning }}</div>
            <div v-if="w.example" class="word-example">
              <span class="example-text">💬 {{ w.example }}</span>
              <span v-if="w.example_trans" class="example-trans">{{ w.example_trans }}</span>
            </div>
            <div v-if="w.learned && w.next_review" class="word-review">
              📅 下次复习：{{ w.next_review }}
            </div>
          </div>
          <div class="word-actions">
            <button v-if="!w.learned" class="btn btn-outline btn-sm" @click="addWord(w)">➕ 加入学习</button>
            <button class="btn btn-outline btn-sm" @click="addToCustom(w)" title="加入生词本">⭐</button>
          </div>
        </div>
      </div>

      <div v-if="total > size" class="pagination">
        <button class="btn btn-outline btn-sm" :disabled="page <= 1" @click="page--; loadWords()">上一页</button>
        <span class="page-info">第 {{ page }} / {{ totalPages }} 页</span>
        <button class="btn btn-outline btn-sm" :disabled="page >= totalPages" @click="page++; loadWords()">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToastStore } from '@/stores/toast'
import api from '@/utils/api'

const route = useRoute()
const toast = useToastStore()
const bookId = route.params.id

const bookName = ref('词库详情')
const words = ref([])
const loading = ref(false)
const keyword = ref('')
const page = ref(1)
const size = ref(20)
const total = ref(0)

const totalPages = computed(() => Math.ceil(total.value / size.value))

const loadWords = async () => {
  loading.value = true
  try {
    const res = await api.get(`/vocab/${bookId}/words?page=${page.value}&size=${size.value}&keyword=${encodeURIComponent(keyword.value)}`)
    if (res.code === 200) {
      words.value = res.data.list || []
      total.value = res.data.total || 0
    }
  } catch (e) {
    toast.error('加载词汇失败')
  } finally {
    loading.value = false
  }
}

const loadBookInfo = async () => {
  try {
    const res = await api.get('/vocab/list')
    if (res.code === 200) {
      const all = [...(res.data.preset || []), ...(res.data.custom || [])]
      const b = all.find(b => b.id === Number(bookId))
      if (b) bookName.value = b.name
    }
  } catch (e) {}
}

const addWord = async (w) => {
  try {
    const res = await api.post('/word/add-custom', {
      word: w.word,
      meaning: w.meaning,
      phonetic: w.phonetic,
      example: w.example,
      example_trans: w.example_trans
    })
    if (res.code === 200) {
      toast.success('已加入学习队列')
      w.learned = true
      w.status = 'new'
    } else {
      toast.warning(res.message || '添加失败')
    }
  } catch (e) {
    toast.error(e?.message || '添加失败')
  }
}

const addToCustom = async (w) => {
  try {
    const res = await api.post('/word/add-custom', {
      word: w.word,
      meaning: w.meaning,
      phonetic: w.phonetic,
      example: w.example,
      example_trans: w.example_trans
    })
    if (res.code === 200) {
      toast.success('已加入生词本')
    } else {
      toast.warning(res.message || '该单词已存在')
    }
  } catch (e) {
    toast.error(e?.message || '添加失败')
  }
}

onMounted(() => {
  loadBookInfo()
  loadWords()
})
</script>

<style scoped>
.back-link {
  display: inline-block;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}
.back-link:hover { color: var(--primary); }
.search-box { width: 280px; }
.word-list { display: flex; flex-direction: column; gap: 12px; }
.word-item {
  display: flex;
  justify-content: space-between;
  padding: 16px 18px;
  background: #f9fafb;
  border-radius: 12px;
  gap: 16px;
  transition: all 0.2s;
}
.word-item:hover { background: #f3f4f6; }
.word-item.learned { background: #ecfdf5; }
.word-main { flex: 1; min-width: 0; }
.word-head { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap; }
.word-name { font-size: 18px; font-weight: 700; color: var(--text); }
.word-ipa { font-size: 13px; color: var(--text-secondary); }
.word-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}
.status-mastered { background: #d1fae5; color: #059669; }
.status-learning { background: #dbeafe; color: #2563eb; }
.status-new { background: #fef3c7; color: #d97706; }
.word-meaning { font-size: 14px; color: var(--text); margin-bottom: 6px; line-height: 1.6; }
.word-example {
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid var(--primary-light);
  margin-top: 8px;
}
.example-text { display: block; font-size: 13px; color: #1f2937; font-style: italic; margin-bottom: 4px; }
.example-trans { display: block; font-size: 12px; color: var(--text-secondary); }
.word-review { margin-top: 8px; font-size: 12px; color: var(--text-secondary); }
.word-actions { display: flex; flex-direction: column; gap: 8px; flex-shrink: 0; align-items: flex-end; }
.btn-sm { padding: 6px 12px; font-size: 12px; }
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
}
.page-info { font-size: 14px; color: var(--text-secondary); }
</style>
