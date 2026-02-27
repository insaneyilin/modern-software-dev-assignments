import { useState, useEffect, useCallback } from 'react';
import { supabase, type Note } from '../lib/supabase';

export function useNotes() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNotes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const { data, error: err } = await supabase
        .from('notes')
        .select('*')
        .order('updated_at', { ascending: false });

      if (err) throw err;
      setNotes(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch notes');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);

  const createNote = useCallback(async () => {
    try {
      const { data, error: err } = await supabase
        .from('notes')
        .insert([{ title: 'Untitled Note', content: '' }])
        .select()
        .single();

      if (err) throw err;
      if (data) {
        setNotes((prev) => [data, ...prev]);
        return data;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create note');
    }
  }, []);

  const updateNote = useCallback(
    async (id: string, title: string, content: string) => {
      try {
        const { data, error: err } = await supabase
          .from('notes')
          .update({ title, content, updated_at: new Date().toISOString() })
          .eq('id', id)
          .select()
          .single();

        if (err) throw err;
        if (data) {
          setNotes((prev) =>
            prev.map((note) => (note.id === id ? data : note))
          );
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update note');
      }
    },
    []
  );

  const deleteNote = useCallback(async (id: string) => {
    try {
      const { error: err } = await supabase.from('notes').delete().eq('id', id);

      if (err) throw err;
      setNotes((prev) => prev.filter((note) => note.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete note');
    }
  }, []);

  return {
    notes,
    loading,
    error,
    createNote,
    updateNote,
    deleteNote,
    fetchNotes,
  };
}
