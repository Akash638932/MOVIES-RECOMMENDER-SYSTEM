from flask import Flask, request, jsonify, render_template
import pickle
import requests

app = Flask(__name__)

# Load data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url).json()
    return {
        "title": response.get("title"),
        "overview": response.get("overview"),
        "poster": f"https://image.tmdb.org/t/p/w500{response.get('poster_path')}" if response.get("poster_path") else None,
        "release_date": response.get("release_date"),
        "rating": response.get("vote_average"),
        "genres": [genre["name"] for genre in response.get("genres", [])]
    }

def fetch_reviews(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url).json()
    reviews = [{"author": r["author"], "content": r["content"]} for r in response.get("results", [])]
    return reviews

@app.route('/')
def home():
    return render_template('index.html', movies=movies['title'].values)

@app.route('/recommend', methods=['POST'])
def recommend_movies():
    data = request.json
    movie_title = data.get('movie')
    index = movies[movies['title'] == movie_title].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommendations = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        details = fetch_movie_details(movie_id)
        recommendations.append({"details": details})
    return jsonify({"recommendations": recommendations})

@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    details = fetch_movie_details(movie_id)
    reviews = fetch_reviews(movie_id)
    if not details:
        return "Movie details not found.", 404
    return render_template('movie_details.html' , details=details, reviews=reviews)


if __name__ == '__main__':
    app.run(debug=True)