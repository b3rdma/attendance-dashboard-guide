#!/usr/bin/env python3
"""Build independent DAX acceptance fixtures, not execute DAX.

Write disposable calculated-table declarations and arithmetic expectations outside
the repository. Create the tables only in a separate empty Power BI test model.
"""

import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def fixtures():
    # Match the existing review's three-session common fixture.
    base_sessions = [
        {"SessionID": "S1", "Session Number": 1, "Session Duration Seconds": 1800, "Attended Participants": 1},
        {"SessionID": "S2", "Session Number": 2, "Session Duration Seconds": 3600, "Attended Participants": 3},
        {"SessionID": "S3", "Session Number": 3, "Session Duration Seconds": 3600, "Attended Participants": 1},
    ]
    base_attendance = [(1, "A", 1800), (2, "A", 1800), (2, "B", 1800), (2, "C", 1800), (3, "B", 3600)]
    growth_sessions = [
        {"SessionID": f"S{i}", "Session Number": i, "Session Duration Seconds": 3600,
         "Attended Participants": 2 if i in (2, 7) else 1}
        for i in range(1, 8)
    ]
    growth_attendance = [(i, "A", 3600) for i in range(1, 8)] + [(2, "B", 1800), (7, "C", 900)]

    def make(sessions, attendance):
        facts = [{"SessionID": f"S{number}", "Session Number": number,
                  "Email": f"person{person.lower()}@example.invalid",
                  "Attendance Duration Seconds": duration}
                 for number, person, duration in attendance]
        people = [{"Email": email, "Participant Name": f"Fixture person {email[6].upper()}"}
                  for email in sorted({row["Email"] for row in facts})]
        return {"dimSession": sessions, "factAttendance": facts, "dimPerson": people}

    return {"base": make(base_sessions, base_attendance), "growth": make(growth_sessions, growth_attendance)}


def expected(fixture, selected_sessions=None, selected_people=None):
    """Evaluate business definitions in Python; this is not DAX filter simulation."""
    sessions = fixture["dimSession"]
    history = fixture["factAttendance"]
    by_id = {row["SessionID"]: row for row in sessions}
    selected = [row for row in sessions if selected_sessions is None or row["Session Number"] in selected_sessions]
    selected_ids = {row["SessionID"] for row in selected}
    emails = None if selected_people is None else {f"person{p.lower()}@example.invalid" for p in selected_people}
    visible = [row for row in history if row["SessionID"] in selected_ids and (emails is None or row["Email"] in emails)]
    first = {email: min(row["Session Number"] for row in history if row["Email"] == email)
             for email in {row["Email"] for row in history}}
    visits = Counter(row["Email"] for row in visible)
    new = sum(row["Session Number"] == first[row["Email"]] for row in visible)
    ratios = [Fraction(row["Attendance Duration Seconds"], by_id[row["SessionID"]]["Session Duration Seconds"]) for row in visible]
    per_session = [[ratio for row, ratio in zip(visible, ratios) if row["SessionID"] == session["SessionID"]] for session in selected]
    session_means = [sum(values) / len(values) for values in per_session if values]
    attended_seconds = sum(row["Attendance Duration Seconds"] for row in visible)
    opportunity_seconds = sum(by_id[row["SessionID"]]["Session Duration Seconds"] for row in visible)
    repeat_people = sum(count >= 2 for count in visits.values())
    return {
        "SelectedSessions": len(selected), "AttendanceEvents": len(visible), "UniqueAttendees": len(visits),
        "NewAttendanceEvents": new, "ReturningAttendanceEvents": len(visible) - new,
        "AdditionalVisitsWithinSelection": len(visible) - len(visits), "RepeatParticipants": repeat_people,
        "RepeatParticipantShare": repeat_people / len(visits) if visits else None,
        "ParticipantHours": attended_seconds / 3600,
        "AverageIndividualCoverage": float(sum(ratios) / len(ratios)) if ratios else None,
        "EqualSessionCoverage": float(sum(session_means) / len(session_means)) if session_means else None,
        "DurationWeightedCoverage": attended_seconds / opportunity_seconds if opportunity_seconds else None,
        "AverageAttendeesPerSelectedSession": len(visible) / len(selected) if selected else None,
        "PeopleBySessionCount": dict(sorted(Counter(visits.values()).items())),
        "FirstRecordedSessionForSelectedPerson": first[next(iter(emails))] if emails is not None and len(emails) == 1 else None,
    }


def table_declaration(name, rows):
    fields = list(rows[0])
    quote = lambda value: '"' + value.replace('"', '""') + '"'
    types = {field: "INTEGER" if isinstance(rows[0][field], int) else "STRING" for field in fields}
    schema = ",\n    ".join(f"{quote(field)}, {types[field]}" for field in fields)
    values = ",\n        ".join("{" + ", ".join(str(row[field]) if types[field] == "INTEGER" else quote(row[field]) for field in fields) + "}" for row in rows)
    return f"{name} =\nDATATABLE(\n    {schema},\n    {{\n        {values}\n    }}\n)\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="A disposable directory outside this repository")
    args = parser.parse_args()
    output = (args.output_dir or Path(tempfile.mkdtemp(prefix="attendance-dax-fixture-"))).resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("Choose an output directory outside the repository")
    output.mkdir(parents=True, exist_ok=True)
    data = fixtures()
    cases = [
        ("base_all", "base", None, None),
        ("base_S1", "base", [1], None),
        ("base_S2", "base", [2], None),
        ("base_S3", "base", [3], None),
        ("base_S2_S3", "base", [2, 3], None),
        ("base_non_contiguous_S1_S3", "base", [1, 3], None),
        ("base_person_B", "base", None, ["B"]),
        ("base_person_B_no_visit_in_S1", "base", [1], ["B"]),
        ("base_no_selected_sessions", "base", [], None),
        ("growth_seven_visits", "growth", None, None),
        ("growth_last_session", "growth", [7], None),
    ]
    results = [{"Case": name, "Fixture": fixture, "Sessions": sessions, "People": people,
                "Expected": expected(data[fixture], sessions, people)}
               for name, fixture, sessions, people in cases]
    base = results[0]["Expected"]
    assert (base["AttendanceEvents"], base["UniqueAttendees"], base["NewAttendanceEvents"], base["ReturningAttendanceEvents"]) == (5, 3, 3, 2)
    assert base["AverageIndividualCoverage"] == 0.7
    assert base["EqualSessionCoverage"] == float(Fraction(5, 6))
    assert base["DurationWeightedCoverage"] == float(Fraction(2, 3))
    assert results[7]["Expected"]["FirstRecordedSessionForSelectedPerson"] == 2
    assert results[9]["Expected"]["PeopleBySessionCount"] == {1: 2, 7: 1}
    for fixture, tables in data.items():
        directory = output / fixture
        directory.mkdir(exist_ok=True)
        for name, rows in tables.items():
            (directory / f"{name}.dax").write_text(table_declaration(name, rows))
    record = {"Method": "Independent arithmetic expectations, not DAX execution", "Cases": results}
    (output / "expected_results.json").write_text(json.dumps(record, indent=2) + "\n")
    (output / "fixture_data.json").write_text(json.dumps(data, indent=2) + "\n")
    print("Generated disposable table declarations and 11 arithmetic expectations; DAX has not been executed")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
