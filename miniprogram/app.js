App({
  globalData: {
    // apiBaseUrl: 'http://127.0.0.1:8000',
    apiBaseUrl: 'http://192.168.3.10:8000',
    openId: 'demo-parent-001',
    accessToken: '',
    user: null,
    childProfile: null,
    pendingInvite: null,
    lastShareOpenKey: '',
    lastShareOpenAt: 0,
    loginReady: null
  },

  onLaunch(options) {
    this.captureInvite(options && options.query)
    const openId = wx.getStorageSync('openId')
    const accessToken = wx.getStorageSync('accessToken')
    const user = wx.getStorageSync('user')
    const childProfile = wx.getStorageSync('childProfile')
    const pendingInvite = wx.getStorageSync('pendingInvite')
    if (openId) this.globalData.openId = openId
    if (accessToken) this.globalData.accessToken = accessToken
    if (user) this.globalData.user = user
    if (childProfile) this.globalData.childProfile = childProfile
    if (pendingInvite) this.globalData.pendingInvite = pendingInvite
    this.globalData.loginReady = accessToken ? Promise.resolve(accessToken) : this.login()
    this.globalData.loginReady.then(() => this.completePendingInvite())
  },

  onShow(options) {
    this.captureInvite(options && options.query)
    if (this.globalData.accessToken) {
      this.completePendingInvite()
    }
  },

  captureInvite(query) {
    const inviterId = Number(query && (query.inviter_user_id || query.inviter))
    if (!inviterId) return
    const sourceContentId = Number(query.source_content_id || query.id) || null
    const currentUser = this.globalData.user || wx.getStorageSync('user')
    if (currentUser && Number(currentUser.id) === inviterId) return

    const pendingInvite = {
      inviter_user_id: inviterId,
      source_content_id: sourceContentId
    }
    this.globalData.pendingInvite = pendingInvite
    wx.setStorageSync('pendingInvite', pendingInvite)
    this.recordShareOpen(pendingInvite)
  },

  recordShareOpen(payload) {
    if (!payload.source_content_id) return
    const key = `${payload.inviter_user_id}:${payload.source_content_id}`
    const now = Date.now()
    if (this.globalData.lastShareOpenKey === key && now - this.globalData.lastShareOpenAt < 3000) {
      return
    }
    this.globalData.lastShareOpenKey = key
    this.globalData.lastShareOpenAt = now
    wx.request({
      url: `${this.globalData.apiBaseUrl}/api/v1/shares/open`,
      method: 'POST',
      data: payload,
      header: { 'content-type': 'application/json' }
    })
  },

  login(force) {
    if (!force && this.globalData.accessToken) {
      return Promise.resolve(this.globalData.accessToken)
    }
    return new Promise((resolve) => {
      wx.login({
        success: (res) => {
          if (!res.code) {
            resolve(this.useCachedAuth())
            return
          }
          this.callLoginApi(res.code)
            .then((data) => {
              const user = {
                id: data.user_id,
                open_id: data.open_id,
                nickname: data.nickname || '',
                avatar_url: data.avatar_url || ''
              }
              this.globalData.openId = data.open_id
              this.globalData.accessToken = data.access_token
              this.globalData.user = user
              wx.setStorageSync('openId', data.open_id)
              wx.setStorageSync('accessToken', data.access_token)
              wx.setStorageSync('user', user)
              this.completePendingInvite()
              resolve(data.access_token)
            })
            .catch(() => {
              resolve(this.useCachedAuth())
            })
        },
        fail: () => {
          resolve(this.useCachedAuth())
        }
      })
    })
  },

  callLoginApi(code) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}/api/v1/auth/wechat-login`,
        method: 'POST',
        data: { code },
        header: { 'content-type': 'application/json' },
        success(res) {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
            return
          }
          reject(new Error('登录失败'))
        },
        fail: reject
      })
    })
  },

  useCachedAuth() {
    const openId = wx.getStorageSync('openId') || this.globalData.openId
    const accessToken = wx.getStorageSync('accessToken') || this.globalData.accessToken
    this.globalData.openId = openId
    this.globalData.accessToken = accessToken
    wx.setStorageSync('openId', openId)
    if (accessToken) wx.setStorageSync('accessToken', accessToken)
    return accessToken
  },

  completePendingInvite() {
    const pendingInvite = this.globalData.pendingInvite || wx.getStorageSync('pendingInvite')
    const token = this.globalData.accessToken || wx.getStorageSync('accessToken')
    const user = this.globalData.user || wx.getStorageSync('user')
    if (!pendingInvite || !token || !user) return
    if (Number(pendingInvite.inviter_user_id) === Number(user.id)) {
      this.clearPendingInvite()
      return
    }
    wx.request({
      url: `${this.globalData.apiBaseUrl}/api/v1/invites/complete`,
      method: 'POST',
      data: pendingInvite,
      header: {
        'content-type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          this.clearPendingInvite()
        }
      }
    })
  },

  clearPendingInvite() {
    this.globalData.pendingInvite = null
    wx.removeStorageSync('pendingInvite')
  },

  setUserProfile(profile) {
    const user = {
      id: profile.user_id,
      open_id: profile.open_id,
      nickname: profile.nickname || '',
      avatar_url: profile.avatar_url || ''
    }
    this.globalData.user = user
    wx.setStorageSync('user', user)
  },

  logout() {
    this.globalData.openId = 'demo-parent-001'
    this.globalData.accessToken = ''
    this.globalData.user = null
    this.globalData.childProfile = null
    this.globalData.loginReady = null
    wx.removeStorageSync('openId')
    wx.removeStorageSync('accessToken')
    wx.removeStorageSync('user')
    wx.removeStorageSync('childProfile')
  }
})
