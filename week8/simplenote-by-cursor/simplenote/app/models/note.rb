class Note < ApplicationRecord
    # 验证：笔记必须包含标题或内容
    validate :must_have_content
    
    # 作用域
    scope :recent, -> { order(updated_at: :desc) }
    scope :search, ->(query) {
      return none if query.blank?
      where(
        "title LIKE ? OR content LIKE ?",
        "%#{sanitize_sql_like(query)}%",
        "%#{sanitize_sql_like(query)}%"
      )
    }
    
    # 实例方法
    def display_title
      title.presence || "Untitled"
    end
    
    def preview_content(length = 50)
      content.to_s.truncate(length)
    end
    
    private
    
    def must_have_content
      if title.blank? && content.blank?
        errors.add(:base, "笔记必须包含标题或内容")
      end
    end
  end
