import { useState, useEffect } from 'react';
import { Trash2 } from 'lucide-react';
import { Note } from '../lib/supabase';

interface NoteEditorProps {
  note: Note | null;
  onUpdate: (title: string, content: string) => void;
  onDelete: () => void;
  saving: boolean;
}

export function NoteEditor({ note, onUpdate, onDelete, saving }: NoteEditorProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | null>(null);

  useEffect(() => {
    if (note) {
      setTitle(note.title);
      setContent(note.content);
      setUnsavedChanges(false);
      setSaveStatus(null);
    }
  }, [note]);

  useEffect(() => {
    if (!unsavedChanges || !note) return;

    setSaveStatus('saving');
    const timer = setTimeout(() => {
      onUpdate(title, content);
      setSaveStatus('saved');
      setUnsavedChanges(false);

      const clearTimer = setTimeout(() => setSaveStatus(null), 2000);
      return () => clearTimeout(clearTimer);
    }, 1000);

    return () => clearTimeout(timer);
  }, [unsavedChanges, title, content, note, onUpdate]);

  const handleTitleChange = (value: string) => {
    setTitle(value);
    setUnsavedChanges(true);
  };

  const handleContentChange = (value: string) => {
    setContent(value);
    setUnsavedChanges(true);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      onDelete();
    }
  };

  if (!note) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50 text-gray-400">
        <p>Select a note to begin editing</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex-1">
          <input
            type="text"
            value={title}
            onChange={(e) => handleTitleChange(e.target.value)}
            placeholder="Untitled Note"
            className="text-2xl font-semibold w-full focus:outline-none"
          />
        </div>
        <button
          onClick={handleDelete}
          className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
          title="Delete note"
        >
          <Trash2 size={20} />
        </button>
      </div>

      <div className="px-6 py-2 border-b border-gray-200 flex items-center justify-between text-sm text-gray-500">
        <div>
          Created {new Date(note.created_at).toLocaleDateString()}
        </div>
        <div>
          {saveStatus === 'saving' && <span className="text-blue-500">Saving...</span>}
          {saveStatus === 'saved' && <span className="text-green-500">Saved</span>}
          {!unsavedChanges && !saveStatus && <span>All changes saved</span>}
          {unsavedChanges && <span className="text-orange-500">Unsaved changes</span>}
        </div>
      </div>

      <textarea
        value={content}
        onChange={(e) => handleContentChange(e.target.value)}
        placeholder="Start typing your note..."
        className="flex-1 px-6 py-4 resize-none focus:outline-none"
      />
    </div>
  );
}
