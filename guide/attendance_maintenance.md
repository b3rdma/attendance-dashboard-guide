# Maintain and recover the attendance model

[Attendance guide](../attendance_dashboard_guide.md) · [Data flow](attendance_data_flow.md) · [Result checks](../review/attendance_dax_validation.md)

## Separate updates from development

A routine update adds or replaces exports within the existing source rules. A change to query logic, relationships, measures or report filters changes how results are produced and needs a development copy and a separate check record.

Keep the last working report and source-file inventory. Use representative history in the development copy and check an unchanged meeting after each change as well as the affected case.

## Trace the result before editing

Follow the path from source field to prepared column, relationship, measure and report value. Query dependencies describe preparation during refresh. Relationships control how report selections affect tables.

| Change | Check downstream |
| --- | --- |
| Site or folder parameter | File selection, every prepared table and retained history |
| Section markers or source headings | Meeting/participant extraction and all dependent fields |
| Timestamp or duration text | Date parsing, session keys and duration calculations |
| Filename or session key | Meeting uniqueness, filename match, relationships and meeting counts |
| Person identity | Person lookup, unique counts and first/returning classifications |
| Measure | Dependent measures, totals, cards, tables and charts |
| Attendance Bands | Available labels, selected-period counts and numeric sorting |
| Report fields or interactions | Included records, denominator scope and saved selections |

Use [data flow](attendance_data_flow.md), [the data dictionary](attendance_data_dictionary.md), [relationships](../dashboard_relationships/attendance_relationships.md) and [the measure catalogue](../dashboard_measures/attendance_rebuild_measures.md). Inspect the actual field bindings when a report value differs from the expected result.

## Move a source

1. Record existing parameter values, source-file inventory and report version.
2. Keep a recovery copy of the report and preserve the source files.
3. Change the parameters in the development copy using [the setup procedure](attendance_setup.md).
4. Check all selected filenames and full paths for missing history, duplicates or unintended matches.
5. Refresh and compare tables and representative measures with the previous configuration.
6. Check connections and refresh separately in every affected environment.
7. Update the reporting copy only after the results reconcile.

A parameter change can alter reporting scope without changing a formula. Restore the previous values and source scope if the move gives unsuitable results.

## Handle an export-format change

Keep examples of the previous and new layouts in the appropriate source location. Compare delimiter, encoding, section markers, headings, date text and duration text against [the source contract](attendance_source_contract.md).

Identify which step depends on the changed field. Test its correction with both old and new exports before updating the reporting copy. Reassess an actual layout change rather than assuming the .csv extension guarantees compatibility.

### Confirm the long-meeting duration convention

Compare newly observed duration text with [the supported grammar](attendance_duration_parsing.md). The parser accepts whole-number h, m and s components in order; omitted components contribute zero. Keep the raw text for diagnosis.

Check the participant duration and both session-summary duration fields independently. A successful conversion of one does not establish that the others use the correct input. For synthetic tests, include seconds-only, minute-only and hour-bearing values, plus malformed values that should raise errors.

## Keep the intended history

The model reads the currently matching files. Removing earlier exports changes totals, chronological numbering and first-attendance classifications. Decide the retained period before changing the source inventory.

Keep one intended export per meeting. For a replacement, preserve the preceding copy outside matching paths. For older additions, follow [the historical-session checks](attendance_refresh.md#adding-historical-sessions).

A stable Email identifies a person. If the same Email appears with different display names, the current name/Email-pair query can create duplicate lookup keys. Investigate the actual variation and choose one intended display label per Email in a reviewed change.

## Check and release a change

Use temporary Table or Matrix visuals and [the synthetic controls](../review/attendance_dax_validation.md) to check one meeting, several meetings, one person, empty selections and growing bands. Check totals according to their definitions, rather than adding displayed percentages or distinct counts.

Record:

- The report version and environment.
- The source inventory, parameters and retained period.
- Changed objects and the intended behaviour.
- Test selections, expected values and observed values.
- Remaining limits and the recovery point.

A report layout is optional. The figures must retain the definitions in the measure catalogue regardless of styling.

## Recover and hand over

For a failed source addition, preserve the suspect file outside the selected scope and refresh a recovery copy against the preceding inventory. For a failed model change, restore the previous report and recheck its connection and representative results.

A restored report still reads the current SharePoint files. Restore the intended source scope as well as the report when recovering.

Record the responsible maintainer, report/source locations, update routine, access requirements, recovery process and last successful checks. Walk through one complete export-to-report update with the next maintainer. Keep credentials outside the guide.
