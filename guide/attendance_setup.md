# Set up the attendance source

[Attendance guide](../attendance_dashboard_guide.md) · [Build from the start](attendance_rebuild.md) · [Routine update](attendance_refresh.md)

## Choose the starting point

For a new report, follow [the ordered build](attendance_rebuild.md). For an existing report, save a recovery copy and record its current parameters, file list and last successful refresh before changing the connection.

Use a development copy to test a new location. A saved report can still read changed SharePoint files, so the source inventory is part of the recovery record.

## Prepare the source folder

Keep the original Teams attendance exports in the intended SharePoint folder. Retain one uniquely named export per meeting and preserve its contents. Check [the assumptions](attendance_assumptions.md) and [source layout](attendance_source_contract.md).

Keep duplicate downloads, replaced copies and archives outside every path matched by the folder parameter. A child folder called Archive can remain included because the query checks whether the full path contains the configured text.

## Set the parameters

Open Power Query Editor and inspect Manage Parameters:

| Parameter | Set or check |
| --- | --- |
| basePath | SharePoint site URL, rather than an individual file, page or sharing link |
| attendanceFolder | Text contained in the full folder path of the intended exports |

Use [the parameter definitions](../dashboard_parameters/attendance_parameters.md) and preserve their exact object names. Both values must contain suitable text. Their optional/Any metadata does not validate the site or folder.

Changing basePath also affects the survey source if both models share it. Use an account with access to the intended source. Resolve account or permission problems before changing query logic.

## Inspect the selected files

In src_Files, check every Name, Extension and complete Folder Path. Confirm the expected history is present and no unrelated files or duplicates are selected. The template uses the documented .csv extension and folder-text rules.

Run a full Desktop refresh after changing parameters. Compare meeting titles, dates, source filenames, participant records and representative durations with the intended source. Test one meeting, several meetings and one person using [the measures](../dashboard_measures/attendance_rebuild_measures.md).

Record the changed values, source scope, checks and recovery point. If results are unsuitable, restore the preceding values, refresh and repeat the checks. A successful connection alone does not prove the correct files were selected.

## If Power BI Service Is Used

Desktop and Service have separate connection and refresh settings. For a published report:

1. Identify the workspace, responsible maintainer and intended readers.
2. Publish the checked model through the intended reporting process.
3. Check deployed parameters, source credentials and any required connections.
4. Run an on-demand Service refresh and compare its data with Desktop.
5. Set a schedule only after that refresh succeeds. Record its time zone and failure contact.
6. Check access using the intended reader permissions.

Keep Desktop and Service validation records separate. Refresh updates the model's data; it does not distribute an independently saved Desktop file to every reader.
