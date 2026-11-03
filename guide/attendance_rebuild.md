# Build the attendance model

[Attendance guide](../attendance_dashboard_guide.md) · [Measures](../dashboard_measures/attendance_rebuild_measures.md) · [Assumptions](attendance_assumptions.md)

Build and check the data model before choosing report layouts. Use a development copy for changes to an existing report, or start with a blank Power BI file.

## 1. Prepare the source

Confirm access to Power BI Desktop and the intended SharePoint site. Keep one original, uniquely named Teams attendance export per meeting. Use [the input assumptions](attendance_assumptions.md) and [source layout](attendance_source_contract.md) to check whether these templates suit the exports.

Record the source location and intended file list. Keep a recovery copy of an existing report before changing it.

## 2. Create the parameters

Open Transform data to enter Power Query Editor. Create the following parameters with their exact names:

| Parameter | Value | Definition |
| --- | --- | --- |
| basePath | The SharePoint site URL, rather than a file, page or sharing link | [Site parameter](../dashboard_parameters/attendance_parameter_site.md) |
| attendanceFolder | Text found in the full folder path of the intended exports | [Folder parameter](../dashboard_parameters/attendance_parameter_folder.md) |

Use the linked expressions and replace the example site value. Parameter metadata does not validate the location. Inspect the selected files in the next step.

## 3. Create the four queries

Create a Blank query, open Advanced Editor and replace the starter code with the complete expression from its reference page. Give it the exact name shown below. Do not paste the Markdown fence lines or add an extra Source binding around the expression.

Create the queries in this order:

| Order | Query | Output | Enable load |
| --- | --- | --- | --- |
| 1 | [src_Files](../dashboard_queries/attendance_query_files.md) | Selected SharePoint file list | Off |
| 2 | [dimSession](../dashboard_queries/attendance_query_sessions.md) | One meeting summary per export | On |
| 3 | [factAttendance](../dashboard_queries/attendance_query_records.md) | One person-meeting attendance record | On |
| 4 | [dimPerson](../dashboard_queries/attendance_query_people.md) | Person names and Email keys | On |

With load off, src_Files remains available to the other queries without creating an extra reporting table. Keep refresh participation enabled.

Inspect src_Files before continuing. Check Name, Extension and the complete Folder Path for every selected file. A matching child folder can still be included. Resolve missing files, duplicates and unintended matches before accepting the selection.

## 4. Prepare the engagement column types

Apply [the engagement typing addition](attendance_engagement_typing.md) after AddAttendanceSeconds in factAttendance. Follow its instructions for the comma, outer query bindings and final return.

Check all eight action columns have the whole-number type. The addition converts empty source text to zero, preserves null and rejects unsupported counts. Attendance measures can be built without engagement analysis, but the field types must be correct before calculating action counts.

## 5. Check tables and types

Select Close & Apply and complete a full refresh. Check the final tables:

| Table | Meaning of one row | Required structure |
| --- | --- | --- |
| dimSession | One retained meeting | 12 columns; unique nonblank SessionID |
| factAttendance | One person attending one meeting | 19 columns; matching SessionID and complete Email |
| dimPerson | One stable name/Email pair | Two columns; unique Email under the name-stability assumption |

Use [the data dictionary](attendance_data_dictionary.md) for every column. Keep SessionID and Email as text, Session Number and duration seconds as whole numbers, Session Date as date, and start/join/leave timestamps as date/time. Keep raw duration text alongside parsed seconds.

These templates read US month/day timestamp text using en-US. Confirm that this matches the source. Changing the date's display format does not change how the original text is read.

## 6. Create the two relationships

Open Model view and create these active, one-to-many relationships. Set Cross filter direction to Single from the lookup table to attendance:

| One side | Many side | Direction |
| --- | --- | --- |
| dimSession[SessionID] | factAttendance[SessionID] | dimSession to factAttendance |
| dimPerson[Email] | factAttendance[Email] | dimPerson to factAttendance |

Check the one and many markers. Remove automatically inferred links outside this design. Use the specified keys rather than names, titles or chronological session numbers. Resolve duplicate one-side keys instead of changing the relationship to many-to-many. Read [the relationship explanation](../dashboard_relationships/attendance_relationships.md).

## 7. Add the calculated table and measures

Follow [the attendance measure catalogue](../dashboard_measures/attendance_rebuild_measures.md). Create Attendance Bands through New table, then create the measures through New measure in the stated order. Keep Attendance Bands disconnected. Its expression supplies the Sessions Attended column name directly.

Keep exact names and dependencies. Format counts as whole numbers, ratios as percentages and minutes/hours as numbers. Sort Session Number and Sessions Attended numerically. Do not turn the numeric measures into text to format them.

## 8. Check results in simple tables

Use temporary Table or Matrix visuals before relying on charts:

1. Show dimSession Session Number, title, date and source filename. Compare one row per intended export.
2. Show dimPerson Email and name with Sessions Attended. Check a known person's selected meetings.
3. Show meeting Session Number with Total Attendance Records, New Attendees and Returning Attendance Events. New plus returning must equal total visits, including totals across meetings.
4. Compare Average Attendance Coverage % with each visit's attendance seconds divided by its matching meeting seconds. Include seconds-only and hour-bearing duration formats.
5. Show Attendance Bands Sessions Attended with People in Attendance Band. Its total must equal Unique Attendees in the same selection. Select fewer meetings and check that people move between bands correctly.
6. Run [the synthetic calculation checks](../review/attendance_dax_validation.md), including more than six meetings, non-consecutive selections, no attendance and a person with no selected visit.
7. Record the inputs, selections, expected values and observed values. Investigate differences before using the report.

Use dimSession fields for meeting/date selections and dimPerson fields for people. A field copied into factAttendance can restrict attendance without restricting the meeting table in the same way.

## 9. Record the handover

Record the report location/version, source scope, responsible maintainer, update routine, completed checks and recovery copy. Record Desktop and Service refresh separately if both are used. Keep credentials outside the documentation.

Use [the refresh procedure](attendance_refresh.md) for new exports and [maintenance and recovery](attendance_maintenance.md) for later changes. [Session Explorer](../dashboard_report_pages/attendance_session_explorer.md) is an optional layout example; reproducing its appearance is not part of checking the calculations.
