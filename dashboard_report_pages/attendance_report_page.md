# Example attendance overview

[Attendance guide](../attendance_dashboard_guide.md) · [Measure catalogue](../dashboard_measures/attendance_rebuild_measures.md)

Build the model and check its results before choosing a layout. This is an optional arrangement, not a required report design.

| Display | Suggested fields or measures |
| --- | --- |
| Headline counts | Total Sessions, Total Attendance Records, Unique Attendees |
| Recorded time | Average Attendance Coverage %, Total Attendance Hours |
| Return behaviour | Repeat Participant Rate % with its people-based label |
| Visits by meeting | dimSession Session Number and Total Attendance Records |
| First and returning visits | New Attendees and Returning Attendance Events by meeting |
| Coverage by meeting | Average Attendance Coverage % by meeting |
| Repeat distribution | Attendance Bands Sessions Attended and People in Attendance Band |

Use dimSession fields for meeting/date selections and dimPerson fields for people. Keep counts and percentage bases visible in tooltips. A distinct-person total is recalculated, rather than added across meeting bars.

Confirm each visual's fields, filters and interactions. Different chart types, fonts and colours are acceptable when they preserve the defined quantities and selections. Use [the detail example](attendance_session_explorer.md) when visit-level inspection is useful.
