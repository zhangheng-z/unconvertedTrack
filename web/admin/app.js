const metricsEl = document.querySelector('#metrics')
const preferenceGroupsEl = document.querySelector('#preferenceGroups')
const rankingRowsEl = document.querySelector('#rankingRows')
const contentRankingRowsEl = document.querySelector('#contentRankingRows')
const openContentRankingModalButton = document.querySelector('#openContentRankingModal')
const contentRankingModal = document.querySelector('#contentRankingModal')
const closeContentRankingModalButton = document.querySelector('#closeContentRankingModal')
const contentRankingModalRowsEl = document.querySelector('#contentRankingModalRows')
const contentRankingPaginationEl = document.querySelector('#contentRankingPagination')
const contentListEl = document.querySelector('#contentList')
const contentCountEl = document.querySelector('#contentCount')
const contentTitleFilter = document.querySelector('#contentTitleFilter')
const contentSubjectFilter = document.querySelector('#contentSubjectFilter')
const contentGradeFilter = document.querySelector('#contentGradeFilter')
const contentFormatFilter = document.querySelector('#contentFormatFilter')
const clearContentFiltersButton = document.querySelector('#clearContentFilters')
const contentPaginationEl = document.querySelector('#contentPagination')
const taxonomyForm = document.querySelector('#taxonomyForm')
const taxonomyParentSelect = document.querySelector('#taxonomyParentSelect')
const taxonomyGroupsEl = document.querySelector('#taxonomyGroups')
const taxonomyActionModal = document.querySelector('#taxonomyActionModal')
const taxonomyActionForm = document.querySelector('#taxonomyActionForm')
const closeTaxonomyActionModalButton = document.querySelector('#closeTaxonomyActionModal')
const cancelTaxonomyActionModalButton = document.querySelector('#cancelTaxonomyActionModal')
const taxonomyActionTitle = document.querySelector('#taxonomyActionTitle')
const taxonomyActionHint = document.querySelector('#taxonomyActionHint')
const taxonomyActionLabelField = document.querySelector('#taxonomyActionLabelField')
const taxonomyConfirmText = document.querySelector('#taxonomyConfirmText')
const taxonomyActionMessage = document.querySelector('#taxonomyActionMessage')
const submitTaxonomyActionModalButton = document.querySelector('#submitTaxonomyActionModal')
const reviewListEl = document.querySelector('#reviewList')
const reviewCountEl = document.querySelector('#reviewCount')
const refreshButton = document.querySelector('#refreshButton')
const form = document.querySelector('#contentForm')
const formMessage = document.querySelector('#formMessage')
const generatedTitle = document.querySelector('#generatedTitle')
const generatedTags = document.querySelector('#generatedTags')
const generatedOutline = document.querySelector('#generatedOutline')
const generatedPdfLink = document.querySelector('#generatedPdfLink')
const generatedSource = document.querySelector('#generatedSource')
const generatedTokenUsage = document.querySelector('#generatedTokenUsage')
const generatedSteps = document.querySelector('#generatedSteps')
const resultPanel = document.querySelector('#resultPanel')
const resultEmptyState = document.querySelector('#resultEmptyState')
const resultGeneratedContent = document.querySelector('#resultGeneratedContent')
const generatedStatus = document.querySelector('#generatedStatus')
const viewGeneratedContentButton = document.querySelector('#viewGeneratedContent')
const publishGeneratedContentButton = document.querySelector('#publishGeneratedContent')
const pageTitle = document.querySelector('#pageTitle')
const datePreset = document.querySelector('#datePreset')
const startDateInput = document.querySelector('#startDate')
const endDateInput = document.querySelector('#endDate')
const priorityTopicEl = document.querySelector('#priorityTopic')
const priorityReasonEl = document.querySelector('#priorityReason')
const productionTipsEl = document.querySelector('#productionTips')
const topicPreferencesEl = document.querySelector('#topicPreferences')
const topicContentRatesEl = document.querySelector('#topicContentRates')
const topicSuggestionsEl = document.querySelector('#topicSuggestions')
const generateTopicSuggestionsButton = document.querySelector('#generateTopicSuggestions')
const topicGenerationMessage = document.querySelector('#topicGenerationMessage')
const openTopicSuggestionModalButton = document.querySelector('#openTopicSuggestionModal')
const topicSuggestionModal = document.querySelector('#topicSuggestionModal')
const topicSuggestionForm = document.querySelector('#topicSuggestionForm')
const topicSuggestionModalTitle = document.querySelector('#topicSuggestionModalTitle')
const topicSuggestionFormMessage = document.querySelector('#topicSuggestionFormMessage')
const closeTopicSuggestionModalButton = document.querySelector('#closeTopicSuggestionModal')
const cancelTopicSuggestionModalButton = document.querySelector('#cancelTopicSuggestionModal')
const topicDeleteModal = document.querySelector('#topicDeleteModal')
const topicDeleteTitle = document.querySelector('#topicDeleteTitle')
const topicDeleteMessage = document.querySelector('#topicDeleteMessage')
const closeTopicDeleteModalButton = document.querySelector('#closeTopicDeleteModal')
const cancelTopicDeleteModalButton = document.querySelector('#cancelTopicDeleteModal')
const confirmTopicDeleteButton = document.querySelector('#confirmTopicDelete')
const generatorSelectedProblemTagsEl = document.querySelector('#generatorSelectedProblemTags')
const generatorProblemTagInputsEl = document.querySelector('#generatorProblemTagInputs')
const openGeneratorProblemTagPickerButton = document.querySelector('#openGeneratorProblemTagPicker')
const topicSelectedProblemTagsEl = document.querySelector('#topicSelectedProblemTags')
const topicProblemTagInputsEl = document.querySelector('#topicProblemTagInputs')
const openTopicProblemTagPickerButton = document.querySelector('#openTopicProblemTagPicker')
const funnelStepsEl = document.querySelector('#funnelSteps')
const opportunityListEl = document.querySelector('#opportunityList')
const activityListEl = document.querySelector('#activityList')
const followUserAvatarEl = document.querySelector('#followUserAvatar')
const followUserNameEl = document.querySelector('#followUserName')
const followUserProfileEl = document.querySelector('#followUserProfile')
const followIntentTagsEl = document.querySelector('#followIntentTags')
const followTagsEl = document.querySelector('#followTags')
const followActionEl = document.querySelector('#followAction')
const followAdviceEl = document.querySelector('#followAdvice')
const followLastActiveEl = document.querySelector('#followLastActive')
const viewFollowUserDetailButton = document.querySelector('#viewFollowUserDetail')
const insightTitleEl = document.querySelector('#insightTitle')
const insightListEl = document.querySelector('#insightList')
const followRankingEl = document.querySelector('#followRanking')
const userRowsEl = document.querySelector('#userRows')
const registeredUserCountEl = document.querySelector('#registeredUserCount')
const userPaginationEl = document.querySelector('#userPagination')
const openContentModalButton = document.querySelector('#openContentModal')
const contentModal = document.querySelector('#contentModal')
const uploadContentForm = document.querySelector('#uploadContentForm')
const selectedProblemTagsEl = document.querySelector('#selectedProblemTags')
const problemTagInputsEl = document.querySelector('#problemTagInputs')
const openProblemTagPickerButton = document.querySelector('#openProblemTagPicker')
const problemTagModal = document.querySelector('#problemTagModal')
const problemTagOptionsEl = document.querySelector('#problemTagOptions')
const closeProblemTagModalButton = document.querySelector('#closeProblemTagModal')
const cancelProblemTagPickerButton = document.querySelector('#cancelProblemTagPicker')
const applyProblemTagPickerButton = document.querySelector('#applyProblemTagPicker')
const closeContentModalButton = document.querySelector('#closeContentModal')
const cancelContentModalButton = document.querySelector('#cancelContentModal')
const contentModalTitle = document.querySelector('#contentModalTitle')
const uploadContentMessage = document.querySelector('#uploadContentMessage')
const aiLogRowsEl = document.querySelector('#aiLogRows')
const aiLogCountEl = document.querySelector('#aiLogCount')
const aiLogRequestIdInput = document.querySelector('#aiLogRequestId')
const aiLogStatusInput = document.querySelector('#aiLogStatus')
const aiLogSearchButton = document.querySelector('#aiLogSearchButton')
const aiLogModal = document.querySelector('#aiLogModal')
const closeAiLogModalButton = document.querySelector('#closeAiLogModal')
const aiLogModalTitle = document.querySelector('#aiLogModalTitle')
const aiLogModalMeta = document.querySelector('#aiLogModalMeta')
const aiLogPromptText = document.querySelector('#aiLogPromptText')
const aiLogResponseText = document.querySelector('#aiLogResponseText')

const state = {
  dashboard: null,
  preferences: null,
  topicContext: null,
  contents: [],
  reviewContents: [],
  suggestions: [],
  users: [],
  recommendedUsers: [],
  userTotal: 0,
  userPage: 1,
  aiLogs: [],
  taxonomyTags: [],
  taxonomyOptions: {
    subjects: [],
    grades: [],
    problems: [],
    problem_categories: []
  },
  taxonomyActiveType: 'problem',
  taxonomyActiveProblemCategoryId: 'all',
  taxonomyPage: 1,
  contentFilters: {
    title: '',
    subject: '',
    grade: '',
    format: ''
  },
  contentPage: 1,
  contentRankingPage: 1,
  generatedPdf: null,
  selectedProblemTags: [],
  generatorSelectedProblemTags: [],
  topicSelectedProblemTags: [],
  problemTagPickerTarget: 'content',
  problemTagDraft: [],
  pendingTopicDeleteId: null
}

const CONTENT_PAGE_SIZE = 5
const CONTENT_RANKING_PAGE_SIZE = 5
const TAXONOMY_PAGE_SIZE = 15
const USER_PAGE_SIZE = 5

const metricConfig = [
  { key: 'new_users', label: '新增用户', icon: 'assets/icons/user-plus.svg' },
  { key: 'claimed', label: '资料领取', icon: 'assets/icons/file-check.svg' },
  { key: 'shared', label: '分享次数', icon: 'assets/icons/share.svg' },
  { key: 'downloaded', label: '测评完成', icon: 'assets/icons/assessment.svg' },
  { key: 'active_users', label: '训练营报名', icon: 'assets/icons/camp.svg' },
  { key: 'leads', label: '转化线索', icon: 'assets/icons/conversion.svg' }
]

const preferenceConfig = [
  { key: 'ages', label: '年龄', color: 'green', fallback: ['7岁', '一年级'] },
  { key: 'subjects', label: '学科', color: 'blue', fallback: ['语文', '数学', '专注力'] },
  { key: 'problems', label: '问题', color: 'orange', fallback: ['识字少', '阅读理解差', '计算慢', '应用题不会做'] },
  { key: 'content_types', label: '内容类型', color: 'purple', fallback: ['PDF', '图片', '测评'] }
]

const DEFAULT_TAXONOMY_OPTIONS = {
  subjects: ['语文', '数学', '英语', '编程'],
  grades: ['幼小衔接', '一年级', '二年级', '三年级', '四年级', '五年级', '六年级', '小升初'],
  problems: ['识字少', '阅读理解差', '计算慢', '应用题不会做', '作业拖拉', '注意力不集中', '粗心马虎', '幼小衔接']
}

const taxonomyTypeLabels = {
  subject: '学科',
  grade: '年级',
  problem_category: '问题分类',
  problem: '问题'
}

const titleMap = {
  dashboard: '数据看板',
  users: '用户画像',
  contents: '内容管理',
  topics: 'AI选题推荐',
  ai: 'AI内容生成',
  aiLogs: 'AI调用日志',
  review: '素材审核',
  report: '效果复盘',
  leads: '线索管理'
}

async function request(url, options = {}) {
  const response = await fetch(url, options)
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || '请求失败')
  }
  if (response.status === 204) return null
  const text = await response.text()
  if (!text) return null
  return JSON.parse(text)
}

