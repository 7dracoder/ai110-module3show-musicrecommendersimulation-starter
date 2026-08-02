"""Command-line entry point for the TuneMatch applied AI system."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.recommender import (
    ProfileValidationError,
    RecommendationAssistant,
    UserProfile,
    load_song_objects,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def configure_logging(log_path: Path) -> None:
    """Record normal operations and errors in a reusable, timestamped log."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
        force=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Retrieve and rank music recommendations from a local catalog."
    )
    parser.add_argument("--genre", default="pop", help="favorite genre (default: pop)")
    parser.add_argument("--mood", default="happy", help="favorite mood (default: happy)")
    parser.add_argument(
        "--energy",
        type=float,
        default=0.8,
        help="target energy from 0.0 to 1.0 (default: 0.8)",
    )
    parser.add_argument(
        "--likes-acoustic",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="whether acoustic music suits this listening session",
    )
    parser.add_argument("--limit", type=int, default=5, help="number of songs to return")
    parser.add_argument(
        "--data",
        type=Path,
        default=PROJECT_ROOT / "data" / "songs.csv",
        help="path to the CSV catalog",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=PROJECT_ROOT / "logs" / "recommender.log",
        help="where to write the application log",
    )
    return parser


def format_response(profile: UserProfile, response) -> str:
    """Turn a grounded recommendation response into readable terminal output."""
    lines = [
        "\nTuneMatch — retrieval-augmented music recommendations",
        (
            f"Profile: genre={profile.favorite_genre}, mood={profile.favorite_mood}, "
            f"energy={profile.target_energy:.2f}, likes_acoustic={profile.likes_acoustic}"
        ),
        (
            f"Retrieved {response.retrieved_count} catalog records | "
            f"confidence: {response.confidence:.0%}\n"
        ),
    ]
    for index, recommendation in enumerate(response.recommendations, start=1):
        song = recommendation.song
        lines.extend(
            [
                f"{index}. {song.title} — {song.artist} (score: {recommendation.score:.2f})",
                f"   {recommendation.explanation}",
            ]
        )
    if response.audit_notes:
        lines.append("\nCatalog notes:")
        lines.extend(f"- {note}" for note in response.audit_notes)
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    configure_logging(args.log_file)
    logger = logging.getLogger(__name__)
    try:
        profile = UserProfile(
            favorite_genre=args.genre,
            favorite_mood=args.mood,
            target_energy=args.energy,
            likes_acoustic=args.likes_acoustic,
        )
        assistant = RecommendationAssistant(load_song_objects(args.data))
        response = assistant.recommend(profile, k=args.limit)
    except (OSError, ValueError, ProfileValidationError) as error:
        logger.exception("recommendation request could not be completed")
        print(f"Could not create recommendations: {error}")
        return 1

    print(format_response(profile, response))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
