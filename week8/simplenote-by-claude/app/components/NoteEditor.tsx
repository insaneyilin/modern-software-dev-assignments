'use client';

import { useState, useEffect } from 'react';
import { Note } from '@/types/note';
import { updateNote } from '../actions/note-actions';

interface NoteEditorProps {
  note: Note | null;
  onNoteUpdate: (note: Note) => void;
}

export default function NoteEditor({ note, onNoteUpdate }: NoteEditorProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (note) {
      setTitle(note.title);
      setContent(note.content);
    }
  }, [note]);

  const handleSave = async () => {
    if (!note) return;

    try {
      setIsSaving(true);
      const updatedNote = await updateNote(note._id, { title, content });
      onNoteUpdate(updatedNote);
    } catch (error) {
      console.error('保存失败:', error);
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    if (!note) return;

    const timer = setTimeout(() => {
      if (title !== note.title || content !== note.content) {
        handleSave();
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [title, content]);

  if (!note) {
    return (
      <div className="flex-1 flex items-center justify-center bg-white">
        <div className="text-center text-gray-400">
          <p className="text-lg">选择或创建一个笔记</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      <div className="p-8 flex-1 flex flex-col">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Untitled"
          className="text-3xl font-bold mb-4 outline-none border-none focus:ring-0"
        />
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="开始写作..."
          className="flex-1 outline-none border-none resize-none focus:ring-0 text-lg leading-relaxed"
        />
        {isSaving && (
          <div className="text-sm text-gray-400 mt-2">保存中...</div>
        )}
      </div>
    </div>
  );
}
