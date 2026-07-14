"""
tests/test_watchlist.py — CineLog

Tests for the watchlist service.
Modeled after tests/test_collection.py patterns.
"""

import pytest
from app import create_app, db
from models import User, Film, WatchlistEntry
from services.watchlist_service import (
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist,
    AlreadyInWatchlistError,
    NotInWatchlistError,
)
from services.collection_service import FilmNotFoundError


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    """A film to use in tests."""
    with app.app_context():
        film = Film(title="Paddington 2", year=2017, genre="Comedy")
        db.session.add(film)
        db.session.commit()
        return film.id


# ── Nonexistent film ─────────────────────────────────────────────────────────

def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """
    Adding a film_id that doesn't exist in the database should raise
    FilmNotFoundError, not a database integrity error.

    Modeled after test_add_to_collection_nonexistent_film_raises.
    """
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)


# ── Remove ───────────────────────────────────────────────────────────────────

def test_remove_from_watchlist_removes_entry(app, sample_user, sample_film):
    """
    remove_from_watchlist should delete an existing entry.
    Modeled after remove_from_collection patterns.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)
        assert remove_from_watchlist(user_id=sample_user, film_id=sample_film) is True

        remaining = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count()
        assert remaining == 0


def test_remove_from_watchlist_missing_raises(app, sample_user, sample_film):
    """
    Removing a film that is not on the watchlist should raise NotInWatchlistError.
    """
    with app.app_context():
        with pytest.raises(NotInWatchlistError):
            remove_from_watchlist(user_id=sample_user, film_id=sample_film)


# ── Deduplication (stretch edge case) ────────────────────────────────────────

def test_add_to_watchlist_duplicate_raises(app, sample_user, sample_film):
    """
    Adding the same film twice should raise AlreadyInWatchlistError,
    not silently create a duplicate entry.

    Chosen because Comment 3 only covered nonexistent film_id; this locks in
    the Comment 2 dedup behavior the same way test_add_to_collection_duplicate_raises
    does for collections.
    """
    with app.app_context():
        add_to_watchlist(user_id=sample_user, film_id=sample_film)

        with pytest.raises(AlreadyInWatchlistError):
            add_to_watchlist(user_id=sample_user, film_id=sample_film)

        count = WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count()
        assert count == 1


def test_add_to_watchlist_respects_public_flag(app, sample_user, sample_film):
    """Callers can set visibility explicitly via the public parameter."""
    with app.app_context():
        entry = add_to_watchlist(
            user_id=sample_user, film_id=sample_film, public=False
        )
        assert entry.public is False

