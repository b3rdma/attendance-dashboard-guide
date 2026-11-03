# Select attendance files

[Query index](attendance_queries.md) · [Parameters](../dashboard_parameters/attendance_parameters.md)

Create this query as **src_Files** with Enable load off. It lists files from the SharePoint site and keeps .csv files whose full folder path contains attendanceFolder.

The folder rule is a text match, not an exact folder boundary. A matching subfolder is included. Inspect Name, Extension and Folder Path before accepting the selection. Keep duplicate or replaced exports outside every matching path.

The output includes Content (the file bytes) and file metadata. dimSession and factAttendance read the same selected inventory. Disabling load keeps this preparation table out of the model without stopping those dependent queries.

## Advanced Editor code

```powerquery
// Enumerate files first, then apply the configured selection rules.
let
    // Use the SharePoint site parameter, not a local folder path.
    Source = SharePoint.Files(
        basePath,
        [ApiVersion = 15]
    ),



    // The folder test matches any path containing the parameter text.
    Filtered =
        Table.SelectRows(
            Source,
            each
                Text.EndsWith([Extension], ".csv")
                and Text.Contains([Folder Path], attendanceFolder)
        )



in
    Filtered
```
