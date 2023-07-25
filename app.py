from flask import Flask
from flask import json
from flask import request
import random
from markupsafe import escape

json.provider.DefaultJSONProvider.ensure_ascii = False

app = Flask(__name__)

about_me = {
    "name": "Кирилл",
    "surname": "Звонкин",
    "email": "slip686@gmail.com"
}

quotes = [
    {
        "id": 3,
        "author": "Rick Cook",
        "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и "
                "лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока "
                "вселенная побеждает.",
        "rating": 1
    },
    {
        "id": 5,
        "author": "Waldi Ravens",
        "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми "
                "бритвами в руках.",
        "rating": 2
    },
    {
        "id": 6,
        "author": "Mosher’s Law of Software Engineering",
        "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.",
        "rating": 3
    },
    {
        "id": 8,
        "author": "Yoggi Berra",
        "text": "В теории, теория и практика неразделимы. На практике это не так.",
        "rating": 4
    },
]


def get_id():
    new_id = quotes[-1]["id"] + 1
    return new_id


@app.route("/")
def hello_world():
    return "<h1>Hello, World!!!<h1>"


@app.route("/about")
def about_author():
    return about_me


@app.route("/quotes")
def quotes_list():
    return quotes


@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    for quote in quotes:
        if quote['id'] == quote_id:
            return quote
    return f"Quote with id={quote_id} not found", 404


@app.route("/quotes/count")
def get_quotes_count():
    return {"count": f"{len(quotes)}"}


@app.route("/quotes/random")
def get_random_quote():
    return random.choice(quotes)


@app.route("/quotes", methods=['POST'])
def create_quote():
    data = request.json
    data["id"] = get_id()
    if not data.get("rating") or int(data["rating"]) > 5:
        data["rating"] = 1
    quotes.append(data)
    print("data = ", data)
    return data, 201


@app.route("/quotes/<quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    new_data = request.json
    for quote in quotes:
        if int(quote_id) == quote["id"]:
            if new_data.get("text"):
                quote["text"] = new_data["text"]
            if new_data.get("author"):
                quote["author"] = new_data["author"]
            if new_data.get("rating"):
                if int(new_data["rating"]) <= 5:
                    quote["rating"] = int(new_data["rating"])
            return quote, 201
    return f"Quote with id={quote_id} not found", 404


@app.route("/quotes/<quote_id>", methods=["DELETE"])
def delete(quote_id):
    for quote in quotes:
        if int(quote_id) == quote["id"]:
            quotes.remove(quote)
            return f"Quote with id {quote_id} is deleted.", 200
    return f"Quote with id={quote_id} not found", 404


@app.route("/quotes/filter")
def get_quote_with_filter():
    args = request.args
    result = []
    if args.get("rating_range"):
        rating_range = args["rating_range"].split(",")
        for quote in quotes:
            if quote["rating"] in range(int(rating_range[0]), int(rating_range[1])+1):
                result.append(quote)
        return result, 200
    if args.get("id_range"):
        id_range = args["id_range"].split(",")
        for quote in quotes:
            if quote["id"] in range(int(id_range[0]), int(id_range[1])+1):
                result.append(quote)
        return result, 200


    # result = []
    # for quote in quotes:
    #     if args.get("author"):
    #         if quote["author"] == args.get("author"):
    #             result.append(quote)
    #     if args.get("rating"):



