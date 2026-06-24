App({
  globalData: {
    apiBaseUrl: 'http://127.0.0.1:8000',
    openId: 'demo-parent-001',
    accessToken: '',
    user: null,
    childProfile: null,
    loginReady: null
  },

  onLaunch() {
    const openId = wx.getStorageSync('openId')
    const accessToken = wx.getStorageSync('accessToken')
    const user = wx.getStorageSync('user')
    const childProfile = wx.getStorageSync('childProfile')
    if (openId) this.globalData.openId = openId
    if (accessToken) this.globalData.accessToken = accessToken
    if (user) this.globalData.user = user
    if (childProfile) this.globalData.childProfile = childProfile
    this.globalData.loginReady = accessToken ? Promise.resolve(accessToken) : this.login()
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
