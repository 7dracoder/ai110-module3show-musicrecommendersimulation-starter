# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**TuneMatch 1.0**

---

## 2. Intended Use  

TuneMatch ranks songs from a small catalog for a listener who provides a
favorite genre, favorite mood, target energy, and acoustic preference. It
assumes those preferences describe what the listener wants right now. It is a
classroom simulation for exploring recommendation logic, not a production
service for real users.

---

## 3. How the Model Works  

TuneMatch compares a song's genre and mood with the listener's favorites, then
checks how close its energy is to the listener's target. Genre is worth 3
points, mood is worth 2, and energy closeness is worth up to 1. The
object-oriented version adds half a point when the song's acoustic character
fits the listener's preference. It then puts the highest-scoring songs first.
The starter returned songs in their original order; this version calculates a
real score, ranks the catalog, and explains the matching features.

---

## 4. Data  

The provided catalog contains 10 fictional songs. Its genres are pop, lofi,
rock, ambient, jazz, synthwave, and indie pop. Its moods are happy, chill,
intense, relaxed, moody, and focused. No songs were added or removed. The data
does not cover many genres, cultures, languages, eras, lyrical themes, or
listener contexts, and some represented categories have only one song.

---

## 5. Strengths  

The system works best when a listener's favorite genre and mood both appear in
the catalog. It reliably places exact categorical matches above songs that only
have similar energy. For an energetic, happy pop profile, "Sunrise City" ranks
first, which matches the song's genre, mood, and energy and agrees with my
intuition.

---

## 6. Limitations and Bias 

The system ignores listening history, artist preference, lyrics, language,
tempo preference, and context. Most genres and moods have only one or two
examples, so users with tastes outside the catalog receive weak matches. Exact
label matching does not recognize that `pop` and `indie pop` may be related.
Fixed genre and mood weights can also overfit to one stated preference and
reduce variety. Users whose tastes match well-represented labels are therefore
served better than users with niche or mixed tastes.

---

## 7. Evaluation  

I ran the automated tests and tried profiles for energetic happy pop, relaxed
jazz, and chill lofi. I checked that the expected exact match appeared first,
that results were sorted by score, that requesting fewer results worked, and
that explanations were not empty. I also compared genre weights and found that
a low genre weight allowed energy similarity to dominate more than expected.

---

## 8. Future Work  

Future versions could learn weights from likes and skips, accept multiple
favorite genres and moods, and use tempo, valence, and danceability preferences.
They could recognize related genre labels, explain the score contribution of
each feature, and deliberately diversify the top results across artists and
genres. Evaluation should also use a larger, more representative catalog and
feedback from different listeners.

---

## 9. Personal Reflection  

I learned that a recommender is a set of human choices about what information
matters and how much it matters. It was interesting that a small weight change
could reorder several songs even though their data stayed the same. I now view
recommendations in music apps less as neutral answers and more as rankings
shaped by available data, product goals, and design decisions.
