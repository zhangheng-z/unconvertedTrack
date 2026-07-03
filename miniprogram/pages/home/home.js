const app = getApp()
const { claimContent, listContents } = require('../../services/api')

Page({
  data: {
    profileAgeText: '7岁',
    keyword: '',
    filters: {
      subject: '',
      content_type: '',
      sort: 'smart'
    },
    contents: [],
    loading: false
  },

  onShow() {
    const profile = app.globalData.childProfile || wx.getStorageSync('childProfile')
    if (!profile) {
      wx.redirectTo({ url: '/pages/onboarding/onboarding' })
      return
    }
    this.setData({
      profileAgeText: profile.ageLabel || `${profile.age}岁`
    })
    this.loadContents()
  },

  onKeywordInput(event) {
    this.setData({ keyword: event.detail.value })
  },

  onFilterChange(event) {
    this.setData({ filters: event.detail })
    this.loadContents()
  },

  loadContents() {
    const profile = app.globalData.childProfile || wx.getStorageSync('childProfile')
    if (!profile) return
    const params = {
      age: profile.age,
      grade: profile.grade,
      subject: this.data.filters.subject,
      content_type: this.data.filters.content_type,
      sort: this.data.filters.sort || 'smart'
    }
    this.setData({ loading: true })
    listContents(params)
      .then((contents) => {
        const keyword = this.data.keyword.trim()
        const concernFiltered = this.filterByConcerns(contents, profile.concerns || [])
        const filtered = keyword ? concernFiltered.filter((item) => item.title.indexOf(keyword) >= 0) : concernFiltered
        this.setData({
          contents: filtered.map((item) => Object.assign({}, item, {
            age_label: profile.ageLabel || `${profile.age}岁`
          }))
        })
      })
      .catch((error) => {
        wx.showToast({ title: error.message || '加载失败', icon: 'none' })
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  },

  filterByConcerns(contents, concerns) {
    const selectedConcerns = (concerns || []).filter(Boolean)
    if (!selectedConcerns.length) return contents
    return contents.filter((item) => {
      const problemTags = Array.isArray(item.problem_tags) && item.problem_tags.length
        ? item.problem_tags
        : [item.problem].filter(Boolean)
      return problemTags.some((tag) => selectedConcerns.indexOf(tag) >= 0)
    })
  },

  handleCardAction(event) {
    const { id, state } = event.detail
    if (state === 'claimed') {
      this.openDetail({ detail: { id } })
      return
    }
    if (state === 'locked') {
      this.openDetail({ detail: { id } })
      return
    }
    claimContent(id)
      .then(() => {
        wx.showToast({ title: '已领取', icon: 'success' })
        this.loadContents()
      })
      .catch((error) => {
        wx.showToast({ title: error.message || '领取失败', icon: 'none' })
      })
  },

  openDetail(event) {
    wx.navigateTo({
      url: `/pages/content-detail/content-detail?id=${event.detail.id}`
    })
  }
})
