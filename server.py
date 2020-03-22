from flask import Flask, request, jsonify
from relationships import get_nationality, get_travel_place, get_relationship
import functools

app = Flask(__name__)

@functools.lru_cache(30000)
def record_processor(sent):
    return {
        "nationality": get_nationality(sent),
        "travel": get_travel_place(sent),
        "relationship": get_relationship(sent),
    }


def process_records(records):
    return [
            {r["patientId"]: record_processor(r["notes"])} for r in records["patients"]
        ]


@app.route("/", methods=["POST"])
def single():
    try:
        req_data = request.get_json()
        results = process_records(req_data)
    except TypeError:
		# abort when not JSON
        abort(400)
    except KeyError:
        # return error when no org paramter
        return jsonify(error="Not the correct request format!")

    return jsonify(patients=results)
