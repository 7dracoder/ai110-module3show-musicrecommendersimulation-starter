# Reproducible Sample Runs

The following transcripts were generated with the checked-in `data/songs.csv`.

## Strong pop match

Command:

```text
python -m src.main --genre pop --mood happy --energy 0.8 --no-likes-acoustic --limit 3
```

Output:

```text
TuneMatch — retrieval-augmented music recommendations
Profile: genre=pop, mood=happy, energy=0.80, likes_acoustic=False
Retrieved 6 catalog records | confidence: 100%

1. Sunrise City — Neon Echo (score: 6.48)
   Recommended because genre matches pop; mood matches happy; energy is very close to your target; fits your preference for less acoustic music.
2. Gym Hero — Max Pulse (score: 4.37)
   Recommended because genre matches pop; energy is close to your target; fits your preference for less acoustic music.
3. Rooftop Lights — Indigo Parade (score: 3.46)
   Recommended because mood matches happy; energy is very close to your target; fits your preference for less acoustic music.
```

## Acoustic lofi session

Command:

```text
python -m src.main --genre lofi --mood chill --energy 0.4 --likes-acoustic --limit 3
```

Output:

```text
TuneMatch — retrieval-augmented music recommendations
Profile: genre=lofi, mood=chill, energy=0.40, likes_acoustic=True
Retrieved 6 catalog records | confidence: 100%

1. Midnight Coding — LoRoom (score: 6.48)
   Recommended because genre matches lofi; mood matches chill; energy is very close to your target; fits your preference for acoustic music.
2. Library Rain — Paper Lanterns (score: 6.45)
   Recommended because genre matches lofi; mood matches chill; energy is very close to your target; fits your preference for acoustic music.
3. Spacewalk Thoughts — Orbit Bloom (score: 3.38)
   Recommended because mood matches chill; energy is close to your target; fits your preference for acoustic music.
```

## Catalog gap guardrail

Command:

```text
python -m src.main --genre classical --mood nostalgic --energy 0.5 --likes-acoustic --limit 3
```

Output:

```text
TuneMatch — retrieval-augmented music recommendations
Profile: genre=classical, mood=nostalgic, energy=0.50, likes_acoustic=True
Retrieved 6 catalog records | confidence: 15%

1. Midnight Coding — LoRoom (score: 1.42)
   Recommended because energy is very close to your target; fits your preference for acoustic music.
2. Coffee Shop Stories — Slow Stereo (score: 1.37)
   Recommended because energy is close to your target; fits your preference for acoustic music.
3. Library Rain — Paper Lanterns (score: 1.35)
   Recommended because energy is close to your target; fits your preference for acoustic music.

Catalog notes:
- No exact genre or mood match exists in this small catalog; these are nearest matches.
- Low confidence: try a broader genre or mood, or add songs to the catalog.
```
