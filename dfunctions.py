import random
from datetime import datetime


import re
from faker import Faker

import secrets

from scipy.stats import skewnorm

fake = Faker()
def rand_skew(a,mean,mu): #generates skewed normal distribution
    result= round(skewnorm.rvs(a,loc=mean,scale=mu,size=1)[0])
    if result <=0:
        return 0
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
def stance():
    return secrets.choice(["Southpaw", "Orthodox"])
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
def generate_date(start_date ="-25y",end_date ="+0d"):
    start = get_date(start_date)
    end = get_date(end_date)
    return str(fake.date_between(start_date=start, end_date=end))


def record():
    w,l,d=random.randint(0,35),random.randint(0,15) ,random.randint(0,2)
    return f"{w}-{d}-{l}"

datatype_map = {
    'name': fake.name,
    'date': generate_date,
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
    "country code": fake.country_code,
    "timestamp": fake.iso8601,
    "HTTP status": http_status,
    "user agent": fake.user_agent,
    "HTTP method": fake.http_method,
    "hostname": fake.hostname,
    "HTTP code": fake.http_status_code,
    "sex": lambda : secrets.choice(["male","female"]),
    "stance":stance,
    "record":record,
    "randfloat":random.uniform,
    "random normal":random.gauss,
    "random skew":rand_skew,
    "win/lose": lambda : secrets.choice(["red","blue"]),
    "time":fake.time,
    "MethodOfWin":lambda :secrets.choice(["Submission","Decision","Knockout"]),
    "style" : lambda :secrets.choice(["Boxing","Kickboxing","Wrestling","Jiu-jitsu","Muay thai","Karate"]),
    "weightclass":lambda :secrets.choice(["Flyweight","Bantamweight","Featherweight","Lightweight","Welterweight","Middleweight","Light Heavyweight","Heavyweight"]),
}

def data_gen(datatype, info=None):
    func = datatype_map.get(datatype)
    if info == {} or info is None:
        return func()
    else:
        return func(**info)
def user_or_email(name, t="user"):
    name = name.replace(" ", "").lower()
    name = name + str(secrets.randbelow(10) + 1)
    if t == "user":
        return name
    elif t == "email":
        return name + "@" + secrets.choice(["outlook.com", "gmail.com", "yahoo.com"])

def doc_generator(schema):
    doc = {}
    n = fake.name()
    style = "Wrestling"#data_gen("style")
    for (field_name, v) in schema.items():
        v = v.copy()
        datatype, params = v.pop("type"), v

        match (datatype, len(params)):
            case ("name", _):
                doc[field_name] = n
            case ("email", _):
                doc[field_name] = user_or_email(n, t="email")
            case ("username", _):
                doc[field_name] = user_or_email(n, t="username")
            case ("style", params_len) if params_len == 0:
                doc[field_name] = style
            case (_, 0):
                doc[field_name] = data_gen(datatype)
            case (_, _):
                if field_name.endswith("strikes thrown"):
                    match style:
                        case "Boxing"|"Kickboxing"|"Karate"|"Muay thai":
                            doc[field_name] = data_gen("random skew",{"a":-2,"mean":300,"mu":100})
                        case "Wrestling"| "Jiu-jitsu":
                            doc[field_name] = data_gen("random skew", {"a":2,"mean":300,"mu":100})
                elif "takedown" in field_name:

                    match style:
                        case "Boxing" | "Kickboxing" | "Karate" | "Muay thai":
                            doc[field_name] = data_gen("random skew", {"a": 6, "mean": 3, "mu": 3})
                        case "Wrestling" | "Jiu-jitsu":

                            doc[field_name] = data_gen("random skew", {"a": 5, "mean": 30, "mu": 15})
                elif "submissions" in field_name:
                    match style:
                        case "Jiu-jitsu":
                            doc[field_name] = data_gen("random skew", {"a": 5, "mean": 9, "mu": 2})
                        case _:
                            doc[field_name] = data_gen("random skew", {"a": 5, "mean": 2, "mu": 1})
                else:
                    doc[field_name] = data_gen(datatype, params)
    return doc

#def rand_int():
    #return random.randrange(0, 101)