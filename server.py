from flask import Flask, request, Response
from relationships import get_nationality, get_travel_place
from relationships import get_relationship, record_processor

app = Flask(__name__)

@functools.lru_cache(30000)
def record_processor(sent):
    return {
        "nationality": get_nationality(sent),
        "travel": get_travel_place(sent),
        "relationship": get_relationship(sent),
    }


def process_records(records):
    return {
        "patients": [
            {r["patientId"]: record_processor(r["notes"])} for r in records["patients"]
        ]
    }


@app.route("/", methods=["POST"])
def single():
    req_data = request.get_json()
    return process_records(req_data)
