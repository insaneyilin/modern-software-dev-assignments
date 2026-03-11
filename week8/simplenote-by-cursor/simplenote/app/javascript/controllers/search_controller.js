import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["input"]
  static values = {
    delay: { type: Number, default: 800 }
  }

  connect() {
    this.timeout = null
    this.lastQuery = this.inputTarget.value
    this.isComposing = false  // 标记是否正在输入法输入
  }

  // 输入法开始输入（拼音输入开始）
  compositionStart() {
    this.isComposing = true
    clearTimeout(this.timeout)
  }

  // 输入法结束输入（拼音输入完成，汉字上屏）
  compositionEnd() {
    this.isComposing = false
    // 输入法完成后立即搜索
    this.performSearch()
  }

  submit() {
    // 如果正在使用输入法输入，不触发搜索
    if (this.isComposing) {
      return
    }

    this.performSearch()
  }

  performSearch() {
    const currentQuery = this.inputTarget.value.trim()

    // 如果查询没有变化，不发送请求
    if (currentQuery === this.lastQuery) {
      return
    }

    clearTimeout(this.timeout)

    this.timeout = setTimeout(() => {
      this.lastQuery = currentQuery
      this.element.requestSubmit()
    }, this.delayValue)
  }

  // 按下 Enter 立即搜索
  submitNow(event) {
    if (event.key === 'Enter') {
      clearTimeout(this.timeout)
      this.isComposing = false
      this.lastQuery = this.inputTarget.value.trim()
      this.element.requestSubmit()
    }
  }

  disconnect() {
    clearTimeout(this.timeout)
  }
}
