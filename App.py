import random
from datetime import datetime
import os

import pandas as pd
from flask import Flask, request
import re
from faker import Faker
from werkzeug.exceptions import BadRequest
from waitress import serve
import json
fake = Faker()
from dfunctions import data_gen, doc_generator, user_or_email, http_status, get_date, datatype_map
#test
def get_integer(strng):
    global num
    while True:
        try:
            num = int(input(strng))
            if num <= 0:
                print("Please enter a positive integer")
                continue
            else:
                break
        except ValueError:
            print("Please enter an integer")
            continue
    return num






"""def get_schema(number_of_keys): #CLI function
    schema = {}
    info = None
    for i in range(number_of_keys):
        while True:
            key_name = input("Enter the name for field " + str(i + 1) + ": ")
            if key_name.strip() == "" or len(key_name) == 0:
                print("Please enter a non-empty string")
                continue
            if key_name.strip() in schema:
                print("This field already exists")
                continue
            else:
                break
        schema[key_name] = None
        while True:
            datatype = input(
                "Enter the data type: ")
            datatype = str(datatype.strip()).lower()
            if datatype in datatype_map:
                if datatype == "random int":
                    print("Lower bound:")
                    a = get_integer(":")
                    print("Upper bound:")
                    b = get_integer(":")
                    schema[key_name] = (datatype, {"a": a, "b": b})
                if datatype == "date":
                    print("End date (should be in format YYYY-MM-DD): ")
                    date = str(input())
                    schema[key_name] = (datatype, {"end_datetime": date})
                else:
                schema[key_name] = datatype
                break
            else:
                print("That is an unsupported data type")
    return schema
"""







def docGenerator_simple(schema):
    """ Takes a simple schema with no user input for ranges, i.e cannot specify date ranges.
    Takes dictionary where values are one item only"""
    doc = {}
    for k, v in schema.items():
        doc[k] = data_gen(v)
    return doc


"""def generate_documents_terminal():
    print("This application generates json documents based on user input. Supported data types are: ")
    [print(f'-{key}') for key in datatype_map.keys()]
    print("Please enter the number of desired data fields:")
    number_of_keys = get_integer(":")
    print('Please enter the number of desired documents:')
    number_of_docs = get_integer(":")
    schema = get_schema(number_of_keys)
    docs = []
    for i in range(number_of_docs):
        docs.append(doc_generator(schema))
    return docs
    """





App = Flask(__name__)

list_of_schema = {
    "Logs": {
        "Destination IP": {"type":"ipv4"},
        "Source IP": {"type":"ipv4"}
    },
    "Person": {
        "DOB": {"type":"date"},
        "Name": {"type":"name"},
        "Email": {"type":"email"},
    }

}

schemas_path = "/app/schemas/schemas.json"
def save_schemas(schema):
    with open(schemas_path, "r") as f:
        data = json.load(f)
    data.update(schema)
    with open(schemas_path, "w") as f:
        json.dump(data, f)
    print("Schemas saved to " + schemas_path)

def load_schemas():
    with open(schemas_path,"r") as f:
        x = json.load(f)
    return x
#save_schemas(list_of_schema)
if schemas_path == "" or schemas_path is None:
    save_schemas(list_of_schema)
list_of_schema = load_schemas()
@App.route("/")
def index():
    save_schemas({})
    return "Flask app is running!"


@App.get("/datatypes")
def view_datatypes():
    return "The supported datatypes are:\n" + ", ".join(datatype_map.keys())


@App.post("/Schemas")
def define_schema():
    """Expects a json with one key-value pair. The key is the schema title, the value is the schema."""
    errors = []
    try:  # catching JSON syntax errors like malformed json, empty json or json too long
        received_json = request.get_json()
        if not received_json:
            errors.append("Empty JSON object provided.")
        if not isinstance(received_json, dict):
            errors.append("Request is in wrong format. Expected JSON with one key-value pair")
        if len(received_json) != 1:
            errors.append("JSON is too long. Expected JSON object with one key-value pair.")
        title = next(iter(received_json.keys()))
        if not title or (isinstance(title, str) and not title.strip()):
            errors.append("Please enter a non-empty string for the schema title")

    except BadRequest:
        return "Invalid/malformed JSON. Please check your syntax", 400

    schema = next(iter(received_json.values()))  # retrieving the schema from the json
    if not isinstance(schema, dict):  # Checking that it is a dictionary
        errors.append('Invalid schema format: expected a JSON object as the schema value.')

    unsupported = []
    for (k, v) in schema.items():
        if not k or (isinstance(k, str) and not k.strip()):  # checking to see if any keys are blank/empty
            errors.append('Empty key detected in schema. Do not leave key blank')

        if type(v) != dict: #checking that values in schema are in dict format
            errors.append("Malformed schema, schema values should be dictionaries")
        if "type" not in v: #if key type is not present return error message
            errors.append("Schema validation error: 'type' is required for all field definitions.")
        if "type" in v and v["type"] not in datatype_map: #if key 'type' is present, but the type is not in datatype map return error
            unsupported.append(v["type"])

    if unsupported:  # Returning error message if there are any unsupported datatypes
        errors.append(f"The following datatypes are unsupported:  {', '.join(unsupported)}")
    if errors:
        errors = list(set(errors))
        return "Error reading schema:\n" + "\n".join(errors), 400
    else:  # If all datatypes in schema are supported, update list of schema with this schema and return success msg
        key = list(received_json.keys())[0]
        list_of_schema.update(received_json)
        save_schemas(list_of_schema)
        return f"The following schema has been defined : {key}", 201


@App.delete("/Schemas/<schema_title>")
def delete_schema(schema_title):
    if schema_title not in list_of_schema:
        return "Schema not in existing list of schemas, unable to delete.", 400
    else:
        del list_of_schema[schema_title]
        return f"Schema: {schema_title}  deleted.", 200

#test
@App.get("/Schemas/<schema_title>")
@App.get("/Schemas")
def view(schema_title=None):
    list_of_schema = load_schemas()
    if schema_title != None:
        return list_of_schema[schema_title]
    else:
        return list_of_schema

#t
@App.get("/Schemas/<schema_title>/data")
def Document_generator(schema_title):
    no_of_docs = request.args.get("no", 1)
    filetype = request.headers.get('Accept', 'application/json')
    list_of_schema = load_schemas()
    if schema_title not in list_of_schema.keys():
        return (
            f"This schema {schema_title} has not been defined. Either define this schema or try again with an existing one",
            400)

    try:
        no_of_docs = int(no_of_docs)
        if no_of_docs < 1:
            return "You have selected a integer less than 1, please try again", 400
    except:
        return "You have to enter a valid number of documents, it should be a positive integer", 400

    schema = list_of_schema[schema_title]
    if filetype == "application/ndjson":
        docs = [json.dumps(doc_generator(schema) )for i in range(no_of_docs)]
        docs = "\n".join(docs)
    elif filetype == "application/json" or filetype == "*/*":
        docs = [doc_generator(schema) for i in range(no_of_docs)]

    elif filetype == "text/csv":
        docs = pd.DataFrame([doc_generator(schema) for i in range(no_of_docs)]).to_csv()
    msg = (f"{no_of_docs} {filetype} have been generated", 201)
    return docs, 201

if __name__ == "__main__":
    App.run(host='0.0.0.0', port=5100)