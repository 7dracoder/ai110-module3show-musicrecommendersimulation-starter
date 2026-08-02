"""Core retrieval, ranking, and safety checks for TuneMatch.

The project intentionally uses transparent rules instead of a black-box model.
It first retrieves the most relevant catalog records, ranks only that evidence,
and then attaches a confidence score and any appropriate catalog warning.
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


logger = logging.getLogger(__name__)

MAX_SCORE = 6.5


class ProfileValidationError(ValueError):
    """Raised when a listener profile cannot be used safely."""


@dataclass(frozen=True)
class Song:
    """One catalog record used as evidence for a recommendation."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass(frozen=True)
class UserProfile:
    """The preferences a listener supplies for their current session."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


@dataclass(frozen=True)
class Recommendation:
    """A ranked recommendation together with its catalog-grounded evidence."""

    song: Song
    score: float
    explanation: str


@dataclass(frozen=True)
class RecommendationResponse:
    """The complete output of the retrieval-augmented recommendation flow."""

    recommendations: Tuple[Recommendation, ...]
    retrieved_count: int
    confidence: float
    audit_notes: Tuple[str, ...]


def validate_profile(user: UserProfile) -> None:
    """Reject incomplete or out-of-range preferences before ranking songs."""
    if not isinstance(user.favorite_genre, str) or not user.favorite_genre.strip():
        raise ProfileValidationError("favorite_genre must be a non-empty value")
    if not isinstance(user.favorite_mood, str) or not user.favorite_mood.strip():
        raise ProfileValidationError("favorite_mood must be a non-empty value")
    if (
        isinstance(user.target_energy, bool)
        or not isinstance(user.target_energy, (int, float))
        or not 0.0 <= user.target_energy <= 1.0
    ):
        raise ProfileValidationError("target_energy must be between 0 and 1")
    if not isinstance(user.likes_acoustic, bool):
        raise ProfileValidationError("likes_acoustic must be true or false")


def _energy_similarity(song_energy: float, target_energy: float) -> float:
    """Return a transparent 0--1 similarity value for two energy ratings."""
    return max(0.0, 1.0 - abs(song_energy - target_energy))


class SongRetriever:
    """Find relevant catalog records before the final recommendation ranking.

    Retrieval is deliberately broader than the final ranker. This helps the
    system preserve near matches when the catalog has no exact match.
    """

    def __init__(self, songs: Sequence[Song]):
        self.songs = list(songs)

    def retrieve(self, user: UserProfile, limit: int = 7) -> List[Song]:
        validate_profile(user)
        if limit <= 0:
            return []

        def retrieval_score(song: Song) -> float:
            score = 0.5 * _energy_similarity(song.energy, user.target_energy)
            if song.genre.casefold() == user.favorite_genre.strip().casefold():
                score += 4.0
            if song.mood.casefold() == user.favorite_mood.strip().casefold():
                score += 3.0
            if (song.acousticness >= 0.5) == user.likes_acoustic:
                score += 0.5
            return score

        ranked = sorted(self.songs, key=retrieval_score, reverse=True)
        candidates = ranked[: min(limit, len(ranked))]
        logger.info("retrieved %s catalog records for recommendation", len(candidates))
        return candidates


class Recommender:
    """Transparent ranker kept compatible with the original class API."""

    def __init__(self, songs: Sequence[Song]):
        self.songs = list(songs)

    def score(self, user: UserProfile, song: Song) -> float:
        """Calculate a score out of ``MAX_SCORE`` for one evidence record."""
        total = 0.0
        if song.genre.casefold() == user.favorite_genre.strip().casefold():
            total += 3.0
        if song.mood.casefold() == user.favorite_mood.strip().casefold():
            total += 2.0
        total += _energy_similarity(song.energy, user.target_energy)
        if (song.acousticness >= 0.5) == user.likes_acoustic:
            total += 0.5
        return total

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return up to ``k`` songs, ordered from best to worst match."""
        validate_profile(user)
        if k <= 0:
            return []
        return sorted(self.songs, key=lambda song: self.score(user, song), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain only the profile features that actually affected a score."""
        reasons = []
        if song.genre.casefold() == user.favorite_genre.strip().casefold():
            reasons.append(f"genre matches {song.genre}")
        if song.mood.casefold() == user.favorite_mood.strip().casefold():
            reasons.append(f"mood matches {song.mood}")

        energy_difference = abs(song.energy - user.target_energy)
        if energy_difference <= 0.1:
            reasons.append("energy is very close to your target")
        elif energy_difference <= 0.25:
            reasons.append("energy is close to your target")

        if (song.acousticness >= 0.5) == user.likes_acoustic:
            preference = "acoustic" if user.likes_acoustic else "less acoustic"
            reasons.append(f"fits your preference for {preference} music")

        if not reasons:
            return "This is one of the closest available matches in the catalog."
        return "Recommended because " + "; ".join(reasons) + "."

    def ranked_recommendations(
        self, user: UserProfile, candidates: Sequence[Song]
    ) -> List[Recommendation]:
        """Rank retrieved evidence and retain a score plus human-readable reason."""
        ranked = [
            Recommendation(
                song=song,
                score=self.score(user, song),
                explanation=self.explain_recommendation(user, song),
            )
            for song in candidates
        ]
        return sorted(ranked, key=lambda result: result.score, reverse=True)


class RecommendationAssistant:
    """Coordinates validation, retrieval, ranking, diversity, and auditing."""

    def __init__(self, songs: Sequence[Song]):
        if not songs:
            raise ValueError("The song catalog cannot be empty")
        self.songs = list(songs)
        self.retriever = SongRetriever(songs)
        self.ranker = Recommender(songs)

    def recommend(self, user: UserProfile, k: int = 5) -> RecommendationResponse:
        """Create a grounded recommendation response for one listener profile."""
        validate_profile(user)
        if k <= 0:
            raise ProfileValidationError("k must be greater than zero")

        retrieval_limit = min(len(self.songs), max(k * 2, 5))
        candidates = self.retriever.retrieve(user, limit=retrieval_limit)
        ranked = self.ranker.ranked_recommendations(user, candidates)
        selected = self._select_diverse_artists(ranked, k)
        confidence = self._confidence(user, selected)
        notes = self._audit(user, selected, confidence, k)

        logger.info(
            "recommendation completed: returned=%s retrieved=%s confidence=%.2f notes=%s",
            len(selected),
            len(candidates),
            confidence,
            len(notes),
        )
        return RecommendationResponse(
            recommendations=tuple(selected),
            retrieved_count=len(candidates),
            confidence=confidence,
            audit_notes=tuple(notes),
        )

    @staticmethod
    def _select_diverse_artists(
        ranked: Sequence[Recommendation], k: int
    ) -> List[Recommendation]:
        """Prefer distinct artists until a second pass is needed to fill ``k``."""
        selected: List[Recommendation] = []
        seen_artists = set()
        for recommendation in ranked:
            artist_key = recommendation.song.artist.casefold()
            if artist_key not in seen_artists:
                selected.append(recommendation)
                seen_artists.add(artist_key)
            if len(selected) == k:
                return selected

        for recommendation in ranked:
            if recommendation not in selected:
                selected.append(recommendation)
            if len(selected) == k:
                break
        return selected

    @staticmethod
    def _confidence(
        user: UserProfile, recommendations: Sequence[Recommendation]
    ) -> float:
        """Estimate confidence from the strongest catalog-supported match."""
        if not recommendations:
            return 0.0
        best = recommendations[0]
        category_matches = int(
            best.song.genre.casefold() == user.favorite_genre.strip().casefold()
        ) + int(best.song.mood.casefold() == user.favorite_mood.strip().casefold())
        score_component = best.score / MAX_SCORE
        category_component = category_matches / 2
        return round(min(1.0, 0.7 * score_component + 0.3 * category_component), 2)

    @staticmethod
    def _audit(
        user: UserProfile,
        recommendations: Sequence[Recommendation],
        confidence: float,
        requested_count: int,
    ) -> List[str]:
        """Add clear guardrail messages instead of overstating weak results."""
        notes: List[str] = []
        if requested_count > len(recommendations):
            notes.append(
                f"Only {len(recommendations)} songs are available after retrieval."
            )
        exact_category_match = any(
            item.song.genre.casefold() == user.favorite_genre.strip().casefold()
            or item.song.mood.casefold() == user.favorite_mood.strip().casefold()
            for item in recommendations
        )
        if not exact_category_match:
            notes.append(
                "No exact genre or mood match exists in this small catalog; these are nearest matches."
            )
        if confidence < 0.5:
            notes.append(
                "Low confidence: try a broader genre or mood, or add songs to the catalog."
            )
        return notes


def load_songs(csv_path: str | Path) -> List[Dict]:
    """Load and type-check records from the original CSV-based starter project."""
    numeric_fields = {
        "id": int,
        "energy": float,
        "tempo_bpm": float,
        "valence": float,
        "danceability": float,
        "acousticness": float,
    }
    songs: List[Dict] = []
    try:
        with open(csv_path, newline="", encoding="utf-8") as csv_file:
            for line_number, row in enumerate(csv.DictReader(csv_file), start=2):
                for field, converter in numeric_fields.items():
                    if not row.get(field):
                        raise ValueError(f"missing {field!r} on CSV line {line_number}")
                    row[field] = converter(row[field])
                for field in ("energy", "valence", "danceability", "acousticness"):
                    if not 0.0 <= row[field] <= 1.0:
                        raise ValueError(
                            f"{field!r} must be between 0 and 1 on CSV line {line_number}"
                        )
                songs.append(row)
    except (OSError, ValueError) as error:
        logger.error("could not load catalog %s: %s", csv_path, error)
        raise

    if not songs:
        raise ValueError("The song catalog is empty")
    logger.info("loaded %s songs from %s", len(songs), csv_path)
    return songs


def load_song_objects(csv_path: str | Path) -> List[Song]:
    """Load CSV evidence into the dataclass API used by the full pipeline."""
    return [Song(**row) for row in load_songs(csv_path)]


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a dictionary record for backward compatibility with the starter app."""
    score = 0.0
    reasons = []
    preferred_genre = str(user_prefs.get("genre", "")).strip()
    preferred_mood = str(user_prefs.get("mood", "")).strip()
    song_genre = str(song.get("genre", ""))
    song_mood = str(song.get("mood", ""))

    if preferred_genre and song_genre.casefold() == preferred_genre.casefold():
        score += 3.0
        reasons.append(f"genre matches {preferred_genre}")
    if preferred_mood and song_mood.casefold() == preferred_mood.casefold():
        score += 2.0
        reasons.append(f"mood matches {preferred_mood}")
    if "energy" in user_prefs and "energy" in song:
        difference = abs(float(song["energy"]) - float(user_prefs["energy"]))
        score += _energy_similarity(float(song["energy"]), float(user_prefs["energy"]))
        if difference <= 0.1:
            reasons.append("energy is very close to your target")
        elif difference <= 0.25:
            reasons.append("energy is close to your target")
    if not reasons:
        reasons.append("it is one of the closest available catalog matches")
    return score, reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Original functional interface, retained for starter-project compatibility."""
    if k <= 0:
        return []
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    return sorted(scored, key=lambda recommendation: recommendation[1], reverse=True)[:k]
