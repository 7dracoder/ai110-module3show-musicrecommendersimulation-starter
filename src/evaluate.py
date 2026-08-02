"""Repeatable reliability checks for the TuneMatch recommendation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.recommender import RecommendationAssistant, UserProfile, load_song_objects


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class EvaluationCase:
    name: str
    profile: UserProfile
    expected_first_title: str | None = None
    expect_low_confidence: bool = False


def run_evaluation() -> int:
    assistant = RecommendationAssistant(load_song_objects(PROJECT_ROOT / "data" / "songs.csv"))
    cases = [
        EvaluationCase(
            "exact pop match",
            UserProfile("pop", "happy", 0.8, False),
            expected_first_title="Sunrise City",
        ),
        EvaluationCase(
            "exact lofi match",
            UserProfile("lofi", "chill", 0.4, True),
            expected_first_title="Midnight Coding",
        ),
        EvaluationCase(
            "exact jazz match",
            UserProfile("jazz", "relaxed", 0.35, True),
            expected_first_title="Coffee Shop Stories",
        ),
        EvaluationCase(
            "catalog gap warning",
            UserProfile("classical", "nostalgic", 0.5, True),
            expect_low_confidence=True,
        ),
    ]

    passed = 0
    print("TuneMatch reliability evaluation")
    for case in cases:
        response = assistant.recommend(case.profile, k=3)
        first_title = response.recommendations[0].song.title
        title_ok = case.expected_first_title is None or first_title == case.expected_first_title
        confidence_ok = not case.expect_low_confidence or response.confidence < 0.5
        note_ok = not case.expect_low_confidence or bool(response.audit_notes)
        success = title_ok and confidence_ok and note_ok
        passed += int(success)
        status = "PASS" if success else "FAIL"
        print(
            f"[{status}] {case.name}: first={first_title}; "
            f"confidence={response.confidence:.2f}; notes={len(response.audit_notes)}"
        )

    print(f"\nSummary: {passed}/{len(cases)} checks passed.")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(run_evaluation())