function formatDateInput(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function parseDateInput(value) {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function addDays(date, days) {
  const next = new Date(date)
  next.setDate(next.getDate() + days)
  return next
}

function initDateRange() {
  const today = new Date()
  datePreset.value = '7'
  endDateInput.value = formatDateInput(today)
  startDateInput.value = formatDateInput(addDays(today, -6))
}

function setPresetRange(preset) {
  const today = new Date()
  if (preset === 'today') {
    startDateInput.value = formatDateInput(today)
    endDateInput.value = formatDateInput(today)
  } else if (preset === '30') {
    startDateInput.value = formatDateInput(addDays(today, -29))
    endDateInput.value = formatDateInput(today)
  } else if (preset === 'month') {
    startDateInput.value = formatDateInput(new Date(today.getFullYear(), today.getMonth(), 1))
    endDateInput.value = formatDateInput(today)
  } else if (preset === '7') {
    startDateInput.value = formatDateInput(addDays(today, -6))
    endDateInput.value = formatDateInput(today)
  }
}

function selectedRangeParams() {
  const params = new URLSearchParams()
  if (startDateInput.value) params.set('start_date', startDateInput.value)
  if (endDateInput.value) params.set('end_date', endDateInput.value)
  return params
}

function adminUrl(path, extraParams = {}) {
  const params = selectedRangeParams()
  Object.entries(extraParams).forEach(([key, value]) => {
    if (value !== undefined && value !== null) params.set(key, value)
  })
  const query = params.toString()
  return query ? `${path}?${query}` : path
}

function rangeLabel() {
  if (!startDateInput.value || !endDateInput.value) return '当前时间范围'
  const start = parseDateInput(startDateInput.value)
  const end = parseDateInput(endDateInput.value)
  const days = Math.max(1, Math.round((end - start) / 86400000) + 1)
  if (days === 1) return '今日'
  if (days === 7) return '近7天'
  if (days === 30) return '近30天'
  return `${days}天内`
}

function compareLabel() {
  if (datePreset.value === 'today') return '较昨日'
  if (datePreset.value === '7') return '较上周'
  if (datePreset.value === '30' || datePreset.value === 'month') return '较上月'
  return '较上一周期'
}

function metricChangeMarkup(metricKey) {
  const change = state.dashboard?.changes?.[metricKey]
  if (!change) return `<small class="flat">${compareLabel()} 0%</small>`
  const direction = change.direction || 'flat'
  const symbol = direction === 'up' ? '▲' : direction === 'down' ? '▼' : '■'
  const percent = Math.abs(Number(change.percent || 0)).toFixed(1).replace(/\.0$/, '')
  return `<small class="${escapeHtml(direction)}">${compareLabel()} ${symbol} ${percent}%</small>`
}

function taxonomyOptions(key) {
  const values = state.taxonomyOptions[key]?.length
    ? state.taxonomyOptions[key]
    : DEFAULT_TAXONOMY_OPTIONS[key]
  return [...new Set(values || [])]
}

function selectOptionsMarkup(key, placeholder, value = '') {
  if (key === 'problems') return problemOptionsMarkup(placeholder, value)
  const selectedValue = readableText(value)
  const options = taxonomyOptions(key)
  const known = options.includes(selectedValue)
  const rows = options
    .map((item) => `<option value="${escapeHtml(item)}" ${item === selectedValue ? 'selected' : ''}>${escapeHtml(item)}</option>`)
    .join('')
  const legacy = selectedValue && !known
    ? `<option value="${escapeHtml(selectedValue)}" selected>${escapeHtml(selectedValue)}（历史值）</option>`
    : ''
  return `<option value="">${escapeHtml(placeholder)}</option>${rows}${legacy}`
}

function problemOptionsMarkup(placeholder, value = '') {
  const selectedValues = Array.isArray(value) ? value.map(readableText).filter(Boolean) : [readableText(value)].filter(Boolean)
  const flatOptions = taxonomyOptions('problems')
  const categorized = new Set()
  const categoryRows = (state.taxonomyOptions.problem_categories || [])
    .filter((category) => category.problems?.length)
    .map((category) => {
      const options = category.problems
        .map((problem) => {
          categorized.add(problem)
          return `<option value="${escapeHtml(problem)}" ${selectedValues.includes(problem) ? 'selected' : ''}>${escapeHtml(problem)}</option>`
        })
        .join('')
      return `<optgroup label="${escapeHtml(category.label)}">${options}</optgroup>`
    })
    .join('')
  const otherRows = flatOptions
    .filter((problem) => !categorized.has(problem))
    .map((problem) => `<option value="${escapeHtml(problem)}" ${selectedValues.includes(problem) ? 'selected' : ''}>${escapeHtml(problem)}</option>`)
    .join('')
  const otherGroup = otherRows ? `<optgroup label="其他">${otherRows}</optgroup>` : ''
  const legacy = selectedValues
    .filter((selectedValue) => !flatOptions.includes(selectedValue))
    .map((selectedValue) => `<option value="${escapeHtml(selectedValue)}" selected>${escapeHtml(selectedValue)}（历史值）</option>`)
    .join('')
  return `<option value="">${escapeHtml(placeholder)}</option>${categoryRows}${otherGroup}${legacy}`
}

function populateTaxonomySelects() {
  document.querySelectorAll('[data-subject-select]').forEach((select) => {
    select.innerHTML = selectOptionsMarkup('subjects', '请选择学科', select.value)
  })
  document.querySelectorAll('[data-grade-select]').forEach((select) => {
    select.innerHTML = selectOptionsMarkup('grades', '请选择年级', select.value)
  })
  document.querySelectorAll('[data-problem-select]').forEach((select) => {
    select.innerHTML = selectOptionsMarkup('problems', '请选择问题', selectedValues(select))
  })
}

function setTaxonomySelectValue(select, key, placeholder, value = '') {
  if (!select) return
  select.innerHTML = selectOptionsMarkup(key, placeholder, value)
  if (select.multiple) {
    const values = Array.isArray(value) ? value : [value].filter(Boolean)
    Array.from(select.options).forEach((option) => {
      option.selected = values.includes(option.value)
    })
    return
  }
  select.value = value || ''
}

function selectedValues(select) {
  if (!select) return []
  if (!select.multiple) return select.value ? [select.value] : []
  return Array.from(select.selectedOptions).map((option) => option.value).filter(Boolean)
}

function contentProblemTags(item) {
  const values = Array.isArray(item?.problem_tags) ? item.problem_tags.filter(Boolean) : []
  if (!values.length && item?.problem) values.push(item.problem)
  return [...new Set(values)]
}

function contentProblemLabel(item) {
  const values = contentProblemTags(item)
  return values.length ? values.join('、') : '-'
}

function setSelectedProblemTags(values, target = 'content') {
  const normalized = [...new Set((values || []).map(readableText).filter(Boolean))]
  if (target === 'topic') {
    state.topicSelectedProblemTags = normalized
    renderTopicSelectedProblemTags()
    return
  }
  if (target === 'generator') {
    state.generatorSelectedProblemTags = normalized
    renderGeneratorSelectedProblemTags()
    return
  }
  state.selectedProblemTags = normalized
  renderSelectedProblemTags()
}

function renderSelectedProblemTags() {
  if (!selectedProblemTagsEl || !problemTagInputsEl) return
  const values = state.selectedProblemTags
  selectedProblemTagsEl.innerHTML = values.length
    ? values.map((tag) => `
      <span class="problem-tag-chip">
        ${escapeHtml(tag)}
        <button type="button" aria-label="移除${escapeHtml(tag)}" data-problem-tag-remove="${escapeHtml(tag)}">×</button>
      </span>
    `).join('')
    : '<span class="problem-tag-empty">点击 + 选择问题标签</span>'
  problemTagInputsEl.innerHTML = values
    .map((tag) => `<input type="hidden" name="problem_tags" value="${escapeHtml(tag)}" />`)
    .join('')
}

function renderTopicSelectedProblemTags() {
  if (!topicSelectedProblemTagsEl || !topicProblemTagInputsEl) return
  const values = state.topicSelectedProblemTags
  topicSelectedProblemTagsEl.innerHTML = values.length
    ? values.map((tag) => `
      <span class="problem-tag-chip">
        ${escapeHtml(tag)}
        <button type="button" aria-label="移除${escapeHtml(tag)}" data-topic-problem-tag-remove="${escapeHtml(tag)}">×</button>
      </span>
    `).join('')
    : '<span class="problem-tag-empty">点击 + 选择问题标签</span>'
  topicProblemTagInputsEl.innerHTML = values
    .map((tag) => `<input type="hidden" name="problem_tags" value="${escapeHtml(tag)}" />`)
    .join('')
}

function renderGeneratorSelectedProblemTags() {
  if (!generatorSelectedProblemTagsEl || !generatorProblemTagInputsEl) return
  const values = state.generatorSelectedProblemTags
  generatorSelectedProblemTagsEl.innerHTML = values.length
    ? values.map((tag) => `
      <span class="problem-tag-chip">
        ${escapeHtml(tag)}
        <button type="button" aria-label="移除${escapeHtml(tag)}" data-generator-problem-tag-remove="${escapeHtml(tag)}">×</button>
      </span>
    `).join('')
    : '<span class="problem-tag-empty">点击 + 选择问题标签</span>'
  generatorProblemTagInputsEl.innerHTML = `
    <input type="hidden" name="problem" value="${escapeHtml(values[0] || '')}" />
    ${values.map((tag) => `<input type="hidden" name="problem_tags" value="${escapeHtml(tag)}" />`).join('')}
  `
}

function groupedProblemOptions() {
  const categorized = new Set()
  const groups = (state.taxonomyOptions.problem_categories || [])
    .filter((category) => category.problems?.length)
    .map((category) => {
      const problems = category.problems.map(readableText).filter(Boolean)
      problems.forEach((problem) => categorized.add(problem))
      return { label: category.label, problems }
    })
    .filter((group) => group.problems.length)
  const others = taxonomyOptions('problems').map(readableText).filter(Boolean).filter((problem) => !categorized.has(problem))
  if (others.length) groups.push({ label: '其他', problems: others })
  return groups
}

function renderProblemTagOptions() {
  if (!problemTagOptionsEl) return
  const selected = new Set(state.problemTagDraft)
  const groups = groupedProblemOptions()
  problemTagOptionsEl.innerHTML = groups.length
    ? groups.map((group) => `
      <div class="problem-tag-group">
        <div class="problem-tag-group-title">${escapeHtml(group.label)}</div>
        <div class="problem-tag-choice-grid">
          ${group.problems.map((problem) => `
            <label class="problem-tag-choice">
              <input type="checkbox" value="${escapeHtml(problem)}" data-problem-tag-option ${selected.has(problem) ? 'checked' : ''} />
              <span>${escapeHtml(problem)}</span>
            </label>
          `).join('')}
        </div>
      </div>
    `).join('')
    : '<div class="empty-state">暂无可选问题标签</div>'
}

function openProblemTagModal(target = 'content') {
  if (!problemTagModal) return
  state.problemTagPickerTarget = target
  if (target === 'topic') {
    state.problemTagDraft = [...state.topicSelectedProblemTags]
  } else if (target === 'generator') {
    state.problemTagDraft = [...state.generatorSelectedProblemTags]
  } else {
    state.problemTagDraft = [...state.selectedProblemTags]
  }
  renderProblemTagOptions()
  problemTagModal.hidden = false
}

function closeProblemTagModal() {
  if (problemTagModal) problemTagModal.hidden = true
}

function activeProblemCategories() {
  return state.taxonomyTags
    .filter((tag) => tag.tag_type === 'problem_category' && tag.is_active)
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0) || a.id - b.id)
}

function populateTaxonomyParentSelect() {
  if (!taxonomyParentSelect || !taxonomyForm) return
  const isProblem = taxonomyForm.elements.tag_type.value === 'problem'
  taxonomyParentSelect.hidden = !isProblem
  taxonomyParentSelect.disabled = !isProblem
  if (!isProblem) {
    taxonomyParentSelect.innerHTML = ''
    return
  }
  const categories = activeProblemCategories()
  taxonomyParentSelect.innerHTML = categories
    .map((category) => `<option value="${category.id}">${escapeHtml(category.label)}</option>`)
    .join('')
}

function readableText(value) {
  const text = String(value ?? '')
  if (!/[ÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßà-ÿ]/.test(text)) return text

  try {
    const bytes = Uint8Array.from(Array.from(text).map((char) => char.charCodeAt(0)))
    return new TextDecoder('utf-8', { fatal: true }).decode(bytes)
  } catch {
    return text
  }
}

function escapeHtml(value) {
  return readableText(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

function formatNumber(value) {
  return Number(value ?? 0).toLocaleString('zh-CN')
}

function setActiveView(viewName, activeHash = `#${viewName}`) {
  const titleKey = activeHash.replace('#', '') || viewName
  document.querySelectorAll('.view').forEach((view) => {
    view.classList.toggle('is-active', view.dataset.view === viewName)
  })
  document.querySelectorAll('.nav-item[data-view-link]').forEach((link) => {
    link.classList.toggle('is-active', link.getAttribute('href') === activeHash)
  })
  pageTitle.textContent = titleMap[titleKey] || titleMap[viewName] || titleMap.dashboard
}

function bindNavigation() {
  document.querySelectorAll('[data-view-link]').forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault()
      const viewName = link.dataset.viewLink
      const hash = link.getAttribute('href') || `#${viewName}`
      if (viewName === 'ai') resetContentGenerationForm()
      window.history.replaceState(null, '', hash)
      setActiveView(viewName, hash)
    })
  })

  const initialHash = window.location.hash || '#dashboard'
  const initialLink = document.querySelector(`[data-view-link][href="${initialHash}"]`)
  if (initialLink) {
    setActiveView(initialLink.dataset.viewLink, initialHash)
  }
}

function bindDateFilters() {
  initDateRange()
  datePreset.addEventListener('change', () => {
    setPresetRange(datePreset.value)
    state.userPage = 1
    refreshAll()
  })
  ;[startDateInput, endDateInput].forEach((input) => {
    input.addEventListener('change', () => {
      if (startDateInput.value && endDateInput.value && startDateInput.value > endDateInput.value) {
        endDateInput.value = startDateInput.value
      }
      datePreset.value = 'custom'
      state.userPage = 1
      refreshAll()
    })
  })
}

function bindContentFilters() {
  if (!contentTitleFilter || !contentSubjectFilter || !contentGradeFilter || !contentFormatFilter) return

  contentTitleFilter.addEventListener('input', () => {
    state.contentFilters.title = contentTitleFilter.value
    state.contentPage = 1
    renderContents()
  })

  contentSubjectFilter.addEventListener('change', () => {
    state.contentFilters.subject = contentSubjectFilter.value
    state.contentPage = 1
    renderContents()
  })

  contentGradeFilter.addEventListener('change', () => {
    state.contentFilters.grade = contentGradeFilter.value
    state.contentPage = 1
    renderContents()
  })

  contentFormatFilter.addEventListener('change', () => {
    state.contentFilters.format = contentFormatFilter.value
    state.contentPage = 1
    renderContents()
  })

  if (clearContentFiltersButton) {
    clearContentFiltersButton.addEventListener('click', () => {
      state.contentFilters = { title: '', subject: '', grade: '', format: '' }
      state.contentPage = 1
      contentTitleFilter.value = ''
      contentSubjectFilter.value = ''
      contentGradeFilter.value = ''
      contentFormatFilter.value = ''
      renderContents()
    })
  }
}

function renderMetrics() {
  const dashboard = state.dashboard || {}
  metricsEl.innerHTML = metricConfig
    .map((metric) => `
      <article class="metric">
        <span class="metric-icon" aria-hidden="true"><img src="${metric.icon}" alt="" /></span>
        <span class="metric-label">${metric.label}</span>
        <strong>${formatNumber(dashboard[metric.key])}</strong>
        ${metricChangeMarkup(metric.key)}
      </article>
    `)
    .join('')
}

