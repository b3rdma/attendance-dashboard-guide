# Prepare meeting summaries

[Query index](attendance_queries.md) · [Column definitions](../guide/attendance_data_dictionary.md)

Create this query as **dimSession** with Enable load on. It reads Section 1 of each selected export and creates one meeting row per file. This assumes one uniquely named export per meeting.

## Key steps

| Stage | Result |
| --- | --- |
| Read the file | Use the tab-delimited layout and parser settings in the code |
| Find section markers | Read rows between 1. Summary and 2. Participants |
| Pivot the summary | Turn each named summary field into a column |
| Parse dates | Interpret source month/day text with en-US culture |
| Sort and number | Assign Session Number in ascending start order |
| Create the key | Format the full start datetime as yyyyMMddHHmmss |
| Parse duration | Convert the separate meeting and summary-average fields to seconds |

An earlier file added later enters its correct chronological position. Later Session Numbers can change. SessionID is the separate relationship key; two different dates with the same clock time produce different keys. The model assumes no two retained meetings share the same complete start timestamp.

Source File identifies the export used to attach meeting details to attendance rows. Keep filenames unique within the selected inventory.

## Duration parsing

The local ParseDurationSeconds function reads hours, minutes and seconds in order. Omitted components contribute zero. Malformed complete values raise an error. Each duration output uses its own source field; do not replace the summary average with the meeting duration.

The code renames Attended participants to Attended Participants in the main rename block. It returns twelve columns. See [duration rules](../guide/attendance_duration_parsing.md) for examples and [the dictionary](../guide/attendance_data_dictionary.md) for each output.

## Advanced Editor code

