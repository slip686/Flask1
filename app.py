from flask import Flask, abort, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pathlib import Path
from sqlalchemy import func

BASE_DIR = Path(__file__).parent
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=False)
    surname = db.Column(db.String(32), unique=True)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, name, surname):
        self.name = name
        self.surname = surname

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname
        }


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)
    rating = db.Column(db.Integer, unique=False, nullable=False, default='1', server_default='1')
    created = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "author": self.author.to_dict(),
            "rating": self.rating,
            "date": self.created
        }


@app.route("/authors")
def get_all_authors():
    authors: list[AuthorModel] = AuthorModel.query.all()
    authors_dict: list[dict] = []
    for author in authors:
        authors_dict.append(author.to_dict())
    if authors_dict:
        return authors_dict, 200
    else:
        return "No authors added", 404


@app.route("/authors/<int:author_id>")
def get_author_by_id(author_id):
    author_obj: AuthorModel = AuthorModel.query.get(author_id)
    if author_obj:
        author_dict = author_obj.to_dict()
        return author_dict, 200
    else:
        return "No such author", 404


@app.route("/authors", methods=["POST"])
def add_new_author():
    new_author_name = request.json.get("name")
    new_author_surname = request.json.get("surname")
    if new_author_name and new_author_surname:
        author = AuthorModel(new_author_name, new_author_surname)
        db.session.add(author)
        db.session.commit()
        return {"id": author.id, "name": author.name, "surname": author.surname}, 200
    else:
        return "Bad request", 400


@app.route("/authors/<int:author_id>", methods=["PUT"])
def edit_author_by_id(author_id):
    author_obj: AuthorModel = AuthorModel.query.get(author_id)
    if author_obj:
        if request.json.get("name"):
            new_name = request.json["name"]
            author_obj.name = new_name
        if request.json.get("surname"):
            new_surname = request.json["surname"]
            author_obj.surname = new_surname
        if request.json.get("name") or request.json.get("surname"):
            db.session.commit()
            return {"id": author_obj.id, "name": author_obj.name, "surname": author_obj.surname}, 200
        else:
            return "Bad request", 400
    else:
        return f"Author with id={author_id} not found", 404


@app.route("/authors/<int:author_id>", methods=["DELETE"])
def delete_author_by_id(author_id):
    author_obj: AuthorModel = AuthorModel.query.get(author_id)
    if author_obj:
        db.session.delete(author_obj)
        db.session.commit()
        return f"Author {author_obj.name} with id={author_obj.id} has been deleted", 200
    else:
        return f"Author with id={author_id} not found", 404


@app.route("/quotes")
def get_quotes():
    quotes: list[QuoteModel] = QuoteModel.query.all()
    quotes_dict: list[dict] = []
    for quote in quotes:
        quotes_dict.append(quote.to_dict())
    return quotes_dict


@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        return "Not found", 404
    return quote.to_dict()


@app.route("/authors/<int:author_id>/quotes")
def get_one_author_quotes(author_id):
    quotes: list[QuoteModel] = []
    author_obj = AuthorModel.query.get(author_id)
    author_quotes = QuoteModel.query.filter(QuoteModel.author_id == author_obj.id).all()
    for quote in author_quotes:
        quotes.append(quote.to_dict())
    if quotes:
        return quotes, 200
    else:
        return f"No quotes for author with id={author_obj.id}", 404


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_quote(author_id):
    author_obj = AuthorModel.query.get(author_id)
    new_quote = request.json.get("text")
    if new_quote:
        quote = QuoteModel(author_obj, new_quote)
        db.session.add(quote)
        db.session.commit()
        return quote.to_dict(), 201
    else:
        return "Bad request", 400


@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote_by_id(quote_id):
    quote_obj = QuoteModel.query.get(quote_id)
    if quote_obj:
        new_text = request.json.get("text")
        if new_text:
            quote_obj.text = new_text
            db.session.commit()
            return {"id": quote_obj.id, "text": new_text}, 200
        else:
            return "Bad request", 400
    else:
        return f"Quote with id={quote_obj.id} not found", 404


@app.route("/quotes/<int:quote_id>/increase_rating")
def increase_rating(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote:
        if quote.rating < 5:
            quote.rating += 1
            db.session.commit()
            return quote.to_dict(), 200
        return quote.to_dict(), 200
    return "Quote not found", 404


@app.route("/quotes/<int:quote_id>/decrease_rating")
def decrease_rating(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote:
        if quote.rating > 1:
            quote.rating -= 1
            db.session.commit()
            return jsonify(quote.to_dict()), 200
        return jsonify(quote.to_dict()), 200
    return "Quote not found", 404


@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote_by_id(quote_id):
    quote_obj: QuoteModel = QuoteModel.query.get(quote_id)
    if quote_obj:
        db.session.delete(quote_obj)
        db.session.commit()
        return f"Quote with id={quote_id} has been deleted", 200
    else:
        return f"Quote with id={quote_id} not found", 404
