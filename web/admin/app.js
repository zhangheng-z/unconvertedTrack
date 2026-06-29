const metricsEl = document.querySelector('#metrics')
const preferenceGroupsEl = document.querySelector('#preferenceGroups')
const rankingRowsEl = document.querySelector('#rankingRows')
const contentListEl = document.querySelector('#contentList')
const contentCountEl = document.querySelector('#contentCount')
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
const publishGeneratedContentButton = document.querySelector('#publishGeneratedContent')
const pageTitle = document.querySelector('#pageTitle')
const datePreset = document.querySelector('#datePreset')
const startDateInput = document.querySelector('#startDate')
const endDateInput = document.querySelector('#endDate')
const priorityTopicEl = document.querySelector('#priorityTopic')
const priorityReasonEl = document.querySelector('#priorityReason')
const productionTipsEl = document.querySelector('#productionTips')
const funnelStepsEl = document.querySelector('#funnelSteps')
const opportunityListEl = document.querySelector('#opportunityList')
const activityListEl = document.querySelector('#activityList')
const followTagsEl = document.querySelector('#followTags')
const followActionEl = document.querySelector('#followAction')
const followAdviceEl = document.querySelector('#followAdvice')
const insightTitleEl = document.querySelector('#insightTitle')
const insightListEl = document.querySelector('#insightList')
const followRankingEl = document.querySelector('#followRanking')
const userRowsEl = document.querySelector('#userRows')
const registeredUserCountEl = document.querySelector('#registeredUserCount')
const openContentModalButton = document.querySelector('#openContentModal')
const contentModal = document.querySelector('#contentModal')
const uploadContentForm = document.querySelector('#uploadContentForm')
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
  contents: [],
  reviewContents: [],
  suggestions: [],
  users: [],
  aiLogs: [],
  generatedPdf: null
}

const metricConfig = [
  { key: 'new_users', label: '新增用户', icon: '新', change: '18.7%' },
  { key: 'claimed', label: '资料领取', icon: '领', change: '22.3%' },
  { key: 'shared', label: '分享次数', icon: '享', change: '16.5%' },
  { key: 'downloaded', label: '测评完成', icon: '测', change: '12.1%' },
  { key: 'active_users', label: '训练营报名', icon: '训', change: '9.8%' },
  { key: 'leads', label: '转化线索', icon: '转', change: '14.3%' }
]

const preferenceConfig = [
  { key: 'ages', label: '年龄', color: 'green', fallback: ['7岁', '一年级'] },
  { key: 'subjects', label: '学科', color: 'blue', fallback: ['语文', '数学', '专注力'] },
  { key: 'problems', label: '问题', color: 'orange', fallback: ['识字少', '阅读差', '计算慢', '作业拖拉'] },
  { key: 'content_types', label: '内容类型', color: 'purple', fallback: ['PDF', '图片', '测评'] }
]

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
  return response.json()
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
    refreshAll()
  })
  ;[startDateInput, endDateInput].forEach((input) => {
    input.addEventListener('change', () => {
      if (startDateInput.value && endDateInput.value && startDateInput.value > endDateInput.value) {
        endDateInput.value = startDateInput.value
      }
      datePreset.value = 'custom'
      refreshAll()
    })
  })
}

