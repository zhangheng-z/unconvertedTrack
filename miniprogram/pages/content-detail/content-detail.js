const app = getApp()
const {
  getContentDetail,
  claimContent,
  downloadContent,
  shareContent
} = require('../../services/api')

Page({
  data: {
    contentId: null,
    detail: {},
    typeLabel: 'PDF',
    ageLabel: '7岁',
    claimCount: 2389,
    shareCount: 684,
    loading: true,
    claiming: false,
    downloading: false,
    sharing: false,
    related: [
      { title: '阅读理解每日一练', type: 'PDF' },
      { title: '一年级语文训练营', type: '营' },
      { title: '识字量自测表', type: '测评' }
    ]
  },

  onLoad(query) {
    const profile = app.globalData.childProfile || wx.getStorageSync('childProfile')
    this.setData({
      contentId: Number(query.id),
      ageLabel: profile && profile.ageLabel ? profile.ageLabel : '7岁'
    })
    this.loadDetail()
  },

  loadDetail() {
    this.setData({ loading: true })
    getContentDetail(this.data.contentId)
      .then((detail) => {
        const labels = {
          pdf: 'PDF',
          image: '图片',
          video: '视频',
          assessment: '测评',
          camp: '训练营'
        }
        this.setData({
          detail,
          typeLabel: labels[detail.content_type] || '资料',
          claimCount: detail.claim_count || (2200 + Number(detail.id || 1) * 189),
          shareCount: detail.share_count || (620 + Number(detail.id || 1) * 64)
        })
      })
      .catch((error) => {
        wx.showToast({ title: error.message || '加载失败', icon: 'none' })
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  },

  claim() {
    this.setData({ claiming: true })
    claimContent(this.data.contentId)
      .then(() => {
        wx.showToast({ title: '已领取', icon: 'success' })
        this.loadDetail()
      })
      .catch((error) => {
        wx.showToast({ title: error.message || '领取失败', icon: 'none' })
      })
      .finally(() => {
        this.setData({ claiming: false })
      })
  },

  download() {
    this.setData({ downloading: true })
    downloadContent(this.data.contentId)
      .then((res) => {
        wx.setClipboardData({
          data: res.download_url,
          success() {
            wx.showToast({ title: '下载链接已复制', icon: 'none' })
          }
        })
      })
      .catch((error) => {
        wx.showToast({ title: error.message || '下载失败', icon: 'none' })
      })
      .finally(() => {
        this.setData({ downloading: false })
      })
  },

  share() {
    this.setData({ sharing: true })
    shareContent(this.data.contentId)
      .then((res) => {
        wx.showToast({ title: res.unlocked ? '已解锁' : '已分享', icon: 'success' })
        this.loadDetail()
      })
      .catch((error) => {
        wx.showToast({ title: error.message || '分享失败', icon: 'none' })
      })
      .finally(() => {
        this.setData({ sharing: false })
      })
  },

  openNextAction() {
    wx.switchTab({ url: '/pages/assessment/assessment' })
  }
})
