'use server';

import { revalidatePath } from 'next/cache';
import { Note } from '@/db/models/note';
import { connectDB } from '@/db/db';

// 获取所有笔记（按更新时间倒序）
export async function getNotes() {
  try {
    await connectDB();
    const notes = await Note.find({})
      .sort({ updatedAt: -1 })
      .lean();
    return JSON.parse(JSON.stringify(notes));
  } catch (error) {
    console.error('获取笔记失败:', error);
    throw new Error('获取笔记失败');
  }
}

// 获取单个笔记
export async function getNote(id: string) {
  try {
    await connectDB();
    const note = await Note.findById(id).lean();
    if (!note) {
      throw new Error('笔记不存在');
    }
    return JSON.parse(JSON.stringify(note));
  } catch (error) {
    console.error('获取笔记失败:', error);
    throw new Error('获取笔记失败');
  }
}

// 创建笔记
export async function createNote() {
  try {
    await connectDB();
    const note = await Note.create({
      title: '',
      content: ''
    });
    revalidatePath('/');
    return JSON.parse(JSON.stringify(note));
  } catch (error) {
    console.error('创建笔记失败:', error);
    throw new Error('创建笔记失败');
  }
}

// 更新笔记
export async function updateNote(id: string, data: { title?: string; content?: string }) {
  try {
    await connectDB();
    const note = await Note.findByIdAndUpdate(
      id,
      { $set: data },
      { new: true, runValidators: true }
    ).lean();

    if (!note) {
      throw new Error('笔记不存在');
    }

    revalidatePath('/');
    return JSON.parse(JSON.stringify(note));
  } catch (error) {
    console.error('更新笔记失败:', error);
    throw new Error('更新笔记失败');
  }
}

// 删除笔记
export async function deleteNote(id: string) {
  try {
    await connectDB();
    const result = await Note.findByIdAndDelete(id);

    if (!result) {
      throw new Error('笔记不存在');
    }

    revalidatePath('/');
    return { success: true };
  } catch (error) {
    console.error('删除笔记失败:', error);
    throw new Error('删除笔记失败');
  }
}
