from flask import Flask, request, jsonify, abort
import spacy
from spacy.tokens import Span
from spacy.tokens import Token
import functools
import re
import json
import urllib.request
import logging

nlp = spacy.load("en_core_web_lg")

logger = logging.getLogger(__name__)


def make_dict_lowercase(d):
    """
        Utliity method to convert keys and values in a dictionary to lowercase.
    """
    lowerCaseDict = dict()
    for k in d.keys():
        lowerCaseDict[k.lower()] = d[k].lower()
    return lowerCaseDict


def to_title_case(string):
    """
        Utility to convert string to Title Case
        Input: this is a sentence.
        Output: This Is A Sentence.
    """
    return " ".join(w.capitalize() for w in string.split(" "))


def load_country_acryonym_json():
    """
        Loading JSON that has alias / acronym : country name mapping.
    """
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/rohanrmallya/coronaIndia/master/data/countries_acronym_aliases_flattened.json"
    ) as url:
        return json.loads(url.read().decode()) if url.getcode() == 200 else {}


country_acronym_lookup = make_dict_lowercase(load_country_acryonym_json())


def acronymToCountry(acronym):
    """
        Retrieve country name from acronym using @country_acronym_lookup as reference
    """
    country = country_acronym_lookup.get(acronym.lower())
    return to_title_case(country) if country != None else to_title_case(acronym)


with urllib.request.urlopen(
    "https://raw.githubusercontent.com/bhanuc/indian-list/master/state-city.json"
) as url:
    state_city = json.loads(url.read().decode())


l = ["India", "Mumbai"]
for k, v in state_city.items():
    l.append(k)
    l = l + v

l = [ele.replace("*", "") for ele in l]


def get_travel_status(span):
    if span.label_ == "GPE":
        prev_token = span.doc[span.start - 1]
        if prev_token.text in ("from", "through", "via", "Via"):
            return "from"
        elif prev_token.text in ("to", "and"):
            return "to"
        return None


def get_nat(span):
    if span.label_ == "NORP":
        return span.text


def get_rel(token):
    if token.text == "of":
        prev_token = token.doc[token.i - 1]
        prev2 = None
        if token.i > 2:
            prev2 = token.doc[token.i - 2]
            if prev2.text.lower() == "and" and str(token.doc[token.i - 3])[0] != "P":
                return f"{token.doc[token.i - 3]} {token.doc[token.i - 2]} {token.doc[token.i - 1]}"
        if prev_token.text.lower() in ("members", "member"):
            return "Family Member"
        else:
            return prev_token.text


def extract_relationship(doc):
    ids = []
    output = []
    for tok in doc:
        if tok._.relationship:
            ids.append(tok.i + 1)
    ids.append(doc.__len__())
    for i in range(len(ids) - 1):
        w = re.findall("P[0-9]+", str(doc[ids[i] : ids[i + 1]]))
        output.append({"link": doc[ids[i] - 1]._.relationship, "with": w})
    return output


def extract_travel_place(doc):
    travel = []
    for ent in doc.ents:
        if ent._.travel_status:
            travel.append(ent.text)
    return list(map(acronymToCountry, travel))


def extract_nationality(doc):
    nat = []
    for ent in doc.ents:
        if ent._.nationality:
            nat.append(ent._.nationality)
    return nat


def extract_foreign(doc):
    is_foreign = []
    for ent in doc.ents:
        if ent._.travel_status:
            is_foreign.append(
                {"place": acronymToCountry(ent.text), "is_foreign": not (ent.text in l)}
            )
    return is_foreign


Span.set_extension("travel_status", getter=get_travel_status, force=True)
Span.set_extension("nationality", getter=get_nat, force=True)
Token.set_extension("relationship", getter=get_rel, force=True)

app = Flask(__name__)

default_result = {
    "nationality": [],
    "travel": [],
    "relationship": [],
    "place_attributes": [],
}


@functools.lru_cache(30000)
def record_processor(sent):
    logger.info(f"Travel Input: {sent}")
    if not sent:
        return default_result
    s = re.sub(r"[^\w\s]", " ", sent)
    doc = nlp(s)
    return {
        "nationality": extract_nationality(doc),
        "travel": extract_travel_place(doc),
        "relationship": extract_relationship(doc),
        "place_attributes": extract_foreign(doc),
    }


def process_records(records):
    history = []
    for r in records["patients"]:
        if not ("notes" in r.keys()):
            history.append(default_result)
            logger.info(f"ಥ_ಥ Missing Notes")
        else:
            history.append({r["patientId"]: record_processor(r["notes"])})
            logger.info(
                f"Travel Output : {r['patientId']}: {record_processor(r['notes'])}"
            )
    return {"patients": history}


@app.route("/", methods=["POST"])
def single():
    try:
        req_data = request.get_json()
        results = process_records(req_data)
    except TypeError:
        logger.info(f"ಠ~ಠ TypeError Aborting")
        logger.info(f"Error Data : {req_data}")
        abort(400)
    except KeyError:
        logger.info(f"ಠ╭╮ಠ KeyError Aborting")
        logger.info(f"Error Data : {req_data}")
        return jsonify(error="Not the correct request format!")
    return results


if __name__ == "__main__":
    app.run()
