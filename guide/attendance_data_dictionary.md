# Attendance data dictionary

[Build the model](attendance_rebuild.md) · [Relationships](../dashboard_relationships/attendance_relationships.md)

One meeting row describes a session. One attendance row describes one person's visit. The person lookup provides a name for each email key.

## File preparation

src_Files retains SharePoint metadata and Content, the file bytes. Name becomes Source File. Extension and Folder Path select the input population. Keep this query unloaded; its dependent queries still use it.

## dimSession: one meeting per row

| Column | Type | Purpose |
| --- | --- | --- |
| Session Number | Whole number | Chronological position, recalculated at refresh |
| Session Date | Date | Date part of the start timestamp |
| SessionID | Text | Full start timestamp formatted yyyyMMddHHmmss; relationship key |
| Source File | Text | Export filename; query merge key |
| Session Title | Text | Meeting title from the export |
| Attended Participants | Whole number | Teams summary participant count |
| Session Start | Date/time | Start parsed with en-US culture |
| Session End | Date/time | End parsed with en-US culture |
| Session Duration | Text | Original meeting-duration text |
| Average attendance time | Text | Original summary average-duration text |
| Session Duration Seconds | Whole number | Numeric meeting duration used for coverage |
| Average Attendance Seconds | Whole number | Numeric summary-average duration for source checks |

Keep the original duration fields separate from their numeric outputs. Source-reported meeting duration need not equal timestamp subtraction exactly. Define a suitable tolerance when comparing the two.

## factAttendance: one person-meeting visit per row

| Column | Type | Purpose |
| --- | --- | --- |
| SessionID | Text | Meeting relationship key |
| Session Number | Whole number | Copied chronological order |
| Session Date | Date | Copied meeting date |
| Session Title | Text | Copied meeting title |
| Participant Name | Text | Person's display name |
| Joined | Date/time | First join, parsed with en-US culture |
| Left | Date/time | Last leave, parsed with en-US culture |
| Attendance Duration | Text | Original In-Meeting Duration |
| Email | Text | Person relationship key |
| Role | Text | Teams permission role |
| Applause | Whole number after typing addition | Applause action count |
| Laugh | Whole number after typing addition | Laugh action count |
| Like | Whole number after typing addition | Like action count |
| Love | Whole number after typing addition | Love action count |
| Surprised | Whole number after typing addition | Surprised action count |
| Camera On | Whole number after typing addition | Camera activation count |
| Raise Hands | Whole number after typing addition | Hand-raise action count |
| Unmute | Whole number after typing addition | Unmute action count |
| Attendance Duration Seconds | Whole number | Numeric duration of the visit |

Apply [the type addition](attendance_engagement_typing.md) for the action fields. Empty source text becomes zero under that declared rule; null stays unknown. Set remaining text fields explicitly in the model where the extraction has inherited rather than declared their type.

## dimPerson and Attendance Bands

| Object | Columns | Rule |
| --- | --- | --- |
| dimPerson | Participant Name, Email | One intended display name per unique Email |
| Attendance Bands | Sessions Attended | Calculated labels from 1 to the number of loaded meetings |

Keep Attendance Bands disconnected. People in Attendance Band calculates its counts when the report is used; counts are not stored in that table.

## Display and counting rules

Keep keys as text. Sort Session Number and Sessions Attended numerically. Format counts as whole numbers, percentages as percentages and time as numeric minutes or hours. Retain extra decimal places while validating.

Unique people cannot be added across meetings because the same person can occur in several. Session fields copied onto attendance do not create reverse filtering. Follow [the metric definitions](dashboard_metrics.md) and use lookup fields for shared meeting/person selections.
