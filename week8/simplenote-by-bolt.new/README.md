# Simplenote Clone

A modern, minimal note-taking application built with React, TypeScript, and Supabase. Create, edit, search, and delete notes with an intuitive interface inspired by Simplenote.

## Features

- **Create Notes** - Quickly create new notes with a single click
- **Edit & Auto-Save** - Type freely with automatic saving (debounced for smooth performance)
- **Delete Notes** - Remove unwanted notes with a confirmation dialog
- **Full-Text Search** - Search notes by title and content in real-time
- **Persistent Storage** - All notes are stored in Supabase
- **Clean UI** - Minimal, distraction-free interface
- **Responsive Design** - Split-pane layout with sidebar and editor

## Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Build Tool**: Vite
- **Database**: Supabase (PostgreSQL)
- **Icons**: Lucide React
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Supabase account and project

### Setup

1. **Clone the repository** (if applicable)
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure Supabase**
   - Create a `.env` file in the project root with your Supabase credentials:
   ```env
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

5. **Build for production**
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── components/
│   ├── NoteEditor.tsx      # Main editor panel with title, content, and delete
│   ├── NotesList.tsx       # Sidebar list of notes
│   ├── SearchBar.tsx       # Search input and new note button
│   └── Sidebar.tsx         # Left sidebar container
├── hooks/
│   └── useNotes.ts         # Custom hook for CRUD operations
├── lib/
│   └── supabase.ts         # Supabase client configuration and types
├── App.tsx                 # Main app component and state management
├── main.tsx                # React DOM entry point
├── index.css               # Tailwind CSS imports
└── vite-env.d.ts          # Vite environment type definitions
```

## Usage

### Creating a Note

1. Click the **"New Note"** button in the top left
2. Enter a title and start typing your content
3. Changes are automatically saved

### Searching Notes

1. Use the search bar to filter notes by title or content
2. Results update in real-time as you type
3. Clear the search to see all notes again

### Editing a Note

1. Select a note from the sidebar
2. Edit the title and content directly
3. Changes are saved automatically with visual feedback

### Deleting a Note

1. Select the note you want to delete
2. Click the trash icon in the editor header
3. Confirm the deletion

## Database Schema

### notes table

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| title | text | Note title |
| content | text | Note body content |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last update time |

## API Reference

### useNotes Hook

Custom React hook for managing notes:

```typescript
const {
  notes,           // Array of all notes
  loading,         // Loading state
  error,           // Error message if any
  createNote,      // Function to create a new note
  updateNote,      // Function to update a note (id, title, content)
  deleteNote,      // Function to delete a note (id)
  fetchNotes       // Function to manually refresh notes
} = useNotes();
```

## Performance Considerations

- **Auto-Save Debouncing**: Updates are debounced by 1 second to prevent excessive database writes
- **Indexed Columns**: Title, content, and updated_at are indexed for fast search and sorting
- **Lazy Loading**: Notes are fetched once on component mount
- **Optimistic Updates**: UI updates immediately while database changes are sent asynchronously

## Security

- Row Level Security (RLS) is enabled on the notes table
- All database access goes through Supabase's secure API
- Environment variables keep sensitive credentials out of the codebase

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Future Enhancements

- User authentication and per-user notes
- Markdown rendering and syntax highlighting
- Note pinning and favorites
- Tags and categories
- Export to various formats (PDF, Markdown, TXT)
- Keyboard shortcuts
- Dark mode
- Note sharing and collaboration

## License

MIT

## Support

For issues or questions, please refer to the project documentation or contact the development team.
