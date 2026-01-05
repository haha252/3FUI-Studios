<script setup>
import { ref, onMounted, computed, reactive, watch } from 'vue'
import { MagnifyingGlassIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/vue/24/outline'

// State
const loading = ref(true)
const projects = ref([]) // Stores all.json (minimal data)
const initialPageData = ref([]) // Stores pages/1.json for New Releases
const allProjectsLoaded = ref(false)
const searchQuery = ref('')
const searchType = ref('title') // 'title' or 'author'
const activeFilters = reactive({
  '发布者': [],
  '规格': [],
  '编码': [],
  '处理': [],
  '下载源': []
})

// Tag Data (Fetched from tags.json)
const tagMap = ref({}) // tag_name -> filename

// Tag Categories (Fetching from tags.json is better, but hardcoded fallback is ok)
const tagCategories = ref([
    { name: "发布者", tags: ["3FUI 核心成员", "普通成员"] },
    { name: "规格", tags: ["2160p", "1440p", "1080p", "720p", "其他分辨率", "高帧率"] },
    { name: "编码", tags: ["H.266/VVC", "AV1", "H.265/HEVC", "H.264/AVC"] },
    { name: "处理", tags: ["直接压制", "滤镜", "AI", "视频帧服务器", "后期制作"] },
    { name: "下载源", tags: ["磁力", "百度云", "蓝奏云", "123网盘", "夸克", "直链"] }
])

// Cache for fetched tag results
const tagResultsCache = reactive({}) // filename -> list of items

// Cache for fetched details
const detailsCache = reactive({}) // id -> detail object

// Fetch Initial Data
onMounted(async () => {
  try {
    // Parallel fetch: pages/1.json (for New Releases) and tags.json
    const [resPage1, resTags] = await Promise.all([
      fetch('/api/pages/1.json'),
      fetch('/api/tags.json')
    ])

    if (resPage1.ok) {
      const pageData = await resPage1.json()
      initialPageData.value = pageData.items || []
    } else {
      console.error('Failed to load pages/1.json')
    }

    if (resTags.ok) {
      const tagsData = await resTags.json()
      tagMap.value = tagsData.map
      if (tagsData.categories) {
        tagCategories.value = tagsData.categories
        // Ensure activeFilters has keys for all categories
        tagsData.categories.forEach(cat => {
            if (!(cat.name in activeFilters)) {
                activeFilters[cat.name] = []
            }
        })
      }
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

// Helper: Fetch tag items
const fetchTagItems = async (tagName) => {
  // Try to find the filename from the map
  let filename = tagMap.value[tagName]
  
  // If not found in map, try to use the tagName directly (handling special chars if needed)
  if (!filename) {
      // Fallback: This might fail if the filename is hashed, but works for simple names
      // In the python script, safe_filename replaces special chars with _. 
      // We should ideally rely on tagMap. If tagMap is empty/not loaded, that's the issue.
      console.warn(`Tag ${tagName} not found in tagMap`, tagMap.value)
      return []
  }

  // Ensure filename ends with .json
  if (!filename.endsWith('.json')) {
      filename += '.json'
  }
  
  if (tagResultsCache[filename]) {
    return tagResultsCache[filename]
  }

  try {
    // Need to encode filename because it might contain spaces or special chars (though safe_filename handles most)
    // Actually, filename from map should be used directly as path segment.
    const res = await fetch(`/api/tags/${filename}`)
    if (res.ok) {
      const items = await res.json()
      // Note: items is { tag: "...", count: N, items: [...] }
      const actualItems = items.items || []
      tagResultsCache[filename] = actualItems
      return actualItems
    } else {
        console.error(`Failed to fetch tag file: ${filename}, status: ${res.status}`)
    }
  } catch (e) {
    console.error(`Failed to fetch tag: ${tagName}`, e)
  }
  return []
}

// Current Filtered Items
const displayProjects = ref([])
const isFiltering = ref(false)

// Logic:
// 1. If Filters -> Fetch tag files, Intersect.
// 2. If Search -> Filter results (from step 1 or all.json).
// 3. Result items: Prefer items with tags (from tag files) over bare items (from all.json).

watch([searchQuery, searchType, activeFilters, projects], async () => {
  isFiltering.value = true
  try {
    let candidates = []
    
    // 1. Check if any filters are active
    const activeCategories = Object.keys(activeFilters).filter(cat => activeFilters[cat].length > 0)
    
    if (activeCategories.length > 0) {
      // Need to fetch tag files
      // We will perform an INTERSECTION of all selected tags.
      // E.g. (TagA OR TagB) AND (TagC) ?
      // Usually: Union within category, Intersection across categories.
      // Let's implement: Union within category, Intersection across categories.
      
      let categoryResults = [] // Array of Sets of IDs or Arrays of Items
      
      for (const cat of activeCategories) {
        const tags = activeFilters[cat]
        // Fetch all tags in this category
        const tagPromises = tags.map(t => fetchTagItems(t))
        const tagFilesData = await Promise.all(tagPromises)
        
        // Union within category
        const catItemsMap = new Map()
        for (const items of tagFilesData) {
          for (const item of items) {
            catItemsMap.set(item.id, item) // Store item with tags
          }
        }
        categoryResults.push(catItemsMap)
      }
      
      // Intersection across categories
      if (categoryResults.length > 0) {
        // Start with the first category's items
        const firstMap = categoryResults[0]
        let resultIds = new Set(firstMap.keys())
        
        for (let i = 1; i < categoryResults.length; i++) {
          const nextMap = categoryResults[i]
          const nextIds = new Set(nextMap.keys())
          // Intersect IDs
          resultIds = new Set([...resultIds].filter(id => nextIds.has(id)))
        }
        
        // Collect items based on intersected IDs
        // We can grab the item object from any map that has it.
        // firstMap is guaranteed to have the ID if it's in resultIds (since resultIds is subset of firstMap)
        candidates = [...resultIds].map(id => firstMap.get(id))
      } else {
        candidates = []
      }
      
    } else {
      // No filters, start with all projects (minimal info, no tags)
      candidates = projects.value
    }

    // 2. Text Search
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      candidates = candidates.filter(p => {
        if (searchType.value === 'author') {
          return p.meta?.author?.toLowerCase().includes(q)
        } else {
          return p.basic?.title?.toLowerCase().includes(q)
        }
      })
    }
    
    // 如果没有任何搜索条件（无 Filter 且无 Search Query），则不显示任何结果
    if (activeCategories.length === 0 && !searchQuery.value) {
        candidates = []
    }
    
    // Sort by ID desc (assuming ID correlates with date/order)
    // projects.value is already sorted. Tag files are sorted. 
    // But intersection might lose order.
    candidates.sort((a, b) => {
        // string comparison for IDs like "2026/01/..."
        if (a.id < b.id) return 1;
        if (a.id > b.id) return -1;
        return 0;
    })

    displayProjects.value = candidates
  } catch (e) {
    console.error("Filtering error", e)
  } finally {
    isFiltering.value = false
  }
}, { immediate: true, deep: true })


// Pagination
const currentPage = ref(1)
const itemsPerPage = 10
const totalPages = computed(() => Math.ceil(displayProjects.value.length / itemsPerPage))
const paginatedProjects = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return displayProjects.value.slice(start, start + itemsPerPage)
})

const changePage = (p) => {
  if (p >= 1 && p <= totalPages.value) {
    currentPage.value = p
  }
}

const toggleFilter = (category, tag) => {
  const current = activeFilters[category]
  const idx = current.indexOf(tag)
  if (idx === -1) {
    current.push(tag)
  } else {
    current.splice(idx, 1)
  }
  currentPage.value = 1
}

// New Releases (Just top 10 from initial page data)
const newReleases = computed(() => {
  return initialPageData.value.slice(0, 10)
})

// Expansion Logic with Lazy Loading
const expandedRows = ref(new Set())
const loadingDetails = ref(new Set()) // Track which IDs are loading

const fetchDetail = async (id) => {
  if (detailsCache[id]) return detailsCache[id]
  
  // loadingDetails.value.add(id) // Optional UI indication
  try {
    const res = await fetch(`/api/details/${id}.json`)
    if (res.ok) {
      const data = await res.json()
      detailsCache[id] = data
      return data
    }
  } catch (e) {
    console.error(`Failed to load detail for ${id}`, e)
  } finally {
    // loadingDetails.value.delete(id)
  }
  return null
}

const toggleExpand = async (id) => {
  if (expandedRows.value.has(id)) {
    expandedRows.value.delete(id)
  } else {
    expandedRows.value.add(id)
    // Fetch detail if missing
    if (!detailsCache[id]) {
        await fetchDetail(id)
    }
  }
}

const expandedNewReleases = ref(new Set())
const toggleExpandNewRelease = async (id) => {
  if (expandedNewReleases.value.has(id)) {
    expandedNewReleases.value.delete(id)
  } else {
    expandedNewReleases.value.add(id)
     if (!detailsCache[id]) {
        await fetchDetail(id)
    }
  }
}

// Helper to get description/download safely
const getDetail = (id) => {
  return detailsCache[id] || {}
}

</script>

<template>
  <div class="min-h-screen flex flex-col max-w-[1200px] mx-auto px-4 py-8">
    
    <!-- Header -->
    <header class="flex items-center gap-4 mb-8">
      <h1 class="text-3xl font-bold text-gray-100">3FUI Studios</h1>
      <span class="text-2xl text-gray-500">压片战争行动</span>
    </header>

    <!-- Intro -->
    <div class="mb-12 text-gray-400 text-sm leading-relaxed max-w-4xl">
      <p class="mb-2">
        3FUI Studios 是由 <a href="#" class="text-blue-400 hover:underline">FFmpegFreeUI</a> (3FUI) 开发者与核心技术支持成员发起的一个视频压制组项目，这个项目直接在 GitHub 上运行，我们不是专业压制组，我们的目标是在视觉无损的前提下压出最小的文件，仅做学习交流之用。我们欢迎所有 FFmpeg 用户加入项目分享你的成果。但是请注意：<span class="text-orange-500">我们拒绝所有版权受限和非法内容，这里不是自由发布影视资源的地方</span>。
      </p>
      <p>
        在发布内容之前，请先完整阅读：<a href="#" class="text-yellow-500 hover:underline">3FUI Studios 社区规则</a>
      </p>
    </div>

    <!-- Search Section -->
    <div class="flex flex-col items-center mb-16">
      <h2 class="text-2xl font-bold text-gray-100 mb-6 tracking-widest">搜索</h2>
      
      <!-- Search Input -->
      <div class="w-full max-w-2xl flex items-center bg-[#2a2a2a] border border-gray-600 rounded-none mb-8">
        <button 
          @click="searchType = 'author'"
          :class="['px-6 py-3 transition-colors border-r border-gray-600', searchType === 'author' ? 'text-gray-100 bg-gray-700' : 'text-gray-400 hover:text-gray-200']"
        >
          搜发布者
        </button>
        <input 
          v-model="searchQuery"
          type="text" 
          class="flex-1 bg-transparent border-none outline-none text-gray-200 px-4 py-3 placeholder-gray-500"
          :placeholder="searchType === 'author' ? '输入发布者名称...' : '输入标题...'"
        />
        <button 
          @click="searchType = 'title'"
          :class="['px-6 py-3 transition-colors border-l border-gray-600', searchType === 'title' ? 'text-gray-100 bg-gray-700' : 'text-gray-400 hover:text-gray-200']"
        >
          搜标题
        </button>
      </div>

      <!-- Filters -->
      <div class="w-full max-w-3xl space-y-3">
        <div v-for="cat in tagCategories" :key="cat.name" class="flex text-sm">
          <span class="text-gray-400 w-24 shrink-0">筛选{{ cat.name }}：</span>
          <div class="flex flex-wrap gap-x-4 gap-y-2">
            <button 
              v-for="tag in cat.tags" 
              :key="tag"
              @click="toggleFilter(cat.name, tag)"
              :class="['transition-colors', activeFilters[cat.name].includes(tag) ? 'text-blue-400 font-bold' : 'text-gray-400 hover:text-gray-200']"
            >
              {{ tag }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Results Section -->
    <div class="mb-16">
      <div class="bg-[#1e1e1e] rounded-sm overflow-hidden min-h-[200px]">
        <!-- Header -->
        <div class="bg-[#252525] px-6 py-4 flex justify-between items-center border-b border-[#333]">
          <span class="text-gray-400">搜索结果 ({{ displayProjects.length }})</span>
          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex gap-2 text-sm">
            <button 
              @click="changePage(currentPage - 1)" 
              :disabled="currentPage === 1"
              class="px-3 py-1 bg-[#333] hover:bg-[#444] disabled:opacity-50 disabled:cursor-not-allowed rounded text-gray-300"
            >
              上一页
            </button>
            <span class="px-2 py-1 text-gray-500">{{ currentPage }} / {{ totalPages }}</span>
            <button 
              @click="changePage(currentPage + 1)" 
              :disabled="currentPage === totalPages"
              class="px-3 py-1 bg-[#333] hover:bg-[#444] disabled:opacity-50 disabled:cursor-not-allowed rounded text-gray-300"
            >
              下一页
            </button>
          </div>
        </div>

        <!-- List -->
        <div v-if="paginatedProjects.length > 0">
          <div v-for="item in paginatedProjects" :key="item.id" class="border-b border-[#333] last:border-0">
            <!-- Row Header (Clickable) -->
            <div 
              @click="toggleExpand(item.id)"
              class="px-6 py-4 cursor-pointer hover:bg-[#252525] transition-colors flex items-center justify-between group"
            >
              <div class="flex flex-col gap-1">
                <div class="flex items-center gap-3">
                  <span class="text-gray-200 font-medium group-hover:text-blue-400 transition-colors">{{ item.basic.title }}</span>
                  <span v-for="tag in (item.basic.tags || []).slice(0, 3)" :key="tag" class="text-xs bg-[#333] text-gray-400 px-1.5 py-0.5 rounded">
                    {{ tag }}
                  </span>
                </div>
                <div class="text-xs text-gray-500 flex gap-4">
                  <span>发布者: {{ item.meta.author }}</span>
                  <span>ID: {{ item.id }}</span>
                </div>
              </div>
              <div>
                <ChevronDownIcon v-if="!expandedRows.has(item.id)" class="w-5 h-5 text-gray-500" />
                <ChevronUpIcon v-else class="w-5 h-5 text-gray-500" />
              </div>
            </div>

            <!-- Expanded Details -->
            <div v-if="expandedRows.has(item.id)" class="bg-[#1a1a1a] px-6 py-4 border-t border-[#333] text-sm text-gray-400">
              <div v-if="!detailsCache[item.id]" class="text-gray-500 py-2">Loading details...</div>
              <template v-else>
                  <div class="mb-4">
                    <p class="mb-2 text-gray-300 font-medium">简介/参数：</p>
                    <p class="whitespace-pre-wrap">{{ getDetail(item.id).basic?.description || '暂无描述' }}</p>
                  </div>
                  <div class="flex gap-4">
                    <a v-if="getDetail(item.id).download?.url" :href="getDetail(item.id).download.url" target="_blank" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded text-sm transition-colors">
                      立即下载
                    </a>
                    <a v-if="getDetail(item.id).source?.url" :href="getDetail(item.id).source.url" target="_blank" class="bg-[#333] hover:bg-[#444] text-gray-200 px-4 py-2 rounded text-sm transition-colors">
                      查看来源
                    </a>
                  </div>
              </template>
            </div>
          </div>
        </div>
        <div v-else class="p-8 text-center text-gray-500">
          {{ isSearchEmpty ? '请在上方输入关键词或选择标签进行搜索' : '没有找到匹配的项目' }}
        </div>
      </div>
    </div>

    <!-- New Releases Section -->
    <div class="mb-16">
      <div class="flex flex-col items-center mb-8">
        <h2 class="text-2xl font-bold text-gray-100 tracking-widest">新发布</h2>
      </div>

      <div class="bg-[#1e1e1e] rounded-sm overflow-hidden">
        <div class="bg-[#252525] px-6 py-4 border-b border-[#333]">
          <span class="text-gray-400">最新 10 个发布</span>
        </div>

        <div v-if="newReleases.length > 0">
          <div v-for="item in newReleases" :key="item.id" class="border-b border-[#333] last:border-0">
             <!-- Row Header (Clickable) -->
             <div 
              @click="toggleExpandNewRelease(item.id)"
              class="px-6 py-4 cursor-pointer hover:bg-[#252525] transition-colors flex items-center justify-between group"
            >
              <div class="flex flex-col gap-1">
                <div class="flex items-center gap-3">
                  <span class="text-gray-200 font-medium group-hover:text-blue-400 transition-colors">{{ item.basic.title }}</span>
                  <span class="bg-red-900/50 text-red-300 text-[10px] px-1.5 py-0.5 rounded border border-red-900">NEW</span>
                </div>
                <div class="text-xs text-gray-500">
                  {{ item.meta.author }}
                </div>
              </div>
              <div>
                <ChevronDownIcon v-if="!expandedNewReleases.has(item.id)" class="w-5 h-5 text-gray-500" />
                <ChevronUpIcon v-else class="w-5 h-5 text-gray-500" />
              </div>
            </div>

            <!-- Expanded Details -->
            <div v-if="expandedNewReleases.has(item.id)" class="bg-[#1a1a1a] px-6 py-4 border-t border-[#333] text-sm text-gray-400">
              <div v-if="!detailsCache[item.id]" class="text-gray-500 py-2">Loading details...</div>
              <template v-else>
                  <div class="mb-4">
                    <p class="whitespace-pre-wrap">{{ getDetail(item.id).basic?.description || '暂无描述' }}</p>
                  </div>
                  <div class="flex gap-4">
                    <a v-if="getDetail(item.id).download?.url" :href="getDetail(item.id).download.url" target="_blank" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded text-sm transition-colors">
                      下载
                    </a>
                  </div>
              </template>
            </div>
          </div>
        </div>
        <div v-else class="p-8 text-center text-gray-500">
          加载中...
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="text-center text-xs text-gray-600 pb-8 space-y-2">
      <p>投诉侵权请直接联系有管理权限的用户，我们会第一时间删除违规内容</p>
      <p>所有内容将被审核，如发现刻意隐藏、虚报信息等欺诈行为，我们将直接进行除名</p>
    </footer>

  </div>
</template>

<style scoped>
/* Add any component-specific styles here */
</style>
