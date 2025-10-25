import json

import pytest
from playwright.sync_api import Playwright, APIRequestContext
from typing import Generator


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    """Create API request context."""
    request_context = playwright.request.new_context(base_url="http://localhost:5000")
    yield request_context
    request_context.dispose()


def test_root_endpoint(api_request_context: APIRequestContext):
    """Test the root endpoint works."""
    response = api_request_context.get("/")
    assert response.status == 200
    assert "Flask app is running" in response.text()


def test_get_datatypes(api_request_context: APIRequestContext):
    """Test getting list of supported datatypes."""
    response = api_request_context.get("/datatypes")
    assert response.status == 200
    assert "name" in response.text()


def test_generate_data(api_request_context: APIRequestContext):
    """Test generating data from Person schema."""
    response = api_request_context.get("/Schemas/Person/data?no=1")
    assert response.status == 201
    data = response.json()
    assert len(data) == 1


def test_get_all_schemas(api_request_context: APIRequestContext):
    """Test retrieving all schemas."""
    response = api_request_context.get("/Schemas")
    assert response.status == 200
    schemas = response.json()
    assert isinstance(schemas, dict)
    assert "Person" in schemas


def test_get_specific_schema(api_request_context: APIRequestContext):
    """Test retrieving a specific schema."""
    response = api_request_context.get("/Schemas/Person")
    assert response.status == 200
    schema = response.json()
    assert "Name" in schema
    # Check for actual fields in Person schema
    assert "DOB" in schema or "Age" in schema


def test_create_schema(api_request_context: APIRequestContext):
    """Test creating a new schema."""
    schema = {
        "TestUser": {
            "ID": {"type": "uuid"},
            "Username": {"type": "username"},
            "Active": {"type": "boolean"}
        }
    }
    response = api_request_context.post("/Schemas", data=schema)
    assert response.status == 201
    assert "TestUser" in response.text()

    # Verify it was created
    get_response = api_request_context.get("/Schemas/TestUser")
    assert get_response.status == 200
    delete_response = api_request_context.delete("/Schemas/TestUser")

def test_generate_multiple_documents(api_request_context: APIRequestContext):
    """Test generating multiple documents."""
    response = api_request_context.get("/Schemas/Person/data?no=10")
    assert response.status == 201
    data = response.json()
    assert len(data) == 10

    # Check all have Name field (common to all Person schemas)
    for doc in data:
        assert "Name" in doc


def test_generate_csv_format(api_request_context: APIRequestContext):
    """Test generating data as CSV."""
    response = api_request_context.get(
        "/Schemas/Person/data?no=5",
        headers={"Accept": "text/csv"}
    )
    assert response.status == 201
    csv_text = response.text()
    lines = csv_text.strip().split('\n')
    assert len(lines) >= 6  # Header + 5 data rows


def test_generate_ndjson_format(api_request_context: APIRequestContext):
    """Test generating data as NDJSON."""
    response = api_request_context.get(
        "/Schemas/Person/data?no=3",
        headers={"Accept": "application/ndjson"}
    )
    assert response.status == 201
    ndjson_text = response.text()
    lines = ndjson_text.strip().split('\n')
    assert len(lines) == 3

    # Verify each line is valid JSON
    import json
    for line in lines:
        doc = json.loads(line)
        assert isinstance(doc, dict)


import json


def test_delete_schema(api_request_context: APIRequestContext):
    schema = {
        "ToDelete": {
            "Field": {"type": "name"}
        }
    }

    # Explicitly send as JSON string
    create_response = api_request_context.post(
        "/Schemas",
        data=json.dumps(schema),
        headers={"Content-Type": "application/json"}
    )
    assert create_response.status == 201

    delete_response = api_request_context.delete("/Schemas/ToDelete")
    assert delete_response.status == 200

def test_create_schema_invalid_type(api_request_context: APIRequestContext):
    """Test creating schema with unsupported type returns 400."""
    schema = {
        "Invalid": {
            "Field": {"type": "not_a_real_type"}
        }
    }
    response = api_request_context.post("/Schemas", data=schema)
    assert response.status == 400
    print(response.text().lower())
    assert "validation error" in response.text().lower()

def test_create_schema_missing_type(api_request_context: APIRequestContext):
    """Test creating schema without type field returns 400."""
    schema = {
        "NoType": {
            "Field": {"parameters": {"mu": 30}}
        }
    }
    response = api_request_context.post("/Schemas", data=schema)
    assert response.status == 400
    assert "type" in response.text().lower()

def test_generate_invalid_count_negative(api_request_context: APIRequestContext):
    """Test generating with negative count returns 400."""
    response = api_request_context.get("/Schemas/Person/data?no=-5")
    assert response.status == 400
    assert "less than 1" in response.text().lower()


def test_generate_invalid_count_zero(api_request_context: APIRequestContext):
    """Test generating with zero count returns 400."""
    response = api_request_context.get("/Schemas/Person/data?no=0")
    assert response.status == 400


def test_generate_invalid_count_string(api_request_context: APIRequestContext):
    """Test generating with non-numeric count returns 400."""
    response = api_request_context.get("/Schemas/Person/data?no=abc")
    assert response.status == 400
    assert "valid number" in response.text().lower()


def test_generate_nonexistent_schema(api_request_context: APIRequestContext):
    """Test generating from non-existent schema returns 400."""
    response = api_request_context.get("/Schemas/DoesNotExist/data")
    assert response.status == 404
    assert "not been defined" in response.text().lower()


def test_delete_nonexistent_schema(api_request_context: APIRequestContext):
    """Test deleting non-existent schema returns 400."""
    response = api_request_context.delete("/Schemas/DoesNotExist")
    assert response.status == 400


def test_uuid_uniqueness(api_request_context: APIRequestContext):
    """Test that UUIDs are unique across documents."""
    schema = {
        "UUIDTest": {
            "ID": {"type": "uuid"}
        }
    }
    api_request_context.post("/Schemas", data=schema)

    response = api_request_context.get("/Schemas/UUIDTest/data?no=50")
    data = response.json()

    uuids = [doc["ID"] for doc in data]
    assert len(uuids) == len(set(uuids)), "UUIDs are not unique"


def test_default_count_is_one(api_request_context: APIRequestContext):
    """Test that default document count is 1 when not specified."""
    response = api_request_context.get("/Schemas/Person/data")
    assert response.status == 201
    data = response.json()
    assert len(data) == 1





if __name__ == "__main__":
    pytest.main([__file__, "-v"])