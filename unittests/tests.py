#Unit tests and dat
from App import data_gen, docGenerator, docGenerator_simple
import re
from playwright.sync_api import Playwright, APIRequest
#Testing data_gen function ability to generate a random instance of data
def test_data_gen_name():
    obtained = data_gen("name")
    pattern = r'\w+\s\w+'
    assert type(obtained) == str

def test_data_gen_email():
    result = data_gen("email")
    pattern = r'^[\w\.\-]+@[\w\-]+\.\w{2,}$'
    assert re.match(pattern, result)

def test_data_gen_ipv4():
    result = data_gen("ipv4")
    pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    assert re.match(pattern, result)

def test_data_gen_date():
    result = data_gen("date")
    pattern = r'\d{4}-\d{2}-\d{2}'
    assert re.match(pattern, result)

def test_data_gen_uuid():
    result = data_gen("uuid")
    pattern = r'^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$'
    assert re.match(pattern, result)
#Testing docGenerator function ability to generate correct documents based off user schema

def test_docGenerator_PersonSchema():#Checking that the random generated data is the correct format
    Schema = {
        "DOB": "date",
        "Name": "name",
        "Email": "email",
    }
    doc = docGenerator_simple(Schema)
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    email_pattern = r'^[\w\.\-]+@[\w\-]+\.\w{2,}$'

    assert "DOB" in doc
    assert "Name" in doc
    assert "Email" in doc

    assert type(doc) == dict
    assert len(doc) == len(Schema)
    assert type(doc["DOB"]) == str
    assert re.match(date_pattern, doc["DOB"])
    assert type(doc["Name"]) == str

    assert type(doc["Email"]) == str
    assert re.match(email_pattern, doc["Email"])


def test_docGenerator_LogsSchema():
    Schema = {
        "Source IP": "ipv4",
        "Destination IP": "ipv4",
        "HTTP Status code": "HTTP code"
    }
    doc = docGenerator_simple(Schema)
    assert type(doc) == dict
    assert len(doc) == len(Schema)
    ipv4_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    HTTP_pattern = r'\d{3}'
    assert re.match(ipv4_pattern, doc["Source IP"])
    assert re.match(ipv4_pattern, doc["Destination IP"])
    assert re.match(HTTP_pattern, str(doc["HTTP Status code"]))

def test_docGenerator_ContactSchema():
    Schema = {
        "Name": "name",
        "Contact no": "phone number",
        "Country code": "country code"
    }
    doc = docGenerator_simple(Schema)
    assert type(doc) == dict
    assert len(doc) == len(Schema)
    assert type(doc["Name"]) == str
    assert type(doc["Country code"]) == str
    assert type(doc["Contact no"]) == str

    phone_pattern = r'^(\+1\s?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}$'
    cc_pattern = r'^[A-Z]{2}'
    #assert re.match(phone_pattern, doc["Contact no"])
    #assert re.match(cc_pattern, doc["Contact no"])
    #assert re.match(r'\w+\s\w+',doc["Name"])
