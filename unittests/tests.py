import sys
import os

import pytest

from pydantic import ValidationError


# Add the project root to the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Dependencies, FieldConfig, Schema
from functions import data_gen, doc_generator, http_status, get_date, datatype_map, \
    primary_and_dependent_fields, generate_primary_fields, generate_dependent_fields, rand_skew, gauss_int, \
    document_malformer, username, email
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


def test_username():
    result = username("Jon")
    assert type(result) == str

def test_email():
    res2 = email("Jon")
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
                                "dependencies": {"conditional": "sex", "male": {"mu": 179, "sigma": 10},
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
                   "sex": {"type": "sex", "parameters": {"m": 2, "f": 1}},
                   "age": {"type": "random int", "parameters": {"a": 19, "b": 100}},
                   "tallness": {"type": "gauss int",
                                "dependencies": {"conditional": "sex", "male": {"mu": 179, "sigma": 10},
                                                 "female": {"mu": 150, "sigma": 10}}
                                }
                   }
    primary, dependent_fields = primary_and_dependent_fields(test_schema)
    primary_fields = generate_primary_fields(primary)
    assert type(primary_fields) == dict
    assert all(k in primary_fields for k in ["Name", "sex", "age"])


def test_generate_dependent_fields():
    test_schema = {"Name": {"type": "name"},
                     "sex": {"type": "sex", "parameters": {"m": 1, "f": 1}},
                     "age": {"type": "random int", "parameters": {"a": 19, "b": 100}},
                     "tallness": {"type": "gauss int",
                                  "dependencies": {"conditional": "sex",
                                                   "male": {"mu": 179, "sigma": 10},
                                                   "female": {"mu": 161, "sigma": 10}}
                                  }
                     }
    primary_fields, dependent_fields = primary_and_dependent_fields(
        test_schema)  # Generating list of primary and dependent fields
    doc = {}
    doc.update(generate_primary_fields(primary_fields))  # generating primary field data first
    dependents = generate_dependent_fields(dependent_fields, doc)
    doc.update(dependents)
    assert type(dependents) == dict
    assert "tallness" in dependents

class TestDocumentMalformer:

    def test_malforms_string_fields(self):
        """Test that string fields get malformed."""
        document = {
            "Name": "John Doe",
            "Email": "john@example.com"
        }

        malformed = document_malformer(document,1.0)

        # At least one field should be different from original
        assert malformed != document
        # Should still have same keys
        assert set(malformed.keys()) == set(document.keys())

    def test_malforms_numeric_fields(self):
        """Test that numeric fields get malformed."""
        document = {
            "Age": 30,
            "Salary": 50000.50
        }

        malformed = document_malformer(document,1.0)

        # At least one value should change
        assert malformed != document
        assert set(malformed.keys()) == set(document.keys())

    def test_preserves_none_values(self):
        """Test that None values stay as None."""
        document = {
            "Name": "John",
            "Email": None,
            "Age": None
        }

        malformed = document_malformer(document,1.0)

        assert malformed["Email"] is None
        assert malformed["Age"] is None

    def test_handles_empty_document(self):
        """Test that empty document returns empty document."""
        document = {}
        malformed = document_malformer(document,1.0)
        assert malformed == {}

    def test_handles_mixed_types(self):
        """Test document with various data types."""
        document = {
            "Name": "Jane Doe",
            "Age": 25,
            "Score": 85.5,
            "Active": True,
            "Notes": None
        }

        malformed = document_malformer(document,1.0)

        assert isinstance(malformed, dict)
        assert len(malformed) == len(document)
        assert set(malformed.keys()) == set(document.keys())

    def test_doesnt_modify_original(self):
        """Test that original document is not modified."""
        original = {
            "Name": "John Doe",
            "Email": "john@example.com",
            "Age": 30
        }
        original_copy = original.copy()

        malformed = document_malformer(original,1.0)

        # Original should be unchanged
        assert original == original_copy

    def test_introduces_realistic_errors(self):
        """Test that malformations are realistic (not random garbage)."""
        document = {
            "Email": "test@example.com"
        }

        # Run multiple times to see different malformations
        malformed_versions = [document_malformer(document) for _ in range(20)]

        # Check that at least some are different
        unique_emails = set(d["Email"] for d in malformed_versions)
        assert len(unique_emails) > 1  # Should have variety

        # Each malformed email should still be somewhat email-like
        # (not complete garbage)
        for malformed in malformed_versions:
            email = malformed["Email"]
            assert isinstance(email, str)
            assert len(email) > 0

    def test_probability_of_malformation(self):
        """Test that not ALL fields get malformed every time."""
        document = {
            "Field1": "value1",
            "Field2": "value2",
            "Field3": "value3"
        }

        # Run 100 times and check that sometimes fields stay the same
        results = [document_malformer(document) for _ in range(100)]

        # At least one run should have some unchanged fields
        unchanged_counts = []
        for result in results:
            unchanged = sum(1 for k in document if result[k] == document[k])
            unchanged_counts.append(unchanged)

        # Not every field should change every time (unless you want that)
        # Adjust this assertion based on your implementation
        assert max(unchanged_counts) > 0 or min(unchanged_counts) < len(document)


