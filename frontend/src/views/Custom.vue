<template>
  <div class="container">
    <div class="page-header">
      <div>
        <h1 class="page-title">⭐ 我的生词本</h1>
        <p class="page-subtitle">手动添加的单词，重点攻克</p>
      </div>
      <div class="page-actions">
        <button class="btn btn-primary" @click="showAddModal = true">
          ➕ 添加单词
        </button>
      </div>
    </div>

    <div class="grid grid-4 summary-grid">
      <div class="card stat-item s1">
        <div class="stat-icon">📚</div>
        <div>
          <div class="stat-num">{{ total }}</div>
          <div class="stat-lbl">生词总数</div>
        </div>
      </div>
      <div class="card stat-item s2">
        <div class="stat-icon">🆕</div>
        <div>
          <div class="stat-num">{{ newCount }}</div>
          <div class="stat-lbl">未学习</div>
        </div>
      </div>
      <div class="card stat-item s3">
        <div class="stat-icon">📖</div>
        <div>
          <div class="stat-num">{{ learningCount }}</div>
          <div class="stat-lbl">学习中</div>
        </div>
      </div>
      <div class="card stat-item s4">
        <div class="stat-icon">✅</div>
        <div>
          <div class="stat-num">{{ masteredCount }}</div>
          <div class="stat-lbl">已掌握</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div v-if="loading" class="empty">
        <div class="empty-icon">⏳</div>
        <div class="empty-text">加载中...</div>
      </div>
      <div v-else-if="!words.length" class="empty">
        <div class="empty-icon">📝</div>
        <div class="empty-text">生词本还是空的～</div>
        <div class="empty-subtext">点击右上角按钮添加你想记忆的单词</div>
      </div>
      <div v-else class="word-list">
        <div v-for="w in words" :key="w.id" class="word-item">
          <div class="word-main">
            <div class="word-head">
              <span class="word-name">{{ w.word }}</span>
              <span v-if="w.phonetic" class="word-ipa">{{ w.phonetic }}</span>
              <span class="word-status" :class="'status-' + w.status">
                {{ w.status === 'mastered' ? '已掌握' : w.status === 'learning' ? '学习中' : '新词' }}
              </span>
            </div>
            <div class="word-meaning">{{ w.meaning }}</div>
            <div v-if="w.example" class="word-example">
              <span class="example-text">💬 {{ w.example }}</span>
              <span v-if="w.example_trans" class="example-trans">{{ w.example_trans }}</span>
            </div>
            <div class="word-meta">
              <span>📅 下次复习：{{ w.next_review || '-' }}</span>
              <span>🔄 复习次数：{{ w.total_reviews || 0 }}</span>
              <span>✅ 正确：{{ w.correct_count || 0 }}</span>
            </div>
          </div>
          <div class="word-actions">
            <button class="btn btn-danger btn-sm" @click="deleteWord(w)" title="删除">🗑️ 删除</button>
          </div>
        </div>
      </div>

      <div v-if="total > size" class="pagination">
        <button class="btn btn-outline btn-sm" :disabled="page <= 1" @click="page--; loadList()">上一页</button>
        <span class="page-info">第 {{ page }} / {{ totalPages }} 页</span>
        <button class="btn btn-outline btn-sm" :disabled="page >= totalPages" @click="page++; loadList()">下一页</button>
      </div>
    </div>

    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">➕ 添加单词</div>
          <button class="modal-close" @click="showAddModal = false">×</button>
        </div>
        <form @submit.prevent="addWord">
          <div class="form-group">
            <label class="form-label">单词 <span class="required">*</span></label>
            <input v-model="form.word" type="text" class="form-input" placeholder="例如：vocabulary" required />
          </div>
          <div class="form-group">
            <label class="form-label">音标</label>
            <input v-model="form.phonetic" type="text" class="form-input" placeholder="例如：/vəˈkæbjəleri/" />
          </div>
          <div class="form-group">
            <label class="form-label">释义 <span class="required">*</span></label>
            <textarea v-model="form.meaning" class="form-input" rows="2" placeholder="例如：n. 词汇，词汇量" required></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">例句</label>
            <input v-model="form.example" type="text" class="form-input" placeholder="英文例句" />
          </div>
          <div class="form-group">
            <label class="form-label">例句翻译</label>
            <input v-model="form.example_trans" type="text" class="form-input" placeholder="例句的中文翻译" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="showAddModal = false">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="adding">
              {{ adding ? '添加中...' : '添加' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToastStore } from '@/stores/toast'
import api from '@/utils/api'

const toast = useToastStore()
const words = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)

