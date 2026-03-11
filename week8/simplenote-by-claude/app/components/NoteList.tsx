'use client';

import { Note } from '@/types/note';
import NoteListItem from './NoteListItem';

interface NoteListProps {
  notes: Note[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function NoteList({ notes, selectedId, onSelect, onDelete }: NoteListProps) {
  if (notes.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 text-center">
        <div className="text-gray-400">
          <p className="text-lg mb-2">还没有笔记</p>
          <p className="text-sm">点击上方按钮创建第一条笔记</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {notes.map((note) => (
        <NoteListItem
          key={note._id}
          note={note}
          isSelected={note._id === selectedId}
          onSelect={() => onSelect(note._id)}
          onDelete={() => onDelete(note._id)}
        />
      ))}
    </div>
  );
}
