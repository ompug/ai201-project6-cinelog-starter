# PR Response Doc — CineLog Watchlist Feature

## AI Usage
<!-- Fill in at the end — how you used AI tools during this project -->

## Comment 1 — Rename
**What I did:**
Renamed `save_to_watchlist()` to `add_to_watchlist()` in `services/watchlist_service.py` so it matches the project's `verb_to_noun` naming convention (same pattern as `add_to_collection()`). Updated the import and call site in `routes/watchlist/watchlist.py`.

**How I verified:**
I searched the whole repo for `save_to_watchlist` (ripgrep) and confirmed only two hits before the rename: the function definition and the route import/call. After the change, that search returned zero matches. I also ran `pytest tests/ -v` to make sure nothing else broke.

## Comment 2 — Deduplication
**What I did:**
Looked at how `add_to_collection()` in `services/collection_service.py` handles duplicates: it queries for an existing `CollectionEntry` with the same `user_id` + `film_id`, and if one exists it raises `AlreadyInCollectionError` instead of inserting again. I followed that exact pattern in `add_to_watchlist()` — check `WatchlistEntry.query.filter_by(user_id=..., film_id=...).first()`, and if a row is found raise a new `AlreadyInWatchlistError`. The watchlist add route now catches that error and returns HTTP 409 (same status the collection route uses for duplicates).

**How I verified:**
Compared the new check side-by-side with `add_to_collection()`'s dedup block. Ran `pytest tests/ -v` after the change to confirm the existing suite still passes. (A dedicated duplicate-edge-case test for watchlist comes later as a stretch feature.)

## Comment 3 — Missing test
**What I did:**
Created `tests/test_watchlist.py` with `test_add_to_watchlist_nonexistent_film_raises`. It uses the same fixtures pattern as `tests/test_collection.py` (`app`, `sample_user`) and asserts that calling `add_to_watchlist` with a fake film id raises `FilmNotFoundError` — exactly the case the reviewer asked for.

**How I verified:**
Modeled the test directly on `test_add_to_collection_nonexistent_film_raises` (same fake UUID, same `pytest.raises(FilmNotFoundError)` structure). Ran `pytest tests/test_watchlist.py -v` and then the full suite.

## Comment 4 — Default visibility
**My position:**
Keep `public=True` as the default for new watchlist entries.

**Reasoning:**
CineLog is a community film-tracking app, not a private diary. The value of a watchlist here is partly social: friends browse what someone is planning to watch the same way they browse collections of films already logged. If new saves defaulted to private, most entries would never surface in that discovery loop unless the user remembered to flip a toggle every time — and "to-watch" adds are often quick, low-friction gestures. Defaulting to public matches that gesture and keeps the social layer alive without requiring setup. Users who want a private backlog can still opt out per entry once we expose a visibility control (see stretch), but the common path should favor sharing.

**Tradeoff acknowledged:**
A private default would better protect people who treat their watchlist as a personal queue and don't want others seeing half-formed taste signal (or spoiler-adjacent titles). That safer default is real for privacy-minded users. I'm still choosing public because CineLog's product promise leans community discovery first; the cost of an accidental public entry is recoverable with an edit, while a private-by-default world quietly kills the "what's on your radar?" interaction that makes public lists interesting in the first place.

## Comment 5 — Sort order
**My position:**
Sort watchlists by `date_added` descending (newest first), matching `get_collection()`.

**Reasoning:**
A watchlist is a queue of intent — "I just saved this, I want to pick it up soon." Chronological newest-first is how people revisit that queue in practice: recent saves are the ones still warm, older ones drift into backlog. Alphabetical title sort forces you to scan for the movie you remember saving yesterday instead of finding it at the top. Aligning with collection sort also keeps mental models consistent across both user lists in CineLog.

**Engagement with reviewer's point:**
I agree with the maintainer that most users want to see what they added recently. That's especially true for watchlists: the "added recently" stack is the actionable part of the list, while A–Z is more useful when you're hunting a known title in a large archive. Alphabetical still isn't wrong as a future secondary sort/filter option, but for the default response from `get_watchlist()` I think date-added newest-first is the right call — so I changed the query accordingly.

## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->
