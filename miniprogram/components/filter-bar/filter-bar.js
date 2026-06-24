Component({
  properties: {
    value: {
      type: Object,
      value: {}
    }
  },

  data: {
    subjects: [
      { label: '全部', value: '' },
      { label: '语文', value: '语文' },
      { label: '数学', value: '数学' },
      { label: '英语', value: '英语' },
      { label: '专注力', value: '专注力' }
    ],
    types: [
      { label: '全部', value: '' },
      { label: 'PDF', value: 'pdf' },
      { label: '图片', value: 'image' },
      { label: '视频', value: 'video' },
      { label: '测评', value: 'assessment' },
      { label: '训练营', value: 'camp' }
    ],
    sorts: [
      { label: '智能推荐', value: 'smart' },
      { label: '最新', value: 'latest' },
      { label: '最热', value: 'popular' }
    ]
  },

  methods: {
    selectFilter(event) {
      const key = event.currentTarget.dataset.key
      const value = event.currentTarget.dataset.value
      const next = Object.assign({}, this.properties.value, {
        [key]: value
      })
      this.triggerEvent('change', next)
    }
  }
})

