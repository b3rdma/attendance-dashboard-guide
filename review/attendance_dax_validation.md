# Test attendance measures

[Build the model](../guide/attendance_rebuild.md) · [Measure catalogue](../dashboard_measures/attendance_rebuild_measures.md)

These invented examples give small results that can be checked by hand. The generator calculates expected values in Python; it does not execute DAX or test Power BI relationships.

## Generate a separate test model

```sh
python3 scripts/build_attendance_dax_fixture.py
```

The script prints a temporary directory containing base and growth table declarations and expected results. In a separate blank Power BI file, create dimSession, factAttendance and dimPerson using the base declarations. Add the two active Single relationships and the measures from the catalogue. Create Attendance Bands as a disconnected table.

Use lookup fields for meeting and person selections. The fixtures omit dates, titles and engagement fields; check those separately with the intended source.

## Base fixture

| Meeting | Duration | Attendance |
| --- | ---: | --- |
| S1 | 30 minutes | A: 30 minutes |
| S2 | 60 minutes | A, B and C: 30 minutes each |
| S3 | 60 minutes | B: 60 minutes |

A first appears in S1; B and C first appear in S2.

| Selection | Visits | People | New visits | Returning visits | Repeat people | Primary coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All meetings | 5 | 3 | 3 | 2 | 2 | 70% |
| S1 | 1 | 1 | 1 | 0 | 0 | 100% |
| S2 | 3 | 3 | 2 | 1 | 0 | 50% |
| S3 | 1 | 1 | 0 | 1 | 0 | 100% |
| S2 and S3 | 4 | 3 | 2 | 2 | 1 | 62.5% |
| S1 and S3 | 2 | 2 | 1 | 1 | 0 | 100% |
| B, all meetings | 2 | 1 | 1 | 1 | 1 | 75% |
| B, S1 only | 0 | 0 | 0 | 0 | 0 | Blank |

All-meeting participant time is 180 minutes, or three hours. Mean visit duration is 36 minutes. Time-weighted coverage is 180 / 270 = 66.666667%, which differs from the primary mean of 70%.

With B and S1 selected, First Session Attended still returns 2 because it searches retained history. The repeat label is blank when B has no selected attendance. With A and S1, that label is No. A total spanning several people must not infer one person just because a single attendance row is visible.

## Inspect results in DAX

Run this query in the fixture model and compare both rows and overall totals:

```dax
EVALUATE
SUMMARIZECOLUMNS(
    dimSession[Session Number],
    "Visits", [Total Attendance Records],
    "People", [Unique Attendees],
    "New visits", [New Attendees],
    "Returning visits", [Returning Attendance Events],
    "Repeat people", [Repeat Participants],
    "Coverage", [Average Attendance Coverage %],
    "Participant-hours", [Total Attendance Hours]
)
ORDER BY dimSession[Session Number]
```

A grouped query does not by itself test a total. Inspect cards or a Matrix total as well.

## Growth and edge cases

Use the separate growth fixture: A attends all seven one-hour meetings, B attends S2 for 30 minutes and C attends S7 for 15 minutes. Expect nine visits, three people, three new visits and six returning visits. Bands contain two people at one meeting and one person at seven meetings.

At S7 alone, expect two visits, one new and one returning, no selected-period repeat people and 62.5% primary coverage. The seventh band must remain available in the full history.

Test single and multiple bands, non-contiguous meetings, a person with no selected attendance and an explicit filter matching no rows. Counts should be zero for an empty population; undefined ratios stay blank. Clearing a slicer normally restores all records rather than creating an empty selection.

Compare integer counts exactly and ratios within a stated tolerance, such as 0.000000001. Record the Power BI version, formula revision, source/fixture, selections and observed results. Add source-date, chart-interaction and action-count checks before deploying the reporting copy.
