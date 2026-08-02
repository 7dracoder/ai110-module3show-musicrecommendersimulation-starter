from pathlib import Path

import pytest

from src.recommender import (
    ProfileValidationError,
    RecommendationAssistant,
    Recommender,
    Song,
    SongRetriever,
    UserProfile,
    load_songs,
)


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Second Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile("pop", "happy", 0.8, False)
    results = make_small_recommender().recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile("pop", "happy", 0.8, False)
    recommender = make_small_recommender()

    explanation = recommender.explain_recommendation(user, recommender.songs[0])

    assert isinstance(explanation, str)
    assert "genre matches pop" in explanation


def test_retriever_returns_a_bounded_candidate_set():
    user = UserProfile("pop", "happy", 0.8, False)
    songs = make_small_recommender().songs

    candidates = SongRetriever(songs).retrieve(user, limit=1)

    assert [song.title for song in candidates] == ["Test Pop Track"]


def test_assistant_audits_a_catalog_gap():
    assistant = RecommendationAssistant(make_small_recommender().songs)
    response = assistant.recommend(UserProfile("classical", "nostalgic", 0.5, True), k=2)

    assert response.confidence < 0.5
    assert any("No exact genre or mood match" in note for note in response.audit_notes)


def test_invalid_energy_is_rejected_before_retrieval():
    assistant = RecommendationAssistant(make_small_recommender().songs)

    with pytest.raises(ProfileValidationError, match="between 0 and 1"):
        assistant.recommend(UserProfile("pop", "happy", 1.2, False))


def test_load_songs_rejects_out_of_range_catalog_values(tmp_path: Path):
    catalog = tmp_path / "bad_songs.csv"
    catalog.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n"
        "1,Bad,Artist,pop,happy,1.2,120,0.5,0.5,0.5\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="energy"):
        load_songs(catalog)
