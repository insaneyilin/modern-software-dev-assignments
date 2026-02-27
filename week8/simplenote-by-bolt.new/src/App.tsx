import { useState } from 'react';
import { useNotes } from './hooks/useNotes';
import { Sidebar } from './components/Sidebar';
import { NoteEditor } from './components/NoteEditor';

function App() {
  const { notes, loading, createNote, updateNote, deleteNote } = useNotes();
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const selectedNote = notes.find((note) => note.id === selectedNoteId) || null;

  const handleCreateNote = async () => {
    const newNote = await createNote();
    if (newNote) {
      setSelectedNoteId(newNote.id);
    }
  };

  const handleUpdateNote = (title: string, content: string) => {
    if (selectedNoteId) {
      updateNote(selectedNoteId, title, content);
    }
  };

  const handleDeleteNote = () => {
    if (selectedNoteId) {
      deleteNote(selectedNoteId);
      setSelectedNoteId(null);
    }
  };

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      <Sidebar
        notes={notes}
        selectedNoteId={selectedNoteId}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onSelectNote={setSelectedNoteId}
        onNewNote={handleCreateNote}
        loading={loading}
      />
      <NoteEditor
        note={selectedNote}
        onUpdate={handleUpdateNote}
        onDelete={handleDeleteNote}
        saving={false}
      />
    </div>
  );
}

export default App;
