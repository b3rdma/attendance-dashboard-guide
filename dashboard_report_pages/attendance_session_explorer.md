# Example session detail page

[Attendance build](../guide/attendance_rebuild.md) · [Core measures](../dashboard_measures/attendance_rebuild_measures.md)

Use an optional detail page to inspect one meeting or a selection of meetings. Layout and styling are flexible. If specifying positions, use a 1920 x 1080 Full HD canvas.

## Fields and interactions

- Use dimSession Session Number in a multi-select slicer, sorted numerically.
- Show attendance visits, new visits, returning visits, primary coverage, mean minutes and participant-hours.
- Use dimPerson name/email in the participant table with Sessions Attended and the relevant measures.
- Use meeting fields from dimSession so the same selection applies to attendance and meeting denominators.
- Check directional visual interactions; do not let a selected chart silently change only some populations.

## Display measures

Create the following through New measure. A separate wide title and date/duration text box avoids placing an excessively long combined value in one card. Keep multi-meeting and empty contexts labelled clearly.

```dax
Session Explorer Title =
VAR SessionCount = COUNTROWS(dimSession)
RETURN
SWITCH(
    TRUE(),
    SessionCount = 0, "No sessions in the current selection",
    SessionCount = 1,
        "Session " & FORMAT(SELECTEDVALUE(dimSession[Session Number]), "0")
            & " | " & SELECTEDVALUE(dimSession[Session Title]),
    FORMAT(SessionCount, "0") & " sessions selected"
)
```

```dax
Session Explorer Metadata =
VAR SessionCount = COUNTROWS(dimSession)
RETURN
SWITCH(
    TRUE(),
    SessionCount = 1,
        FORMAT(SELECTEDVALUE(dimSession[Session Date]), "dd mmm yyyy", "en-GB")
            & " | Recorded duration: " & SELECTEDVALUE(dimSession[Session Duration]),
    SessionCount > 1, "Attendance records across the selected meetings",
    BLANK()
)
```

The combined context expression below is an alternative for a table or tooltip. Use text wrapping where the chosen visual supports it.

```dax
Session Explorer Context =
VAR SessionCount = COUNTROWS(dimSession)
RETURN
SWITCH(
    TRUE(),
    SessionCount = 0, "No sessions in the current selection",
    SessionCount = 1,
        "Session " & FORMAT(SELECTEDVALUE(dimSession[Session Number]), "0")
            & " | " & SELECTEDVALUE(dimSession[Session Title])
            & UNICHAR(10)
            & FORMAT(SELECTEDVALUE(dimSession[Session Date]), "dd mmm yyyy", "en-GB")
            & " | Recorded duration: " & SELECTEDVALUE(dimSession[Session Duration]),
    FORMAT(SessionCount, "0") & " sessions selected | Attendance records across the selected meetings"
)
```

## Optional coverage distribution

Create the following disconnected table through New table, followed by the measure through New measure:

```dax
Attendance Coverage Bands =
DATATABLE(
    "Band Order", INTEGER,
    "Coverage Band", STRING,
    {
        {1, "0% to <25%"},
        {2, "25% to <50%"},
        {3, "50% to <75%"},
        {4, "75% to 100%"},
        {5, "Over 100%"},
        {6, "Unavailable"}
    }
)
```

```dax
Attendance Records by Coverage Band =
VAR SelectedBands =
    VALUES('Attendance Coverage Bands'[Band Order])
RETURN
COALESCE(
    COUNTROWS(
        FILTER(
            factAttendance,
            VAR Coverage =
                DIVIDE(
                    factAttendance[Attendance Duration Seconds],
                    RELATED(dimSession[Session Duration Seconds])
                )
            VAR BandOrder =
                SWITCH(
                    TRUE(),
                    ISBLANK(Coverage), 6,
                    Coverage < 0.25, 1,
                    Coverage < 0.50, 2,
                    Coverage < 0.75, 3,
                    Coverage <= 1, 4,
                    5
                )
            RETURN
                BandOrder IN SelectedBands
        )
    ),
    0
)
```

Use Attendance Coverage Bands[Coverage Band] on the chart axis and Attendance Records by Coverage Band as the value. Sort Coverage Band by Band Order. Add a visual-level filter with the measure greater than zero and leave Show items with no data off. This hides empty categories while preserving their definitions.

A person can contribute several visits across selected meetings, so this chart counts attendance records rather than distinct people. Over 100% and Unavailable remain diagnostic categories when records meet those conditions; do not force empty categories to occupy chart space.

## Check the page

1. Compare one selected meeting with its source and the underlying records.
2. Select several meetings and confirm title, counts, coverage and participant rows use that scope.
3. Confirm new plus returning equals attendance visits.
4. Reconcile coverage-band counts to included visits and inspect any unavailable or over-100% record.
5. Check no-data contexts, person filters, sorting and chart interactions using the synthetic acceptance cases.

Keep the numerical meaning fixed when changing the presentation. This page adds optional display and coverage-category objects; the twenty core measures remain in the main catalogue.