function normalizePreferenceItems(items, fallback) {
  const source = Array.isArray(items) && items.length
    ? items
    : fallback.map((key, index) => ({ key, count: fallback.length - index }))

  const max = Math.max(...source.map((item) => item.count || 1), 1)
  return source.slice(0, 4).map((item) => ({
    label: item.key,
    count: item.count || 1,
    percent: Math.max(18, Math.round(((item.count || 1) / max) * 100))
  }))
}

function renderPreferences() {
  const preferences = state.preferences || {}
  preferenceGroupsEl.innerHTML = preferenceConfig
    .map((group) => {
      const items = normalizePreferenceItems(preferences[group.key], group.fallback)
      return `
        <div class="preference-group">
          <div class="preference-label">${group.label}</div>
          <div class="tag-cloud">
            ${items.slice(0, 3).map((item) => `<span class="tag ${group.color}">${escapeHtml(item.label)}</span>`).join('')}
          </div>
          <div class="bars">
            ${items.slice(0, 3).map((item) => `
              <div class="bar">
                <div class="bar-track"><div class="bar-fill" style="width: ${item.percent}%"></div></div>
                <span class="bar-value">${item.percent}%</span>
              </div>
            `).join('')}
          </div>
        </div>
      `
    })
    .join('')
}

function typeLabel(type) {
  const labels = {
    pdf: 'PDF',
    image: '图片',
    video: '视频',
    assessment: '测评',
    camp: '训练营'
  }
  return labels[type] || readableText(type) || '-'
}

function unlockLabel(item) {
  if (item.unlock_type === 'invite') {
    return `邀请 ${item.unlock_threshold || 1} 人解锁`
  }
  return '免费领取'
}

function renderRanking() {
  const rows = rankedContents().slice(0, 5)

  if (!rows.length) {
    rankingRowsEl.innerHTML = '<tr><td colspan="5" class="empty-state">暂无内容数据</td></tr>'
    if (contentRankingRowsEl) {
      contentRankingRowsEl.innerHTML = '<div class="empty-state">暂无内容数据</div>'
    }
    renderContentRankingModal()
    return
  }

  rankingRowsEl.innerHTML = rows
    .map((item, index) => `
      <tr>
        <td><span class="rank-badge">${index + 1}</span>${escapeHtml(item.title)}</td>
        <td>${escapeHtml(typeLabel(item.content_type))}</td>
        <td>${formatNumber(item.claim_count)}</td>
        <td>${formatNumber(item.share_count)}</td>
        <td>${formatNumber(item.lead_count)}</td>
      </tr>
    `)
    .join('')

  if (contentRankingRowsEl) {
    contentRankingRowsEl.innerHTML = rows
      .map((item, index) => `
        <article class="ranking-mini-card">
          <div class="ranking-mini-head">
            <span class="rank-badge">${index + 1}</span>
            <span class="format-pill">${escapeHtml(typeLabel(item.content_type))}</span>
          </div>
          <div class="ranking-mini-title">${escapeHtml(item.title)}</div>
          <div class="ranking-mini-stats">
            <span>领取 ${formatNumber(item.claim_count)}</span>
            <span>分享 ${formatNumber(item.share_count)}</span>
            <span>线索 ${formatNumber(item.lead_count)}</span>
          </div>
        </article>
      `)
      .join('')
  }
  renderContentRankingModal()
}

function rankedContents() {
  return [...state.contents]
    .sort((a, b) => {
      const scoreA = (a.claim_count || 0) + (a.share_count || 0) * 2 + (a.lead_count || 0) * 3
      const scoreB = (b.claim_count || 0) + (b.share_count || 0) * 2 + (b.lead_count || 0) * 3
      return scoreB - scoreA
    })
}

function contentRankingModalRow(item, index) {
  return `
      <tr>
        <td><span class="rank-badge">${index + 1}</span></td>
        <td><div class="ranking-title-cell">${escapeHtml(item.title)}</div></td>
        <td>${escapeHtml(typeLabel(item.content_type))}</td>
        <td>${formatNumber(item.claim_count)}</td>
        <td>${formatNumber(item.share_count)}</td>
        <td>${formatNumber(item.lead_count)}</td>
      </tr>
    `
}

function renderContentRankingPagination(total) {
  if (!contentRankingPaginationEl) return
  const totalPages = Math.max(1, Math.ceil(total / CONTENT_RANKING_PAGE_SIZE))
  state.contentRankingPage = Math.min(Math.max(1, state.contentRankingPage), totalPages)

  if (!total) {
    contentRankingPaginationEl.innerHTML = ''
    return
  }

  const start = (state.contentRankingPage - 1) * CONTENT_RANKING_PAGE_SIZE + 1
  const end = Math.min(total, state.contentRankingPage * CONTENT_RANKING_PAGE_SIZE)
  contentRankingPaginationEl.innerHTML = `
    <span class="pagination-summary">第 ${state.contentRankingPage} / ${totalPages} 页 · 显示 ${start}-${end} 条，共 ${total} 条</span>
    <div class="pagination-actions">
      <button class="secondary compact" type="button" data-ranking-page="prev" ${state.contentRankingPage <= 1 ? 'disabled' : ''}>上一页</button>
      <button class="secondary compact" type="button" data-ranking-page="next" ${state.contentRankingPage >= totalPages ? 'disabled' : ''}>下一页</button>
    </div>
  `
}

function renderContentRankingModal() {
  if (!contentRankingModalRowsEl) return
  const rows = rankedContents()
  const totalPages = Math.max(1, Math.ceil(rows.length / CONTENT_RANKING_PAGE_SIZE))
  state.contentRankingPage = Math.min(Math.max(1, state.contentRankingPage), totalPages)

  if (!rows.length) {
    contentRankingModalRowsEl.innerHTML = '<tr><td colspan="6" class="empty-state">暂无内容数据</td></tr>'
    renderContentRankingPagination(0)
    return
  }

  const pageStart = (state.contentRankingPage - 1) * CONTENT_RANKING_PAGE_SIZE
  const pageRows = rows.slice(pageStart, pageStart + CONTENT_RANKING_PAGE_SIZE)
  contentRankingModalRowsEl.innerHTML = pageRows
    .map((item, index) => contentRankingModalRow(item, pageStart + index))
    .join('')
  renderContentRankingPagination(rows.length)
}

function openContentRankingModal() {
  if (!contentRankingModal) return
  state.contentRankingPage = 1
  renderContentRankingModal()
  contentRankingModal.hidden = false
}

function closeContentRankingModal() {
  if (contentRankingModal) contentRankingModal.hidden = true
}

function contentCard(item, mode = 'content') {
  return `
      <article class="content-card" data-content-id="${item.id}">
        <div>
          <div class="content-title">${escapeHtml(item.title)}</div>
          <div class="content-meta">${escapeHtml(typeLabel(item.content_type))} · ${escapeHtml(item.subject || '-')} · ${escapeHtml(contentProblemLabel(item))} · ${escapeHtml(item.grade || '不限年级')}</div>
          <div class="content-meta">解锁方式：${escapeHtml(unlockLabel(item))}</div>
          <div class="content-meta">领取 ${formatNumber(item.claim_count)} · 分享 ${formatNumber(item.share_count)} · 线索 ${formatNumber(item.lead_count)}</div>
          <div class="content-meta">${escapeHtml(item.summary || '')}</div>
          <div class="content-actions">
            ${item.file_path ? `<a href="/files/${escapeHtml(item.file_path)}" target="_blank" rel="noreferrer">查看文件</a>` : ''}
            <button type="button" data-content-action="edit" data-content-id="${item.id}">编辑</button>
            ${mode === 'review' ? `<button class="primary compact" type="button" data-content-action="approve" data-content-id="${item.id}">发布</button>` : ''}
            <button class="danger" type="button" data-content-action="delete" data-content-id="${item.id}">删除</button>
          </div>
        </div>
        <span class="content-status">${item.is_published ? '已发布' : '未发布'}</span>
      </article>
    `
}

function fileExtension(path) {
  const name = String(path || '')
  const match = name.match(/\.([a-z0-9]+)(?:$|\?)/i)
  return match ? match[1].toUpperCase() : ''
}

function contentTableRow(item) {
  return `
      <tr data-content-id="${item.id}">
        <td>
          <div class="content-title">${escapeHtml(item.title)}</div>
          <div class="content-meta">${escapeHtml(item.summary || '')}</div>
        </td>
        <td><span class="format-pill">${escapeHtml(fileExtension(item.file_path) || typeLabel(item.content_type))}</span></td>
        <td>${escapeHtml(item.grade || '不限年级')}</td>
        <td>${escapeHtml(item.subject || '-')}</td>
        <td><span class="content-status">${item.is_published ? '已发布' : '未发布'}</span></td>
        <td>
          <div class="content-meta">领取 ${formatNumber(item.claim_count)} · 分享 ${formatNumber(item.share_count)}</div>
          <div class="content-meta">线索 ${formatNumber(item.lead_count)} · ${escapeHtml(unlockLabel(item))}</div>
        </td>
        <td>
          <div class="content-actions table-actions">
            ${item.file_path ? `<a href="/files/${escapeHtml(item.file_path)}" target="_blank" rel="noreferrer">查看</a>` : ''}
            <button type="button" data-content-action="edit" data-content-id="${item.id}">编辑</button>
            <button class="danger" type="button" data-content-action="delete" data-content-id="${item.id}">删除</button>
          </div>
        </td>
      </tr>
    `
}

function uniqueContentValues(key) {
  return [...new Set(state.contents.map((item) => readableText(item[key] || '').trim()).filter(Boolean))]
    .sort((a, b) => a.localeCompare(b, 'zh-CN'))
}

function renderContentFilterOptions() {
  if (!contentSubjectFilter || !contentGradeFilter) return
  const selectedSubject = state.contentFilters.subject
  const selectedGrade = state.contentFilters.grade

  contentSubjectFilter.innerHTML = `
    <option value="">全部学科</option>
    ${taxonomyOptions('subjects').map((subject) => `<option value="${escapeHtml(subject)}">${escapeHtml(subject)}</option>`).join('')}
  `
  contentGradeFilter.innerHTML = `
    <option value="">全部年级</option>
    ${taxonomyOptions('grades').map((grade) => `<option value="${escapeHtml(grade)}">${escapeHtml(grade)}</option>`).join('')}
  `

  contentSubjectFilter.value = taxonomyOptions('subjects').includes(selectedSubject) ? selectedSubject : ''
  contentGradeFilter.value = taxonomyOptions('grades').includes(selectedGrade) ? selectedGrade : ''
  state.contentFilters.subject = contentSubjectFilter.value
  state.contentFilters.grade = contentGradeFilter.value
}

function filteredContents() {
  const title = state.contentFilters.title.trim().toLowerCase()
  return state.contents.filter((item) => {
    const itemTitle = readableText(item.title || '').toLowerCase()
    const matchesTitle = !title || itemTitle.includes(title)
    const matchesSubject = !state.contentFilters.subject || readableText(item.subject || '') === state.contentFilters.subject
    const matchesGrade = !state.contentFilters.grade || readableText(item.grade || '') === state.contentFilters.grade
    const matchesFormat = !state.contentFilters.format || item.content_type === state.contentFilters.format
    return matchesTitle && matchesSubject && matchesGrade && matchesFormat
  })
}

function renderContentPagination(total) {
  if (!contentPaginationEl) return
  const totalPages = Math.max(1, Math.ceil(total / CONTENT_PAGE_SIZE))
  state.contentPage = Math.min(Math.max(1, state.contentPage), totalPages)

  if (!total) {
    contentPaginationEl.innerHTML = ''
    return
  }

  const start = (state.contentPage - 1) * CONTENT_PAGE_SIZE + 1
  const end = Math.min(total, state.contentPage * CONTENT_PAGE_SIZE)
  contentPaginationEl.innerHTML = `
    <span class="pagination-summary">第 ${state.contentPage} / ${totalPages} 页 · 显示 ${start}-${end} 条，共 ${total} 条</span>
    <div class="pagination-actions">
      <button class="secondary compact" type="button" data-content-page="prev" ${state.contentPage <= 1 ? 'disabled' : ''}>上一页</button>
      <button class="secondary compact" type="button" data-content-page="next" ${state.contentPage >= totalPages ? 'disabled' : ''}>下一页</button>
    </div>
  `
}

