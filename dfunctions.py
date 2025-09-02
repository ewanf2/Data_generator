import random
from datetime import datetime

import re
from faker import Faker
import numexpr
import secrets

from scipy.stats import skewnorm

fake = Faker()


def rand_skew(a, mean, mu):  # generates skewed normal distribution
    result = round(skewnorm.rvs(a, loc=mean, scale=mu, size=1)[0])
    if result <= 0:
        return str(0)
    else:
        return str(result)


def get_date(inp):
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


def http_status():
    status_codes = [
        "500 Internal Server Error: Unexpected condition encountered.",
        "501 Not Implemented: Server does not support the functionality.",
        "502 Bad Gateway: Invalid response from upstream server.",
        "503 Service Unavailable: Server is temporarily overloaded or under maintenance.",
        "504 Gateway Timeout: Upstream server failed to send a request in time.",
        "505 HTTP Version Not Supported: Server does not support HTTP version used in request.",
        "507 Insufficient Storage: Server is unable to store the representation needed.",
        "508 Loop Detected: Server detected an infinite loop in processing.",
        "510 Not Extended: Further extensions are required for the request.",
        "511 Network Authentication Required: Client must authenticate to gain network access.",
        "400 Bad Request: The server could not understand the request.",
        "401 Unauthorized: Authentication is required and has failed.",
        "403 Forbidden: The server understood the request but refuses to authorize it.",
        "404 Not Found: The requested resource could not be found.",
        "405 Method Not Allowed: The method is not supported for the requested resource.",
        "406 Not Acceptable: Requested resource is only capable of generating unacceptable content.",
        "408 Request Timeout: The server timed out waiting for the request.",
        "409 Conflict: The request could not be completed due to a conflict.",
        "410 Gone: The resource requested is no longer available and will not be available again.",
        "413 Payload Too Large: The request entity is larger than the server is willing to process.",
        "414 URI Too Long: The URI provided was too long for the server to process.",
        "415 Unsupported Media Type: The server does not support the media type transmitted.",
        "429 Too Many Requests: The user has sent too many requests in a given amount of time."
    ]
    return secrets.choice(status_codes)


def generate_date(start_date="-25y", end_date="+0d"):
    start = get_date(start_date)
    end = get_date(end_date)
    return str(fake.date_between(start_date=start, end_date=end))


def gauss_int(mu=0, sigma=1):
    n = round(random.gauss(mu, sigma))
    if n < 0:
        return 0
    else:
        return n


def user_or_email(name, t="user"):
    name = name.replace(" ", "").lower()
    name = name + str(secrets.randbelow(10) + 1)
    if t == "user":
        return name
    elif t == "email":
        return name + "@" + secrets.choice(["outlook.com", "gmail.com", "yahoo.com"])


# "Flyweight","Bantamweight","Featherweight","Lightweight","Welterweight","Middleweight","Light Heavyweight","Heavyweight"
datatype_map = {
    'name': fake.name,
    'date': generate_date,
    "uuid": fake.uuid4,
    'email': user_or_email,
    'ipv4': fake.ipv4,
    'ipv6': fake.ipv6,
    'phone number': fake.phone_number,
    'address': fake.address,
    'username': fake.user_name,
    'password': fake.password,
    'boolean': fake.boolean,
    'domain': fake.domain_name,
    "random int": random.randint,
    "country code": fake.country_code,
    "timestamp": fake.iso8601,
    "HTTP status": http_status,
    "user agent": fake.user_agent,
    "HTTP method": fake.http_method,
    "hostname": fake.hostname,
    "HTTP code": fake.http_status_code,
    "sex": lambda a, b: random.choices(["male", "female"], weights=[a, b])[0],
    "stance": lambda: random.choices(["Southpaw", "Conventional", "Switch"], [1, 3, 0.7])[0],
    "randfloat": random.uniform,
    "random normal": random.gauss,
    "gauss int": gauss_int,
    "clamped gauss": lambda mu, sigma, max: min(gauss_int(mu, sigma), max),
    "Org": lambda: random.choices(
        ["UFC", "PFL", "ONE FC", "BELLATOR", "KC", "Cage Warriors", "Invicta FC", "RIZIN", "EFC", "KSW"],
        [3, 1.5, 2, 1.5, 1.8, 0.8, 0.5, 0.6, 0.4, 0.3])[0],
    "style": lambda: random.choices(["boxer", "kickboxing", "wrestler", "jiu-jitsu", "muay thai", "karate", "judo"],
                                    [1.4, 1.3, 1.8, 1, 1.7, 0.4, 0.4])[0],
    "weightclass": lambda: random.choices(
        ["Flyweight", "Bantamweight", "Featherweight", "Lightweight", "Welterweight", "Middleweight",
         "Light Heavyweight", "Heavyweight"], [1, 1.2, 1.4, 1.8, 1.7, 1.6, 1, 0.8])[0],
    "linear": lambda x, m, c: m * x + c,
    "quadratic": lambda x, m, c: m * x ** 2 + c,
    "Sizes": lambda: random.choices(["Flyweight", "Lightweight", "Heavyweight"])[0],
    "style small": lambda: random.choices(["boxer", "wrestler"])[0]
}


