import random
from datetime import datetime
import os
from flask_cors import CORS
import pandas as pd
from flask import Flask, request, jsonify
import re
from faker import Faker
from werkzeug.exceptions import BadRequest
from waitress import serve
import json

fake = Faker()
from functions import data_gen, doc_generator, username, email, http_status, get_date, datatype_map, document_malformer
from models import Schema, validate_schema
from storage import init_db, get_all_schemas, get_schema, add_schema, delete_schema as remove_schema, db_healthy

App = Flask(__name__)
CORS(App)
list_of_schema = {
    "Logs": {
        "Destination IP": {"type": "ipv4"},
        "Source IP": {"type": "ipv4"}
    },
    "Person": {
        "DOB": {"type": "date"},
        "Name": {"type": "name"},

    }

}

# Create the schemas table and add the starter schemas if they aren't there yet
init_db(list_of_schema)


@App.route("/")
def index():
    return "Flask app is running!"


@App.get("/datatypes")
def view_datatypes():
    return "The supported datatypes are:\n" + ", ".join(datatype_map.keys())


@App.post("/Schemas")
def define_schema():
    """Expects a json with one key-value pair. The key is the schema title, the value is the schema."""
    received_json = request.get_json()
    validated = validate_schema(received_json)
    if validated is not True:
        return f"{validated}", 400

    key = list(received_json.keys())[0]
    if not add_schema(key, received_json[key]):
        return jsonify({
            "error": f"The schema \"{key}\" is already defined.",
        }), 400
    return f"The following schema has been defined : {key}", 201


@App.delete("/Schemas/<schema_title>")
def delete_schema(schema_title):
    if not remove_schema(schema_title):
        return "Schema not in existing list of schemas, unable to delete.", 400
    return f"Schema: {schema_title}  deleted.", 200


# test
@App.get("/Schemas/<schema_title>")
@App.get("/Schemas")
def view(schema_title=None):
    if schema_title is None:
        return get_all_schemas()
    schema = get_schema(schema_title)
    if schema is None:
        return f"The schema {schema_title} has not been defined.", 404
    return schema


# t
@App.get("/Schemas/<schema_title>/data")
def Document_generator(schema_title):
    no_of_docs = request.args.get("no", 1)
    mal = request.args.get("malf", "False")
    filetype = request.headers.get('Accept', 'application/json')
    schema = get_schema(schema_title)
    if schema is None:
        return (
            f"This schema {schema_title} has not been defined. Either define this schema or try again with an existing one",
            404)

    try:
        no_of_docs = int(no_of_docs)
        if no_of_docs < 1:
            return "You have selected a integer less than 1, please try again", 400
    except:
        return "You have to enter a valid number of documents, it should be a positive integer", 400

    if filetype == "application/ndjson":
        if mal == "True":  # producing malformed data
            docs = [json.dumps(document_malformer(doc_generator(schema))) for i in range(no_of_docs)]
        else:
            docs = [json.dumps(doc_generator(schema)) for i in range(no_of_docs)]
        docs = "\n".join(docs)
    elif filetype == "application/json" or filetype == "*/*":
        if mal == "True":  # producing malformed data
            docs = [document_malformer(doc_generator(schema)) for i in range(no_of_docs)]
        else:
            docs = [doc_generator(schema) for i in range(no_of_docs)]


    elif filetype == "text/csv":
        if mal == "True":
            docs = pd.DataFrame([document_malformer(doc_generator(schema)) for i in range(no_of_docs)]).to_csv()
        else:
            docs = pd.DataFrame([doc_generator(schema) for i in range(no_of_docs)]).to_csv()
    msg = (f"{no_of_docs} {filetype} have been generated", 201)
    return docs, 201


@App.route("/health")
def health_check():
    """Health check endpoint for Docker/orchestration."""
    if db_healthy():
        return {"status": "healthy"}, 200
    return {"status": "unhealthy"}, 503


if __name__ == "__main__":
    App.run(host='0.0.0.0', port=5050)
