'use client';

import { useState } from 'react';
import { createNote } from '../actions/note-actions';
import { Note } from '@/types/note';

interface NewNoteButtonProps {
  onNoteCreated: (note: Note) => void;
}

export default function NewNoteButton({ onNoteCreated }: NewNoteButtonProps) {
  const [isCreating, setIsCreating] = useState(false);

  const handleCreate = async () => {
    try {
      setIsCreating(true);
      const note = await createNote();
      onNoteCreated(note);
    } catch (error) {
      console.error('创建笔记失败:', error);
      alert('创建笔记失败，请重试');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <button
      onClick={handleCreate}
      disabled={isCreating}
      className="m-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
    >
      {isCreating ? '创建中...' : '+ 新建笔记'}
    </button>
  );
}
