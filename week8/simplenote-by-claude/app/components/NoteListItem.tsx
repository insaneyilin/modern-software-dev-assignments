'use client';

import { Note } from '@/types/note';

interface NoteListItemProps {
  note: Note;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

export default function NoteListItem({ note, isSelected, onSelect, onDelete }: NoteListItemProps) {
  const title = note.title || 'Untitled';
  const preview = note.content.slice(0, 50) || '无内容';
  const updatedAt = new Date(note.updatedAt).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm(`确定要删除笔记 "${title}" 吗？`)) {
      onDelete();
    }
  };

  return (
    <div
      onClick={onSelect}
      className={`p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors relative group ${
        isSelected ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
      }`}
    >
      <div className="pr-8">
        <h3 className="font-semibold text-gray-900 truncate mb-1">{title}</h3>
        <p className="text-sm text-gray-600 truncate mb-2">{preview}</p>
        <p className="text-xs text-gray-400">{updatedAt}</p>
      </div>
      <button
        onClick={handleDelete}
        className="absolute right-2 top-4 opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-red-100 rounded"
        title="删除笔记"
      >
        <svg
          className="w-4 h-4 text-red-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  );
}
