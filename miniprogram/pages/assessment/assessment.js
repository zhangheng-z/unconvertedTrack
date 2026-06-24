Page({
  data: {
    scores: [
      { name: '识字量', score: 60, level: '' },
      { name: '阅读理解', score: 55, level: '' },
      { name: '表达能力', score: 70, level: 'orange' },
      { name: '专注力', score: 50, level: 'green' },
      { name: '学习习惯', score: 58, level: 'purple' }
    ]
  },

  goCamp() {
    wx.switchTab({ url: '/pages/camp/camp' })
  }
})

