import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["title", "content", "status"]
  static values = { delay: Number }

  connect() {
    this.timeout = null
    this.originalTitle = this.titleTarget.value
    this.originalContent = this.contentTarget.value
  }

  save() {
    this.statusTarget.textContent = "保存中..."
    clearTimeout(this.timeout)

    this.timeout = setTimeout(() => {
      this.performSave()
    }, this.delayValue)
  }

  async performSave() {
    // Check if content actually changed
    if (this.titleTarget.value === this.originalTitle &&
        this.contentTarget.value === this.originalContent) {
      this.statusTarget.textContent = "所有更改已保存"
      return
    }

    try {
      const form = this.element
      const formData = new FormData(form)

      const response = await fetch(form.action, {
        method: "PATCH",
        body: formData,
        headers: {
          "Accept": "text/vnd.turbo-stream.html"
        }
      })

      if (response.ok) {
        this.originalTitle = this.titleTarget.value
        this.originalContent = this.contentTarget.value
        this.statusTarget.textContent = "所有更改已保存"
      } else {
        this.statusTarget.textContent = "保存失败，请重试"
      }
    } catch (error) {
      console.error("保存失败:", error)
      this.statusTarget.textContent = "保存失败，请重试"
    }
  }
}
