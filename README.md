# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This version ranks a small catalog of songs by comparing each song's genre,
mood, and energy with a listener's preferences. The object-oriented version
also considers whether the listener likes acoustic music. It returns the
strongest matches first and provides a plain-language reason for each result.

---

## How The System Works

Each `Song` stores its title and artist along with genre, mood, energy, tempo,
valence, danceability, and acousticness. A `UserProfile` stores a favorite
genre, favorite mood, target energy, and whether the listener likes acoustic
music.

The recommender gives 3 points for a genre match and 2 points for a mood match.
Energy adds up to 1 point: a song at the target gets the full point, while a
song farther from the target gets less. The object-oriented recommender adds
0.5 point when a song's acousticness agrees with the user's preference. Songs
are sorted from highest to lowest total, and the first `k` are returned. Exact
genre and mood matches therefore matter most, while numeric features refine
the ranking.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Example output from the starter profile:

```
User profile: genre=pop, mood=happy, energy=0.8
Recommendations:
  1. Sunrise City - Score: 5.98
     Because: genre matches pop; mood matches happy; energy is very close to your target
  2. Gym Hero - Score: 3.87
     Because: genre matches pop; energy is close to your target
  3. Rooftop Lights - Score: 2.96
     Because: mood matches happy; energy is very close to your target
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

I compared rankings with a strong genre weight and with a smaller genre
weight. A weight of 3 kept a user's selected genre near the top, while a small
weight let songs with only similar energy outrank genre matches too easily. I
also tried profiles for energetic pop, relaxed jazz, and chill lofi. Exact
genre-and-mood matches ranked first when the catalog contained one, and energy
helped order songs that matched only one categorical preference.

---

## Limitations and Risks

The catalog has only ten songs, so several tastes have just one example or no
example at all. The scoring rule does not understand lyrics, language, artists,
listening history, or changing context. Exact text matching also treats related
labels such as `pop` and `indie pop` as different genres, and the fixed weights
can over-favor a single genre or mood rather than producing diverse results.

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

I learned that even a small recommender turns preferences into predictions by
choosing measurable features, assigning weights, and ranking calculated
scores. The recommendations are not objective: changing one weight can change
the entire order, so the designer's choices become part of the model's idea of
good taste.

Bias can enter through both the catalog and the scoring rule. Genres with more
songs have more chances to appear, while missing genres can never be
recommended. Exact categories can also exclude music that is similar but
labeled differently. A real system should use a broader catalog, evaluate many
types of listeners, and balance relevance with variety and discovery.



