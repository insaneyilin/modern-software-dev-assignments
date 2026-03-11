'use client';

import { useState } from 'react';
import { Note } from '@/types/note';
import Sidebar from './Sidebar';
import NoteEditor from './NoteEditor';

interface NotesAppProps {
  initialNotes: Note[];
}

export default function NotesApp({ initialNotes }: NotesAppProps) {
  const [notes, setNotes] = useState<Note[]>(initialNotes);
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(
    initialNotes[0]?._id || null
  );

  const selectedNote = notes.find(n => n._id === selectedNoteId) || null;

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        notes={notes}
        selectedNoteId={selectedNoteId}
        onNotesChange={setNotes}
        onSelectNote={setSelectedNoteId}
      />
      <NoteEditor
        note={selectedNote}
        onNoteUpdate={(updatedNote) => {
          setNotes(notes.map(n => n._id === updatedNote._id ? updatedNote : n));
        }}
      />
    </div>
  );
}
