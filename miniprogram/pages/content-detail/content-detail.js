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
    claimCount: 0,
    shareCount: 0,
    unlockTitle: '免费领取',
    unlockBadge: '已解锁',
    unlockCopy: '',
    primaryActionText: '免费领取',
    primaryActionState: 'claimable',
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
        const state = this.primaryActionState(detail)
        this.setData({
          detail,
          typeLabel: labels[detail.content_type] || '资料',
          claimCount: detail.claim_count || 0,
          shareCount: detail.share_count || 0,
          unlockTitle: this.unlockTitle(detail),
          unlockBadge: this.unlockBadge(detail),
          unlockCopy: this.unlockCopy(detail),
          primaryActionText: this.primaryActionText(detail),
          primaryActionState: state
        })
      })
      .catch((error) => {
        wx.showToast({ title: error.message || '加载失败', icon: 'none' })
      })
      .finally(() => {
        this.setData({ loading: false })
      })
  },

  primaryActionState(detail) {
    if (detail.is_claimed) return 'claimed'
    if (detail.is_unlocked) return 'claimable'
    if (detail.unlock_type === 'invite') return 'locked'
    return 'claimable'
  },

  unlockTitle(detail) {
    const state = this.primaryActionState(detail)
    if (state === 'claimed') return '已领取'
    if (state === 'locked') return '邀请解锁'
    return '免费领取'
  },

  unlockBadge(detail) {
    const state = this.primaryActionState(detail)
    if (state === 'claimed') return '可下载'
    if (state === 'locked') return '待解锁'
    return '已解锁'
  },

  unlockCopy(detail) {
    const state = this.primaryActionState(detail)
    if (state === 'claimed') return '资料已保存到“我的资料”，可直接下载或继续分享给其他家长。'
    if (state === 'claimable') return '已满足领取条件，点击免费领取后保存到“我的资料”。'
    const rest = Math.max((detail.unlock_threshold || 1) - (detail.user_share_count || 0), 1)
    return `还需邀请${rest}位家长解锁完整资料。`
  },

  primaryActionText(detail) {
    const state = this.primaryActionState(detail)
    if (state === 'claimed') return '下载资料'
    if (state === 'claimable') return '免费领取'
    return `邀请${detail.unlock_threshold || 1}人解锁`
  },

  handlePrimaryAction() {
    const state = this.data.primaryActionState
    if (state === 'claimed') {
      this.download()
      return
    }
    if (state === 'claimable') {
      this.claim()
      return
    }
    this.share()
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
