# Meeting attendance guide

[Home](README.md) · [Understand the figures](guide/manager_briefing.md)

The attendance model reads Teams exports from SharePoint. It creates a meeting table, an attendance table and a person table, then calculates figures for the selected meetings and people.

## Understand the data

- Read [purpose and scope](guide/attendance_foundations.md) for the main questions the model answers.
- Check [the source assumptions](guide/attendance_assumptions.md) before using the design.
- Use [the metric explanations](guide/attendance_reading_report.md) for counts, time, returning visits and repeat attendance.

One person attending three meetings contributes three visits and one unique attendee across those meetings. A visit is a person attending a meeting, rather than each separate join or leave event.

The design assumes complete, stable email identities, one intended export per meeting and the documented Teams export layout. If those conditions do not hold, review the source and preparation rules before relying on the results.

## Build or maintain the model

| Task | Reference |
| --- | --- |
| Build from the start | [Ordered data-model build](guide/attendance_rebuild.md) |
| Configure the source | [Setup and parameters](guide/attendance_setup.md) |
| Create the calculations | [Attendance measures](dashboard_measures/attendance_rebuild_measures.md) |
| Add an export and update the figures | [Refresh and check](guide/attendance_refresh.md) |
| Change or recover the model | [Maintenance](guide/attendance_maintenance.md) and [troubleshooting](guide/attendance_troubleshooting.md) |
| Check the calculated results | [Small test examples](review/attendance_dax_validation.md) |
| Find exact fields and dependencies | [Technical reference](guide/attendance_technical_reference.md) |

Follow the build in order: source, preparation, relationships, measures and result checks. Keep object names and relationship directions consistent with the formulas.

## Read the main measures correctly

**Average attendance coverage** calculates the fraction of the meeting attended for each visit, then averages those fractions.

**New attendance** means a person's first appearance in the retained files. Adding an earlier meeting can change this classification.

**Returning visits** count later visits in that history. **Repeat participants** count people attending at least two of the currently selected meetings. These answer different questions.

No invitation list or learning assessment is included. Attendance records do not establish attention, learning or the proportion of invitees who attended.

## Choose a report layout

Check the data and calculations before designing pages. [Session Explorer](dashboard_report_pages/attendance_session_explorer.md) is an optional layout example. Change the appearance while keeping measure meanings, filters and percentage bases consistent.