function renderTaxonomyGroups() {
  if (!taxonomyGroupsEl) return
  const groups = ['subject', 'grade', 'problem_category', 'problem']
  const activeType = groups.includes(state.taxonomyActiveType) ? state.taxonomyActiveType : 'problem'
  const allActiveTypeTags = state.taxonomyTags.filter((tag) => tag.tag_type === activeType)
  const categoryId = state.taxonomyActiveProblemCategoryId
  const activeTags = activeType === 'problem' && categoryId !== 'all'
    ? allActiveTypeTags.filter((tag) => String(tag.parent_id || '') === String(categoryId))
    : allActiveTypeTags
  const taxonomyTotalPages = Math.max(1, Math.ceil(activeTags.length / TAXONOMY_PAGE_SIZE))
  if (activeType !== 'problem') {
    state.taxonomyPage = 1
  } else {
    state.taxonomyPage = Math.min(Math.max(1, state.taxonomyPage), taxonomyTotalPages)
  }
  const visibleTags = activeType === 'problem'
    ? activeTags.slice((state.taxonomyPage - 1) * TAXONOMY_PAGE_SIZE, state.taxonomyPage * TAXONOMY_PAGE_SIZE)
    : activeTags
  const tabs = groups.map((type) => {
    const count = state.taxonomyTags.filter((tag) => tag.tag_type === type && tag.is_active).length
    return `
      <button class="taxonomy-tab ${activeType === type ? 'active' : ''}" type="button" data-taxonomy-tab="${type}">
        <span>${taxonomyTypeLabels[type]}</span>
        <strong>${count}</strong>
      </button>
    `
  }).join('')
  const categoryTabs = activeType === 'problem'
    ? `
      <div class="taxonomy-category-tabs">
        <button class="${categoryId === 'all' ? 'active' : ''}" type="button" data-problem-category-filter="all">全部</button>
        ${state.taxonomyTags.filter((tag) => tag.tag_type === 'problem_category').map((category) => {
          const count = state.taxonomyTags.filter((tag) => tag.tag_type === 'problem' && tag.parent_id === category.id && tag.is_active).length
          return `<button class="${String(categoryId) === String(category.id) ? 'active' : ''} ${category.is_active ? '' : 'inactive'}" type="button" data-problem-category-filter="${category.id}">${escapeHtml(category.label)} ${count}</button>`
        }).join('')}
      </div>
    `
    : ''
  const body = visibleTags.length
    ? visibleTags.map((tag) => `
      <span class="taxonomy-tag ${tag.is_active ? 'active' : 'inactive'}">
        <span class="taxonomy-tag-name">${escapeHtml(tag.label)}</span>
        ${activeType === 'problem' ? `<span class="taxonomy-tag-parent">${escapeHtml(state.taxonomyTags.find((item) => item.tag_type === 'problem_category' && item.id === tag.parent_id)?.label || '未分类')}</span>` : ''}
        <button class="taxonomy-icon-button" type="button" title="改名" aria-label="改名" data-taxonomy-edit="${tag.id}" data-taxonomy-type="${tag.tag_type}" data-taxonomy-label="${escapeHtml(tag.label)}">✎</button>
        <button class="taxonomy-icon-button delete" type="button" title="删除" aria-label="删除" data-taxonomy-delete="${tag.id}" data-taxonomy-type="${tag.tag_type}" data-taxonomy-label="${escapeHtml(tag.label)}">❌</button>
      </span>
    `).join('')
    : '<span class="empty-inline">暂无标签</span>'
  const pagination = activeType === 'problem' && activeTags.length > TAXONOMY_PAGE_SIZE
    ? `
      <div class="taxonomy-pagination">
        <span class="pagination-summary">第 ${state.taxonomyPage} / ${taxonomyTotalPages} 页 · 共 ${activeTags.length} 个问题</span>
        <div class="pagination-actions">
          <button class="secondary compact" type="button" data-taxonomy-page="prev" ${state.taxonomyPage <= 1 ? 'disabled' : ''}>上一页</button>
          <button class="secondary compact" type="button" data-taxonomy-page="next" ${state.taxonomyPage >= taxonomyTotalPages ? 'disabled' : ''}>下一页</button>
        </div>
      </div>
    `
    : ''

  taxonomyGroupsEl.innerHTML = `
    <div class="taxonomy-tabs">${tabs}</div>
    <section class="taxonomy-current">
      <div class="taxonomy-current-head">
        <h3>当前：${taxonomyTypeLabels[activeType]}</h3>
        <span>${activeTags.length} 个标签，${activeTags.filter((tag) => tag.is_active).length} 个启用</span>
      </div>
      ${categoryTabs}
      <div class="taxonomy-tags">${body}</div>
      ${pagination}
    </section>
  `
  populateTaxonomyParentSelect()
}

function openTaxonomyActionModal(action, tag) {
  if (!taxonomyActionModal || !taxonomyActionForm) return
  const label = tag.label || ''
  taxonomyActionForm.reset()
  taxonomyActionForm.elements.action.value = action
  taxonomyActionForm.elements.tag_id.value = tag.id
  taxonomyActionForm.elements.tag_type.value = tag.tag_type
  taxonomyActionForm.elements.label.value = label
  taxonomyActionMessage.textContent = ''
  taxonomyActionMessage.className = 'form-message'
  taxonomyActionForm.classList.toggle('is-delete', action === 'delete')
  taxonomyActionLabelField.hidden = action !== 'edit'
  taxonomyConfirmText.hidden = action !== 'delete'
  if (action === 'edit') {
    taxonomyActionTitle.textContent = '修改标签'
    taxonomyActionHint.textContent = `当前：${label}`
    taxonomyConfirmText.textContent = ''
    submitTaxonomyActionModalButton.textContent = '保存修改'
    submitTaxonomyActionModalButton.className = 'primary compact'
    setTimeout(() => taxonomyActionForm.elements.label.focus(), 0)
  } else {
    taxonomyActionTitle.textContent = '删除标签'
    taxonomyActionHint.textContent = '该操作会立即生效'
    taxonomyConfirmText.innerHTML = `<span>确认删除</span><strong>${escapeHtml(label)}</strong><small>删除后会从后台下拉选项中移除。</small>`
    submitTaxonomyActionModalButton.textContent = '确认删除'
    submitTaxonomyActionModalButton.className = 'danger-action compact'
  }
  taxonomyActionModal.hidden = false
}

function closeTaxonomyActionModal() {
  if (taxonomyActionModal) taxonomyActionModal.hidden = true
}

function renderContents() {
  const rows = filteredContents()
  contentCountEl.textContent = rows.length === state.contents.length
    ? `${state.contents.length} 条已发布内容`
    : `${rows.length} / ${state.contents.length} 条已发布内容`
  contentListEl.classList.add('is-table')

  if (!state.contents.length) {
    contentListEl.innerHTML = '<div class="empty-state">暂无已发布内容，请先在素材审核中发布素材。</div>'
    renderContentPagination(0)
    return
  }

  if (!rows.length) {
    contentListEl.innerHTML = '<div class="empty-state">没有符合筛选条件的内容</div>'
    renderContentPagination(0)
    return
  }

  const totalPages = Math.max(1, Math.ceil(rows.length / CONTENT_PAGE_SIZE))
  state.contentPage = Math.min(Math.max(1, state.contentPage), totalPages)
  const pageStart = (state.contentPage - 1) * CONTENT_PAGE_SIZE
  const pageRows = rows.slice(pageStart, pageStart + CONTENT_PAGE_SIZE)

  contentListEl.innerHTML = `
    <div class="table-wrap content-table-wrap">
      <table class="content-table">
        <thead>
          <tr>
            <th>内容名称</th>
            <th>格式</th>
            <th>年级</th>
            <th>学科</th>
            <th>状态</th>
            <th>数据</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          ${pageRows.map((item) => contentTableRow(item)).join('')}
        </tbody>
      </table>
    </div>
  `
  renderContentPagination(rows.length)
}

function renderReview() {
  reviewCountEl.textContent = `${state.reviewContents.length} 条待审核素材`

  if (!state.reviewContents.length) {
    reviewListEl.innerHTML = '<div class="empty-state">暂无待审核素材，AI生成后会先出现在这里。</div>'
    return
  }

  reviewListEl.innerHTML = state.reviewContents
    .map((item) => contentCard(item, 'review'))
    .join('')
}

function bestContent() {
  return [...state.contents].sort((a, b) => {
    const scoreA = (a.claim_count || 0) + (a.share_count || 0) * 2 + (a.lead_count || 0) * 3
    const scoreB = (b.claim_count || 0) + (b.share_count || 0) * 2 + (b.lead_count || 0) * 3
    return scoreB - scoreA
  })[0]
}

function topPreference(key, fallback) {
  const rows = state.preferences?.[key]
  return readableText(rows?.[0]?.key || fallback)
}

function contentMatchesProblem(item, problem) {
  const tags = contentProblemTags(item).map(readableText)
  return tags.includes(readableText(problem))
}

function relatedInsightContents(subject, problem) {
  const rows = state.contents || []
  const subjectText = readableText(subject)
  const problemText = readableText(problem)
  const strictRows = rows.filter((item) => readableText(item.subject) === subjectText && contentMatchesProblem(item, problemText))
  if (strictRows.length) return strictRows
  return rows.filter((item) => readableText(item.subject) === subjectText || contentMatchesProblem(item, problemText))
}

function topicContextContent(item) {
  return (state.topicContext?.related_contents || []).find((row) => Number(row.content_id) === Number(item.id))
}

function contentMetricValue(item, key) {
  const value = Number(item[key])
  if (!Number.isNaN(value)) return value
  const related = topicContextContent(item)
  const relatedValue = Number(related?.[key])
  return Number.isNaN(relatedValue) ? 0 : relatedValue
}

function sumContentMetric(rows, key) {
  return rows.reduce((total, item) => total + contentMetricValue(item, key), 0)
}

function contentRate(rows, numeratorKey) {
  const claims = sumContentMetric(rows, 'claim_count')
  if (!claims) return null
  return sumContentMetric(rows, numeratorKey) / claims
}

function formatPercentRate(value) {
  if (value === null || Number.isNaN(value)) return '-'
  return `${Math.round(value * 100)}%`
}

function insightComparison(label, relatedRows, allRows, numeratorKey) {
  const relatedRate = contentRate(relatedRows, numeratorKey)
  const averageRate = contentRate(allRows, numeratorKey)
  if (relatedRate === null || averageRate === null) return `${label}暂无足够数据`
  const diff = Math.round((relatedRate - averageRate) * 100)
  if (diff > 0) return `${label}${formatPercentRate(relatedRate)}，高于平均 ${diff} 个百分点`
  if (diff < 0) return `${label}${formatPercentRate(relatedRate)}，低于平均 ${Math.abs(diff)} 个百分点`
  return `${label}${formatPercentRate(relatedRate)}，与平均持平`
}

function renderProductionTips() {
  const subject = topPreference('subjects', '语文')
  const problem = topPreference('problems', '识字少')
  const type = typeLabel(topPreference('content_types', 'pdf')).toUpperCase()
  const top = bestContent()
  const suggestion = state.suggestions[0]
  const title = readableText(suggestion?.title || top?.title || `${subject}${problem}7天提升计划`)

  if (priorityTopicEl) priorityTopicEl.textContent = title
  if (priorityReasonEl) {
    priorityReasonEl.textContent = `当前用户更集中在「${subject} / ${problem}」，建议优先生产 ${type} 资料，并在资料末尾绑定测评或训练营入口。`
  }

  const tips = [
    {
      title: `把「${problem}」做成可领取清单`,
      meta: `${subject}用户需求集中，适合低门槛领取`,
      score: '优先级 A'
    },
    {
      title: '给高分享内容补一个转化入口',
      meta: top ? `参考：${readableText(top.title)}` : '把领取后的下一步动作固定为测评',
      score: '转化提升'
    },
    {
      title: '补齐家长可执行的7天练习表',
      meta: '用短任务降低行动成本，适合训练营承接',
      score: '可复用'
    }
  ]

  if (!productionTipsEl) return
  productionTipsEl.innerHTML = tips.map((tip, index) => `
    <article class="suggestion-card">
      <span class="suggestion-index">${index + 1}</span>
      <div>
        <div class="suggestion-title">${escapeHtml(tip.title)}</div>
        <div class="suggestion-meta">${escapeHtml(tip.meta)}</div>
      </div>
      <span class="score-pill">${escapeHtml(tip.score)}</span>
    </article>
  `).join('')
}

function preferenceRows(items, fallback = []) {
  const rows = Array.isArray(items) && items.length
    ? items
    : fallback.map((key) => ({ key, count: 0 }))
  return [...rows].sort((a, b) => (Number(b.count) || 0) - (Number(a.count) || 0)).slice(0, 5)
}

function preferencePercentValue(item, rows) {
  const max = rows.reduce((current, row) => Math.max(current, Number(row.count) || 0), 0)
  if (!max) return 0
  return Math.round(((Number(item.count) || 0) / max) * 100)
}

function topicPreferenceRows(items, fallback = [], limit = 5) {
  return preferenceRows(items, fallback).slice(0, limit)
}

function renderTopicContext() {
  if (topicPreferencesEl) {
    const preferences = state.topicContext?.preferences || state.preferences || {}
    const groups = [
      { label: '年龄', tone: 'green', items: topicPreferenceRows(preferences.ages, ['7']) },
      { label: '学科', tone: 'blue', items: topicPreferenceRows(preferences.subjects, ['语文']) },
      { label: '问题', tone: 'orange', items: topicPreferenceRows(preferences.problems, ['识字少'], 3) },
      { label: '内容类型', tone: 'purple', items: topicPreferenceRows(preferences.content_types, ['pdf']) }
    ]
    topicPreferencesEl.innerHTML = groups.map((group) => `
      <div class="topic-pref-group">
        <span class="topic-pref-label">${escapeHtml(group.label)}</span>
        <div class="topic-pref-tags">
          ${group.items.map((item) => `<b class="topic-pref-chip is-${group.tone}">${escapeHtml(typeLabel(item.key) === '-' ? readableText(item.key) : typeLabel(item.key))}</b>`).join('')}
        </div>
        <div class="topic-pref-bars">
          ${group.items.map((item) => {
            const percent = preferencePercentValue(item, group.items)
            return `
              <div class="topic-pref-bar">
                <i><span style="width: ${percent}%"></span></i>
                <em>${percent}%</em>
              </div>
            `
          }).join('')}
        </div>
      </div>
    `).join('')
  }

  if (topicContentRatesEl) {
    const rows = (state.topicContext?.related_contents || [])
      .filter((item) => (Number(item.download_rate) || 0) > 0 || (Number(item.share_rate) || 0) > 0)
      .sort((a, b) => ((Number(b.download_rate) || 0) + (Number(b.share_rate) || 0)) - ((Number(a.download_rate) || 0) + (Number(a.share_rate) || 0)))
    topicContentRatesEl.innerHTML = rows.length
      ? rows.slice(0, 6).map((item) => `
        <article class="topic-content-rate">
          <strong>${escapeHtml(item.title)}</strong>
          <span>${escapeHtml(typeLabel(item.content_type))} · ${escapeHtml((item.problem_tags || []).join('、') || item.subject || '-')}</span>
          <div>
            <b>下载率 ${Math.round((item.download_rate || 0) * 100)}%</b>
            <b>分享率 ${Math.round((item.share_rate || 0) * 100)}%</b>
          </div>
        </article>
      `).join('')
      : '<div class="empty-state">暂无相关内容表现</div>'
  }

  renderTopicSuggestions()
}

