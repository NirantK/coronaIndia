import pytest

from relationship_server import process_records, record_processor


def test_record_processor():
    """
    Testing record_processor: Should return empty list when there is no input.
    """
    assert record_processor("   ") == {
        "nationality": [],
        "travel": [],
        "relationship": [],
        "place_attributes": [],
    }
    assert record_processor("") == {
        "nationality": [],
        "travel": [],
        "relationship": [],
        "place_attributes": [],
    }


def test_nationality():
    """Checks Nationality
    """
    assert record_processor("Indian Student Studying in Italy") == {
        "nationality": ["Indian"],
        "travel": [],
        "relationship": [],
        "place_attributes": [],
    }


def test_travel():
    """Checks if the Travel place is returned with appropriate `place_attributes`
    """
    assert record_processor("Traveled from Italy") == {
        "nationality": [],
        "travel": ["Italy"],
        "relationship": [],
        "place_attributes": [{"place": "Italy", "is_foreign": True}],
    }
    assert record_processor("Traveled to Pune") == {
        "nationality": [],
        "travel": ["Pune"],
        "relationship": [],
        "place_attributes": [{"place": "Pune", "is_foreign": False}],
    }
    assert record_processor("Traveled from United Kingdom") == {
        "nationality": [],
        "travel": ["United Kingdom"],
        "relationship": [],
        "place_attributes": [{"place": "United Kingdom", "is_foreign": True}],
    }


def test_travel_acronymns():
    """Checks for acronymn to country name mapping
    """
    assert record_processor("Traveled to UK") == {
        "nationality": [],
        "travel": ["United Kingdom"],
        "relationship": [],
        "place_attributes": [{"place": "United Kingdom", "is_foreign": True}],
    }
    assert record_processor("Traveled from UK") == {
        "nationality": [],
        "travel": ["United Kingdom"],
        "relationship": [],
        "place_attributes": [{"place": "United Kingdom", "is_foreign": True}],
    }
    assert record_processor("Traveled from US") == {
        "nationality": [],
        "travel": ["United States"],
        "relationship": [],
        "place_attributes": [{"place": "United States", "is_foreign": True}],
    }
    assert record_processor("Traveled from USA") == {
        "nationality": [],
        "travel": ["United States"],
        "relationship": [],
        "place_attributes": [{"place": "United States", "is_foreign": True}],
    }
    assert record_processor("Traveled to UK and Japan") == {
        "nationality": [],
        "travel": ["United Kingdom", "Japan"],
        "relationship": [],
        "place_attributes": [
            {"place": "United Kingdom", "is_foreign": True},
            {"place": "Japan", "is_foreign": True},
        ],
    }


def test_travel_aliases():
    """Checks for Aliases to country name mapping
    """
    assert record_processor("Traveled from Republic of South Korea") == {
        "nationality": [],
        "travel": ["South Korea"],
        "relationship": [],
        "place_attributes": [{"place": "South Korea", "is_foreign": True},],
    }  # Republic is picked up as a relationship

    assert record_processor("Traveled from Aphsny Axwynthkharra") == {
        "nationality": [],
        "travel": ["Abkhazia"],
        "relationship": [],
        "place_attributes": [{"place": "Abkhazia", "is_foreign": True},],
    }

    assert record_processor("Traveled from Holland") == {
        "nationality": [],
        "travel": ["Netherlands"],
        "relationship": [],
        "place_attributes": [{"place": "Netherlands", "is_foreign": True},],
    }


def test_relationship():
    """Relationship mapping
    """
    assert record_processor("Son of P13") == {
        "nationality": [],
        "travel": [],
        "relationship": [{"link": "Son", "with": ["P13"]}],
        "place_attributes": [],
    }
    # Same link with Multiple people
    assert record_processor("Son of P13 and P14") == {
        "nationality": [],
        "travel": [],
        "relationship": [{"link": "Son", "with": ["P13", "P14"]}],
        "place_attributes": [],
    }
    # Multiple Links
    assert record_processor("Son of P13 and P14 friend of P16, P17, P18") == {
        "nationality": [],
        "travel": [],
        "relationship": [
            {"link": "Son", "with": ["P13", "P14"]},
            {"link": "friend", "with": ["P16", "P17", "P18"]},
        ],
        "place_attributes": [],
    }


def test_process_records():
    """
    """
    records = {
        "patients": [
            {
                "patientId": "1",
                "notes": "Indian Student Travelled from Italy, Family Member of P13 Friend with P12",
            }
        ]
    }
    assert process_records(records) == {
        "patients": [
            {
                "1": {
                    "nationality": ["Indian"],
                    "travel": ["Italy"],
                    "relationship": [{"link": "Family Member", "with": ["P13", "P12"]}],
                    "place_attributes": [{"place": "Italy", "is_foreign": True}],
                }
            }
        ]
    }


def test_input_error_missing_notes():
    """process_records should return default output if notes are missing.
    """
    records = {"patients": [{"patientId": "1"}]}
    assert process_records(records) == {
        "patients": [
            {
                "nationality": [],
                "travel": [],
                "relationship": [],
                "place_attributes": [],
            }
        ]
    }


def test_input_error_missing_patientId():
    """process_records should throw KeyError if patientId is missing.
    """
    records = {
        "patients": [
            {
                "notes": "Indian Student Travelled from Italy, Family Member of P3 Friend with P2"
            }
        ]
    }
    with pytest.raises(Exception) as excinfo:
        process_records(records)
    assert type(excinfo.value) == KeyError
    assert excinfo.value.args[0] == "patientId"
