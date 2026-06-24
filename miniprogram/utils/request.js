function compactData(data) {
  const result = {}
  Object.keys(data || {}).forEach((key) => {
    const value = data[key]
    if (value !== undefined && value !== null && value !== '') {
      result[key] = value
    }
  })
  return result
}

function doRequest(options, retried) {
  const app = getApp()
  const baseUrl = app.globalData.apiBaseUrl
  const token = app.globalData.accessToken || wx.getStorageSync('accessToken')
  const header = Object.assign(
    { 'content-type': 'application/json' },
    token ? { Authorization: `Bearer ${token}` } : {}
  )
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${baseUrl}${options.url}`,
      method: options.method || 'GET',
      data: compactData(options.data),
      header,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
          return
        }
        if (res.statusCode === 401 && !retried && app.login) {
          app.login(true)
            .then(() => doRequest(options, true).then(resolve).catch(reject))
            .catch(reject)
          return
        }
        const message = res.data && res.data.detail ? res.data.detail : '请求失败'
        reject(new Error(message))
      },
      fail(error) {
        reject(error)
      }
    })
  })
}

function request(options) {
  const app = getApp()
  if (options.skipAuth) {
    return doRequest(options, false)
  }
  const ready = app.globalData.loginReady || Promise.resolve()
  return ready.then(() => doRequest(options, false))
}

module.exports = {
  request
}