function suggestionMetric(item, key) {
  return item?.source_metrics && item.source_metrics[key]
}

function sortTopicSuggestions(rows) {
  const priorityOrder = { high: 0, medium: 1, low: 2 }
  return [...rows].sort((a, b) => {
    const priorityA = priorityOrder[suggestionMetric(a, 'priority')] ?? 3
    const priorityB = priorityOrder[suggestionMetric(b, 'priority')] ?? 3
    if (priorityA !== priorityB) return priorityA - priorityB
    return new Date(b.created_at || 0) - new Date(a.created_at || 0)
  })
}

function renderTopicSuggestions() {
  if (!topicSuggestionsEl) return
  const rows = sortTopicSuggestions(state.suggestions || []).slice(0, 4)
  topicSuggestionsEl.innerHTML = rows.length
    ? rows.map((item) => {
      const tags = suggestionMetric(item, 'problem_tags') || []
      const priority = suggestionMetric(item, 'priority') || 'draft'
      const subject = suggestionMetric(item, 'subject') || '-'
      const grade = suggestionMetric(item, 'grade') || '-'
      const priorityLabels = { high: '高优先级', medium: '中优先级', low: '低优先级', draft: '草稿' }
      const priorityClass = ['high', 'medium', 'low'].includes(priority) ? priority : 'draft'
      return `
        <article class="topic-suggestion-card is-${escapeHtml(priorityClass)}">
          <div class="topic-suggestion-body">
            <div class="topic-suggestion-title-row">
              <span class="topic-priority">${escapeHtml(priorityLabels[priority] || priority)}</span>
              <h3>${escapeHtml(item.title)}</h3>
            </div>
            <p>${escapeHtml(item.reason || '')}</p>
            <div class="topic-tags">
              <span class="is-type">${escapeHtml(typeLabel(item.content_type))}</span>
              <span class="is-subject">${escapeHtml(subject)}</span>
              <span class="is-grade">${escapeHtml(grade)}</span>
              ${(Array.isArray(tags) ? tags : []).map((tag) => `<span class="is-problem">${escapeHtml(tag)}</span>`).join('')}
            </div>
          </div>
          <div class="topic-suggestion-actions">
            <button class="primary compact" type="button" data-topic-use="${item.id}">AI内容生成</button>
            <button class="secondary compact" type="button" data-topic-edit="${item.id}">编辑</button>
            <button class="link-danger" type="button" data-topic-delete="${item.id}">删除</button>
          </div>
        </article>
      `
    }).join('')
    : '<div class="empty-state">暂无选题，点击 AI生成选题 后生成。</div>'
}

function setTopicGenerationMessage(text, type = '') {
  if (!topicGenerationMessage) return
  topicGenerationMessage.textContent = text
  topicGenerationMessage.className = `form-message${type === 'error' ? ' is-error' : ''}${type === 'success' ? ' is-success' : ''}`
}

function setTopicSuggestionFormMessage(text, type = '') {
  if (!topicSuggestionFormMessage) return
  topicSuggestionFormMessage.textContent = text
  topicSuggestionFormMessage.className = `form-message${type === 'error' ? ' is-error' : ''}${type === 'success' ? ' is-success' : ''}`
}

function topicSuggestionById(id) {
  return state.suggestions.find((item) => String(item.id) === String(id))
}

function openTopicSuggestionModal(item = null) {
  if (!topicSuggestionModal || !topicSuggestionForm) return
  topicSuggestionForm.reset()
  populateTaxonomySelects()
  const metrics = item?.source_metrics || {}
  topicSuggestionForm.elements.suggestion_id.value = item?.id || ''
  topicSuggestionForm.elements.title.value = item?.title || ''
  topicSuggestionForm.elements.target_audience.value = item?.target_audience || ''
  topicSuggestionForm.elements.content_type.value = item?.content_type || 'pdf'
  topicSuggestionForm.elements.priority.value = metrics.priority || 'medium'
  topicSuggestionForm.elements.reason.value = item?.reason || ''
  topicSuggestionForm.elements.next_action.value = metrics.next_action || ''
  setTaxonomySelectValue(topicSuggestionForm.elements.subject, 'subjects', '请选择学科', metrics.subject || '')
  setTaxonomySelectValue(topicSuggestionForm.elements.grade, 'grades', '请选择年级', metrics.grade || '')
  setSelectedProblemTags(metrics.problem_tags || [], 'topic')
  topicSuggestionModalTitle.textContent = item ? '编辑选题' : '新增选题'
  setTopicSuggestionFormMessage('', '')
  topicSuggestionModal.hidden = false
}

function closeTopicSuggestionModal() {
  if (topicSuggestionModal) topicSuggestionModal.hidden = true
}

function openTopicDeleteModal(item) {
  if (!topicDeleteModal || !item) return
  state.pendingTopicDeleteId = item.id
  if (topicDeleteTitle) topicDeleteTitle.textContent = item.title || '未命名选题'
  if (topicDeleteMessage) {
    topicDeleteMessage.textContent = ''
    topicDeleteMessage.className = 'form-message'
  }
  if (confirmTopicDeleteButton) confirmTopicDeleteButton.disabled = false
  topicDeleteModal.hidden = false
}

function closeTopicDeleteModal() {
  state.pendingTopicDeleteId = null
  if (topicDeleteModal) topicDeleteModal.hidden = true
}

function topicSuggestionPayloadFromForm() {
  const formData = new FormData(topicSuggestionForm)
  return {
    title: formData.get('title'),
    target_audience: formData.get('target_audience') || null,
    content_type: formData.get('content_type') || 'pdf',
    subject: formData.get('subject'),
    grade: formData.get('grade'),
    problem_tags: formData.getAll('problem_tags').filter(Boolean),
    priority: formData.get('priority') || 'medium',
    reason: formData.get('reason') || null,
    next_action: formData.get('next_action') || null
  }
}

function useTopicForContentGeneration(item) {
  if (!item) return
  fillFormFromTopicSuggestion(item)
  closeTopicSuggestionModal()
  window.history.replaceState(null, '', '#ai')
  setActiveView('ai', '#ai')
  setFormMessage('已带入选题数据，可继续生成内容。', 'success')
}

function fillFormFromTopicSuggestion(item) {
  if (!form) return
  if (!item) return
  const metrics = item.source_metrics || {}
  form.title.value = item.title || form.title.value
  if (metrics.subject) setTaxonomySelectValue(form.elements.subject, 'subjects', '请选择学科', metrics.subject)
  if (metrics.grade) setTaxonomySelectValue(form.elements.grade, 'grades', '请选择年级', metrics.grade)
  setSelectedProblemTags(metrics.problem_tags || [], 'generator')
  if (item.content_type) {
    const typeInput = Array.from(form.querySelectorAll('input[name="content_type"]')).find((input) => input.value === item.content_type)
    if (typeInput) typeInput.checked = true
  }
  if (metrics.next_action) form.elements.next_action.value = metrics.next_action
  form.elements.summary.value = item.reason || form.elements.summary.value
  renderGeneratedPreview()
}

function renderFunnel() {
  if (!funnelStepsEl) return
  const dashboard = state.dashboard || {}
  const steps = [
    { name: '新增用户', value: dashboard.new_users || 0 },
    { name: '资料领取', value: dashboard.claimed || 0 },
    { name: '分享扩散', value: dashboard.shared || 0 },
    { name: '转化线索', value: dashboard.leads || 0 }
  ]
  const max = Math.max(...steps.map((step) => step.value), 1)

  funnelStepsEl.innerHTML = steps.map((step) => {
    const width = Math.max(8, Math.round((step.value / max) * 100))
    return `
      <div class="funnel-step">
        <span class="funnel-name">${escapeHtml(step.name)}</span>
        <div class="funnel-track"><div class="funnel-fill" style="width: ${width}%"></div></div>
        <span class="funnel-value">${formatNumber(step.value)}</span>
      </div>
    `
  }).join('')

  const note = funnelStepsEl.parentElement.querySelector('.funnel-note')
  if (!note) {
    funnelStepsEl.insertAdjacentHTML('afterend', '<p class="funnel-note">线索偏低时，优先检查领取后的下一步动作是否清晰；分享高但线索低，适合增加限时测评入口。</p>')
  }
}

function renderOpportunities() {
  if (!opportunityListEl) return
  const subjects = normalizePreferenceItems(state.preferences?.subjects, ['语文', '数学', '专注力'])
  const problems = normalizePreferenceItems(state.preferences?.problems, ['识字少', '计算慢', '注意力不集中'])
  const rows = problems.slice(0, 3).map((problem, index) => ({
    title: `${readableText(subjects[index % subjects.length]?.label || '语文')} · ${readableText(problem.label)}专题`,
    meta: index === 0 ? '建议做成PDF领取页，并绑定5分钟测评' : '建议拆成图片卡片和训练营打卡任务',
    heat: `${problem.percent}%热度`,
    tags: ['PDF资料', '测评入口', index === 0 ? '本周优先' : '可排期']
  }))

  opportunityListEl.innerHTML = rows.map((row) => `
    <article class="opportunity-card">
      <div>
        <div class="opportunity-title">${escapeHtml(row.title)}</div>
        <div class="opportunity-meta">${escapeHtml(row.meta)}</div>
        <div class="opportunity-tags">
          ${row.tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
        </div>
      </div>
      <span class="heat">${escapeHtml(row.heat)}</span>
    </article>
  `).join('')
}

function renderActivity() {
  if (!activityListEl) return
  const top = bestContent()
  const dashboard = state.dashboard || {}
  const rows = [
    {
      time: '今天 10:30',
      text: top ? `${readableText(top.title)} 进入内容排行前列，建议复用选题结构。` : '数据看板已刷新，等待第一批内容表现。'
    },
    {
      time: '今天 09:12',
      text: `分享次数达到 ${formatNumber(dashboard.shared)}，适合补充邀请解锁或测评入口。`
    },
    {
      time: '昨天 18:40',
      text: `新增用户 ${formatNumber(dashboard.new_users)}，优先生产低门槛领取资料承接新用户。`
    }
  ]

  activityListEl.innerHTML = rows.map((row) => `
    <article class="activity-item">
      <div class="activity-time">${escapeHtml(row.time)}</div>
      <div class="activity-text">${escapeHtml(row.text)}</div>
    </article>
  `).join('')
}

function timestamp(value) {
  const time = new Date(value || 0).getTime()
  return Number.isNaN(time) ? 0 : time
}

function recommendedFollowUser() {
  const source = state.recommendedUsers.length ? state.recommendedUsers : state.users
  return [...source].sort((a, b) => {
    const scoreDiff = (b.intent_score || 0) - (a.intent_score || 0)
    if (scoreDiff) return scoreDiff
    return timestamp(b.last_active_at || b.registered_at) - timestamp(a.last_active_at || a.registered_at)
  })[0]
}

function followProfileText(user) {
  return [user.child_age ? `${user.child_age}岁` : '', user.child_grade]
    .filter(Boolean)
    .join(' · ') || '-'
}

function followBehaviorText(user) {
  const actions = [
    user.download_count ? `下载 ${formatNumber(user.download_count)} 份资料` : '',
    user.claim_count ? `领取 ${formatNumber(user.claim_count)} 份资料` : '',
    user.share_count ? `分享 ${formatNumber(user.share_count)} 次` : '',
    user.assessment_count ? `完成 ${formatNumber(user.assessment_count)} 次测评` : '',
    user.camp_count ? `参与 ${formatNumber(user.camp_count)} 个训练营` : ''
  ].filter(Boolean)
  return actions.slice(0, 2).join(' · ') || '暂无近期行为'
}

function renderParentAvatar(user) {
  if (!followUserAvatarEl) return
  const fallback = escapeHtml(displayName(user).slice(0, 1))
  followUserAvatarEl.innerHTML = user.avatar_url
    ? `<img src="${escapeHtml(user.avatar_url)}" alt="" onerror="this.hidden=true;this.nextElementSibling.hidden=false" /><span hidden>${fallback}</span>`
    : `<span>${fallback}</span>`
}

function renderFollowUser() {
  const user = recommendedFollowUser()
  if (!user) {
    if (followUserAvatarEl) followUserAvatarEl.innerHTML = '<span>-</span>'
    if (followUserNameEl) followUserNameEl.textContent = '暂无推荐用户'
    if (followUserProfileEl) followUserProfileEl.textContent = '-'
    if (followIntentTagsEl) followIntentTagsEl.innerHTML = '<span class="tag">暂无数据</span>'
    if (followTagsEl) followTagsEl.textContent = '-'
    if (followActionEl) followActionEl.textContent = '-'
    if (followAdviceEl) followAdviceEl.textContent = '-'
    if (followLastActiveEl) followLastActiveEl.textContent = '-'
    if (viewFollowUserDetailButton) viewFollowUserDetailButton.removeAttribute('data-user-id')
    return
  }

  renderParentAvatar(user)
  if (followUserNameEl) followUserNameEl.textContent = displayName(user)
  if (followUserProfileEl) followUserProfileEl.textContent = followProfileText(user)
  if (followIntentTagsEl) {
    const isActive = timestamp(user.last_active_at) > 0 || (user.claim_count || user.download_count || user.share_count || user.assessment_count || user.camp_count) > 0
    followIntentTagsEl.innerHTML = `
      <span class="tag">${isActive ? '活跃用户' : '新注册用户'}</span>
      <span class="tag orange">${escapeHtml(intentLabel(user.intent_level))}</span>
    `
  }
  if (followTagsEl) followTagsEl.textContent = (user.tags || []).slice(0, 3).join(' · ') || '暂无偏好标签'
  if (followActionEl) followActionEl.textContent = followBehaviorText(user)
  if (followAdviceEl) followAdviceEl.textContent = user.recommended_action || '发送入门资料'
  if (followLastActiveEl) followLastActiveEl.textContent = formatDateTime(user.last_active_at || user.registered_at)
  if (viewFollowUserDetailButton) viewFollowUserDetailButton.dataset.userId = user.user_id
}

