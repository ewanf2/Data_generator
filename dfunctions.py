import random
from datetime import datetime

import re
from faker import Faker

import secrets

from scipy.stats import skewnorm

fake = Faker()


def rand_skew(a, mean, mu):  # generates skewed normal distribution
    result = round(skewnorm.rvs(a, loc=mean, scale=mu, size=1)[0])
    if result <= 0:
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



# "Flyweight","Bantamweight","Featherweight","Lightweight","Welterweight","Middleweight","Light Heavyweight","Heavyweight"
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
    "sex": lambda a, b: random.choices(["male", "female"], weights=[a, b])[0],
    "stance": lambda: random.choices(["Southpaw", "Conventional", "Switch"], [1, 3, 0.7])[0],
    "randfloat": random.uniform,
    "random normal": random.gauss,
    "gauss int": gauss_int,
    "clamped gauss": lambda mu, sigma, max: min(gauss_int(mu, sigma), max),
    "Org": lambda: random.choices(["UFC", "PFL", "ONE FC", "BELLATOR", "KC"], [3, 1.5, 2, 1.5, 1.8])[0],
    "style": lambda: random.choices(["Boxing", "Kickboxing", "Wrestling", "Jiu-jitsu", "Muay thai", "Karate", "Judo"],
                                    [1.4, 1.3, 1.8, 1, 1.7, 0.4, 0.4]),
    "weightclass": lambda: random.choices(
        ["Flyweight", "Bantamweight", "Featherweight", "Lightweight", "Welterweight", "Middleweight",
         "Light Heavyweight", "Heavyweight"], [1, 1.2, 1.4, 1.8, 1.7, 1.6, 1, 0.8]),
    "linear": lambda x,m,c: m*x + c ,
    "quadratic": lambda x,m,c: m*x**2 + c
}


def data_gen(datatype, kwargs=None):
    func = datatype_map.get(datatype)
    if kwargs == {} or kwargs is None:
        return func()
    else:
        return func(**kwargs)


def user_or_email(name, t="user"):
    name = name.replace(" ", "").lower()
    name = name + str(secrets.randbelow(10) + 1)
    if t == "user":
        return name
    elif t == "email":
        return name + "@" + secrets.choice(["outlook.com", "gmail.com", "yahoo.com"])


weightclass_info = {
    "Flyweight": {"height": 160, "KO_rate": 0.16},
    "Bantamweight": {"height": 166, "KO_rate": 0.18},
    "Featherweight": {"height": 171, "KO_rate": 0.25},
    "Lightweight": {"height": 176, "KO_rate": 0.31},
    "Welterweight": {"height": 180, "KO_rate": 0.38},
    "Middleweight": {"height": 185, "KO_rate": 0.43},
    "Light Heavyweight": {"height": 190, "KO_rate": 0.51},
    "Heavyweight": {"height": 192, "KO_rate": 0.52}
}
fightstyle_info = {
    "Boxing": {"ko_rate": 0.65, "takedown_rate": 0.05, "strike_rate": 1.9, "sub_rate": 0.05},
    "Kickboxing": {"ko_rate": 0.55, "takedown_rate": 0.10, "strike_rate": 1.82, "sub_rate": 0.05},
    "Wrestling": {"ko_rate": 0.15, "takedown_rate": 0.85, "strike_rate": 1, "sub_rate": 0.55},
    "Jiu-jitsu": {"ko_rate": 0.05, "takedown_rate": 0.70, "strike_rate": 0.9, "sub_rate": 0.80},
    "Muay thai": {"ko_rate": 0.60, "takedown_rate": 0.20, "strike_rate": 1.5, "sub_rate": 0.08},
    "Karate": {"ko_rate": 0.40, "takedown_rate": 0.15, "strike_rate": 1.4, "sub_rate": 0.10},
    "Judo": {"ko_rate": 0.25, "takedown_rate": 0.75, "strike_rate": 1.1, "sub_rate": 0.70}
}


def apply_field_modifications(params, field_to_modify, style,
                              weightclass):  # modifying the params for KO rate,takedown and strike rate data generation
    # function only works on gauss int
    modify_params = params.copy()
    match field_to_modify:
        case "height/reach":  # making the height and reach match the weightclass
            modify_params["mu"] = weightclass_info[weightclass]["height"]
        case "strikes":
            modify_params["mu"] = fightstyle_info[style]["strike_rate"] * params["mu"]
        case "takedowns":
            modify_params["mu"] = fightstyle_info[style]["takedown_rate"] * params["mu"]
        case "submissions":
            modify_params["mu"] = params["mu"] * fightstyle_info[style]["sub_rate"]
        case "knockout":
            modify_params["mu"] = fightstyle_info[style]["ko_rate"] * weightclass_info[weightclass]["KO_rate"] * 5 * params["mu"]
    return data_gen("gauss int", modify_params)





def doc_generator(schema):
    doc = {}
    n = fake.name()
    style = data_gen("style")[0]
    weightclass = data_gen("weightclass")[0]
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
            case ("style", 0):
                doc[field_name] = style
            case ("weightclass", 0):
                doc[field_name] = weightclass
            case (_, 0):
                doc[field_name] = data_gen(datatype)
            case (_, _):
                if "height" in field_name.lower() or "reach" in field_name.lower() and datatype == "gauss int":  # making the height and reach match the weightclass
                    doc[field_name] = apply_field_modifications(params, "height/reach", style, weightclass)

                elif field_name.endswith(
                        "strikes thrown") and datatype == "gauss int":  # number of strikes thrown should depend on fighting style
                    doc[field_name] = apply_field_modifications(params, "strikes", style, weightclass)

                elif "takedown" in field_name and datatype == "gauss int":  # modifying the mean of this normal distribution by the takedown rate which depends on fight style
                    doc[field_name] = apply_field_modifications(params, "takedowns", style, weightclass)
                elif "submission" in field_name.lower() and datatype == "gauss int":  # calclating knockout rate based on fighter weight and style
                    doc[field_name] = min(apply_field_modifications(params, "submissions", style, weightclass),doc["Wins"]-doc["Knockout wins"])

                elif "knockout" in field_name.lower() and datatype == "gauss int":  # calclating knockout rate based on fighter weight and style
                    doc[field_name] = min(apply_field_modifications(params, "knockout", style, weightclass),
                                          doc["Wins"])
                else:
                    doc[field_name] = data_gen(datatype, params)
    return doc