function renderMetrics() {
  const dashboard = state.dashboard || {}
  metricsEl.innerHTML = metricConfig
    .map((metric) => `
      <article class="metric" data-icon="${metric.icon}">
        <span>${metric.label}</span>
        <strong>${formatNumber(dashboard[metric.key])}</strong>
        <small>较上周 ▲ ${metric.change}</small>
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
  const rows = [...state.contents]
    .sort((a, b) => {
      const scoreA = (a.claim_count || 0) + (a.share_count || 0) * 2 + (a.lead_count || 0) * 3
      const scoreB = (b.claim_count || 0) + (b.share_count || 0) * 2 + (b.lead_count || 0) * 3
      return scoreB - scoreA
    })
    .slice(0, 5)

  if (!rows.length) {
    rankingRowsEl.innerHTML = '<tr><td colspan="5" class="empty-state">暂无内容数据</td></tr>'
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
}

function contentCard(item, mode = 'content') {
  return `
      <article class="content-card" data-content-id="${item.id}">
        <div>
          <div class="content-title">${escapeHtml(item.title)}</div>
          <div class="content-meta">${escapeHtml(typeLabel(item.content_type))} · ${escapeHtml(item.subject || '-')} · ${escapeHtml(item.problem || '-')} · ${escapeHtml(item.grade || '不限年级')}</div>
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

function renderContents() {
  contentCountEl.textContent = `${state.contents.length} 条已发布内容`

  if (!state.contents.length) {
    contentListEl.innerHTML = '<div class="empty-state">暂无已发布内容，请先在素材审核中发布素材。</div>'
    return
  }

  contentListEl.innerHTML = state.contents
    .map((item) => contentCard(item))
    .join('')
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

function renderProductionTips() {
  const subject = topPreference('subjects', '语文')
  const problem = topPreference('problems', '识字阅读')
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
  const problems = normalizePreferenceItems(state.preferences?.problems, ['识字阅读', '数学计算', '注意力不集中'])
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

function renderFollowUser() {
  const subject = topPreference('subjects', '语文')
  const problem = topPreference('problems', '识字阅读')
  const type = typeLabel(topPreference('content_types', 'pdf')).toUpperCase()
  const top = bestContent()

  if (followTagsEl) followTagsEl.textContent = `${subject} · ${problem} · ${type}`
  if (followActionEl) {
    const claimed = top?.claim_count ?? state.dashboard?.claimed ?? 0
    followActionEl.textContent = `下载 ${Math.max(1, claimed)} 份资料 · 完成${subject}测评`
  }
  if (followAdviceEl) followAdviceEl.textContent = `推送${subject}训练营 + ${problem}提升计划`
}

function renderInsightCard() {
  const subject = topPreference('subjects', '语文')
  const problem = topPreference('problems', '识字')
  const age = topPreference('ages', '7')
  const dashboard = state.dashboard || {}
  const shareRate = dashboard.claimed ? Math.round(((dashboard.shared || 0) / dashboard.claimed) * 100) : 0
  const leadGap = dashboard.leads === 0 ? '训练营报名仍有提升空间' : '线索已开始沉淀，适合继续加码'

  if (insightTitleEl) {
    insightTitleEl.textContent = `${rangeLabel()}，${age}岁用户对${subject}${problem}内容兴趣上升。`
  }

  if (!insightListEl) return
  insightListEl.innerHTML = [
    `相关内容下载率高于平均水平 ${Math.max(18, shareRate || 38)}%`,
    `分享率高于平均水平 ${Math.max(12, Math.round((dashboard.shared || 1) * 1.3))}%`,
    `测评转化率中等，${leadGap}`
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

function renderUserProfiles() {
  if (!registeredUserCountEl || !userRowsEl || !followRankingEl) return
  registeredUserCountEl.textContent = `${state.users.length} 位用户`

  const ranked = state.users.filter((user) => user.intent_score > 0).slice(0, 3)
  followRankingEl.innerHTML = ranked.length
    ? ranked.map((user, index) => `
      <article class="follow-rank-card">
        <div class="rank-card-head">
          <div class="rank-card-user">
            <span class="user-avatar">${index + 1}</span>
            <div>
              <strong>${escapeHtml(displayName(user))}</strong>
              <span>${escapeHtml(user.source_channel || '-')} · ${escapeHtml(user.child_grade || '-')}</span>
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
            <span class="user-avatar">${escapeHtml(displayName(user).slice(0, 1))}</span>
            <div>
              <strong>${escapeHtml(displayName(user))}</strong>
              <span>${escapeHtml(user.open_id)} · 注册 ${escapeHtml(formatDateTime(user.registered_at))}</span>
            </div>
          </div>
        </td>
        <td>${escapeHtml(user.child_age ?? '-')}岁 · ${escapeHtml(user.child_grade || '-')}</td>
        <td>${escapeHtml(user.source_channel || '-')}</td>
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
        <td>
          <span class="intent-badge ${escapeHtml(user.intent_level)}">${escapeHtml(intentLabel(user.intent_level))}</span>
          <div class="content-meta">${escapeHtml(user.recommended_action)} · ${formatNumber(user.intent_score)}分</div>
        </td>
      </tr>
    `).join('')
    : '<tr><td colspan="6" class="empty-state">暂无注册用户</td></tr>'
}

function renderGeneratedPreview() {
  const formData = new FormData(form)
  const title = formData.get('title') || '一年级孩子识字少，每天怎么练？'
  const tags = [
    formData.get('subject') || '语文',
    formData.get('problem') || '识字',
    `${formData.get('target_age_min') || 7}岁`,
    formData.get('grade') || '一年级',
    typeLabel(formData.get('content_type') || 'pdf'),
    '家长必看'
  ]

  generatedTitle.textContent = title
  generatedTags.innerHTML = tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join('')
}

function renderGeneratedResult(result) {
  state.generatedPdf = result
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
  generatedPdfLink.hidden = false
  publishGeneratedContentButton.disabled = false
}

function resetGeneratedResult() {
  state.generatedPdf = null
  generatedPdfLink.hidden = true
  generatedPdfLink.removeAttribute('href')
  generatedSource.hidden = true
  generatedSource.textContent = ''
  generatedTokenUsage.hidden = true
  generatedTokenUsage.textContent = ''
  generatedSteps.hidden = true
  generatedSteps.innerHTML = ''
  publishGeneratedContentButton.disabled = true
}

function setFormMessage(message, type = '') {
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

function openContentModal(item = null) {
  uploadContentForm.reset()
  setUploadMessage('')
  contentModalTitle.textContent = item ? '编辑本地文件内容' : '上传本地文件'
  uploadContentForm.elements.content_id.value = item?.id || ''
  uploadContentForm.elements.title.value = item?.title || ''
  uploadContentForm.elements.content_type.value = item?.content_type || 'pdf'
  uploadContentForm.elements.subject.value = item?.subject || ''
  uploadContentForm.elements.problem.value = item?.problem || ''
  uploadContentForm.elements.grade.value = item?.grade || ''
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
  const payload = {
    title: formData.get('title'),
    content_type: formData.get('content_type'),
    subject: formData.get('subject') || null,
    problem: formData.get('problem') || null,
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

async function loadPreferences() {
  state.preferences = await request(adminUrl('/admin/preferences'))
  renderPreferences()
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
  renderContents()
  renderReview()
  renderDashboardExtras()
}

async function loadUsers() {
  state.users = await request(adminUrl('/admin/users'))
  renderUserProfiles()
}

async function loadSuggestions() {
  try {
    state.suggestions = await request('/admin/ai/topic-suggestions')
    const first = state.suggestions[0]
    if (first && !form.title.value) {
      form.title.value = first.title
      renderGeneratedPreview()
    }
    renderDashboardExtras()
  } catch {
    state.suggestions = []
  }
}

async function refreshAll() {
  metricsEl.innerHTML = '<div class="empty-state">加载看板数据中...</div>'
  preferenceGroupsEl.innerHTML = '<div class="empty-state">加载偏好数据中...</div>'
  rankingRowsEl.innerHTML = '<tr><td colspan="5" class="empty-state">加载排行中...</td></tr>'
  contentListEl.innerHTML = '<div class="empty-state">加载内容中...</div>'
  if (reviewListEl) reviewListEl.innerHTML = '<div class="empty-state">加载待审核素材中...</div>'
  if (followRankingEl) followRankingEl.innerHTML = '<div class="empty-state">加载推荐跟进榜单中...</div>'
  if (userRowsEl) userRowsEl.innerHTML = '<tr><td colspan="6" class="empty-state">加载用户画像中...</td></tr>'
  if (productionTipsEl) productionTipsEl.innerHTML = '<div class="empty-state">整理生产建议中...</div>'
  if (funnelStepsEl) funnelStepsEl.innerHTML = '<div class="empty-state">计算转化漏斗中...</div>'
  if (opportunityListEl) opportunityListEl.innerHTML = '<div class="empty-state">挖掘内容机会中...</div>'
  if (activityListEl) activityListEl.innerHTML = '<div class="empty-state">加载近期动态中...</div>'

  try {
    await Promise.all([loadDashboard(), loadPreferences(), loadContents(), loadUsers(), loadSuggestions(), loadAiLogs()])
  } catch (error) {
    const message = escapeHtml(error.message || '加载失败')
    metricsEl.innerHTML = `<div class="error-state">看板加载失败：${message}</div>`
    preferenceGroupsEl.innerHTML = '<div class="error-state">偏好数据加载失败</div>'
    rankingRowsEl.innerHTML = '<tr><td colspan="5" class="error-state">内容排行加载失败</td></tr>'
    contentListEl.innerHTML = '<div class="error-state">内容列表加载失败，请确认后端服务已启动。</div>'
    if (reviewListEl) reviewListEl.innerHTML = '<div class="error-state">素材审核列表加载失败</div>'
    if (followRankingEl) followRankingEl.innerHTML = '<div class="error-state">推荐跟进榜单加载失败</div>'
    if (userRowsEl) userRowsEl.innerHTML = '<tr><td colspan="6" class="error-state">用户画像加载失败</td></tr>'
  }
}

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

publishGeneratedContentButton.addEventListener('click', async () => {
  if (!state.generatedPdf) {
    setFormMessage('请先生成PDF。', 'error')
    return
  }
  setFormMessage('正在提交到素材审核...', '')

  try {
    const formData = new FormData(form)
    const payload = {
      title: state.generatedPdf.title,
      content_type: 'pdf',
      subject: formData.get('subject') || null,
      problem: formData.get('problem') || null,
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

openContentModalButton.addEventListener('click', () => openContentModal())
closeContentModalButton.addEventListener('click', closeContentModal)
cancelContentModalButton.addEventListener('click', closeContentModal)
contentModal.addEventListener('click', (event) => {
  if (event.target === contentModal) closeContentModal()
})

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

if (aiLogSearchButton) {
  aiLogSearchButton.addEventListener('click', loadAiLogs)
}

if (aiLogRowsEl) {
  aiLogRowsEl.addEventListener('click', (event) => {
    const button = event.target.closest('[data-ai-log-id]')
    if (button) openAiLogModal(button.dataset.aiLogId)
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

bindNavigation()
bindDateFilters()
renderGeneratedPreview()
refreshAll()
