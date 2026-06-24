const { request } = require('../utils/request')

function wechatLogin(payload) {
  return request({
    url: '/api/v1/auth/wechat-login',
    method: 'POST',
    data: payload,
    skipAuth: true
  })
}

function onboardProfile(payload) {
  return request({
    url: '/api/v1/onboarding/profile',
    method: 'POST',
    data: payload
  })
}

function listContents(params) {
  return request({
    url: '/api/v1/contents',
    data: params
  })
}

function getContentDetail(contentId) {
  return request({
    url: `/api/v1/contents/${contentId}`
  })
}

function claimContent(contentId) {
  return request({
    url: `/api/v1/contents/${contentId}/claim`,
    method: 'POST'
  })
}

function downloadContent(contentId) {
  return request({
    url: `/api/v1/contents/${contentId}/download`,
    method: 'POST'
  })
}

function shareContent(contentId) {
  return request({
    url: `/api/v1/contents/${contentId}/share`,
    method: 'POST'
  })
}

function listMyAssets() {
  return request({
    url: '/api/v1/me/assets'
  })
}

function getInviteSummary() {
  return request({
    url: '/api/v1/me/invite-summary'
  })
}

function getMyProfile() {
  return request({
    url: '/api/v1/me/profile'
  })
}

function updateMyProfile(payload) {
  return request({
    url: '/api/v1/me/profile',
    method: 'PATCH',
    data: payload
  })
}

function uploadAvatar(filePath) {
  const app = getApp()
  const ready = app.globalData.loginReady || Promise.resolve()
  return ready.then(() => new Promise((resolve, reject) => {
    const token = app.globalData.accessToken || wx.getStorageSync('accessToken')
    wx.uploadFile({
      url: `${app.globalData.apiBaseUrl}/api/v1/me/avatar`,
      filePath,
      name: 'avatar',
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(res.data))
          } catch (error) {
            reject(error)
          }
          return
        }
        reject(new Error('头像上传失败'))
      },
      fail: reject
    })
  }))
}

module.exports = {
  wechatLogin,
  onboardProfile,
  listContents,
  getContentDetail,
  claimContent,
  downloadContent,
  shareContent,
  listMyAssets,
  getInviteSummary,
  getMyProfile,
  updateMyProfile,
  uploadAvatar
}