const showAddModal = ref(false)
const adding = ref(false)
const form = reactive({ word: '', phonetic: '', meaning: '', example: '', example_trans: '' })

const totalPages = computed(() => Math.ceil(total.value / size.value))
const newCount = computed(() => words.value.filter(w => w.status === 'new').length)
const learningCount = computed(() => words.value.filter(w => w.status === 'learning').length)
const masteredCount = computed(() => words.value.filter(w => w.status === 'mastered').length)

const loadList = async () => {
  loading.value = true
  try {
    const res = await api.get(`/word/custom-list?page=${page.value}&size=${size.value}`)
    if (res.code === 200) {
      words.value = res.data.list || []
      total.value = res.data.total || 0
    }
  } catch (e) {
    toast.error('加载失败')
  } finally {
    loading.value = false
  }
}

const addWord = async () => {
  if (!form.word.trim() || !form.meaning.trim()) {
    toast.warning('单词和释义不能为空')
    return
  }
  adding.value = true
  try {
    const res = await api.post('/word/add-custom', { ...form })
    if (res.code === 200) {
      toast.success('添加成功')
      showAddModal.value = false
      Object.assign(form, { word: '', phonetic: '', meaning: '', example: '', example_trans: '' })
      page.value = 1
      loadList()
    } else {
      toast.error(res.message || '添加失败')
    }
  } catch (e) {
    toast.error(e?.message || '添加失败')
  } finally {
    adding.value = false
  }
}

const deleteWord = async (w) => {
  if (!confirm(`确定从生词本中删除"${w.word}"吗？`)) return
  try {
    const res = await api.delete(`/word/custom/${w.user_word_id || w.id}`)
    if (res.code === 200) {
      toast.success('删除成功')
      loadList()
    }
  } catch (e) {
    toast.error('删除失败')
  }
}

onMounted(loadList)
</script>

<style scoped>
.summary-grid { margin-bottom: 24px; }
.stat-item {
  display: flex;
  align-items: center;
  gap: 14px;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.s1 .stat-icon { background: #ede9fe; }
.s2 .stat-icon { background: #fef3c7; }
.s3 .stat-icon { background: #dbeafe; }
.s4 .stat-icon { background: #d1fae5; }
.stat-num { font-size: 26px; font-weight: 800; }
.stat-lbl { font-size: 13px; color: var(--text-secondary); }

.word-list { display: flex; flex-direction: column; gap: 12px; }
.word-item {
  display: flex;
  justify-content: space-between;
  padding: 18px 20px;
  background: #f9fafb;
  border-radius: 12px;
  gap: 16px;
}
.word-main { flex: 1; min-width: 0; }
.word-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.word-name { font-size: 20px; font-weight: 700; }
.word-ipa { font-size: 13px; color: var(--text-secondary); }
.word-status {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 500;
}
.status-mastered { background: #d1fae5; color: #059669; }
.status-learning { background: #dbeafe; color: #2563eb; }
.status-new { background: #fef3c7; color: #d97706; }
.word-meaning { font-size: 15px; color: var(--text); margin-bottom: 8px; line-height: 1.6; }
.word-example {
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid var(--primary-light);
  margin-bottom: 10px;
}
.example-text { display: block; font-size: 13px; color: #1f2937; font-style: italic; margin-bottom: 4px; }
.example-trans { display: block; font-size: 12px; color: var(--text-secondary); }
.word-meta { display: flex; gap: 16px; flex-wrap: wrap; font-size: 12px; color: var(--text-secondary); }
.word-actions { display: flex; flex-direction: column; gap: 8px; flex-shrink: 0; align-items: flex-end; }
.btn-sm { padding: 6px 12px; font-size: 12px; }
.required { color: var(--danger); }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
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
