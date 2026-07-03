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
      const problemTags = Array.isArray(item.problem_tags) && item.problem_tags.length
        ? item.problem_tags
        : [item.problem].filter(Boolean)
      this.setData({
        typeLabel,
        display: Object.assign({}, item, {
          problemTags,
          coverTitle: item.title || typeLabel,
          ageLabel: item.age_label || '7岁',
          claimCount: item.claim_count || 0,
          shareCount: item.share_count || 0,
          actionText: this.actionText(item),
          actionState: this.actionState(item)
        })
      })
    }
  },

  methods: {
    actionState(item) {
      if (item.is_claimed) return 'claimed'
      if (item.is_unlocked) return 'claimable'
      if (item.unlock_type === 'invite') return 'locked'
      return 'claimable'
    },

    actionText(item) {
      const state = this.actionState(item)
      if (state === 'claimed') return '已领取'
      if (state === 'claimable') return '免费领取'
      return `邀请${item.unlock_threshold || 1}人解锁`
    },

    handleTap() {
      this.triggerEvent('select', { id: this.properties.item.id })
    },

    handleAction() {
      this.triggerEvent('action', {
        id: this.properties.item.id,
        state: this.data.display.actionState
      })
    }
  }
})
