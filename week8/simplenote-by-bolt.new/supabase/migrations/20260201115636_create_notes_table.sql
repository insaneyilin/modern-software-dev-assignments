/*
  # Create notes table

  1. New Tables
    - `notes`
      - `id` (uuid, primary key)
      - `title` (text, note title)
      - `content` (text, note body content)
      - `created_at` (timestamp, creation time)
      - `updated_at` (timestamp, last update time)
  
  2. Security
    - Enable RLS on `notes` table
    - Add policy for public read access
    - Add policy for public create access
    - Add policy for public update access
    - Add policy for public delete access

  3. Indexes
    - Index on `updated_at` for efficient sorting
    - Index on `title` and `content` for search performance
*/

CREATE TABLE IF NOT EXISTS notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title text NOT NULL DEFAULT '',
  content text NOT NULL DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notes_updated_at ON notes(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);
CREATE INDEX IF NOT EXISTS idx_notes_content ON notes(content);

ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read"
  ON notes FOR SELECT
  TO anon
  USING (true);

CREATE POLICY "Allow public create"
  ON notes FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "Allow public update"
  ON notes FOR UPDATE
  TO anon
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete"
  ON notes FOR DELETE
  TO anon
  USING (true);
