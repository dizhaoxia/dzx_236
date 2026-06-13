<template>
  <div class="container">
    <div class="page-header">
      <div>
        <h1 class="page-title">📚 词库管理</h1>
        <p class="page-subtitle">选择适合你的词库，开启高效学习之旅</p>
      </div>
      <div class="page-actions">
        <div class="search-box">
          <input v-model="searchWord" type="text" class="form-input" placeholder="🔍 搜索单词或释义..." @keyup.enter="doSearch" />
        </div>
      </div>
    </div>

    <div v-if="searchResults" class="card search-results-card">
      <div class="card-header">
        <h3 class="card-title">🔎 搜索结果（{{ searchResults.length }}）</h3>
        <button class="btn btn-outline" @click="searchResults = null">关闭</button>
      </div>
      <div v-if="!searchResults.length" class="empty" style="padding: 30px">
        <div class="empty-icon">🔍</div>
        <div class="empty-text">未找到匹配的单词</div>
      </div>
      <div v-else class="word-list compact">
        <div v-for="w in searchResults" :key="w.id" class="word-item compact">
          <div class="word-main">
            <div class="word-name">{{ w.word }} <span class="word-ipa">{{ w.phonetic }}</span></div>
            <div class="word-meaning">{{ w.meaning }}</div>
          </div>
          <div class="word-actions">
            <span v-if="w.status === 'mastered'" class="badge badge-success">已掌握</span>
            <span v-else-if="w.status === 'learning'" class="badge badge-primary">学习中</span>
            <span v-else class="badge badge-warning">新词</span>
            <button class="btn btn-outline btn-sm" @click="addToCustom(w)" title="加入生词本">➕</button>
          </div>
        </div>
      </div>
    </div>

    <div class="section-title">🎯 预设词库</div>
    <div v-if="!books.preset?.length" class="card">
      <div class="empty"><div class="empty-icon">📭</div><div class="empty-text">暂无预设词库</div></div>
    </div>
    <div class="grid grid-3">
      <div v-for="b in books.preset || []" :key="b.id" class="card vocab-card">
        <div class="vocab-header">
          <div class="vocab-icon preset">🎓</div>
          <div class="vocab-info">
            <div class="vocab-name">{{ b.name }}</div>
            <div class="vocab-desc">{{ b.description }}</div>
          </div>
        </div>
        <div class="vocab-stats">
          <div><span class="num">{{ b.word_count }}</span>词汇量</div>
          <div><span class="num">{{ b.learned_count }}</span>已学</div>
          <div><span class="num">{{ b.word_count ? Math.round(b.learned_count / b.word_count * 100) : 0 }}%</span>进度</div>
        </div>
        <div class="vocab-footer">
          <button
            class="btn btn-block"
            :class="b.is_active ? 'btn-primary' : 'btn-outline'"
            @click="toggleBook(b)"
          >
            {{ b.is_active ? '✅ 已启用（点击停用）' : '⚡ 启用此词库' }}
          </button>
          <router-link :to="`/vocab/${b.id}`" class="btn btn-outline btn-block" style="margin-top: 8px">
            查看词汇
          </router-link>
        </div>
      </div>
    </div>

    <div class="section-title" style="margin-top: 32px">⭐ 我的自定义词库</div>
    <div class="section-actions">
      <button class="btn btn-primary" @click="showCreateModal = true">
        ➕ 新建词库
      </button>
    </div>
    <div v-if="!books.custom?.length" class="card">
      <div class="empty"><div class="empty-icon">📝</div><div class="empty-text">还没有自定义词库</div><div class="empty-subtext">点击上方按钮创建专属词库</div></div>
    </div>
    <div v-else class="grid grid-3">
      <div v-for="b in books.custom || []" :key="b.id" class="card vocab-card custom">
        <div class="vocab-header">
          <div class="vocab-icon custom">✨</div>
          <div class="vocab-info">
            <div class="vocab-name">{{ b.name }}</div>
            <div class="vocab-desc">{{ b.description }}</div>
          </div>
        </div>
        <div class="vocab-stats">
          <div><span class="num">{{ b.word_count }}</span>词汇量</div>
          <div><span class="num">{{ b.learned_count }}</span>已学</div>
          <div>
            <button class="del-btn" @click="deleteBook(b)" title="删除">🗑️</button>
          </div>
        </div>
        <div class="vocab-footer">
          <button
            class="btn btn-block"
            :class="b.is_active ? 'btn-primary' : 'btn-outline'"
            @click="toggleBook(b)"
          >
            {{ b.is_active ? '✅ 已启用' : '⚡ 启用' }}
          </button>
          <router-link :to="`/vocab/${b.id}`" class="btn btn-outline btn-block" style="margin-top: 8px">
            查看词汇
          </router-link>
        </div>
      </div>
    </div>

    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">新建自定义词库</div>
          <button class="modal-close" @click="showCreateModal = false">×</button>
        </div>
        <div class="form-group">
          <label class="form-label">词库名称</label>
          <input v-model="newBook.name" type="text" class="form-input" placeholder="例如：我的高频词" />
        </div>
        <div class="form-group">
          <label class="form-label">词库描述</label>
          <textarea v-model="newBook.desc" class="form-input" rows="3" placeholder="简单描述一下这个词库..."></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showCreateModal = false">取消</button>
          <button class="btn btn-primary" @click="createBook" :disabled="creating">
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToastStore } from '@/stores/toast'
import api from '@/utils/api'

