import spacy
from spacy.tokens import Span
from spacy.tokens import Token
import functools
import re
import json

# [{ patientId : '', notes : ""}, {}...]
nlp = spacy.load("en_core_web_sm")

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


def get_relationship(sent):
    if not sent:
        return []
    s = re.sub(r"[^\w\s]", " ", sent)
    doc = nlp(s)
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


def get_travel_place(sent):
    if not sent:
        return []
    s = re.sub(r"[^\w\s]", " ", sent)
    doc = nlp(s)
    travel = []
    for ent in doc.ents:
        if ent._.travel_status:
            travel.append(ent.text)
    return travel


def get_nationality(sent):
    if not sent:
        return []
    s = re.sub(r"[^\w\s]", " ", sent)
    doc = nlp(s)
    nat = []
    for ent in doc.ents:
        if ent._.nationality:
            nat.append(ent._.nationality)
    return nat


Span.set_extension("travel_status", getter=get_travel_status, force=True)
Span.set_extension("nationality", getter=get_nat, force=True)
Token.set_extension("relationship", getter=get_rel, force=True)