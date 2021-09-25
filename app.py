from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from api import build_response, initial_response


@app.route('/')
def hello_world() -> str:
    return render_template("index.html")


@app.route('/api/delivery')
def delivery() -> Response:
    try:
        per_page = request.args.get('perPage', 5, type=int)
        current_page = request.args.get('currentPage', 1, type=int)
        query = request.args.get('query', '')
    except ValueError:
        return jsonify(initial_response(request=request.full_path, error="Bad query", page=1))
    prepared_response = build_response(current_page, per_page, request.full_path, query)
    return jsonify(prepared_response)


if __name__ == '__main__':
    app.run()