def data_gen(datatype, kwargs=None):
    func = datatype_map.get(datatype)
    if kwargs == {} or kwargs is None:
        return func()
    else:
        return func(**kwargs)


def primary_and_dependent_fields(schema):
    primary_fields, dependent_fields = {}, {}
    for (field_name,
         field_spec) in schema.items():  # creating dictionaries for fields that depend on other fields and fields that don't
        if "dependencies" in field_spec:
            dependent_fields[field_name] = field_spec
        else:
            primary_fields[field_name] = field_spec
    return primary_fields, dependent_fields


def generate_primary_fields(primary_fields):
    document = {}
    for (field_name, field_spec) in primary_fields.items():  # generating fields that don't depend on other fields
        datatype = field_spec["type"]
        parameters = field_spec["parameters"] if "parameters" in field_spec else None

        document[field_name] = data_gen(datatype, parameters)
    return document


def generate_dependent_fields(dependent_fields, doc):
    document = {}
    generated_docs_so_far = doc.copy()
    dependent_fields = dependent_fields.copy()
    # print(generated_docs_so_far)
    for (field_name, field_spec) in dependent_fields.items():  # generating data for all the dependent fields
        dependencies, datatype = field_spec["dependencies"], field_spec["type"]
        if "categorical" in dependencies:
            dependencies = field_spec["dependencies"].copy()
            source_field_names = dependencies.pop("categorical")
            match source_field_names:
                case list():  # more than one field categorical dependency

                    sources = {i: generated_docs_so_far[i] for i in
                               source_field_names}  # the other fields that this field depends on
                    sources_values = list(sources.values())
                    params = dependencies
                    for value in sources_values:
                        params = params[value]

                    document[field_name] = data_gen(datatype, params)
                    generated_docs_so_far.update(document)
                case str():  # where the source field dependencies is only one field
                    category_value = doc[source_field_names]

                    params = dependencies[category_value]
                    document[field_name] = data_gen(datatype, params)
                    generated_docs_so_far.update(document)
        elif "textual" in dependencies:
            dependencies = field_spec["dependencies"].copy()

            source_field = dependencies.pop("textual")

            parameters = dependencies.pop("parameters")
            new_vals = [generated_docs_so_far[value] if value == source_field else value for value in parameters.values()]
            new_params = {k: v for k, v in zip(parameters.keys(), new_vals)}
            document[field_name] = data_gen(datatype, new_params)


        elif "numerical" in dependencies:
            dependencies = field_spec["dependencies"].copy()
            source_field_names, formula = dependencies.pop("numerical"), dependencies[
                "formula"]  # the field name we have a numerical dependency on
            for i in source_field_names:
                source_field_value = generated_docs_so_far  # the value of that field in this document

                formula = formula.replace(i, str(generated_docs_so_far[i]))


            document[field_name] = eval(formula)
            generated_docs_so_far.update(document)
    return document


def doc_generator(schema):  # new doc_generator function, less hardcoded
    primary_fields, dependent_fields = primary_and_dependent_fields(
        schema)  # Generating list of primary and dependent fields
    doc = {}
    doc.update(generate_primary_fields(primary_fields))  # generating primary field data first
    doc.update(generate_dependent_fields(dependent_fields, doc))
    return doc
