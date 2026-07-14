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
**How I verified:**

## Comment 4 — Default visibility
**My position:**
**Reasoning:**
**Tradeoff acknowledged:**

## Comment 5 — Sort order
**My position:**
**Reasoning:**
**Engagement with reviewer's point:**

## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->
