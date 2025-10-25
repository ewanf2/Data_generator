import pydantic

from pydantic import BaseModel, field_validator, RootModel
from typing import Dict, Optional

from functions import datatype_map

test = {"FieldName": {
    "type": "gauss_int",
    "dependencies": {
        "reference": "SourceField",
        "parameters": {
            "param1": "SourceField",
            "param2": "static_value"
        }}}}
bad= {7: {
    "type": "datatype",
    "dependencies": {
        "reference": "SourceField",
        "parameter": {
            "param1": "SourceField",
            "param2": "static_value"
        }}}}


class Dependencies(BaseModel):
    reference: str
    parameters: Optional[Dict[str, str]] = None

class FieldConfig(BaseModel):
    type: str
    dependencies: Optional[Dependencies] = None
    parameters: Optional[Dict[str, str]] = None
    @field_validator("type")
    def validate_type(cls, v):
        if v not in datatype_map:
            raise ValueError(f"Type {v} not in supported datatypes")
        return v

class Schema(RootModel[Dict[str, Dict[str, FieldConfig]]]):
    pass

def validate_schema(schema):
    try:
        Schema.model_validate(schema)
    except pydantic.ValidationError as error:
        return error
    else:
        return True
