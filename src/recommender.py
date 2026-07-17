from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return up to ``k`` songs, ordered from best to worst match."""
        if k <= 0:
            return []

        def score(song: Song) -> float:
            total = 0.0
            if song.genre.casefold() == user.favorite_genre.casefold():
                total += 3.0
            if song.mood.casefold() == user.favorite_mood.casefold():
                total += 2.0

            # Energy contributes at most one point and decreases smoothly as
            # the song moves away from the user's target.
            total += max(0.0, 1.0 - abs(song.energy - user.target_energy))

            is_acoustic = song.acousticness >= 0.5
            if is_acoustic == user.likes_acoustic:
                total += 0.5
            return total

        return sorted(self.songs, key=score, reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain the parts of a song that match the supplied profile."""
        reasons = []
        if song.genre.casefold() == user.favorite_genre.casefold():
            reasons.append(f"it matches your favorite genre ({song.genre})")
        if song.mood.casefold() == user.favorite_mood.casefold():
            reasons.append(f"it matches your favorite mood ({song.mood})")

        energy_difference = abs(song.energy - user.target_energy)
        if energy_difference <= 0.1:
            reasons.append("its energy is very close to your target")
        elif energy_difference <= 0.25:
            reasons.append("its energy is reasonably close to your target")

        is_acoustic = song.acousticness >= 0.5
        if is_acoustic == user.likes_acoustic:
            preference = "acoustic" if user.likes_acoustic else "less acoustic"
            reasons.append(f"it fits your preference for {preference} music")

        if not reasons:
            return "This song is one of the closest available matches in the catalog."
        return "Recommended because " + ", ".join(reasons) + "."

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    numeric_fields = {
        "id": int,
        "energy": float,
        "tempo_bpm": float,
        "valence": float,
        "danceability": float,
        "acousticness": float,
    }
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            for field, converter in numeric_fields.items():
                row[field] = converter(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    preferred_genre = str(user_prefs.get("genre", ""))
    preferred_mood = str(user_prefs.get("mood", ""))
    song_genre = str(song.get("genre", ""))
    song_mood = str(song.get("mood", ""))

    if preferred_genre and song_genre.casefold() == preferred_genre.casefold():
        score += 3.0
        reasons.append(f"genre matches {preferred_genre}")
    if preferred_mood and song_mood.casefold() == preferred_mood.casefold():
        score += 2.0
        reasons.append(f"mood matches {preferred_mood}")

    if "energy" in user_prefs and "energy" in song:
        energy_difference = abs(float(song["energy"]) - float(user_prefs["energy"]))
        energy_points = max(0.0, 1.0 - energy_difference)
        score += energy_points
        if energy_difference <= 0.1:
            reasons.append("energy is very close to your target")
        elif energy_difference <= 0.25:
            reasons.append("energy is close to your target")

    if not reasons:
        reasons.append("it is one of the closest available catalog matches")
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    if k <= 0:
        return []

    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored_songs.append((song, score, "; ".join(reasons)))

    scored_songs.sort(key=lambda recommendation: recommendation[1], reverse=True)
    return scored_songs[:k]
