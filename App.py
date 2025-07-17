import random
from datetime import datetime
import pandas as pd
from flask import Flask, request
import re
from faker import Faker
from werkzeug.exceptions import BadRequest
from waitress import serve
fake = Faker()



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


def getDate(inp):
    ptrn = r'^[+-]\d+[dwmy]$'

    try:

        out = datetime.strptime(inp, "%Y-%m-%d").date()
        return out
    except ValueError:
        if re.match(ptrn, inp):
            return inp
        else:
            return (
                "Invalid input, please enter in the form YYYY-MM-DD or relative date input like +30y or -5d to signify +30 years or -5 days")


datatype_map = {
    'name': fake.name,
    'date': fake.date,
    "uuid": fake.uuid4,
    'email': fake.email,
    'ipv4': fake.ipv4,
    'ipv6': fake.ipv6,
    'phone number': fake.phone_number,
    'address': fake.address,
    'username': fake.user_name,
    'password': fake.password,
    'boolean': fake.boolean,
    'domain': fake.domain_name,
    "random int": random.randint,
    "country code" : fake.country_code
}


def data_gen(datatype, info=None):
    func = datatype_map.get(datatype)
    if info is not None:
        return func(**info)
    else:
        return func()


def get_schema(number_of_keys):
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
                """if datatype == "random int":
                    print("Lower bound:")
                    a = get_integer(":")
                    print("Upper bound:")
                    b = get_integer(":")
                    schema[key_name] = (datatype, {"a": a, "b": b})
                if datatype == "date":
                    print("End date (should be in format YYYY-MM-DD): ")
                    date = str(input())
                    schema[key_name] = (datatype, {"end_datetime": date})
                else:"""
                schema[key_name] = datatype
                break
            else:
                print("That is an unsupported data type")
    return schema


def docGenerator(schema):
    doc = {}
    for (k, v) in schema.items():
        match v:
            case str():
                doc[k] = data_gen(v)
            case (val, valinfo):

                if "end_datetime" in valinfo:
                    valinfo["end_datetime"] = getDate(valinfo["end_datetime"])
                    doc[k] = data_gen(val, valinfo)

                else:
                    doc[k] = data_gen(val, info=valinfo)
    return doc


def docGenerator_simple(schema):
    """ Takes a simple schema with no user input for ranges, i.e cannot specify date ranges.
    Takes dictionary where values are one item only"""
    doc = {}
    for k, v in schema.items():
        doc[k] = data_gen(v)
    return doc


def generate_documents_terminal():
    print("This application generates json documents based on user input. Supported data types are: ")
    [print(f'-{key}') for key in datatype_map.keys()]
    print("Please enter the number of desired data fields:")
    number_of_keys = get_integer(":")
    print('Please enter the number of desired documents:')
    number_of_docs = get_integer(":")
    schema = get_schema(number_of_keys)
    docs = []
    for i in range(number_of_docs):
        docs.append(docGenerator(schema))
    return docs


# print(generate_documents_terminal())
ex = {'namer': 'name', 'dob': ('date', {'end_datetime': '+30d'})}
ex2 = {'name': 'name', "DOB": "date"}
ex3 = {"randint": ("random int", {"a": 1, "b": 10})
       }

App = Flask(__name__)

list_of_schema = {
    "Logs": {
        "Destination IP": "ipv4",
        "Source IP": "ipv4"
    },
    "Person": {
        "DOB": "date",
        "Name": "name",
        "Email": "email",
    }
}



@App.get("/datatypes")
def view_datatypes():
    return "The following datatypes are:\n" + ", ".join(datatype_map.keys())

@App.post("/Schemas")
def define_schema():
    """Expects a json with one key-value pair. The key is the schema title, the value is the schema."""
    errors = []
    try: #catching JSON syntax errors like malformed json, empty json or json too long
        received_json = request.get_json()
        if not received_json:
            errors.append( "Empty JSON object provided.")
        if not isinstance(received_json, dict):
            errors.append("Request is in wrong format. Expected JSON with one key-value pair")
        if len(received_json) != 1:
            errors.append("JSON is too long. Expected JSON object with one key-value pair.")
        title = next(iter(received_json.keys()))
        if not title or (isinstance(title, str) and not title.strip()):
            errors.append("Please enter a non-empty string for the schema title")
        
    except BadRequest:
        return "Invalid/malformed JSON. Please check your syntax",400

    schema = next(iter(received_json.values())) #retrieving the schema from the json
    if not isinstance(schema, dict):  #Checking that it is a dictionary
        errors.append( 'Invalid schema format: expected a JSON object as the schema value.')

    unsupported = []
    for (k, v) in schema.items():
        if not k or (isinstance(k, str) and not k.strip()): #checking to see if any keys are blank/empty
            errors.append( 'Empty key detected in schema. Do not leave key blank')
        match v:  # looping through the schema to check if all datatypes are in the datatype map
            case str():
                if v.lower().strip() not in datatype_map:
                    unsupported.append(v)
            case (val, valinfo):  # datatype, optional parameters to go with datatype gen function
                if val.lower().strip() not in datatype_map:
                    unsupported.append(val)
    if len(unsupported) > 0: #Returning error message if there are any unsupported datatypes
        errors.append( f"The following datatypes are unsupported:  {', '.join(unsupported)}")
    if errors:
        return "Error reading schema:\n" + "\n".join(errors), 400
    else: #If all datatypes in schema are supported, update list of schema with this schema and return success msg
        key = list(received_json.keys())[0]
        list_of_schema.update(received_json)
        return f"The following schema has been defined : {key}", 201

@App.delete("/Schemas/<schema_title>")
def delete_schema(schema_title):
    if schema_title not in list_of_schema:
        return "Schema not in existing list of schemas, unable to delete.",400
    else:
        del list_of_schema[schema_title]
        return f"Schema: {schema_title}  deleted.", 200


@App.get("/Schemas/<schema_title>")
@App.get("/Schemas")
def view(schema_title=None):
    if schema_title != None:
        return list_of_schema[schema_title]
    else:
        return list_of_schema


@App.get("/Schemas/<schema_title>/data")
def Document_generator(schema_title):

    no_of_docs = request.args.get("no", 1)
    filetype = request.args.get("file", "json")
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
    if filetype == "json":
        docs = [docGenerator(schema) for i in range(no_of_docs)]
    elif filetype == "csv":
        docs = pd.DataFrame([docGenerator(schema) for i in range(no_of_docs)]).to_csv()
    msg = (f"{no_of_docs} {filetype} have been generated", 201)
    return docs, 201
if __name__=="__main__":
    App.run(host="0.0.0.0", port=5000)
