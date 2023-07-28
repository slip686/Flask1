from flask import Flask
from flask import json
from flask import request
from pathlib import Path
from flask import g
import random
import sqlite3
from markupsafe import escape

json.provider.DefaultJSONProvider.ensure_ascii = False

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "test.db"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def tuple_to_dict(quote: tuple):
    keys = ["id", "author", "text"]
    return dict(zip(keys, quote))


def get_all_quotes_query():
    select_all = "SELECT * FROM quotes"
    return select_all


def get_quote_by_id_query(quote_id):
    select_by_id = "SELECT * FROM quotes WHERE id={}".format(quote_id)
    return select_by_id


def add_new_quote_query(author, text):
    add_new_quote = """INSERT INTO quotes (author, text) VALUES ("{}", "{}")""".format(author, text)
    return add_new_quote


def db_query_exec(query: str, select_mode=None):
    result = None
    connection = sqlite3.connect("test.db")
    cursor = connection.cursor()
    cursor.execute(query)
    print(query)
    if select_mode:
        if select_mode == 'fetchall':
            result = cursor.fetchall()
        if select_mode == 'fetchone':
            result = cursor.fetchone()
    else:
        connection.commit()
    cursor.close()
    connection.close()
    if result:
        return list(map(tuple_to_dict, result))


@app.route("/quotes")
def quotes_list():
    result = db_query_exec(get_all_quotes_query(), select_mode='fetchall')
    return result


@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    result = db_query_exec(get_quote_by_id_query(quote_id), select_mode='fetchall')
    print(get_quote_by_id_query(quote_id))
    if result:
        return result
    else:
        return f"Quote with id={quote_id} not found", 404


# @app.route("/quotes/count")
# def get_quotes_count():
#     return {"count": f"{len(quotes)}"}


# @app.route("/quotes/random")
# def get_random_quote():
#     return random.choice(quotes)


@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(add_new_quote_query(author=new_quote.get("author"), text=new_quote.get("text")))
    connection.commit()
    new_quote["id"] = cursor.lastrowid
    return new_quote, 201

# @app.route("/quotes/<quote_id>", methods=["PUT"])
# def edit_quote(quote_id):
#     new_data = request.json
#     for quote in quotes:
#         if quote_id == quote["id"]:
#             if new_data.get("text"):
#                 quote["text"] = new_data["text"]
#             if new_data.get("author"):
#                 quote["author"] = new_data["author"]
#             if new_data.get("rating"):
#                 if int(new_data["rating"]) <= 5:
#                     quote["rating"] = int(new_data["rating"])
#             return quote, 201
#     return f"Quote with id={quote_id} not found", 404
#
#
# @app.route("/quotes/<quote_id>", methods=["DELETE"])
# def delete_quote(quote_id):
#     for quote in quotes:
#         if int(quote_id) == quote["id"]:
#             quotes.remove(quote)
#             return f"Quote with id {quote_id} is deleted.", 200
#     return f"Quote with id={quote_id} not found", 404
#
#
# @app.route("/quotes/filter")
# def get_quote_with_filter():
#     args = request.args
#     author = args.get("author")
#     rating = args.get("rating")
#     result = []
#
#     if args.get("rating_range"):
#         rating_range = args["rating_range"].split(",")
#         for quote in quotes:
#             if quote["rating"] in range(int(rating_range[0]), int(rating_range[1]) + 1):
#                 result.append(quote)
#     elif args.get("id_range"):
#         id_range = args["id_range"].split(",")
#         for quote in quotes:
#             if quote["id"] in range(int(id_range[0]), int(id_range[1]) + 1):
#                 result.append(quote)
#     else:
#         if None not in (author, rating):
#             for quote in quotes:
#                 if quote["author"] == author and quote["rating"] == int(rating):
#                     result.append(quote)
#
#         elif author is not None:
#             for quote in quotes:
#                 if quote["author"] == author:
#                     result.append(quote)
#
#         elif rating is not None:
#             for quote in quotes:
#                 if quote["rating"] == int(rating):
#                     result.append(quote)
#     if result:
#         return result, 200
#     else:
#         return f"Quotes not found", 404
