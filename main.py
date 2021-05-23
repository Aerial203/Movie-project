from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


API_KEY = "b2a40feaaf779d94071751e54f1f6647"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie-record.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()


class RateMovieForm(FlaskForm):
    rating = StringField(label="Your rating out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your review", validators=[DataRequired()])
    submit = SubmitField()


class AddMovieForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    add_movie = SubmitField()


@app.route("/")
def home():
    all_movie = Movie.query.order_by(Movie.rating).all()
    for i in range(0, len(all_movie)):
        all_movie[i].ranking = len(all_movie) - i
    db.session.commit()
    return render_template("index.html", movies=all_movie)


@app.route("/edit", methods=['POST', 'GET'])
def edit_movie():
    edit_form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if edit_form.validate_on_submit():
        movie.rating = float(edit_form.rating.data)
        movie.review = edit_form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=edit_form)


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    add_form = AddMovieForm()
    if add_form.validate_on_submit():
        title = add_form.title.data
        movie_url="https://api.themoviedb.org/3/search/movie"
        paramter = {
            "api_key": API_KEY,
            "query": title,
            "include_adult": False,
        }
        response = requests.get(url=movie_url, params=paramter)
        result = response.json()["results"]
        return render_template("select.html", movies_data=result)
    return render_template("add.html", form=add_form)


@app.route("/find")
def find_movie():
    movie_id = request.args.get("id")
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    response = requests.get(url=movie_url, params={"api_key": API_KEY})
    result = response.json()
    title = result["title"]
    img_url = f"https://image.tmdb.org/t/p/w500/{result['poster_path']}"
    description = result["overview"]
    year = result["release_date"].split("-")[0]
    new_movie = Movie(
        title=title,
        year=year,
        description=description,
        img_url=img_url
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("edit_movie", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
