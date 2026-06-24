Component({
  properties: {
    item: {
      type: Object,
      value: {}
    }
  },

  data: {
    typeLabel: 'PDF',
    display: {}
  },

  observers: {
    item(item) {
      const labels = {
        pdf: 'PDF',
        image: '图片',
        video: '视频',
        assessment: '测评',
        camp: '训练营'
      }
      const typeLabel = labels[item.content_type] || '资料'
      const claimCount = item.claim_count || (1800 + Number(item.id || 1) * 137)
      const shareCount = item.share_count || (320 + Number(item.id || 1) * 61)
      this.setData({
        typeLabel,
        display: Object.assign({}, item, {
          coverTitle: item.title || typeLabel,
          ageLabel: item.age_label || '7岁',
          claimCount,
          shareCount,
          actionText: item.unlock_type === 'share' ? '邀请1人解锁' : '免费领取'
        })
      })
    }
  },

  methods: {
    handleTap() {
      this.triggerEvent('select', { id: this.properties.item.id })
    },

    handleAction() {
      this.triggerEvent('select', { id: this.properties.item.id })
    }
  }
})

