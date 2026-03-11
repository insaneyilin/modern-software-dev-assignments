require "test_helper"

class NoteTest < ActiveSupport::TestCase
  test "should be valid with title" do
    note = Note.new(title: "Test", content: "")
    assert note.valid?
  end
  
  test "should be valid with content" do
    note = Note.new(title: "", content: "Content")
    assert note.valid?
  end
  
  test "should be invalid without title and content" do
    note = Note.new(title: "", content: "")
    assert_not note.valid?
  end
  
  test "display_title returns title when present" do
    note = Note.new(title: "My Title")
    assert_equal "My Title", note.display_title
  end
  
  test "display_title returns Untitled when title is blank" do
    note = Note.new(title: "")
    assert_equal "Untitled", note.display_title
  end
  
  test "search finds by title" do
    note = Note.create!(title: "Searchable", content: "")
    results = Note.search("Search")
    assert_includes results, note
  end
  
  test "search finds by content" do
    note = Note.create!(title: "", content: "Find me")
    results = Note.search("Find")
    assert_includes results, note
  end
end
