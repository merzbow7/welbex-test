import json
import logging
from datetime import datetime
from urllib.parse import urlencode

from flask_sqlalchemy import Pagination, BaseQuery
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from sqlalchemy.sql.elements import TextClause

from models import Welbextest

query_translate_column = {
    "Название": "name",
    "Количество": "count",
    "Расстояние": "distance",
    "Дата": "date",
}

query_translate_operand = {
    "больше": ">",
    "меньше": "<",
    "равно": "=",
    "содержит": "contains",
}


def make_page_url(page_number: int, per_page: int) -> str:
    if page_number:
        return f'/api/delivery?{urlencode({"currentPage": page_number, "perPage": per_page})}'
    return ''


def make_db_query(query: dict, page_number: int = 1, per_page: int = 10) -> Pagination:
    column, operand, value = query.values()
    if all(query.values()):
        if operand == "contains":
            sql_query: BaseQuery = Welbextest.query.filter(getattr(Welbextest, column).contains(value))
        else:
            query_fragment: TextClause = text(f"{column} {operand} :value")
            query_fragment = query_fragment.bindparams(value=value)
            sql_query: BaseQuery = Welbextest.query.filter(query_fragment)
    else:
        sql_query: BaseQuery = Welbextest.query

    return sql_query.paginate(page_number, per_page, error_out=False)


def validate_query(query: str) -> dict:
    query_json = json.loads(query)

    column = query_translate_column.get(query_json.get("column", ''), '')
    operand = query_translate_operand.get(query_json.get("operand", ''), '')
    value = query_json.get("value", '')
    if column == "date":
        try:
            value = datetime.strptime(value, "%d-%m-%Y").date()
        except ValueError:
            return {}
    return {"column": column, "operand": operand, "value": value}


def initial_response(page: int, request: str, error: str = "") -> dict:
    return {"data": [], "request": request, "page": page, error: error, "next": '', "prev": ''}


def build_response(page_number: int, per_page: int, full_path: str, query: str) -> dict:
    prepared_response = initial_response(page=page_number, request=full_path)
    verified_query = validate_query(query)
    if not verified_query:
        prepared_response["error"] = "Bad request query"
        return prepared_response
    try:
        if page_number < 1:
            page_number = 1
            prepared_response["error"] = "Bad page number. Reset to 1"
            prepared_response["page"] = 1
        page: Pagination = make_db_query(verified_query, page_number, per_page)

        if page.items and page_number > page.pages:
            prepared_response["error"] = "Bad page number. Reset to 1"
            prepared_response["page"] = 1
            page: Pagination = make_db_query(verified_query, 1, per_page)

        prepared_response["next"] = make_page_url(page.next_num, per_page)
        prepared_response["prev"] = make_page_url(page.prev_num, per_page)

        if page.items:
            for item in page.items:
                prepared_response["data"].append(
                    {
                        "count": item.count,
                        "date": item.date.strftime("%d-%m-%Y"),
                        "distance": item.distance,
                        "name": item.name
                    }
                )
        else:
            prepared_response["warning"] = "Empty result"

    except SQLAlchemyError as error:
        prepared_response["error"] = "Internal Error"
        logging.error(error)

    return prepared_response
