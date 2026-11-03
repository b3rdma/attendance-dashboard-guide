# Attendance troubleshooting

[Attendance guide](../attendance_dashboard_guide.md) · [Refresh checks](attendance_refresh.md) · [Build steps](attendance_rebuild.md)

## Record the problem

Record the report version, environment, refresh time, failing query and step, full error text and recently changed files. Keep a recovery copy and diagnose in a development file.

Check stages in order: selected files, meeting summaries, participant rows, meeting-key match, person lookup, relationships and measures. A working preview does not prove all later stages are correct.

## Source and refresh problems

| Symptom | Check | Action |
| --- | --- | --- |
| SharePoint connection fails | Site parameter, account and source access | Restore the correct connection before changing preparation logic |
| No files or a missing meeting | Name, Extension and full Folder Path in src_Files | Compare the selected inventory with the intended history and parameters |
| Unexpected extra meetings | Duplicate downloads, replacements and matching child folders | Keep one intended export per meeting inside the selected scope |
| Section or heading error | Exact markers and headings | Compare with [the source contract](attendance_source_contract.md) and investigate the changed layout |
| Date error or implausible date | Raw timestamp and en-US conversion | Check source parsing separately from display formatting |
| Duration error | Raw duration and the installed calculation | Compare with [the supported grammar](attendance_duration_parsing.md); preserve the original text |
| Person relationship fails | Unique Email in dimPerson and associated names | Resolve duplicate lookup rows; do not hide the issue with many-to-many cardinality |
| Session relationship fails | Unique filenames, one export per meeting and full timestamp keys | Resolve the source or key mismatch before changing the relationship |
| Desktop works but Service fails | Deployed parameters, credentials and refresh history | Check [Service setup](attendance_setup.md#if-power-bi-service-is-used) separately |

One incompatible export can stop refresh. Moving it outside the selected scope can isolate the failure, but does not make the new format supported.

## Figures that look wrong

| Result | Explanation or check |
| --- | --- |
| Session Numbers changed | The retained chronology changed. Use SessionID, date, title and filename to identify meetings. |
| Visits exceed unique attendees | A person can attend several meetings. Visits count each attendance; unique attendees count the person once. |
| Summary count differs from a person-filtered count | The summary describes the whole meeting; a person selection restricts attendance rows. |
| Coverage measures differ | Primary coverage and time-weighted coverage use different weighting. Check [their definitions](../dashboard_measures/attendance_rebuild_measures.md). |
| New plus returning does not equal visits | Check the installed formulas, dependencies and selections. Both measures must use the same attendance population. |
| A returning person is not a repeat participant | Historical returning status and repeating within the current selection are different tests. |
| A high attendance band is missing | Check that the growing table refreshed and its column/measure bindings are correct. |
| Selecting fewer meetings gives the wrong band | Use the person-session counting measure, dimSession selection fields and the documented relationships. |
| Earlier meetings disappeared | Compare source files and parameters with the intended history. Removed files stop contributing. |
| A ratio is blank | Check for no selected attendance, no valid denominator or a person-level helper used at a total. Blank is not automatically zero. |

Use [the measure catalogue](../dashboard_measures/attendance_rebuild_measures.md) and [small expected examples](../review/attendance_dax_validation.md) to separate a calculation problem from display rounding or an unexpected selection.

## Recover and record

Restore the preceding report or parameter values and the intended file inventory. Refresh and recheck representative meetings and metrics. Keep the cause, affected records, recovery action and observed result with the change record.

Follow [maintenance and handover](attendance_maintenance.md) before returning the changed model to reporting use.
