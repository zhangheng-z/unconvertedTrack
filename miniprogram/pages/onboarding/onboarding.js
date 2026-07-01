const app = getApp()
const { listTaxonomyOptions, onboardProfile } = require('../../services/api')

Page({
  data: {
    ages: [
      { label: '3-4岁', value: 4 },
      { label: '5-6岁', value: 6 },
      { label: '7岁', value: 7 },
      { label: '8岁', value: 8 },
      { label: '9-12岁', value: 10 }
    ],
    grades: ['幼小衔接', '一年级', '二年级', '三年级', '四年级', '五年级', '六年级', '小升初'],
    concernCategories: [
      { key: 'common', label: '常见', items: ['识字少', '阅读理解差', '计算慢', '应用题不会做', '作业拖拉', '注意力不集中', '粗心马虎', '幼小衔接'] },
      { key: 'chinese', label: '语文', items: ['识字少', '拼音不熟', '阅读理解差', '写字慢', '看图写话不会写', '作文没思路'] },
      { key: 'math', label: '数学', items: ['计算慢', '计算容易错', '口算薄弱', '应用题不会做', '审题不清', '数感弱'] },
      { key: 'english', label: '英语', items: ['字母不熟', '单词记不住', '自然拼读薄弱', '听力跟不上', '口语不敢说', '阅读看不懂'] },
      { key: 'habit', label: '习惯', items: ['作业拖拉', '注意力不集中', '粗心马虎', '坐不住', '依赖家长陪写', '学习主动性差'] },
      { key: 'emotion', label: '情绪/适应', items: ['畏难情绪', '考试紧张', '抗拒学习', '缺乏自信', '亲子沟通困难', '入学适应慢'] }
    ],
    activeConcernCategory: 'common',
    currentConcerns: ['识字少', '阅读理解差', '计算慢', '应用题不会做', '作业拖拉', '注意力不集中', '粗心马虎', '幼小衔接'],
    selectedConcerns: {},
    selectedConcernList: [],
    form: {
      child_age: 7,
      age_label: '7岁',
      child_grade: '一年级'
    },
    submitting: false
  },

  onLoad() {
    listTaxonomyOptions()
      .then((options) => {
        const grades = options.grades?.length ? options.grades : this.data.grades
        const problems = options.problems?.length ? options.problems : this.data.currentConcerns
        const categories = options.problem_categories?.length
          ? options.problem_categories.map((category) => ({
            key: String(category.id),
            label: category.label,
            items: category.problems || []
          })).filter((category) => category.items.length)
          : this.data.concernCategories.map((category) => (
            category.key === 'common' ? Object.assign({}, category, { items: problems }) : category
          ))
        const activeCategory = categories[0] || this.data.concernCategories[0]
        this.setData({
          grades,
          concernCategories: categories,
          activeConcernCategory: activeCategory.key,
          currentConcerns: activeCategory.items
        })
      })
      .catch(() => {})
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

  selectConcernCategory(event) {
    const key = event.currentTarget.dataset.key
    const category = this.data.concernCategories.find((item) => item.key === key)
    if (!category) return
    this.setData({
      activeConcernCategory: key,
      currentConcerns: category.items
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
    const selectedConcernList = Object.keys(selected).filter((key) => selected[key])
    this.setData({ selectedConcerns: selected, selectedConcernList })
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
