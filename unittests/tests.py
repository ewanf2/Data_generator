import sys
import os

# Add the project root to the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions import data_gen, doc_generator, user_or_email, http_status, get_date, datatype_map, \
    primary_and_dependent_fields, generate_primary_fields, generate_dependent_fields, rand_skew, gauss_int
import re


# Testing data_gen function ability to generate a random instance of data
def test_data_gen_name():
    obtained = data_gen("name")
    pattern = r'\w+\s\w+'

    assert type(obtained) == str
    assert re.match(pattern, obtained)





def test_rand_skew():
    result = rand_skew(1, 1, 1)
    assert type(result) == str


def test_gauss_int():
    result = gauss_int()
    assert type(result) == int
    res2 = gauss_int(-200, 0)
    assert res2 == 0


def test_user_or_email():
    result = user_or_email("Jon")
    assert type(result) == str
    res2 = user_or_email("Jon", "email")
    assert type(res2) == str


def test_data_gen_ipv4():
    result = data_gen("ipv4")
    pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    assert re.match(pattern, result)


def test_data_gen_date():
    result = data_gen("date")
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    assert re.match(pattern, result)


def test_data_gen_uuid():
    result = data_gen("uuid")
    pattern = r'^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$'
    assert re.match(pattern, result)


# Testing docGenerator function ability to generate correct documents based off user schema

def test_docGenerator_PersonSchema():  # Checking that the random generated data is the correct format
    Schema = {
        "DOB": {"type": "date", "start_date": "1998-02-02", "end_date": "+30y"},
        "Name": {"type": "name"},

    }
    doc = doc_generator(Schema)
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    email_pattern = r'^[\w\.\-]+@[\w\-]+\.\w{2,}$'

    assert "DOB" in doc
    assert "Name" in doc


    assert type(doc) == dict
    assert len(doc) == len(Schema)
    assert type(doc["DOB"]) == str
    assert re.match(date_pattern, doc["DOB"])
    assert type(doc["Name"]) == str




def test_docGenerator_LogsSchema():
    Schema = {
        "Source IP": {"type": "ipv4"},
        "Destination IP": {"type": "ipv4"},
        "HTTP Status code": {"type": "HTTP code"}
    }

    doc = doc_generator(Schema)
    for (k, v) in Schema.items():
        assert k in doc
    assert type(doc) == dict
    assert len(doc) == len(Schema)
    ipv4_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    HTTP_pattern = r'\d{3}'
    assert re.match(ipv4_pattern, doc["Source IP"])
    assert re.match(ipv4_pattern, doc["Destination IP"])
    assert re.match(HTTP_pattern, str(doc["HTTP Status code"]))


def test_docGenerator_ContactSchema():
    Schema = {
        "Name": {"type": "name"},
        "Contact no": {"type": "phone number"},
        "Country code": {"type": "country code"}
    }
    doc = doc_generator(Schema)
    assert type(doc) == dict
    assert len(doc) == len(Schema)
    assert type(doc["Name"]) == str
    assert type(doc["Country code"]) == str
    assert type(doc["Contact no"]) == str
    for (k, v) in Schema.items():
        assert k in doc
    phone_pattern = r'^(\+1\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}$'
    cc_pattern = r'^[a-z]{2}'

    # assert re.match(cc_pattern, doc["Country code"])
    # assert re.match(r'\w+\s\w+',doc["Name"])


def test_http_status():
    result = http_status()
    assert type(result) == str


def test_primary_and_dependent_fields():
    test_schema = {"Name": {"type": "name"},
                   "sex": {"type": "sex", "parameters": {"a": 2, "b": 1}},
                   "age": {"type": "random int", "parameters": {"a": 19, "b": 100}},
                   "tallness": {"type": "gauss int",
                                "dependencies": {"categorical": "sex", "male": {"mu": 179, "sigma": 10},
                                                 "female": {"mu": 150, "sigma": 10}}
                                }
                   }
    prim, dep = primary_and_dependent_fields(test_schema)
    assert type(prim) == dict
    assert "tallness" in dep
    assert all(k in prim for k in ["Name", "sex", "age"])
    assert type(dep) == dict


def test_generate_primary_fields():
    test_schema = {"Name": {"type": "name"},
                   "sex": {"type": "sex", "parameters": {"a": 2, "b": 1}},
                   "age": {"type": "random int", "parameters": {"a": 19, "b": 100}},
                   "tallness": {"type": "gauss int",
                                "dependencies": {"categorical": "sex", "male": {"mu": 179, "sigma": 10},
                                                 "female": {"mu": 150, "sigma": 10}}
                                }
                   }
    primary, dependent_fields = primary_and_dependent_fields(test_schema)
    primary_fields = generate_primary_fields(primary)
    assert type(primary_fields) == dict
    assert all(k in primary_fields for k in ["Name", "sex", "age"])


def test_generate_dependent_fields():
    test_schema = {"Name": {"type": "name"},
                     "sex": {"type": "sex", "parameters": {"a": 1, "b": 1}},
                     "age": {"type": "random int", "parameters": {"a": 19, "b": 100}},
                     "tallness": {"type": "gauss int",
                                  "dependencies": {"categorical": "sex",
                                                   "male": {"mu": 179, "sigma": 10},
                                                   "female": {"mu": 161, "sigma": 10}}
                                  },
                     "weight": {"type": "gauss int",
                                "dependencies": {"numerical": ["age"], "formula": "age*0.7+40"}}
                     }
    primary_fields, dependent_fields = primary_and_dependent_fields(
        test_schema)  # Generating list of primary and dependent fields
    doc = {}
    doc.update(generate_primary_fields(primary_fields))  # generating primary field data first
    dependents = generate_dependent_fields(dependent_fields, doc)
    doc.update(dependents)
    assert type(dependents) == dict
    assert "tallness" in dependents
    assert "weight" in dependents
