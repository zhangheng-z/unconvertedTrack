const app = getApp()
const {
  getInviteSummary,
  getMyProfile,
  listMyAssets,
  updateMyProfile,
  uploadAvatar
} = require('../../services/api')

Page({
  data: {
    isLoggedIn: false,
    isEditingProfile: false,
    nickname: '',
    displayName: '7岁孩子的家长',
    avatarUrl: '',
    avatarTempPath: '',
    savingProfile: false,
    profileAgeText: '7岁',
    profileText: '7岁 / 一年级',
    concernText: '语文 / 识字 / 专注力',
    inviteCopy: '已邀请0位家长，仅可领取部分免费资料',
    assets: []
  },

  onShow() {
    this.refreshLoginState()
    this.refreshChildProfile()
    this.loadProfile()
    this.loadAssets()
    this.loadInviteSummary()
  },

  refreshLoginState() {
    const token = app.globalData.accessToken || wx.getStorageSync('accessToken')
    const user = app.globalData.user || wx.getStorageSync('user') || {}
    const nickname = user.nickname || this.data.nickname
    this.setData({
      isLoggedIn: Boolean(token),
      nickname,
      displayName: nickname || `${this.data.profileAgeText}孩子的家长`,
      avatarUrl: user.avatar_url || this.data.avatarUrl
    })
  },

  refreshChildProfile() {
    const profile = app.globalData.childProfile || wx.getStorageSync('childProfile')
    if (!profile) return
    const ageText = profile.ageLabel || `${profile.age}岁`
    this.setData({
      profileAgeText: ageText,
      profileText: `${ageText} / ${profile.grade}`,
      concernText: (profile.concerns || []).join(' / ') || '语文 / 识字 / 专注力',
      displayName: this.data.nickname || `${ageText}孩子的家长`
    })
  },

  loadProfile() {
    getMyProfile()
      .then((profile) => {
        app.setUserProfile(profile)
        this.setData({
          nickname: profile.nickname || '',
          displayName: profile.nickname || `${this.data.profileAgeText}孩子的家长`,
          avatarUrl: profile.avatar_url || '',
          avatarTempPath: ''
        })
      })
      .catch(() => {
        this.refreshLoginState()
      })
  },

  loadAssets() {
    listMyAssets()
      .then((assets) => {
        this.setData({ assets })
      })
      .catch(() => {
        this.setData({ assets: [] })
      })
  },

  loadInviteSummary() {
    getInviteSummary()
      .then((summary) => {
        this.setData({
          inviteCopy: summary.display_text || '已邀请0位家长，仅可领取部分免费资料'
        })
      })
      .catch(() => {
        this.setData({ inviteCopy: '已邀请0位家长，仅可领取部分免费资料' })
      })
  },

  chooseAvatar(event) {
    const avatarTempPath = event.detail && event.detail.avatarUrl
    if (!avatarTempPath) return
    this.setData({
      avatarTempPath,
      avatarUrl: avatarTempPath,
      isEditingProfile: true
    })
  },

  onNicknameInput(event) {
    const nickname = event.detail.value
    this.setData({
      nickname,
      displayName: nickname || `${this.data.profileAgeText}孩子的家长`
    })
  },

  showProfileEditor() {
    this.setData({ isEditingProfile: true })
  },

  hideProfileEditor() {
    const user = app.globalData.user || wx.getStorageSync('user') || {}
    this.setData({
      isEditingProfile: false,
      nickname: user.nickname || '',
      displayName: user.nickname || `${this.data.profileAgeText}孩子的家长`,
      avatarUrl: user.avatar_url || this.data.avatarUrl,
      avatarTempPath: ''
    })
  },

  saveWechatProfile() {
    if (!this.data.isLoggedIn) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }
    const nickname = this.data.nickname.trim()
    this.setData({ savingProfile: true })
    const avatarTask = this.data.avatarTempPath
      ? uploadAvatar(this.data.avatarTempPath).then((result) => result.avatar_url)
      : Promise.resolve(this.data.avatarUrl)

    avatarTask
      .then((avatarUrl) => updateMyProfile({ nickname, avatar_url: avatarUrl }))
      .then((profile) => {
        app.setUserProfile(profile)
        this.setData({
          nickname: profile.nickname || '',
          displayName: profile.nickname || `${this.data.profileAgeText}孩子的家长`,
          avatarUrl: profile.avatar_url || '',
          avatarTempPath: '',
          isEditingProfile: false
        })
        wx.showToast({ title: '已保存', icon: 'success' })
      })
      .catch(() => {
        wx.showToast({ title: '保存失败', icon: 'none' })
      })
      .finally(() => {
        this.setData({ savingProfile: false })
      })
  },

  loginAgain() {
    app.globalData.loginReady = app.login(true)
    app.globalData.loginReady.then(() => {
      this.refreshLoginState()
      this.loadProfile()
      this.loadAssets()
      this.loadInviteSummary()
    })
  },

  logout() {
    wx.showModal({
      title: '退出登录',
      content: '退出后会清除当前登录状态和孩子档案，需要重新生成内容池。',
      confirmText: '退出',
      confirmColor: '#d92d20',
      success: (res) => {
        if (!res.confirm) return
        app.logout()
        this.setData({
          isLoggedIn: false,
          isEditingProfile: false,
          nickname: '',
          displayName: '7岁孩子的家长',
          avatarUrl: '',
          avatarTempPath: '',
          assets: [],
          inviteCopy: '已邀请0位家长，仅可领取部分免费资料',
          profileAgeText: '7岁',
          profileText: '未设置',
          concernText: '未设置'
        })
        wx.showToast({ title: '已退出', icon: 'success' })
        setTimeout(() => {
          app.globalData.loginReady = app.login(true)
          wx.navigateTo({ url: '/pages/onboarding/onboarding' })
        }, 400)
      }
    })
  },

  goOnboarding() {
    wx.navigateTo({ url: '/pages/onboarding/onboarding' })
  },

  goMaterials() {
    wx.switchTab({ url: '/pages/materials/materials' })
  },

  goAssessment() {
    wx.switchTab({ url: '/pages/assessment/assessment' })
  },

  goCamp() {
    wx.switchTab({ url: '/pages/camp/camp' })
  }
})
