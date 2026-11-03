# Attendance measures for the documented rebuild

[Build the attendance model](../guide/attendance_rebuild.md) · [Understand the metrics](../guide/attendance_reading_report.md) · [Check expected results](../review/attendance_dax_validation.md)

## Use this catalogue

Create these twenty measures and the calculated Attendance Bands table for the example attendance model. Copy each expression into the stated Power BI object. The table supplies labels at refresh; measures calculate results for the current selection.

The calculations assume one attendance row per person per meeting, complete stable email keys and the two Single relationships. Read [the assumptions](../guide/attendance_assumptions.md) and test [the invented controls](../review/attendance_dax_validation.md) before using a new source.

## Install and format

Create the calculated table below through New table. Create the measures through New measure in the order on this page. Use dimSession as the home table for Total Sessions and Average Session Attendance; use factAttendance for the other measures. A measure's home table organises the field list and does not change its calculation. Hide First Session Attended only if report authors do not need to add it to a person table.

Format counts as whole numbers, percentages with one decimal place, and minutes/hours with one or two decimals. Retain extra decimal places during validation. Keep numeric results numeric; do not apply FORMAT to the core values. Zero means a defined count of none. A blank percentage or average means there is no valid denominator or supported context.

Use dimSession fields for meeting/date axes and slicers, and dimPerson fields for person selections. A field copied into factAttendance may filter attendance without filtering the session denominator. Check totals as calculations in their own right; do not assume every total is a sum of displayed rows.

## Attendance Bands calculated table

Create this once before People in Attendance Band. Keep it disconnected. The highest label grows with the number of loaded meetings at refresh, while a report selection changes which band each person occupies. The expression names its output Sessions Attended explicitly, so no manual Value-column rename is needed for this version.

```dax
Attendance Bands =
SELECTCOLUMNS(
    GENERATESERIES(
        1,
        MAX(1, COUNTROWS(dimSession)),
        1
    ),
    "Sessions Attended", [Value]
)
```

## Total Attendance Records

**Plain-English meaning: Attendance visits.** Count one attendance visit for every retained person-meeting row. One person attending three meetings contributes three visits. Return zero when no visits are selected.

```dax
Total Attendance Records =
COALESCE(COUNTROWS(factAttendance), 0)
```

## Unique Attendees

**Plain-English meaning: Different people.** Count each email once across the selected meetings. The same person attending three meetings contributes one person to this figure. Return zero when no people are selected.

```dax
Unique Attendees =
COALESCE(DISTINCTCOUNT(factAttendance[Email]), 0)
```

## Total Sessions

**Plain-English meaning: Selected meetings.** Count the selected rows in dimSession. Selecting a person does not reduce this meeting population because the relationships filter towards attendance records, not backwards into meetings.

```dax
Total Sessions =
COALESCE(COUNTROWS(dimSession), 0)
```

## Sessions Attended

**Plain-English meaning: Meetings represented by the attendance selection.** Count different meeting keys in the selected attendance rows. For one selected person, this is the number of selected meetings that person attended. It can be lower than Total Sessions.

```dax
Sessions Attended =
COALESCE(DISTINCTCOUNT(factAttendance[SessionID]), 0)
```

## Average Attendance Minutes

**Plain-English meaning: Average recorded visit length.** Average the recorded attendance seconds across the selected visits and convert the result to minutes. Each visit has the same weight. This is neither total participant time nor the length of the meeting.

```dax
Average Attendance Minutes =
// Convert mean row duration from seconds to minutes.
DIVIDE(
    AVERAGE(
        factAttendance[Attendance Duration Seconds]
    ),
    60
)
```

## Average Attendees per Session

**Plain-English meaning: Attendance visits per selected meeting.** Divide selected visits by selected meetings. A selected meeting with no visit for the selected people still contributes to the denominator. Use dimSession fields when selecting meetings.

```dax
Average Attendees per Session =
// Divide retained attendance rows by selected session rows.
DIVIDE(
    [Total Attendance Records],
    [Total Sessions]
)
```

## Average Session Attendance

**Plain-English meaning: Source-summary attendance check.** Average the participant counts supplied by Teams in the meeting summaries. Keep this as a separately labelled reconciliation measure. It describes selected meeting summaries and does not shrink when selecting one person.

```dax
Average Session Attendance =
// Average the source-reported count across selected session rows.
AVERAGE(
    dimSession[Attended Participants]
)
```

## Average Attendance Coverage %

**Plain-English meaning: Primary attendance duration percentage.** For every selected visit, divide that person's recorded attendance seconds by the duration of that visit's meeting. Average those individual percentages. Each person-meeting visit has equal weight. For example, 100% and 50% average to 75%. An undefined ratio is left blank.

```dax
Average Attendance Coverage % =
AVERAGEX(
    factAttendance,
    DIVIDE(
        factAttendance[Attendance Duration Seconds],
        RELATED(dimSession[Session Duration Seconds])
    )
)
```

## Time-weighted Attendance Coverage %

**Plain-English meaning: Companion percentage weighted by duration.** Divide all selected attendance time by the possible attendance time of those same visits. Count the matching meeting duration once for each selected visit. Longer meeting opportunities carry more weight. Keep its label distinct from the primary average.

```dax
Time-weighted Attendance Coverage % =
DIVIDE(
    SUM(factAttendance[Attendance Duration Seconds]),
    SUMX(
        factAttendance,
        RELATED(dimSession[Session Duration Seconds])
    )
)
```

## Total Attendance Hours

**Plain-English meaning: Total participant time.** Add the selected attendance seconds and divide by 3,600. Ten people attending a one-hour meeting contribute ten participant-hours. This is recorded attendance time, not hours of learning achieved.

