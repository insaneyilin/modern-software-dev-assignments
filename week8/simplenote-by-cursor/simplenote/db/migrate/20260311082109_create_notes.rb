class CreateNotes < ActiveRecord::Migration[8.1]
  def change
    create_table :notes do |t|
      t.string :title
      t.text :content

      t.timestamps
    end

    add_index :notes, :updated_at  # 用于按时间排序
  end
end
