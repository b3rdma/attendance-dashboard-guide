# Attendance queries

[Build the model](../guide/attendance_rebuild.md) · [Source format](../guide/attendance_source_contract.md)

Power Query reads the exports and prepares three model tables. Create the parameters first, then the four queries in this order. Copy only the code block into Advanced Editor.

| Order | Query | What it does | Enable load |
| --- | --- | --- | --- |
| 1 | [src_Files](attendance_query_files.md) | Select the files from SharePoint | Off |
| 2 | [dimSession](attendance_query_sessions.md) | Create one row per meeting | On |
| 3 | [factAttendance](attendance_query_records.md) | Combine participant summaries and attach their meeting keys | On |
| 4 | [dimPerson](attendance_query_people.md) | Create the person lookup | On |

Apply the [engagement type addition](../guide/attendance_engagement_typing.md) after creating factAttendance. The lookup relationships are a separate model setting; query dependencies do not create them automatically.