function renderInsightCard() {
  const subject = topPreference('subjects', '语文')
  const problem = topPreference('problems', '识字少')
  const age = topPreference('ages', '7')
  const relatedRows = relatedInsightContents(subject, problem)
  const allRows = state.contents || []

  if (insightTitleEl) {
    insightTitleEl.textContent = `${rangeLabel()}，${age}岁用户对${subject}${problem}内容兴趣上升。`
  }

  if (!insightListEl) return
  insightListEl.innerHTML = [
    insightComparison('相关内容下载率 ', relatedRows, allRows, 'download_count'),
    insightComparison('相关内容分享率 ', relatedRows, allRows, 'share_count'),
    insightComparison('相关内容线索转化率 ', relatedRows, allRows, 'lead_count')
  ].map((item) => `<li>${escapeHtml(item)}</li>`).join('')
}

function renderDashboardExtras() {
  renderFollowUser()
  renderInsightCard()
}

function intentLabel(level) {
  if (level === 'high') return '高意向'
  if (level === 'medium') return '中意向'
  return '低意向'
}

function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  return `${formatDateInput(date)} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function formatJsonBlock(value) {
  if (value === undefined || value === null || value === '') return '-'
  if (typeof value === 'string') {
    try {
      return JSON.stringify(JSON.parse(value), null, 2)
    } catch {
      return readableText(value)
    }
  }
  return JSON.stringify(value, null, 2)
}

function renderAiLogs() {
  if (!aiLogRowsEl || !aiLogCountEl) return
  aiLogCountEl.textContent = `${state.aiLogs.length} 条调用记录`
  aiLogRowsEl.innerHTML = state.aiLogs.length
    ? state.aiLogs.map((log) => `
      <tr>
        <td>${escapeHtml(formatDateTime(log.started_at))}</td>
        <td>
          <strong>${escapeHtml(log.step_name)}</strong>
          <div class="content-meta">${escapeHtml(log.task_type || '-')}</div>
        </td>
        <td><code>${escapeHtml(log.request_id || '-')}</code></td>
        <td>${escapeHtml(log.model || log.provider || '-')}</td>
        <td><span class="status-chip ${escapeHtml(log.status)}">${escapeHtml(log.status)}</span></td>
        <td>${formatNumber(log.total_tokens)}</td>
        <td>${formatNumber(log.duration_ms)}ms</td>
        <td><button class="secondary compact" type="button" data-ai-log-id="${log.id}">查看</button></td>
      </tr>
    `).join('')
    : '<tr><td colspan="8" class="empty-state">暂无大模型调用记录</td></tr>'
}

async function loadAiLogs() {
  if (!aiLogRowsEl) return
  const extra = { limit: 100 }
  const requestId = aiLogRequestIdInput?.value?.trim()
  const status = aiLogStatusInput?.value
  if (requestId) extra.request_id = requestId
  if (status) extra.status = status
  state.aiLogs = await request(adminUrl('/admin/ai/model-call-logs', extra))
  renderAiLogs()
}

async function openAiLogModal(logId) {
  const log = await request(`/admin/ai/model-call-logs/${logId}`)
  aiLogModalTitle.textContent = `${log.step_name} #${log.id}`
  aiLogModalMeta.textContent = `${formatDateTime(log.started_at)} · ${log.status} · ${log.model || log.provider || '-'} · ${formatNumber(log.duration_ms)}ms`
  aiLogPromptText.textContent = formatJsonBlock(log.prompt_text)
  aiLogResponseText.textContent = formatJsonBlock(log.response_text || log.error_message)
  aiLogModal.hidden = false
}

function closeAiLogModal() {
  aiLogModal.hidden = true
}

function displayName(user) {
  return readableText(user.nickname || `用户${user.user_id}`)
}

function userAvatarMarkup(user) {
  const fallback = escapeHtml(displayName(user).slice(0, 1))
  if (!user.avatar_url) return `<span class="user-avatar">${fallback}</span>`
  return `
    <span class="user-avatar has-image">
      <img src="${escapeHtml(user.avatar_url)}" alt="" onerror="this.hidden=true;this.nextElementSibling.hidden=false" />
      <span class="user-avatar-fallback" hidden>${fallback}</span>
    </span>
  `
}

function renderUserProfiles() {
  if (!registeredUserCountEl || !userRowsEl || !followRankingEl) return
  registeredUserCountEl.textContent = `${state.userTotal} 位用户`

  const ranked = state.recommendedUsers.filter((user) => user.intent_score > 0).slice(0, 3)
  followRankingEl.innerHTML = ranked.length
    ? ranked.map((user, index) => `
      <article class="follow-rank-card">
        <div class="rank-card-head">
          <div class="rank-card-user">
            ${userAvatarMarkup(user)}
            <div>
              <strong>${escapeHtml(displayName(user))}</strong>
              <span>${escapeHtml(followProfileText(user))}</span>
            </div>
          </div>
          <span class="intent-badge ${escapeHtml(user.intent_level)}">${escapeHtml(intentLabel(user.intent_level))}</span>
        </div>
        <div class="rank-stats">
          <div class="rank-stat"><strong>${formatNumber(user.claim_count)}</strong><span>领取</span></div>
          <div class="rank-stat"><strong>${formatNumber(user.download_count)}</strong><span>下载</span></div>
          <div class="rank-stat"><strong>${formatNumber(user.share_count)}</strong><span>分享</span></div>
        </div>
        <div class="recommended-action">${escapeHtml(user.recommended_action)} · ${formatNumber(user.intent_score)}分</div>
      </article>
    `).join('')
    : '<div class="empty-state">当前时间范围内暂无高意向行为。</div>'

  userRowsEl.innerHTML = state.users.length
    ? state.users.map((user) => `
      <tr>
        <td>
          <div class="user-name">
            ${userAvatarMarkup(user)}
            <div>
              <strong>${escapeHtml(displayName(user))}</strong>
            </div>
          </div>
        </td>
        <td>${escapeHtml(user.child_age ?? '-')}岁 · ${escapeHtml(user.child_grade || '-')}</td>
        <td>
          <div class="user-tags">
            ${(user.tags || []).slice(0, 3).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join('') || '<span class="behavior-pill">暂无标签</span>'}
          </div>
        </td>
        <td>
          <div class="behavior-tags">
            <span class="behavior-pill">领 ${formatNumber(user.claim_count)}</span>
            <span class="behavior-pill">下 ${formatNumber(user.download_count)}</span>
            <span class="behavior-pill">享 ${formatNumber(user.share_count)}</span>
            <span class="behavior-pill">测 ${formatNumber(user.assessment_count)}</span>
            <span class="behavior-pill">营 ${formatNumber(user.camp_count)}</span>
          </div>
        </td>
        <td>${escapeHtml(formatDateTime(user.registered_at))}</td>
        <td>
          <span class="intent-badge ${escapeHtml(user.intent_level)}">${escapeHtml(intentLabel(user.intent_level))}</span>
          <div class="content-meta">${escapeHtml(user.recommended_action)} · ${formatNumber(user.intent_score)}分</div>
        </td>
      </tr>
    `).join('')
    : '<tr><td colspan="6" class="empty-state">暂无注册用户</td></tr>'
  renderUserPagination()
}

function renderUserPagination() {
  if (!userPaginationEl) return
  const total = state.userTotal
  const totalPages = Math.max(1, Math.ceil(total / USER_PAGE_SIZE))
  state.userPage = Math.min(Math.max(1, state.userPage), totalPages)

  if (!total || total <= USER_PAGE_SIZE) {
    userPaginationEl.innerHTML = ''
    return
  }

  const start = (state.userPage - 1) * USER_PAGE_SIZE + 1
  const end = Math.min(total, state.userPage * USER_PAGE_SIZE)
  userPaginationEl.innerHTML = `
    <span class="pagination-summary">第 ${state.userPage} / ${totalPages} 页 · 显示 ${start}-${end} 位，共 ${total} 位</span>
    <div class="pagination-actions">
      <button class="secondary compact" type="button" data-user-page="prev" ${state.userPage <= 1 ? 'disabled' : ''}>上一页</button>
      <button class="secondary compact" type="button" data-user-page="next" ${state.userPage >= totalPages ? 'disabled' : ''}>下一页</button>
    </div>
  `
}

function renderGeneratedPreview() {
  if (!form || !generatedTitle || !generatedTags) return
  const formData = new FormData(form)
  const title = formData.get('title') || '一年级孩子识字少，每天怎么练？'
  const tags = [
    formData.get('subject') || '语文',
    formData.get('problem') || '识字少',
    `${formData.get('target_age_min') || 7}岁`,
    formData.get('grade') || '一年级',
    typeLabel(formData.get('content_type') || 'pdf'),
    '家长必看'
  ]

  generatedTitle.textContent = title
  generatedTags.innerHTML = tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join('')
}

function resetContentGenerationForm() {
  if (!form) return
  ;['title', 'summary', 'reference_text'].forEach((name) => {
    if (form.elements[name]) form.elements[name].value = ''
  })
  setSelectedProblemTags([], 'generator')
  renderGeneratedPreview()
  resetGeneratedResult()
  setFormMessage('', '')
}

function renderGeneratedResult(result) {
  if (!generatedTitle || !generatedOutline || !generatedPdfLink || !publishGeneratedContentButton) return
  state.generatedPdf = result
  if (resultPanel) resultPanel.hidden = false
  if (resultEmptyState) resultEmptyState.hidden = true
  if (resultGeneratedContent) resultGeneratedContent.hidden = false
  if (generatedStatus) {
    generatedStatus.textContent = '已生成'
    generatedStatus.classList.remove('is-pending')
  }
  generatedTitle.textContent = result.title
  generatedOutline.innerHTML = result.outline.map((item) => `<li>${escapeHtml(item)}</li>`).join('')
  const sourceLabels = {
    'ai-pages': `生成来源：连续分页生图 ${result.model || ''}`,
    llm: `生成来源：大模型 ${result.model || ''}`,
    'llm-image': `生成来源：文本生图 ${result.model || ''}`,
    'reference-image': `生成来源：参考图生图 ${result.model || ''}`,
    'template-image': '生成来源：模板文字 + 生图',
    template: '生成来源：模板兜底'
  }
  generatedSource.textContent = `${sourceLabels[result.generation_source] || `生成来源：${result.generation_source || '未知'}`}${result.generation_error ? `（${result.generation_error}）` : ''}`
  generatedSource.hidden = false
  const usage = result.token_usage || {}
  generatedTokenUsage.textContent = `Token：输入 ${formatNumber(usage.prompt_tokens)} · 输出 ${formatNumber(usage.completion_tokens)} · 总计 ${formatNumber(usage.total_tokens)}${usage.image_tokens ? ` · 图片 ${formatNumber(usage.image_tokens)}` : ''}`
  generatedTokenUsage.hidden = false
  const steps = result.generation_steps || []
  generatedSteps.innerHTML = `
    <div class="step-request">Request ID：${escapeHtml(result.request_id || '-')}</div>
    ${steps.map((step) => `
      <div class="step-row ${escapeHtml(step.status)}">
        <span>${escapeHtml(step.step)}</span>
        <strong>${escapeHtml(step.status)}</strong>
        <em>${formatNumber(step.duration_ms)}ms</em>
        <small>${escapeHtml(step.message)}</small>
      </div>
    `).join('')}
  `
  generatedSteps.hidden = false
  generatedPdfLink.href = result.url
  generatedPdfLink.hidden = true
  if (viewGeneratedContentButton) viewGeneratedContentButton.disabled = false
  publishGeneratedContentButton.disabled = false
}

function resetGeneratedResult() {
  if (!generatedPdfLink || !generatedSource || !generatedTokenUsage || !generatedSteps || !publishGeneratedContentButton) return
  state.generatedPdf = null
  if (resultPanel) resultPanel.hidden = false
  if (resultEmptyState) resultEmptyState.hidden = false
  if (resultGeneratedContent) resultGeneratedContent.hidden = true
  if (generatedStatus) {
    generatedStatus.textContent = '待生成'
    generatedStatus.classList.add('is-pending')
  }
  generatedPdfLink.hidden = true
  generatedPdfLink.removeAttribute('href')
  generatedSource.hidden = true
  generatedSource.textContent = ''
  generatedTokenUsage.hidden = true
  generatedTokenUsage.textContent = ''
  generatedSteps.hidden = true
  generatedSteps.innerHTML = ''
  if (viewGeneratedContentButton) viewGeneratedContentButton.disabled = true
  publishGeneratedContentButton.disabled = true
}

function setFormMessage(message, type = '') {
  if (!formMessage) return
  formMessage.textContent = message
  formMessage.className = `form-message ${type ? `is-${type}` : ''}`
}

function setUploadMessage(message, type = '') {
  uploadContentMessage.textContent = message
  uploadContentMessage.className = `form-message ${type ? `is-${type}` : ''}`
}

function numberOrNull(value) {
  return value === '' || value === null ? null : Number(value)
}

function guessContentType(fileName) {
  const extension = String(fileName || '').split('.').pop().toLowerCase()
  if (extension === 'pdf') return 'pdf'
  if (['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp'].includes(extension)) return 'image'
  if (['mp4', 'mov', 'avi', 'mkv', 'webm'].includes(extension)) return 'video'
  return 'pdf'
}

function guessGrade(fileName) {
  const name = String(fileName || '')
  const directGrade = name.match(/(幼小衔接|[一二三四五六]年级|[1-6]年级)/)
  if (directGrade) {
    return directGrade[1].replace(/^([1-6])年级$/, (_, grade) => `${'一二三四五六'[Number(grade) - 1]}年级`)
  }

  const transition = name.match(/([一二三四五六])升([一二三四五六])/)
  if (transition) return `${transition[1]}升${transition[2]}`

  return ''
}

