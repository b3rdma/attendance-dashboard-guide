# Refresh and check attendance

[Attendance guide](../attendance_dashboard_guide.md) · [Source layout](attendance_source_contract.md) · [Troubleshooting](attendance_troubleshooting.md)

## Prepare the export

1. Download the Teams attendance report for the intended meeting.
2. Keep its original contents. Do not replace the source with a cleaned worksheet or a manually maintained register.
3. Check the title, date, required section markers and headings against [the source layout](attendance_source_contract.md).
4. Check whether the meeting is already represented. Keep one intended export; retain any replaced copy outside all matching folder paths.
5. Save the .csv file in the selected SharePoint folder and allow the upload to finish.
6. Keep a recovery copy of the report before updating the reporting file.

Refresh rebuilds the tables from all currently matching files. It does not append to a separate permanent history store. An accidental duplicate must be removed from the selected source before refreshing.

## Refresh in Power BI Desktop

1. Open the intended report and check its source parameters.
2. Record the meeting selection and file inventory used for comparison.
3. Run a full refresh and wait for completion.
4. If it fails, record the query, step, error and recently changed files. Follow [troubleshooting](attendance_troubleshooting.md).
5. If it succeeds, complete the checks below before saving the updated reporting copy.

A query preview is not a full refresh. If Service refresh is used, check its own refresh history and results separately; see [Service setup](attendance_setup.md#if-power-bi-service-is-used).

## Check the data

| Check | Required result |
| --- | --- |
| File selection | src_Files lists the intended names and full paths |
| Meeting summaries | Each retained export matches the intended title, date and meeting row |
| Keys | SessionID and filenames identify meetings without unintended duplicates |
| Attendance | New participant records match the export and their intended meeting |
| Time | Representative timestamps and duration seconds match the raw values |
| People | Email identifies people consistently; each person lookup key is unique |
| History | Earlier meetings remain present unless an intentional source change explains their removal |

Summary participant counts, extracted rows and unique Email counts are separate quantities. Compare their scope before assuming they must match. Use a temporary table when report charts do not show enough detail.

## Check the figures

1. Select the new meeting and compare its figures with the underlying records.
2. Inspect representative people for duplicate records, missing identities and unusual duration values.
3. Select several meetings and then the full history.
4. Confirm New Attendees plus Returning Attendance Events equals Total Attendance Records.
5. Confirm People in Attendance Band totals to Unique Attendees for the same selection. Check a smaller meeting selection too.
6. Save the report with its intended opening selections once the checks pass.

Use [the measure definitions](../dashboard_measures/attendance_rebuild_measures.md) and [plain-English explanations](attendance_reading_report.md). Keep the source inventory and report selections with the result checks.

## Adding historical sessions

Adding an older export includes it at the next refresh and recalculates chronological Session Number. Later numbers and first-attendance classifications can change. This is intended behaviour.

Test the addition in a development copy. Record the file inventory before and after, check the added meeting and recheck new/returning totals. Identify a meeting by SessionID, date, title and filename rather than its current number alone.

## Replacing or removing files

Removing a selected file removes its contribution at the next refresh. Moving it to a matching child folder may leave it included.

For a correction, preserve the previous export outside the selected scope, retain only the intended replacement inside it and refresh. Recheck the affected meeting and history, then record the change and recovery point.
