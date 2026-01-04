def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_search_case_insensitive_title(client):
    """Test that search is case-insensitive for title field"""
    # Create test notes
    client.post("/notes/", json={"title": "Python Tutorial", "content": "Learn Python"})
    client.post("/notes/", json={"title": "JavaScript Guide", "content": "Learn JS"})

    # Search with lowercase should find "Python Tutorial"
    r = client.get("/notes/search/", params={"q": "python"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["title"] == "Python Tutorial"

    # Search with uppercase should also find it
    r = client.get("/notes/search/", params={"q": "PYTHON"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["title"] == "Python Tutorial"

    # Search with mixed case should also find it
    r = client.get("/notes/search/", params={"q": "PyThOn"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["title"] == "Python Tutorial"


def test_search_case_insensitive_content(client):
    """Test that search is case-insensitive for content field"""
    # Create test notes
    client.post("/notes/", json={"title": "Note 1", "content": "Important Meeting Notes"})
    client.post("/notes/", json={"title": "Note 2", "content": "Random thoughts"})

    # Search with lowercase should find "Important Meeting Notes"
    r = client.get("/notes/search/", params={"q": "meeting"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["content"] == "Important Meeting Notes"

    # Search with uppercase should also find it
    r = client.get("/notes/search/", params={"q": "MEETING"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["content"] == "Important Meeting Notes"


def test_search_matches_title_or_content(client):
    """Test that search matches either title or content"""
    # Create test notes
    client.post("/notes/", json={"title": "Database Design", "content": "SQL basics"})
    client.post("/notes/", json={"title": "API Guide", "content": "Database connections"})

    # Search for "database" should find both notes (one in title, one in content)
    r = client.get("/notes/search/", params={"q": "database"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 2
    titles = [item["title"] for item in items]
    assert "Database Design" in titles
    assert "API Guide" in titles


def test_search_no_results(client):
    """Test that search returns empty list when no matches found"""
    # Create test notes
    client.post("/notes/", json={"title": "Test Note", "content": "Test content"})

    # Search for something that doesn't exist
    r = client.get("/notes/search/", params={"q": "nonexistent"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 0


def test_search_empty_query(client):
    """Test that empty query returns all notes"""
    # Create test notes
    client.post("/notes/", json={"title": "Note 1", "content": "Content 1"})
    client.post("/notes/", json={"title": "Note 2", "content": "Content 2"})

    # Empty query should return all notes
    r = client.get("/notes/search/", params={"q": ""})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2

    # No query parameter should also return all notes
    r = client.get("/notes/search/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2


def test_search_partial_match(client):
    """Test that search finds partial matches"""
    # Create test note
    client.post("/notes/", json={"title": "Understanding", "content": "Comprehensive guide"})

    # Partial match should work
    r = client.get("/notes/search/", params={"q": "under"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["title"] == "Understanding"

    # Partial match in content
    r = client.get("/notes/search/", params={"q": "comprehen"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["content"] == "Comprehensive guide"
