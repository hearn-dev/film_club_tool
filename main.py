from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
from random import randint
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
Bootstrap(app)

movie_api_key = os.environ.get('MOVIE_KEY')

db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, unique=True, nullable=False)
    rating = db.Column(db.String)
    index = db.Column(db.Integer)
    img_url = db.Column(db.String, unique=True, nullable=False)

class AddForm(FlaskForm):
    title = StringField("Title")
    submit = SubmitField("Add Movie")



# with app.app_context():
#     db.create_all()
#     new_movie = Movie(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist",
#         index=0,
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#     )
#     db.session.add(new_movie)
#     db.session.commit()
# with app.app_context():
#     movie = Movie.query.get(1)
#     db.session.delete(movie)
#     db.session.commit()
@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(movies)):
        movies[i].ranking = len(movies) - i
    db.session.commit()
    return render_template("index.html", movies=movies)

# @app.route("/edit", methods=["GET", "POST"])
# def edit():
#     form = EditForm()
#     movie_id = request.args.get('id')
#     movie = Movie.query.get(movie_id)
    
#     if form.validate_on_submit():
#         movie.rating = float(form.rating.data)
#         movie.review = form.review.data
#         db.session.commit()
#         return redirect(url_for('home'))
#     return render_template('edit.html', movie=movie, form=form)

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        query = form.title.data
        query.replace(' ', '%20')
        movie_query_url = f'https://api.themoviedb.org/3/search/movie?api_key={movie_api_key}&language=en-US&page=1&include_adult=false&query={query}'
        response = requests.get(movie_query_url)
        movies = response.json()['results']
        return render_template('select.html', results=movies)
    return render_template('add.html', form=form)

@app.route("/choose", methods=["GET"])
def choose():
    movie_id = request.args.get('id')
    film_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={movie_api_key}&language=en-US'
    response = requests.get(film_url)
    movie = response.json()
    new_movie = Movie(
        id = movie['id'],
        title=movie['title'],
        year=movie['release_date'][0:4],
        description=movie['overview'],
        rating=movie['vote_average'],
        img_url=f"https://image.tmdb.org/t/p/original/{movie['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/random')
def random():
    movies = Movie.query.order_by(Movie.rating).all()
    movie_index = randint(0, len(movies)-1)
    chosen_movie = movies[movie_index]
    return render_template('random.html', film=chosen_movie)

if __name__ == '__main__':
    app.run(debug=True)
