# Model Card: TuneMatch 2.0

## Model and Intended Use

TuneMatch 2.0 is a retrieval-augmented, rule-based music recommender. It is a classroom project that recommends items from a small fictional CSV catalog for a listener's current preferences. It is appropriate for demonstrating retrieval, ranking, confidence communication, and software reliability practices; it is not designed for commercial personalization or any high-stakes use.

## Original Project and Extension

The base project was the Module 3 **Music Recommender Simulation**. Its original goal was to rank a ten-song catalog from genre, mood, and energy preferences. TuneMatch 2.0 keeps that transparent scoring idea while adding an integrated retrieval stage, input and data validation, diversity-aware selection, logs, confidence, and reproducible evaluation.

## How the System Works

1. The listener supplies a favorite genre, mood, target energy, and acoustic preference.
2. The validator rejects empty categories and energy values outside 0.0–1.0.
3. The retriever selects a bounded group of relevant catalog records using genre, mood, energy, and acoustic similarity.
4. The ranker scores only those retrieved records: genre is worth 3 points, mood 2 points, energy similarity up to 1 point, and acoustic agreement 0.5 points.
5. The audit step favors artist variety when possible, estimates confidence from the strongest evidence, and warns if the catalog lacks an exact genre or mood match.

The output is constructed from the retrieved song fields and score reasons. No external model generates artists, lyrics, or facts that are not in the catalog.

## Data

The catalog has ten fictional records with title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. It represents pop, lofi, rock, ambient, jazz, synthwave, and indie pop. Most categories have one or two songs, so the data is too small and narrow to represent real listener diversity, global music culture, or evolving taste.

## Evaluation and Reliability

Automated tests cover ranking order, explanation content, bounded retrieval, profile validation, catalog-range validation, and the missing-category guardrail. The repeatable evaluation script runs four scenarios: energetic happy pop, acoustic chill lofi, relaxed acoustic jazz, and a classical/nostalgic catalog gap. It expects the first three known matches to rank first and the gap case to receive low confidence plus notes.

The current results are recorded in [evidence/evaluation_output.md](evidence/evaluation_output.md). The tests do not measure real listener satisfaction; they establish that the stated rules and safety behavior operate consistently.

## Strengths

- Every recommendation can be traced to a catalog row and an explicit score.
- Bad profiles and malformed catalog values fail early with useful messages.
- Low-evidence results are labeled rather than framed as confident matches.
- The complete system works locally without an API key or network request.

## Limitations, Bias, and Risks

- People whose tastes are absent from the catalog receive weak nearest matches.
- Exact category matching treats related labels as different, such as `pop` and `indie pop`.
- The fixed weights encode the designer's assumptions and may not reflect an individual listener's priorities.
- A catalog with more tracks from one genre or artist can give that group more opportunities to appear. The small artist-diversity step reduces repetition, but it does not solve catalog representation bias.
- The confidence value measures agreement with this catalog and scoring rule, not the probability that someone will enjoy a recommendation.

To reduce these risks in a future version, I would use a broader consented catalog, allow multiple and related preferences, add feedback-based evaluation with diverse listeners, and keep confidence warnings visible when evidence is thin.

## Human Oversight

A listener can inspect the explanation, change their preferences, or decide not to use a suggestion. For a larger deployment, a human should review catalog metadata, weight changes, and evaluation results before release. The automated checks are a regression aid, not a substitute for listening-based evaluation.

## AI Collaboration and Reflection

I used an AI coding assistant as a collaborator to help break the extension into small implementation tasks, draft test cases, and identify documentation that a reviewer would need. I reviewed the generated changes, selected the transparent rule-based approach, and checked that the examples and evaluation claims matched the program's behavior.

One helpful suggestion was to separate retrieval from final ranking. That made the recommendation evidence visible and gave the system a natural place to warn about missing catalog coverage. One flawed early suggestion was to treat a high energy similarity alone as a strong recommendation. I rejected that idea: the final version lowers confidence and shows a clear warning when no exact genre or mood evidence exists. This reinforced that AI suggestions need human review, especially when they could make an output sound more certain than the data supports.

I learned that building an AI system is as much about data limits, tests, and communication as it is about the scoring function. This implementation remains limited by its tiny catalog and cannot infer a person's identity, long-term taste, or likely enjoyment.
