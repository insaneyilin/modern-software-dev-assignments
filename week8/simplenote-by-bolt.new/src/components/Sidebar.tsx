import { Note } from '../lib/supabase';
import { SearchBar } from './SearchBar';
import { NotesList } from './NotesList';

interface SidebarProps {
  notes: Note[];
  selectedNoteId: string | null;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSelectNote: (id: string) => void;
  onNewNote: () => void;
  loading: boolean;
}

export function Sidebar({
  notes,
  selectedNoteId,
  searchQuery,
  onSearchChange,
  onSelectNote,
  onNewNote,
  loading,
}: SidebarProps) {
  const filteredNotes = notes.filter((note) => {
    const query = searchQuery.toLowerCase();
    return (
      note.title.toLowerCase().includes(query) ||
      note.content.toLowerCase().includes(query)
    );
  });

  return (
    <div className="w-80 border-r border-gray-200 bg-white flex flex-col">
      <SearchBar
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        onNewNote={onNewNote}
      />
      <NotesList
        notes={filteredNotes}
        selectedNoteId={selectedNoteId}
        onSelectNote={onSelectNote}
        loading={loading}
        hasSearchResults={searchQuery.length > 0 && filteredNotes.length === 0}
      />
    </div>
  );
}
