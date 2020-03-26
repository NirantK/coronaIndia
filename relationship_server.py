import spacy
from spacy.tokens import Span
from spacy.tokens import Token
import functools
import re
import json
import urllib.request
import logging
from fastapi import FastAPI
from schema import PatientList

# [{ patientId : '', notes : ""}, {}...]
nlp = spacy.load("en_core_web_sm")

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
        return "to"


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
    return travel


def extract_nationality(doc):
    nat = []
    for ent in doc.ents:
        if ent._.nationality:
            nat.append(ent._.nationality)
    return nat


def extract_foreign(doc):
    is_foreign = []
    for ent in doc.ents:
        if ent.label_ == "GPE":
            is_foreign.append({"place": ent.text, "is_foreign":not(ent.text in l)})
    return is_foreign


Span.set_extension("travel_status", getter=get_travel_status, force=True)
Span.set_extension("nationality", getter=get_nat, force=True)
Token.set_extension("relationship", getter=get_rel, force=True)

app = FastAPI()

@functools.lru_cache(30000)
def record_processor(sent):
    if not sent:
        return {
                "nationality": [],
                "travel": [],
                "relationship": [],
                "place_attributes": [],
            }
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
    for r in records.patients:
        history.append({r.patientId: record_processor(r.notes)})
        print(f"Output : {r.patientId}: {record_processor(r.notes)}")

    return {
        "patients": history
    }


@app.post("/")
def single(patients: PatientList):
    try:
        results = process_records(patients)
    except TypeError:
        # abort when not JSON
        abort(400)
    except KeyError:
        # return error when no org paramter
        return jsonify(error="Not the correct request format!")

    print(f"Input : {patients}")
    return results

@app.get("/status/")
def status():
    return {
        "status": "alive"
    }
