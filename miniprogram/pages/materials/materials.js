const { listMyAssets } = require('../../services/api')

Page({
  data: {
    assets: [],
    loading: false
  },

  onShow() {
    this.loadAssets()
  },

  loadAssets() {
    this.setData({ loading: true })
    listMyAssets()
      .then((assets) => {
        const typeMap = {
          pdf: 'PDF',
          image: '图片',
          video: '视频',
          assessment: '测评',
          camp: '营'
        }
        this.setData({
          assets: assets.map((item) => Object.assign({}, item, {
            typeLabel: typeMap[item.content_type] || '资料'
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

  openDetail(event) {
    wx.navigateTo({ url: `/pages/content-detail/content-detail?id=${event.currentTarget.dataset.id}` })
  }
})
