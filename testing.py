import random
import re
from datetime import datetime
from faker import Faker
import pandas as pd
import inspect
def docGenerator_simple(schema):
    """ Takes a simple schema with no user input for ranges, i.e cannot specify date ranges.
    Takes dictionary where values are one item only"""
    doc = {}
    for k, v in schema.items():
        doc[k] = data_gen(v)
    return doc


fake = Faker()
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
}


def data_gen(datatype, info=None):
    func = datatype_map.get(datatype)
    if info != None:
        return func(**info)
    else:
        return func()


# print(fake.date(end_datetime=datetime.today()))
# print(datetime.strptime("2025-07-09", "%Y-%m-%d").date())
date_input = "2025-07-09"


def getDate(inp):
    ptrn = r'^[+-]\d+[dwmy]$'

    try:

        out = datetime.strptime(inp, "%Y-%m-%d").date()
        return (out)
    except ValueError:
        if re.match(ptrn, inp):
            return (inp)
        else:
            return (
                "Invalid input, please enter in the form YYYY-MM-DD or relative date input like +30y or -5d to signify +30 years or -5 days")


"""print(getDate("1998-02-0p"))
print(fake.date(end_datetime=getDate("+30y")))
ex = {'namer': 'name', 'dob': ('date', {'end_datetime': '+30d'})}"""
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


def data_gen(datatype, info=None):
    func = datatype_map.get(datatype)
    if info != None:
        return func(**info)
    else:
        return func()


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


ex = {'name': 'name', 'dob': ('date', {'end_datetime': '+30'})}
ex3 = {"randint": ("random int", {"a": 1, "b": 10})
       }
# print(ex3)
# print(docGenerator(ex))
example = {
    "Contact Details": {
        "Contact no": "phone number",
        'Home address': "address",
        'Email address': "email",
        "date": ("date", {"end_datetime": "+30y"}),
    }
}
e = {
    "Destination IP": "ipv4",
    "Source IP": "ipv4"
}
test = {"     ":"date"}
#print(datatype_map.keys())
s="First Last"

one_word = s.replace(" ", "").lower()
print(one_word)

