# Attendance assumptions

[Understand the figures](manager_briefing.md) · [Build the model](attendance_rebuild.md)

The calculations depend on these input rules. Check that they fit the intended meeting process before using the template.

| Assumption | Why it matters |
| --- | --- |
| Each person has a complete, stable and unique email address | Email connects attendance to the correct person and counts them once across meetings. |
| Each email has one consistent display name | The person query removes duplicate name/email pairs. A name change needs one agreed display label. |
| Keep one original export per meeting | Duplicate copies would count the same attendance again. |
| Filenames are unique within the selected folder scope | The queries match participant records to meeting summaries by filename. |
| One meeting has one complete start timestamp | The full date and time to the second supplies SessionID. |
| Section 2 contains one combined record per person per meeting | Each attendance row represents one visit, including leaving and rejoining. |
| Names are present on genuine participant rows | The name filter can remove the export's empty separator rows. |
| Export sections, labels and columns match the template | The queries use specific English headings and a tab-delimited layout. |
| The selected folder contains only the intended exports | The folder filter is a text match and can include matching subfolders. |

If these rules no longer hold, inspect the actual exception and review the affected query or identity rule. Do not change relationship cardinality just to hide duplicate keys.

## History and numbering

Refresh rebuilds the model from the files currently selected. Removing an export removes its contribution. Adding an earlier meeting inserts it in date order and can change later Session Numbers and first-attendance classifications. That is intended.

Session Number is a display order, not a permanent identity. Use SessionID, date and source filename when recording a comparison.

## What attendance cannot show

Recorded duration does not establish attention, learning or productivity. No invitation list is included, so the model cannot calculate the proportion of invitees who attended. The anonymous survey has a separate population and cannot be joined to participants by its response IDs.

See [the source format](attendance_source_contract.md) for technical requirements and [the metric handbook](dashboard_metrics.md) for definitions.
