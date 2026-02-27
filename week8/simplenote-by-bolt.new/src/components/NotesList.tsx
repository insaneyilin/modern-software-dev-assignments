import { Note } from '../lib/supabase';

interface NotesListProps {
  notes: Note[];
  selectedNoteId: string | null;
  onSelectNote: (id: string) => void;
  loading: boolean;
  hasSearchResults: boolean;
}

export function NotesList({
  notes,
  selectedNoteId,
  onSelectNote,
  loading,
  hasSearchResults,
}: NotesListProps) {
  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400">
        <p>Loading notes...</p>
      </div>
    );
  }

  if (notes.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 p-4 text-center">
        <p>{hasSearchResults ? 'No notes match your search' : 'No notes yet. Create one to get started!'}</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto">
      {notes.map((note) => (
        <button
          key={note.id}
          onClick={() => onSelectNote(note.id)}
          className={`w-full px-4 py-3 text-left border-b border-gray-200 hover:bg-gray-50 transition-colors ${
            selectedNoteId === note.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
          }`}
        >
          <h3 className="font-medium text-gray-900 truncate mb-1">
            {note.title || 'Untitled'}
          </h3>
          <p className="text-sm text-gray-500 line-clamp-2 mb-1">
            {note.content || 'No additional text'}
          </p>
          <p className="text-xs text-gray-400">
            {getTimeAgo(note.updated_at)}
          </p>
        </button>
      ))}
    </div>
  );
}

function getTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) {
    return 'just now';
  } else if (diffMins < 60) {
    return `${diffMins}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    const weeks = Math.floor(diffDays / 7);
    return `${weeks}w ago`;
  }
}
