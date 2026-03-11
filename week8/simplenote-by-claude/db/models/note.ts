import mongoose, { Schema, Document } from 'mongoose';

export interface INote extends Document {
  _id: string;
  title: string;
  content: string;
  createdAt: Date;
  updatedAt: Date;
}

const noteSchema = new Schema<INote>(
  {
    title: {
      type: String,
      default: '',
      trim: true,
      maxlength: [500, '标题不能超过 500 字符']
    },
    content: {
      type: String,
      default: '',
      maxlength: [100000, '内容不能超过 100000 字符']
    }
  },
  {
    timestamps: true  // 自动管理 createdAt 和 updatedAt
  }
);

// 全文搜索索引
noteSchema.index({ title: 'text', content: 'text' });

// 按更新时间排序索引
noteSchema.index({ updatedAt: -1 });

// 防止模型重复定义（Next.js 热重载问题）
export const Note = mongoose.models.Note || mongoose.model<INote>('Note', noteSchema);
