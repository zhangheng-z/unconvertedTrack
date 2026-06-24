const app = getApp()
const { onboardProfile } = require('../../services/api')

Page({
  data: {
    ages: [
      { label: '3-4岁', value: 4 },
      { label: '5-6岁', value: 6 },
      { label: '7岁', value: 7 },
      { label: '8岁', value: 8 },
      { label: '9-12岁', value: 10 }
    ],
    grades: ['幼小衔接', '一年级', '二年级'],
    concerns: ['识字阅读', '数学计算', '专注力', '作业拖拉', '学习习惯', '情绪沟通'],
    selectedConcerns: {},
    form: {
      child_age: 7,
      age_label: '7岁',
      child_grade: '一年级'
    },
    submitting: false
  },

  selectAge(event) {
    this.setData({
      'form.child_age': Number(event.currentTarget.dataset.age),
      'form.age_label': event.currentTarget.dataset.label
    })
  },

  selectGrade(event) {
    this.setData({
      'form.child_grade': event.currentTarget.dataset.value
    })
  },

  toggleConcern(event) {
    const value = event.currentTarget.dataset.value
    const selected = Object.assign({}, this.data.selectedConcerns)
    const count = Object.keys(selected).filter((key) => selected[key]).length
    if (!selected[value] && count >= 3) {
      wx.showToast({ title: '最多选择3个问题', icon: 'none' })
      return
    }
    selected[value] = !selected[value]
    this.setData({ selectedConcerns: selected })
  },

  submitProfile() {
    const concerns = Object.keys(this.data.selectedConcerns).filter((key) => this.data.selectedConcerns[key])
    if (!concerns.length) {
      wx.showToast({ title: '请选择关注问题', icon: 'none' })
      return
    }
    const payload = {
      open_id: app.globalData.openId,
      nickname: '体验家长',
      source_channel: 'wechat_miniprogram',
      child_age: this.data.form.child_age,
      child_grade: this.data.form.child_grade,
      concerns
    }
    this.setData({ submitting: true })
    onboardProfile(payload)
      .then(() => {
        const childProfile = {
          age: payload.child_age,
          ageLabel: this.data.form.age_label,
          grade: payload.child_grade,
          concerns
        }
        app.globalData.childProfile = childProfile
        wx.setStorageSync('childProfile', childProfile)
        wx.switchTab({ url: '/pages/home/home' })
      })
      .catch((error) => {
        wx.showToast({ title: error.message || '保存失败', icon: 'none' })
      })
      .finally(() => {
        this.setData({ submitting: false })
      })
  }
})