```dax
Total Attendance Hours =
DIVIDE(
    COALESCE(SUM(factAttendance[Attendance Duration Seconds]), 0),
    3600
)
```

## First Session Attended

**Plain-English meaning: One person's first retained meeting.** Find the selected person's earliest Session Number in all retained source history. Ignore the current meeting/date selection when finding that first appearance. Leave aggregate multi-person contexts blank. Adding an older export can legitimately change the result.

```dax
First Session Attended =
VAR PersonEmail =
    COALESCE(
        SELECTEDVALUE(dimPerson[Email]),
        IF(
            ISFILTERED(factAttendance[Email]),
            SELECTEDVALUE(factAttendance[Email])
        )
    )
RETURN
IF(
    NOT ISBLANK(PersonEmail),
    CALCULATE(
        MIN(factAttendance[Session Number]),
        REMOVEFILTERS(),
        TREATAS({PersonEmail}, factAttendance[Email])
    )
)
```

## New Attendees

**Plain-English meaning: First recorded attendance in the selection.** Count selected visits that are the person's first in retained history. A person can contribute at most one such visit. Earlier attendance outside the current selection still determines whether the person is new. The total across selected meetings is defined and additive.

```dax
New Attendees =
COALESCE(
    SUMX(
        VALUES(factAttendance[Email]),
        VAR FirstLoadedSession = [First Session Attended]
        RETURN
            CALCULATE(
                COUNTROWS(factAttendance),
                KEEPFILTERS(
                    factAttendance[Session Number] = FirstLoadedSession
                )
            )
    ),
    0
)
```

## Returning Attendance Events

**Plain-English meaning: Visits after a person's first retained attendance.** Subtract first recorded visits from all selected visits. A person can contribute several returning visits. New Attendees plus Returning Attendance Events must equal Total Attendance Records.

```dax
Returning Attendance Events =
[Total Attendance Records] - [New Attendees]
```

## Returning Attendance Share %

**Plain-English meaning: Share of visits made after first appearance.** Divide returning visits by all selected visits. This is a share of attendance events, not the share of people who returned. Leave the ratio blank when there are no visits.

```dax
Returning Attendance Share % =
DIVIDE([Returning Attendance Events], [Total Attendance Records])
```

## Repeat Participants

**Plain-English meaning: People attending at least twice within the selection.** Count selected people who attended at least two selected meetings. Attendance before the selection does not qualify a person unless two meetings remain inside the selection. Count each qualifying person once.

```dax
Repeat Participants =
COALESCE(
    COUNTROWS(
        FILTER(
            VALUES(factAttendance[Email]),
            [Sessions Attended] >= 2
        )
    ),
    0
)
```

## Repeat Participant Rate %

**Plain-English meaning: Share of selected people attending at least twice.** Divide Repeat Participants by Unique Attendees. A person with one selected visit is not a repeat participant in this measure, even if they attended earlier meetings outside the selection.

```dax
Repeat Participant Rate % =
DIVIDE([Repeat Participants], [Unique Attendees])
```

## Repeat Participant (Selected Period)

**Plain-English meaning: Per-person repeat label.** For one person, return Yes for at least two selected meetings and No for exactly one. Leave the result blank for no selected attendance or a multi-person total. Use it in a person table, not as a programme-wide card.

```dax
Repeat Participant (Selected Period) =
VAR AttendedSessions = [Sessions Attended]
RETURN
IF(
    HASONEVALUE(dimPerson[Email]) && AttendedSessions > 0,
    IF(AttendedSessions >= 2, "Yes", "No")
)
```

## Additional Visits in Selection

**Plain-English meaning: Visits beyond one per selected person.** Subtract Unique Attendees from Total Attendance Records. If one person attends three selected meetings, that person contributes two additional visits. This preserves the original Repeat Attendances arithmetic under a clearer name.

```dax
Additional Visits in Selection =
// Subtract one record per visible distinct email from the row count.
[Total Attendance Records] - [Unique Attendees]
```

## Additional Visit Share in Selection

**Plain-English meaning: Share of visits beyond one per selected person.** Divide additional visits by all selected visits. It is different from both a people-based repeat rate and historically returning visits.

```dax
Additional Visit Share in Selection =
// Calculate the share of records beyond one per distinct email.
DIVIDE(
    [Additional Visits in Selection],
    [Total Attendance Records]
)
```

## People in Attendance Band

**Plain-English meaning: People grouped by selected meeting count.** Count selected people whose number of selected meetings matches the chosen band or bands. Count a person once at the total. A six-visit person moves to band five if only five of their meetings are selected. The disconnected band table supplies the labels; it does not filter attendance through a relationship.

```dax
People in Attendance Band =
VAR SelectedBands =
    VALUES('Attendance Bands'[Sessions Attended])
RETURN
COALESCE(
    COUNTROWS(
        FILTER(
            ADDCOLUMNS(
                VALUES(factAttendance[Email]),
                "@AttendanceCount",
                CALCULATE(
                    DISTINCTCOUNT(factAttendance[SessionID])
                )
            ),
            [@AttendanceCount] IN SelectedBands
        )
    ),
    0
)
```

## Check before relying on the results

Use the fixture in [Attendance DAX acceptance](../review/attendance_dax_validation.md). Its main case expects three meetings, five visits, three different people, three participant-hours and 70% primary average coverage. The companion time-weighted percentage is 66.666667%; the two values answer different questions and need not match.

Check single and multiple meetings, a non-contiguous selection, one person with no selected attendance, totals and a seven-meeting history. Record the actual Power BI outputs separately from the independent arithmetic expectations. Run the fixture in the intended Power BI model; generated arithmetic does not execute DAX.

The optional Session Explorer display and coverage-category expressions remain in [the draft report-page example](../dashboard_report_pages/attendance_session_explorer.md). They are not required to reproduce these 20 core measures.