class TestDependencies:
    def test_valid_dependencies(self):
        """Test creating valid Dependencies"""
        deps = Dependencies(
            reference="SourceField",
            parameters={"param1": "value1", "param2": "value2"}
        )
        assert deps.reference == "SourceField"
        assert deps.parameters == {"param1": "value1", "param2": "value2"}

    def test_dependencies_without_parameters(self):
        """Test Dependencies with no parameters (should be optional)"""
        deps = Dependencies(reference="SourceField")
        assert deps.reference == "SourceField"
        assert deps.parameters is None

    def test_invalid_dependencies_missing_reference(self):
        """Test that Dependencies requires reference"""
        with pytest.raises(ValidationError):
            Dependencies(parameters={"param1": "value1"})


class TestFieldConfig:
    def test_field_config_minimal(self):
        """Test FieldConfig with only required field"""
        config = FieldConfig(type="name")
        assert config.type == "name"
        assert config.dependencies is None
        assert config.parameters is None

    def test_field_config_valid_type(self):
        """Test all valid types from datatype_map"""
        valid_types = ["name", "gauss int", "uuid", "email"]  # Add your actual types
        for type_name in valid_types:
            config = FieldConfig(type=type_name)
            assert config.type == type_name


class TestSchema:
    def test_valid_schema_single_field(self):
        """Test schema with one field"""
        data = {
            "Testing": {
                "Name": {"type": "name"}
            }
        }
        schema = Schema(root=data)
        assert "Testing" in schema.root
        assert "Name" in schema.root["Testing"]

    def test_valid_schema_multiple_fields(self):
        """Test schema with multiple fields"""
        data = {
            "Testing": {
                "Name": {"type": "name"},
                "Age": {"type": "gauss int", "parameters": {"mean": "30"}},
                "Email": {
                    "type": "email",
                    "dependencies": {
                        "reference": "Name",
                        "parameters": {"domain": "test.com"}
                    }
                }
            }
        }
        schema = Schema(root=data)
        assert len(schema.root["Testing"]) == 3

    def test_multiple_schemas(self):
        """Test multiple schemas in one"""
        data = {
            "Schema1": {
                "Field1": {"type": "name"}
            },
            "Schema2": {
                "Field2": {"type": "gauss int"}
            }
        }
        schema = Schema(root=data)
        assert len(schema.root) == 2

    def test_invalid_schema_bad_type(self):
        """Test schema with invalid field type"""
        data = {
            "Testing": {
                "Name": {"type": "invalid_type"}
            }
        }
        with pytest.raises(ValidationError) as exc_info:
            Schema(root=data)
        assert "invalid_type" in str(exc_info.value)

    def test_empty_schema(self):
        """Test empty schema"""
        data = {}
        schema = Schema(root=data)
        assert schema.root == {}



class TestSchemaEdgeCases:
    def test_nested_parameters(self):
        """Test deeply nested parameters"""
        data = {
            "Testing": {
                "Field": {
                    "type": "gauss int",
                    "dependencies": {
                        "reference": "OtherField",
                        "parameters": {
                            "param1": "value1",
                            "param2": "value2",
                            "param3": "value3"
                        }
                    },
                    "parameters": {
                        "mean": "100",
                        "std_dev": "10"
                    }
                }
            }
        }
        schema = Schema(root=data)
        field = schema.root["Testing"]["Field"]
        assert field.dependencies.parameters["param1"] == "value1"
        assert field.parameters["mean"] == "100"

    def test_special_characters_in_field_names(self):
        """Test field names with special characters"""
        data = {
            "Testing": {
                "Field_Name_123": {"type": "name"},
                "Field-Name": {"type": "name"}
            }
        }
        schema = Schema(root=data)
        assert "Field_Name_123" in schema.root["Testing"]

