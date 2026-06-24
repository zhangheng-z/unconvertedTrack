const metricsEl = document.querySelector('#metrics')
const contentListEl = document.querySelector('#contentList')
const contentCountEl = document.querySelector('#contentCount')
const refreshButton = document.querySelector('#refreshButton')
const form = document.querySelector('#contentForm')

const metricLabels = {
  new_users: '新增用户',
  active_users: '活跃用户',
  claimed: '领取',
  downloaded: '下载',
  shared: '分享',
  leads: '线索'
}

async function request(url, options = {}) {
  const response = await fetch(url, options)
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || '请求失败')
  }
  return response.json()
}

async function loadDashboard() {
  const data = await request('/admin/dashboard/overview')
  metricsEl.innerHTML = Object.entries(metricLabels)
    .map(([key, label]) => `<div class="metric"><span>${label}</span><strong>${data[key] ?? 0}</strong></div>`)
    .join('')
}

async function loadContents() {
  const rows = await request('/admin/contents')
  contentCountEl.textContent = `${rows.length} 条`
  contentListEl.innerHTML = rows
    .map((item) => `
      <article class="content-card">
        <div>
          <div class="content-title">${item.title}</div>
          <div class="content-meta">${item.content_type || '-'} · ${item.subject || '-'} · ${item.problem || '-'} · ${item.grade || '不限年级'}</div>
          <div class="content-meta">${item.summary || ''}</div>
        </div>
        <span class="status">${item.is_published ? '已发布' : '未发布'}</span>
      </article>
    `)
    .join('')
}

async function uploadFile(file) {
  if (!file) return null
  const body = new FormData()
  body.append('file', file)
  return request('/admin/files', {
    method: 'POST',
    body
  })
}

function numberOrNull(value) {
  return value === '' ? null : Number(value)
}

form.addEventListener('submit', async (event) => {
  event.preventDefault()
  const formData = new FormData(form)
  const upload = await uploadFile(formData.get('file'))
  const payload = {
    title: formData.get('title'),
    content_type: formData.get('content_type'),
    subject: formData.get('subject') || null,
    problem: formData.get('problem') || null,
    grade: formData.get('grade') || null,
    target_age_min: numberOrNull(formData.get('target_age_min')),
    target_age_max: numberOrNull(formData.get('target_age_max')),
    summary: formData.get('summary') || null,
    file_path: upload ? upload.file_path : null,
    next_action: formData.get('next_action') || null,
    tags: []
  }
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
  form.reset()
  await Promise.all([loadDashboard(), loadContents()])
})

refreshButton.addEventListener('click', () => {
  Promise.all([loadDashboard(), loadContents()])
})

Promise.all([loadDashboard(), loadContents()])

