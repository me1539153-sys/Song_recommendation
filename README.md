# Music Recommendation Engine 🎵

A Python-based recommendation system that suggests songs based on content similarity and user ratings.

## ✨ Features
- **Fuzzy Search:** Handles user typos and spelling errors gracefully using `difflib`.
- **Content-Based Filtering:** Recommends songs based on shared Artists, Genres, and Albums.
- **Smart Re-ranking:** Re-prioritizes recommendations based on song popularity/ratings.
- **Trending Section:** Quickly access the top 10 highest-rated songs in the database.
- **Visual Analytics:** Includes a similarity heatmap to visualize how songs relate to one another.

## 🛠️ Technical Stack
- **Python 3**
- **Data Analysis:** `Pandas`, `NumPy`
- **Machine Learning:** `Scikit-learn` (CountVectorizer, Cosine Similarity)
- **Visualization:** `Matplotlib`, `Seaborn`
- **Deployment:** `Pickle` (for exporting the similarity matrix)

## 📊 Dataset Structure
The engine processes the following song attributes:
- `Song-Name`
- `Singer/Artists`
- `Genre`
- `Album/Movie`
- `User-Rating`

## 🚀 Quick Start

1. **Installation:**
   ```bash
   pip install pandas numpy scikit-learn matplotlib seaborn
