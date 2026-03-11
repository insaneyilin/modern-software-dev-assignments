'use client';

import { useState } from 'react';
import { Note } from '@/types/note';
import { deleteNote } from '../actions/note-actions';
import SearchBar from './SearchBar';
import NewNoteButton from './NewNoteButton';
import NoteList from './NoteList';

interface SidebarProps {
  notes: Note[];
  selectedNoteId: string | null;
  onNotesChange: (notes: Note[]) => void;
  onSelectNote: (id: string) => void;
}

export default function Sidebar({ notes, selectedNoteId, onNotesChange, onSelectNote }: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredNotes = searchQuery
    ? notes.filter(note =>
        note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        note.content.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : notes;

  const handleDelete = async (id: string) => {
    try {
      await deleteNote(id);
      const newNotes = notes.filter(n => n._id !== id);
      onNotesChange(newNotes);
      if (selectedNoteId === id) {
        onSelectNote(newNotes[0]?._id || '');
      }
    } catch (error) {
      console.error('删除笔记失败:', error);
      alert('删除笔记失败，请重试');
    }
  };

  return (
    <aside className="w-80 border-r border-gray-200 flex flex-col bg-gray-50">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-bold mb-4">Simplenote</h1>
        <SearchBar value={searchQuery} onChange={setSearchQuery} />
      </div>

      <NewNoteButton
        onNoteCreated={(note) => {
          onNotesChange([note, ...notes]);
          onSelectNote(note._id);
        }}
      />

      <NoteList
        notes={filteredNotes}
        selectedId={selectedNoteId}
        onSelect={onSelectNote}
        onDelete={handleDelete}
      />
    </aside>
  );
}
