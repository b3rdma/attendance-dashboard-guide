# Teams attendance source format

[Attendance build](attendance_rebuild.md) · [Queries](../dashboard_queries/attendance_queries.md)

The template reads the original section-based Teams attendance export. It does not read an Excel master register or a cleaned worksheet. Check a representative export before adopting the parser for a new source.

## File selection and parser settings

Keep one uniquely named .csv export per meeting in the selected SharePoint folder. The source query tests the lower-case extension and whether Folder Path contains attendanceFolder. Check matching subfolders as well as the main folder.

The query code uses a tab delimiter, an eighteen-column limit and Encoding = 65001. These are explicit parser settings, not a promise that every future Teams export has the same format. If the file encoding or layout differs, inspect the original file and review those settings before using its results.

## Sections used

| Exact marker | Use |
| --- | --- |
| 1. Summary | Start of the meeting summary |
| 2. Participants | End of the summary and start of participant records |
| 3. In-Meeting Activities | End of the participant records; activity detail is not loaded |

Section 4 is not needed by the current measures. The name filter removes an empty separator row after participant expansion under the complete-name assumption.

## Summary fields

The session query expands Meeting title, Attended participants, Start time, End time, Meeting duration and Average attendance time. It parses the two dates using en-US culture and creates separate second-based duration columns.

The source date convention is month/day/year. British display formatting does not change that parsing rule. The resulting datetime columns carry no timezone; define timezone handling before adding a cross-timezone reporting requirement.

## Participant fields

The query uses Name, First Join, Last Leave, In-Meeting Duration, Email, Role and the eight engagement summaries named in the code. The full output is listed in [the data dictionary](attendance_data_dictionary.md).

Email must be complete and unique to a person. The template assumes the participant identifier duplicates Email, so it does not retain a second identity column. Anonymous or incomplete identities need a different agreed rule.

Use In-Meeting Duration rather than Last Leave minus First Join: the latter can include disconnected time. Role describes a Teams permission role, rather than a reliable speaker identity. Retain all roles unless the reporting definition explicitly excludes some.

## Durations and layout changes

The parser accepts non-negative whole-number h, m and s components in order, with omitted units contributing zero. It retains the raw text and raises an error for malformed complete values. See [duration rules](attendance_duration_parsing.md).

An added, renamed or removed export column can require a query change. Preserve a representative example, compare it with the required headings and validate the revised extraction before updating the reporting model.