function guessSubject(fileName) {
  const name = String(fileName || '')
  if (/英语|英文|字母/.test(name)) return '英语'
  if (/数学|计算|加减法|口算|应用题|真题卷/.test(name)) return '数学'
  if (/语文|拼音|识字|阅读|课文|作文|古诗/.test(name)) return '语文'
  return ''
}

function titleFromFileName(fileName) {
  return String(fileName || '').replace(/\.[^.]+$/, '').trim()
}

function applyFileGuess(file) {
  if (!file?.name) return
  const elements = uploadContentForm.elements
  const title = titleFromFileName(file.name)
  const grade = guessGrade(file.name)
  const subject = guessSubject(file.name)

  if (title) elements.title.value = title
  elements.content_type.value = guessContentType(file.name)
  if (grade) setTaxonomySelectValue(elements.grade, 'grades', '请选择年级', grade)
  if (subject) setTaxonomySelectValue(elements.subject, 'subjects', '请选择学科', subject)
}

function openContentModal(item = null) {
  uploadContentForm.reset()
  setUploadMessage('')
  contentModalTitle.textContent = item ? '编辑本地文件内容' : '上传本地文件'
  uploadContentForm.elements.content_id.value = item?.id || ''
  uploadContentForm.elements.title.value = item?.title || ''
  uploadContentForm.elements.content_type.value = item?.content_type || 'pdf'
  setTaxonomySelectValue(uploadContentForm.elements.subject, 'subjects', '请选择学科', item?.subject || '')
  setSelectedProblemTags(contentProblemTags(item))
  setTaxonomySelectValue(uploadContentForm.elements.grade, 'grades', '请选择年级', item?.grade || '')
  uploadContentForm.elements.unlock_type.value = item?.unlock_type || 'free'
  uploadContentForm.elements.unlock_threshold.value = item?.unlock_threshold ?? 0
  uploadContentForm.elements.summary.value = item?.summary || ''
  uploadContentForm.elements.next_action.value = item?.next_action || ''
  uploadContentForm.elements.file.required = !item
  contentModal.hidden = false
}

function closeContentModal() {
  contentModal.hidden = true
}

function contentPayloadFromForm(formData, upload, existing) {
  const problemTags = formData.getAll('problem_tags').filter(Boolean)
  const payload = {
    title: formData.get('title'),
    content_type: formData.get('content_type'),
    subject: formData.get('subject') || null,
    problem: problemTags[0] || null,
    problem_tags: problemTags,
    grade: formData.get('grade') || null,
    summary: formData.get('summary') || null,
    next_action: formData.get('next_action') || null,
    unlock_type: formData.get('unlock_type') || 'free',
    unlock_threshold: numberOrNull(formData.get('unlock_threshold')) || 0,
    tags: []
  }
  if (upload) {
    payload.file_path = upload.file_path
  } else if (existing?.file_path) {
    payload.file_path = existing.file_path
  }
  return payload
}

async function uploadFile(file) {
  if (!file || !file.name) return null
  const body = new FormData()
  body.append('file', file)
  return request('/admin/files', {
    method: 'POST',
    body
  })
}

async function loadDashboard() {
  state.dashboard = await request(adminUrl('/admin/dashboard/overview'))
  renderMetrics()
  renderDashboardExtras()
}

async function loadTaxonomy() {
  const [tags, options] = await Promise.all([
    request('/admin/taxonomy-tags'),
    request('/admin/taxonomy-options')
  ])
  state.taxonomyTags = tags
  state.taxonomyOptions = options
  populateTaxonomySelects()
  renderContentFilterOptions()
  renderTaxonomyGroups()
}

async function loadPreferences() {
  state.preferences = await request(adminUrl('/admin/preferences'))
  renderPreferences()
  renderTopicContext()
  renderDashboardExtras()
}

async function loadContents() {
  const [published, drafts] = await Promise.all([
    request(adminUrl('/admin/contents', { is_published: true })),
    request(adminUrl('/admin/contents', { is_published: false }))
  ])
  state.contents = published
  state.reviewContents = drafts
  renderRanking()
  renderContentFilterOptions()
  renderContents()
  renderReview()
  renderTopicContext()
  renderDashboardExtras()
}

async function loadUsers() {
  const result = await request(adminUrl('/admin/users', {
    page: state.userPage,
    page_size: USER_PAGE_SIZE
  }))
  state.users = result.items || []
  state.recommendedUsers = result.recommended || []
  state.userTotal = result.total || 0
  state.userPage = result.page || state.userPage
  renderUserProfiles()
  renderFollowUser()
}

async function loadSuggestions() {
  try {
    state.suggestions = await request('/admin/ai/topic-suggestions')
    renderTopicSuggestions()
    renderDashboardExtras()
  } catch {
    state.suggestions = []
    renderTopicSuggestions()
  }
}

async function loadTopicContext() {
  state.topicContext = await request('/admin/ai/topic-context')
  renderTopicContext()
}

async function refreshAll() {
  metricsEl.innerHTML = '<div class="empty-state">加载看板数据中...</div>'
  preferenceGroupsEl.innerHTML = '<div class="empty-state">加载偏好数据中...</div>'
  rankingRowsEl.innerHTML = '<tr><td colspan="5" class="empty-state">加载排行中...</td></tr>'
  if (contentRankingRowsEl) contentRankingRowsEl.innerHTML = '<div class="empty-state">加载排行中...</div>'
  contentListEl.innerHTML = '<div class="empty-state">加载内容中...</div>'
  if (reviewListEl) reviewListEl.innerHTML = '<div class="empty-state">加载待审核素材中...</div>'
  if (followRankingEl) followRankingEl.innerHTML = '<div class="empty-state">加载推荐跟进榜单中...</div>'
  if (userRowsEl) userRowsEl.innerHTML = '<tr><td colspan="6" class="empty-state">加载用户画像中...</td></tr>'
  if (productionTipsEl) productionTipsEl.innerHTML = '<div class="empty-state">整理生产建议中...</div>'
  if (topicPreferencesEl) topicPreferencesEl.innerHTML = '<div class="empty-state">加载热门偏好中...</div>'
  if (topicContentRatesEl) topicContentRatesEl.innerHTML = '<div class="empty-state">加载内容表现中...</div>'
  if (topicSuggestionsEl) topicSuggestionsEl.innerHTML = '<div class="empty-state">加载推荐选题中...</div>'
  if (funnelStepsEl) funnelStepsEl.innerHTML = '<div class="empty-state">计算转化漏斗中...</div>'
  if (opportunityListEl) opportunityListEl.innerHTML = '<div class="empty-state">挖掘内容机会中...</div>'
  if (activityListEl) activityListEl.innerHTML = '<div class="empty-state">加载近期动态中...</div>'

  try {
    await loadTaxonomy()
    await Promise.all([loadDashboard(), loadPreferences(), loadContents(), loadUsers(), loadSuggestions(), loadTopicContext(), loadAiLogs()])
  } catch (error) {
    const message = escapeHtml(error.message || '加载失败')
    metricsEl.innerHTML = `<div class="error-state">看板加载失败：${message}</div>`
    preferenceGroupsEl.innerHTML = '<div class="error-state">偏好数据加载失败</div>'
    rankingRowsEl.innerHTML = '<tr><td colspan="5" class="error-state">内容排行加载失败</td></tr>'
    if (contentRankingRowsEl) contentRankingRowsEl.innerHTML = '<div class="error-state">内容排行加载失败</div>'
    contentListEl.innerHTML = '<div class="error-state">内容列表加载失败，请确认后端服务已启动。</div>'
    if (reviewListEl) reviewListEl.innerHTML = '<div class="error-state">素材审核列表加载失败</div>'
    if (followRankingEl) followRankingEl.innerHTML = '<div class="error-state">推荐跟进榜单加载失败</div>'
    if (userRowsEl) userRowsEl.innerHTML = '<tr><td colspan="6" class="error-state">用户画像加载失败</td></tr>'
  }
}

if (form) {
form.addEventListener('input', () => {
  renderGeneratedPreview()
  resetGeneratedResult()
})

form.addEventListener('submit', async (event) => {
  event.preventDefault()
  setFormMessage('正在生成PDF...', '')
  resetGeneratedResult()

  try {
    const formData = new FormData(form)
    if ((formData.get('content_type') || 'pdf') !== 'pdf') {
      setFormMessage('该类型生成器暂未完成，请先选择PDF资料。', 'error')
      return
    }

    const referenceUpload = await uploadFile(formData.get('file'))
    const payload = {
      title: formData.get('title'),
      summary: formData.get('summary') || '',
      subject: formData.get('subject') || null,
      problem: formData.get('problem') || null,
      grade: formData.get('grade') || null,
      target_age_min: numberOrNull(formData.get('target_age_min')),
      target_age_max: numberOrNull(formData.get('target_age_max')),
      next_action: formData.get('next_action') || null,
      reference_text: formData.get('reference_text') || null,
      reference_file_path: referenceUpload ? referenceUpload.file_path : null,
      page_count: numberOrNull(formData.get('page_count')) || 2,
      match_reference_style: formData.get('match_reference_style') === 'on'
    }
    const result = await request('/admin/ai/generate/image-pdf', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload)
    })

    renderGeneratedResult(result)
    setFormMessage('PDF已生成，可预览后发布到内容池。', 'success')
  } catch (error) {
    setFormMessage(error.message || '生成失败，请稍后重试。', 'error')
  }
})
}

if (publishGeneratedContentButton && form) {
publishGeneratedContentButton.addEventListener('click', async () => {
  if (!state.generatedPdf) {
    setFormMessage('请先生成PDF。', 'error')
    return
  }
  setFormMessage('正在提交到素材审核...', '')

  try {
    const formData = new FormData(form)
    const problemTags = formData.getAll('problem_tags').filter(Boolean)
    const payload = {
      title: state.generatedPdf.title,
      content_type: 'pdf',
      subject: formData.get('subject') || null,
      problem: problemTags[0] || null,
      problem_tags: problemTags,
      grade: formData.get('grade') || null,
      target_age_min: numberOrNull(formData.get('target_age_min')),
      target_age_max: numberOrNull(formData.get('target_age_max')),
      summary: state.generatedPdf.summary,
      file_path: state.generatedPdf.file_path,
      next_action: formData.get('next_action') || null,
      unlock_type: formData.get('unlock_type') || 'free',
      unlock_threshold: numberOrNull(formData.get('unlock_threshold')) || 0,
      tags: [
        formData.get('subject'),
        formData.get('problem'),
        formData.get('grade'),
        'PDF'
      ].filter(Boolean)
    }

    await request('/admin/contents', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(payload)
    })

    setFormMessage('已提交到素材审核，审核发布后会进入内容管理。', 'success')
    await Promise.all([loadDashboard(), loadPreferences(), loadContents(), loadUsers()])
  } catch (error) {
    setFormMessage(error.message || '提交失败，请稍后重试。', 'error')
  }
})
}

if (viewGeneratedContentButton) {
  viewGeneratedContentButton.addEventListener('click', () => {
    if (!state.generatedPdf?.url) {
      setFormMessage('请先生成内容。', 'error')
      return
    }
    window.open(state.generatedPdf.url, '_blank', 'noopener')
  })
}

openContentModalButton.addEventListener('click', () => openContentModal())
closeContentModalButton.addEventListener('click', closeContentModal)
cancelContentModalButton.addEventListener('click', closeContentModal)
contentModal.addEventListener('click', (event) => {
  if (event.target === contentModal) closeContentModal()
})

if (openProblemTagPickerButton) {
  openProblemTagPickerButton.addEventListener('click', () => openProblemTagModal('content'))
}

if (selectedProblemTagsEl) {
  selectedProblemTagsEl.addEventListener('click', (event) => {
    const removeButton = event.target.closest('[data-problem-tag-remove]')
    if (!removeButton) return
    setSelectedProblemTags(state.selectedProblemTags.filter((tag) => tag !== removeButton.dataset.problemTagRemove))
  })
}

if (openGeneratorProblemTagPickerButton) {
  openGeneratorProblemTagPickerButton.addEventListener('click', () => openProblemTagModal('generator'))
}

if (generatorSelectedProblemTagsEl) {
  generatorSelectedProblemTagsEl.addEventListener('click', (event) => {
    const removeButton = event.target.closest('[data-generator-problem-tag-remove]')
    if (!removeButton) return
    setSelectedProblemTags(
      state.generatorSelectedProblemTags.filter((tag) => tag !== removeButton.dataset.generatorProblemTagRemove),
      'generator'
    )
    renderGeneratedPreview()
    resetGeneratedResult()
  })
}

if (openTopicProblemTagPickerButton) {
  openTopicProblemTagPickerButton.addEventListener('click', () => openProblemTagModal('topic'))
}

if (topicSelectedProblemTagsEl) {
  topicSelectedProblemTagsEl.addEventListener('click', (event) => {
    const removeButton = event.target.closest('[data-topic-problem-tag-remove]')
    if (!removeButton) return
    setSelectedProblemTags(state.topicSelectedProblemTags.filter((tag) => tag !== removeButton.dataset.topicProblemTagRemove), 'topic')
  })
}

if (problemTagOptionsEl) {
  problemTagOptionsEl.addEventListener('change', (event) => {
    const checkbox = event.target.closest('[data-problem-tag-option]')
    if (!checkbox) return
    const value = checkbox.value
    if (checkbox.checked) {
      state.problemTagDraft = [...new Set([...state.problemTagDraft, value])]
      return
    }
    state.problemTagDraft = state.problemTagDraft.filter((tag) => tag !== value)
  })
}

if (applyProblemTagPickerButton) {
  applyProblemTagPickerButton.addEventListener('click', () => {
    const target = state.problemTagPickerTarget
    setSelectedProblemTags(state.problemTagDraft, state.problemTagPickerTarget)
    if (target === 'generator') {
      renderGeneratedPreview()
      resetGeneratedResult()
    }
    closeProblemTagModal()
  })
}

if (closeProblemTagModalButton) {
  closeProblemTagModalButton.addEventListener('click', closeProblemTagModal)
}