const toast = useToastStore()
const books = reactive({ preset: [], custom: [] })
const searchWord = ref('')
const searchResults = ref(null)
const showCreateModal = ref(false)
const newBook = reactive({ name: '', desc: '' })
const creating = ref(false)

const loadBooks = async () => {
  try {
    const res = await api.get('/vocab/list')
    if (res.code === 200) {
      books.preset = res.data.preset || []
      books.custom = res.data.custom || []
    }
  } catch (e) {
    toast.error('加载词库失败')
  }
}

const toggleBook = async (b) => {
  try {
    const res = await api.post(`/vocab/${b.id}/activate`, { active: !b.is_active })
    if (res.code === 200) {
      b.is_active = res.data.is_active
      toast.success(b.is_active ? '已启用词库' : '已停用词库')
    }
  } catch (e) {
    toast.error('操作失败')
  }
}

const createBook = async () => {
  if (!newBook.name.trim()) {
    toast.warning('请输入词库名称')
    return
  }
  creating.value = true
  try {
    const res = await api.post('/vocab/custom', { name: newBook.name, description: newBook.desc })
    if (res.code === 200) {
      toast.success('创建成功')
      showCreateModal.value = false
      newBook.name = ''
      newBook.desc = ''
      loadBooks()
    } else {
      toast.error(res.message || '创建失败')
    }
  } catch (e) {
    toast.error('创建失败')
  } finally {
    creating.value = false
  }
}

const deleteBook = async (b) => {
  if (!confirm(`确定删除词库"${b.name}"吗？`)) return
  try {
    const res = await api.delete(`/vocab/${b.id}`)
    if (res.code === 200) {
      toast.success('删除成功')
      loadBooks()
    }
  } catch (e) {
    toast.error('删除失败')
  }
}

const doSearch = async () => {
  if (!searchWord.value.trim()) return
  try {
    const res = await api.get(`/word/search?keyword=${encodeURIComponent(searchWord.value)}`)
    if (res.code === 200) {
      searchResults.value = res.data
    }
  } catch (e) {
    toast.error('搜索失败')
  }
}

const addToCustom = async (w) => {
  try {
    const res = await api.post('/word/add-custom', { word: w.word, meaning: w.meaning, phonetic: w.phonetic, example: w.example, example_trans: w.example_trans })
    if (res.code === 200) {
      toast.success('已加入生词本')
    } else {
      toast.warning(res.message || '添加失败')
    }
  } catch (e) {
    toast.error(e?.message || '添加失败')
  }
}

onMounted(loadBooks)
</script>

<style scoped>
.search-box { width: 280px; }
.section-title { font-size: 18px; font-weight: 700; margin: 0 0 16px; color: var(--text); }
.section-actions { margin-bottom: 16px; }
.vocab-card { transition: transform 0.2s, box-shadow 0.2s; }
.vocab-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.vocab-header { display: flex; gap: 14px; align-items: flex-start; margin-bottom: 16px; }
.vocab-icon {
  width: 48px; height: 48px; border-radius: 12px; display: flex;
  align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0;
}
.vocab-icon.preset { background: linear-gradient(135deg, #667eea, #764ba2); }
.vocab-icon.custom { background: linear-gradient(135deg, #f093fb, #f5576c); }
.vocab-info { flex: 1; }
.vocab-name { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.vocab-desc { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
.vocab-stats {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;
  padding: 14px 0; margin-bottom: 16px; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
  text-align: center;
}
.vocab-stats > div { font-size: 12px; color: var(--text-secondary); }
.vocab-stats .num { display: block; font-size: 18px; font-weight: 700; color: var(--text); margin-bottom: 2px; }
.del-btn { background: none; border: none; font-size: 18px; cursor: pointer; padding: 4px; border-radius: 6px; }
.del-btn:hover { background: #fee2e2; }
.btn-sm { padding: 6px 10px; font-size: 12px; }
.search-results-card { margin-bottom: 24px; }
.word-list.compact { display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto; }
.word-item.compact {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 14px; background: #f9fafb; border-radius: 10px; gap: 12px;
}
.word-main { flex: 1; min-width: 0; }
.word-name { font-size: 16px; font-weight: 700; margin-bottom: 2px; }
.word-ipa { font-size: 13px; font-weight: 400; color: var(--text-secondary); margin-left: 6px; }
.word-meaning { font-size: 13px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.word-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
</style>
