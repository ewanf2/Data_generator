
import re
import sys
import os

# Add the project root to the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from playwright.sync_api import Playwright, APIRequest, APIRequestContext
from typing import Generator
import pytest
#from App import data_gen, doc_generator
@pytest.fixture(scope="session")
def api_request_context( playwright: Playwright ) -> Generator[APIRequestContext, None, None]:
    request_context = playwright.request.new_context(base_url="http://localhost:5050")
    yield request_context
    request_context.dispose()

def test_uploadSchema(api_request_context: APIRequestContext):
    Schema = {"Example":{
        "DOB": {"type":"date"},
        "Name": {"type":"name"},
        "Email": {"type":"email"}
    }
    }
    new_schema = api_request_context.post("/Schemas",data=Schema)
    #response_msg = new_schema.json()
    check = api_request_context.get("/Schemas/Example")
    assert new_schema.status == 201
    assert check.status == 200


def test_gen_documentsLogs2(api_request_context: APIRequestContext):
    get_data = api_request_context.get("/Schemas/Person/data")
    data= get_data.json()
    assert get_data.status == 201
    PersonSchema = api_request_context.get("/Schemas/Person")
    assert PersonSchema.status == 200
    data = data[0]

    for k,v in PersonSchema.json().items():
        assert k in data

def test_gen_documentsLogs2(api_request_context: APIRequestContext):
    get_data = api_request_context.get("/Schemas/Person/data")
    data= get_data.json()
    assert get_data.status == 201
    PersonSchema = api_request_context.get("/Schemas/Person")
    assert PersonSchema.status == 200
    data = data[0]

    for k,v in PersonSchema.json().items():
        assert k in data