```powerquery
let

    // Read the same selected file set used by the participant query.
    Source = src_Files,

    // Extract a summary table independently from each file binary.
    AddSummary =
        Table.AddColumn(
            Source,
            "Summary",
            each
                let

                    // The .csv extension does not change the configured tab delimiter.
                    FileData =
                        Csv.Document(
                            [Content],
                            [
                                Delimiter = "#(tab)",
                                Columns = 18,
                                Encoding = 65001
                            ]
                        ),

                    // Use row positions to isolate sections before promoting any headers.
                    Indexed =
                        Table.AddIndexColumn(
                            FileData,
                            "RowID",
                            0,
                            1,
                            Int64.Type
                        ),

                    // Locate the first exact summary marker; no missing-marker fallback is present.
                    StartRow =
                        Indexed{
                            List.PositionOf(
                                Indexed[Column1],
                                "1. Summary"
                            )
                        }[RowID],

                    // Stop before the participants section.
                    EndRow =
                        Indexed{
                            List.PositionOf(
                                Indexed[Column1],
                                "2. Participants"
                            )
                        }[RowID],

                    // Exclude the section markers themselves.
                    SummaryRows =
                        Table.SelectRows(
                            Indexed,
                            each
                                [RowID] > StartRow and
                                [RowID] < EndRow
                        ),

                    KeepColumns =
                        Table.SelectColumns(
                            SummaryRows,
                            {"Column1","Column2"}
                        ),

                    RenameColumns =
                        Table.RenameColumns(
                            KeepColumns,
                            {
                                {"Column1","Attribute"},
                                {"Column2","Value"}
                            }
                        ),

                    // Turn summary label/value rows into columns.
                    Pivoted =
                        Table.Pivot(
                            RenameColumns,
                            List.Distinct(
                                RenameColumns[Attribute]
                            ),
                            "Attribute",
                            "Value"
                        )

                in

                    Pivoted
        ),

    // Require the six named summary fields.
    Expanded =
        Table.ExpandTableColumn(
            AddSummary,
            "Summary",
            {
                "Meeting title",
                "Attended participants",
                "Start time",
                "End time",
                "Meeting duration",
                "Average attendance time"
            },
            {
                "Meeting title",
                "Attended participants",
                "Start time",
                "End time",
                "Meeting duration",
                "Average attendance time"
            }
        ),

    ChangeTypes =
        Table.TransformColumnTypes(
            Expanded,
            {
                {"Attended participants", Int64.Type}
            }
        ),

    // Parse export dates with the existing US culture setting.
    ConvertDates =
        Table.TransformColumns(
            ChangeTypes,
            {
                {
                    "Start time",
                    each DateTime.FromText(_, [Culture="en-US"]),
                    type datetime
                },
                {
                    "End time",
                    each DateTime.FromText(_, [Culture="en-US"]),
                    type datetime
                }
            }
        ),

    // Chronological order determines the refresh-time session index.
    Sorted =
        Table.Sort(
            ConvertDates,
            {
                {"Start time", Order.Ascending}
            }
        ),

    // This index can change when earlier exports are added.
    AddSessionNumber =
        Table.AddIndexColumn(
            Sorted,
            "Session Number",
            1,
            1,
            Int64.Type
        ),

    // Build the current key from session start time only.
    AddSessionID =
        Table.AddColumn(
            AddSessionNumber,
            "SessionID",
            each DateTime.ToText(
                [Start time],
                "yyyyMMddHHmmss"
            ),
            type text
        ),
    // Derive a calendar date from the parsed session start.
    AddMeetingDate =
        Table.AddColumn(
            AddSessionID,
            "Session Date",
            each Date.From([Start time]),
            type date
        ),

    Rename =
        Table.RenameColumns(
        AddMeetingDate,
        {
            {"Name","Source File"},
            {"Meeting title","Session Title"},
            {"Start time","Session Start"},
            {"End time","Session End"},
            {"Meeting duration","Session Duration"},
            {"Attended participants","Attended Participants"}
        }
    ),

    // Retain only the documented reporting fields.
    Result =
        Table.SelectColumns(
            Rename,
            {
                "Session Number",
                "Session Date",
                "SessionID",
                "Source File",
                "Session Title",
                "Attended Participants",
                "Session Start",
                "Session End",
                "Session Duration",
                "Average attendance time"
            }
        ),

    // Reuse the participant parser's component logic for both summary fields.
    ParseDurationSeconds = (durationText as nullable text) as number =>
        let
            txt = Text.Trim(durationText),

            // Consume one labelled whole-number component and retain the rest.
            ReadUnit = (remaining as text, unit as text) as record =>
                if Text.Contains(remaining, unit) then
                    let
                        valueText = Text.Trim(Text.BeforeDelimiter(remaining, unit)),
                        value =
                            if valueText <> "" and
                                Text.Select(valueText, {"0".."9"}) = valueText
                            then Number.FromText(valueText, "en-US")
                            else error Error.Record(
                                "InvalidDuration",
                                "Expected a non-negative whole number before " & unit & ".",
                                [Duration = txt, Unit = unit]
                            )
                    in
                        [
                            Value = value,
                            Remaining = Text.Trim(Text.AfterDelimiter(remaining, unit))
                        ]
                else
                    [Value = 0, Remaining = remaining],

            // Each unit reads only the text left by the previous unit.
            hours = ReadUnit(txt, "h"),
            minutes = ReadUnit(hours[Remaining], "m"),
            seconds = ReadUnit(minutes[Remaining], "s")
        in
            // Keep malformed source values visible instead of replacing them with null.
            if txt = null or txt = "" then
                error Error.Record(
                    "InvalidDuration",
                    "Duration must contain at least one h, m or s component.",
                    [Duration = txt]
                )
            else if seconds[Remaining] <> "" then
                error Error.Record(
                    "InvalidDuration",
                    "Use h, m and s in order, with a unit after every number.",
                    [Duration = txt, Remaining = seconds[Remaining]]
                )
            else
                hours[Value] * 3600 + minutes[Value] * 60 + seconds[Value],

    // Convert the source-reported meeting duration to total whole seconds.
    AddSessionDurationSeconds =
        Table.AddColumn(
            Result,
            "Session Duration Seconds",
            each ParseDurationSeconds([Session Duration]),
            Int64.Type
        ),

    // Apply the same local parser to the source-reported average attendance time.
    AddAverageAttendanceSeconds =
        Table.AddColumn(
            AddSessionDurationSeconds,
            "Average Attendance Seconds",
            each ParseDurationSeconds([Average attendance time]),
            Int64.Type
        )
in

    AddAverageAttendanceSeconds
```
