import { getNotes } from './actions/note-actions';
import NotesApp from './components/NotesApp';

export default async function Home() {
  const initialNotes = await getNotes();

  return (
    <main>
      <NotesApp initialNotes={initialNotes} />
    </main>
  );
}