if (cancelProblemTagPickerButton) {
  cancelProblemTagPickerButton.addEventListener('click', closeProblemTagModal)
}

if (problemTagModal) {
  problemTagModal.addEventListener('click', (event) => {
    if (event.target === problemTagModal) closeProblemTagModal()
  })
}

if (openContentRankingModalButton) {
  openContentRankingModalButton.addEventListener('click', openContentRankingModal)
}

if (closeContentRankingModalButton) {
  closeContentRankingModalButton.addEventListener('click', closeContentRankingModal)
}

if (contentRankingModal) {
  contentRankingModal.addEventListener('click', (event) => {
    if (event.target === contentRankingModal) closeContentRankingModal()
  })
}

async function handleContentAction(event) {
  const actionButton = event.target.closest('[data-content-action]')
  if (!actionButton) return
  const contentId = Number(actionButton.dataset.contentId)
  const item = [...state.contents, ...state.reviewContents].find((content) => content.id === contentId)
  if (!item) return

  if (actionButton.dataset.contentAction === 'edit') {
    openContentModal(item)
    return
  }

  if (actionButton.dataset.contentAction === 'approve') {
    await request(`/admin/contents/${contentId}/publish`, {
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ is_published: true })
    })
    await Promise.all([loadDashboard(), loadPreferences(), loadContents(), loadUsers()])
    return
  }

  if (actionButton.dataset.contentAction === 'delete') {
    const ok = window.confirm(`确认删除「${readableText(item.title)}」吗？相关领取和行为记录也会一并删除。`)
    if (!ok) return
    await request(`/admin/contents/${contentId}`, { method: 'DELETE' })
    await Promise.all([loadDashboard(), loadPreferences(), loadContents(), loadUsers()])
  }
}

contentListEl.addEventListener('click', handleContentAction)
reviewListEl.addEventListener('click', handleContentAction)

if (contentPaginationEl) {
  contentPaginationEl.addEventListener('click', (event) => {
    const button = event.target.closest('[data-content-page]')
    if (!button || button.disabled) return
    state.contentPage += button.dataset.contentPage === 'next' ? 1 : -1
    renderContents()
  })
}

if (contentRankingPaginationEl) {
  contentRankingPaginationEl.addEventListener('click', (event) => {
    const button = event.target.closest('[data-ranking-page]')
    if (!button || button.disabled) return
    state.contentRankingPage += button.dataset.rankingPage === 'next' ? 1 : -1
    renderContentRankingModal()
  })
}

if (userPaginationEl) {
  userPaginationEl.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-user-page]')
    if (!button || button.disabled) return
    state.userPage += button.dataset.userPage === 'next' ? 1 : -1
    await loadUsers()
  })
}

if (taxonomyForm) {
  taxonomyForm.addEventListener('change', () => {
    state.taxonomyActiveType = taxonomyForm.elements.tag_type.value
    renderTaxonomyGroups()
  })

  taxonomyForm.addEventListener('submit', async (event) => {
    event.preventDefault()
    const formData = new FormData(taxonomyForm)
    const tagType = formData.get('tag_type')
    await request('/admin/taxonomy-tags', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        tag_type: tagType,
        label: formData.get('label'),
        parent_id: tagType === 'problem' ? Number(formData.get('parent_id')) : null
      })
    })
    taxonomyForm.reset()
    taxonomyForm.elements.tag_type.value = state.taxonomyActiveType
    state.taxonomyPage = 1
    await loadTaxonomy()
  })
}

if (taxonomyGroupsEl) {
  taxonomyGroupsEl.addEventListener('click', async (event) => {
    const tabButton = event.target.closest('[data-taxonomy-tab]')
    if (tabButton) {
      state.taxonomyActiveType = tabButton.dataset.taxonomyTab
      if (state.taxonomyActiveType !== 'problem') state.taxonomyActiveProblemCategoryId = 'all'
      state.taxonomyPage = 1
      if (taxonomyForm) taxonomyForm.elements.tag_type.value = state.taxonomyActiveType
      renderTaxonomyGroups()
      return
    }
    const categoryFilter = event.target.closest('[data-problem-category-filter]')
    if (categoryFilter) {
      state.taxonomyActiveProblemCategoryId = categoryFilter.dataset.problemCategoryFilter
      state.taxonomyPage = 1
      renderTaxonomyGroups()
      return
    }
    const pageButton = event.target.closest('[data-taxonomy-page]')
    if (pageButton && !pageButton.disabled) {
      state.taxonomyPage += pageButton.dataset.taxonomyPage === 'next' ? 1 : -1
      renderTaxonomyGroups()
      return
    }
    const editButton = event.target.closest('[data-taxonomy-edit]')
    if (editButton) {
      openTaxonomyActionModal('edit', {
        id: editButton.dataset.taxonomyEdit,
        tag_type: editButton.dataset.taxonomyType,
        label: editButton.dataset.taxonomyLabel || ''
      })
      return
    }
    const deleteButton = event.target.closest('[data-taxonomy-delete]')
    if (deleteButton) {
      openTaxonomyActionModal('delete', {
        id: deleteButton.dataset.taxonomyDelete,
        tag_type: deleteButton.dataset.taxonomyType,
        label: deleteButton.dataset.taxonomyLabel || '该标签'
      })
      return
    }
    const button = event.target.closest('[data-taxonomy-id]')
    if (!button) return
    await request(`/admin/taxonomy-tags/${button.dataset.taxonomyType}/${button.dataset.taxonomyId}`, {
      method: 'PATCH',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ is_active: button.dataset.taxonomyActive === 'true' })
    })
    await loadTaxonomy()
  })
}

if (taxonomyActionForm) {
  taxonomyActionForm.addEventListener('submit', async (event) => {
    event.preventDefault()
    const action = taxonomyActionForm.elements.action.value
    const tagId = taxonomyActionForm.elements.tag_id.value
    const tagType = taxonomyActionForm.elements.tag_type.value
    taxonomyActionMessage.textContent = ''
    taxonomyActionMessage.className = 'form-message'
    try {
      if (action === 'edit') {
        const label = taxonomyActionForm.elements.label.value.trim()
        if (!label) {
          taxonomyActionMessage.textContent = '请输入标签名称'
          taxonomyActionMessage.classList.add('is-error')
          return
        }
        await request(`/admin/taxonomy-tags/${tagType}/${tagId}`, {
          method: 'PATCH',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ label })
        })
      } else {
        await request(`/admin/taxonomy-tags/${tagType}/${tagId}`, {
          method: 'DELETE'
        })
      }
      closeTaxonomyActionModal()
      await loadTaxonomy()
    } catch (error) {
      taxonomyActionMessage.textContent = error.message || '操作失败'
      taxonomyActionMessage.classList.add('is-error')
    }
  })
}

if (closeTaxonomyActionModalButton) {
  closeTaxonomyActionModalButton.addEventListener('click', closeTaxonomyActionModal)
}

if (cancelTaxonomyActionModalButton) {
  cancelTaxonomyActionModalButton.addEventListener('click', closeTaxonomyActionModal)
}

if (taxonomyActionModal) {
  taxonomyActionModal.addEventListener('click', (event) => {
    if (event.target === taxonomyActionModal) closeTaxonomyActionModal()
  })
}

uploadContentForm.elements.file.addEventListener('change', () => {
  applyFileGuess(uploadContentForm.elements.file.files?.[0])
})

if (aiLogSearchButton) {
  aiLogSearchButton.addEventListener('click', loadAiLogs)
}

if (aiLogRowsEl) {
  aiLogRowsEl.addEventListener('click', (event) => {
    const button = event.target.closest('[data-ai-log-id]')
    if (button) openAiLogModal(button.dataset.aiLogId)
  })
}

if (viewFollowUserDetailButton) {
  viewFollowUserDetailButton.addEventListener('click', () => {
    window.history.replaceState(null, '', '#users')
    setActiveView('users', '#users')
    document.querySelector('#usersView')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

if (closeAiLogModalButton) {
  closeAiLogModalButton.addEventListener('click', closeAiLogModal)
}

if (aiLogModal) {
  aiLogModal.addEventListener('click', (event) => {
    if (event.target === aiLogModal) closeAiLogModal()
  })
}

uploadContentForm.addEventListener('submit', async (event) => {
  event.preventDefault()
  setUploadMessage('正在保存...', '')
  try {
    const formData = new FormData(uploadContentForm)
    const contentId = Number(formData.get('content_id') || 0)
    const existing = state.contents.find((content) => content.id === contentId)
    const file = formData.get('file')
    const upload = await uploadFile(file)
    const payload = contentPayloadFromForm(formData, upload, existing)

    if (contentId) {
      await request(`/admin/contents/${contentId}`, {
        method: 'PATCH',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (existing?.is_published) {
        await request(`/admin/contents/${contentId}/publish`, {
          method: 'PATCH',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ is_published: true })
        })
      }
    } else {
      const content = await request('/admin/contents', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(payload)
      })
      await request(`/admin/contents/${content.id}/publish`, {
        method: 'PATCH',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ is_published: true })
      })
    }

    closeContentModal()
    await Promise.all([loadDashboard(), loadPreferences(), loadContents(), loadUsers()])
  } catch (error) {
    setUploadMessage(error.message || '保存失败，请稍后重试。', 'error')
  }
})

refreshButton.addEventListener('click', refreshAll)

if (generateTopicSuggestionsButton) {
  generateTopicSuggestionsButton.addEventListener('click', async () => {
    setTopicGenerationMessage('正在调用大模型生成选题...', '')
    generateTopicSuggestionsButton.disabled = true
    try {
      state.suggestions = await request('/admin/ai/topic-suggestions/generate', { method: 'POST' })
      renderTopicSuggestions()
      renderProductionTips()
      setTopicGenerationMessage('已生成推荐选题。', 'success')
      await loadAiLogs()
    } catch (error) {
      setTopicGenerationMessage(error.message || 'AI选题生成失败', 'error')
    } finally {
      generateTopicSuggestionsButton.disabled = false
    }
  })
}

if (openTopicSuggestionModalButton) {
  openTopicSuggestionModalButton.addEventListener('click', () => openTopicSuggestionModal())
}

if (closeTopicSuggestionModalButton) {
  closeTopicSuggestionModalButton.addEventListener('click', closeTopicSuggestionModal)
}

if (cancelTopicSuggestionModalButton) {
  cancelTopicSuggestionModalButton.addEventListener('click', closeTopicSuggestionModal)
}

if (topicSuggestionModal) {
  topicSuggestionModal.addEventListener('click', (event) => {
    if (event.target === topicSuggestionModal) closeTopicSuggestionModal()
  })
}

if (topicSuggestionsEl) {
  topicSuggestionsEl.addEventListener('click', async (event) => {
    const useButton = event.target.closest('[data-topic-use]')
    if (useButton) {
      useTopicForContentGeneration(topicSuggestionById(useButton.dataset.topicUse))
      return
    }
    const editButton = event.target.closest('[data-topic-edit]')
    if (editButton) {
      openTopicSuggestionModal(topicSuggestionById(editButton.dataset.topicEdit))
      return
    }
    const deleteButton = event.target.closest('[data-topic-delete]')
    if (deleteButton) {
      const item = topicSuggestionById(deleteButton.dataset.topicDelete)
      openTopicDeleteModal(item)
    }
  })
}

if (confirmTopicDeleteButton) {
  confirmTopicDeleteButton.addEventListener('click', async () => {
    if (!state.pendingTopicDeleteId) return
    confirmTopicDeleteButton.disabled = true
    if (topicDeleteMessage) {
      topicDeleteMessage.textContent = '正在删除...'
      topicDeleteMessage.className = 'form-message'
    }
    try {
      await request(`/admin/ai/topic-suggestions/${state.pendingTopicDeleteId}`, { method: 'DELETE' })
      state.suggestions = state.suggestions.filter((suggestion) => suggestion.id !== state.pendingTopicDeleteId)
      renderTopicSuggestions()
      closeTopicDeleteModal()
    } catch (error) {
      if (topicDeleteMessage) {
        topicDeleteMessage.textContent = error.message || '删除失败，请稍后重试'
        topicDeleteMessage.className = 'form-message is-error'
      }
      confirmTopicDeleteButton.disabled = false
    }
  })
}

if (closeTopicDeleteModalButton) {
  closeTopicDeleteModalButton.addEventListener('click', closeTopicDeleteModal)
}

if (cancelTopicDeleteModalButton) {
  cancelTopicDeleteModalButton.addEventListener('click', closeTopicDeleteModal)
}

if (topicDeleteModal) {
  topicDeleteModal.addEventListener('click', (event) => {
    if (event.target === topicDeleteModal) closeTopicDeleteModal()
  })
}

if (topicSuggestionForm) {
  topicSuggestionForm.addEventListener('submit', async (event) => {
    event.preventDefault()
    setTopicSuggestionFormMessage('正在保存...', '')
    const suggestionId = Number(topicSuggestionForm.elements.suggestion_id.value || 0)
    try {
      await request(suggestionId ? `/admin/ai/topic-suggestions/${suggestionId}` : '/admin/ai/topic-suggestions', {
        method: suggestionId ? 'PATCH' : 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(topicSuggestionPayloadFromForm())
      })
      closeTopicSuggestionModal()
      await loadSuggestions()
    } catch (error) {
      setTopicSuggestionFormMessage(error.message || '保存失败', 'error')
    }
  })
}

bindNavigation()
bindDateFilters()
bindContentFilters()
populateTaxonomySelects()
if (form) {
  setTaxonomySelectValue(form.elements.subject, 'subjects', '请选择学科', form.elements.subject.value || '语文')
  setTaxonomySelectValue(form.elements.grade, 'grades', '请选择年级', form.elements.grade.value || '一年级')
  renderGeneratorSelectedProblemTags()
}
if (taxonomyForm) taxonomyForm.elements.tag_type.value = state.taxonomyActiveType
renderGeneratedPreview()
resetGeneratedResult()
refreshAll()
