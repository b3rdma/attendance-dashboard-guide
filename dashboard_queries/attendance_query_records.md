# Prepare attendance records

[Query index](attendance_queries.md) · [Source format](../guide/attendance_source_contract.md) · [Column definitions](../guide/attendance_data_dictionary.md)

Create this query as **factAttendance** with Enable load on. One row represents one person attending one meeting. The model expects the participant-summary section to combine that person's participation, including leaving and rejoining.

## Key steps

| Stage | Result |
| --- | --- |
| Read each file | Locate Section 2 between the Participants and In-Meeting Activities markers |
| Promote headings | Use the participant column names from the supported export |
| Expand participant tables | Combine the records from all selected files |
| Filter empty names | Remove the section-separator rows under the complete-name assumption |
| Match Source File | Attach SessionID and meeting details from dimSession |
| Parse dates and duration | Create date/time fields and numeric attendance seconds |

The filename join attaches meeting details; expanding participant tables is the step that combines records. Keep one uniquely named export per meeting. Email is the person key. The query omits the duplicate participant identifier under the assumption that it matches Email.

Use Teams' In-Meeting Duration. Subtracting first join from final leave can include a gap while someone was disconnected. Keep the original duration text beside the parsed seconds for checking.

The code below returns nineteen columns. After creating it, apply [the engagement type addition](../guide/attendance_engagement_typing.md) to make the eight action fields whole numbers. That addition does not change row membership or attendance durations.

## Advanced Editor code

```powerquery
let

    // Read the selected SharePoint file metadata and content binaries.
    Source = src_Files,

    // Extract a participant table separately from each selected file.
    AddParticipants =
        Table.AddColumn(
            Source,
            "Participants",
            each
                let

                    // Use the configured tab delimiter, 18-column width and encoding option.
                    FileData =
                        Csv.Document(
                            [Content],
                            [
                                Delimiter = "#(tab)",
                                Columns = 18,
                                Encoding = 65001
                            ]
                        ),

                    Indexed =
                        Table.AddIndexColumn(
                            FileData,
                            "RowID",
                            0,
                            1,
                            Int64.Type
                        ),

                    // Find the exact participants marker; absence is not handled here.
                    StartRow =
                        Indexed{
                            List.PositionOf(
                                Indexed[Column1],
                                "2. Participants"
                            )
                        }[RowID],

                    // Use the activity section only as the end boundary.
                    EndRow =
                        Indexed{
                            List.PositionOf(
                                Indexed[Column1],
                                "3. In-Meeting Activities"
                            )
                        }[RowID],

                    // Retain the participant header row and its data rows.
                    ParticipantRows =
                        Table.SelectRows(
                            Indexed,
                            each
                                [RowID] > StartRow and
                                [RowID] < EndRow
                        ),

                    RemoveRowID =
                        Table.RemoveColumns(
                            ParticipantRows,
                            {"RowID"}
                        ),

                    // Promote the first retained row to column names.
                    PromotedHeaders =
                        Table.PromoteHeaders(
                            RemoveRowID,
                            [PromoteAllScalars=true]
                        )

                in

                    PromotedHeaders
        ),

    // Expand the explicitly named participant and engagement fields.
    Expanded =
        Table.ExpandTableColumn(
            AddParticipants,
            "Participants",
            {
                "Name",
                "First Join",
                "Last Leave",
                "In-Meeting Duration",
                "Email",
                "Participant ID (UPN)",
                "Role",
                "Engagement: Reaction-Applause",
                "Engagement: Reaction-Laugh",
                "Engagement: Reaction-Like",
                "Engagement: Reaction-Love",
                "Engagement: Reaction-Surprised",
                "Engagement: Camera On",
                "Engagement: Raise Hands",
                "Engagement: Unmute"
            },
            {
                "Participant Name",
                "Joined",
                "Left",
                "Attendance Duration",
                "Email",
                "Participant ID",
                "Role",
                "Applause",
                "Laugh",
                "Like",
                "Love",
                "Surprised",
                "Camera On",
                "Raise Hands",
                "Unmute"
            }
        ),

    // Keep only rows with a non-blank participant name.
    FilterNullNames =
        Table.SelectRows(
            Expanded,
            each [Participant Name] <> null and
            Text.Trim([Participant Name]) <> ""
        ),

    // Parse join and leave timestamps using the export culture setting.
    ConvertDates =
        Table.TransformColumns(
            FilterNullNames,
            {
                {
                    "Joined",
                    each DateTime.FromText(_, [Culture="en-US"]),
                    type datetime
                },
                {
                    "Left",
                    each DateTime.FromText(_, [Culture="en-US"]),
                    type datetime
                }
            }
        ),

    Rename =
        Table.RenameColumns(
        ConvertDates,
        {
            {"Name","Source File"}
        }
    ),

    // Join on file basename; uniqueness is an operational assumption.
    MergeSession =
        Table.NestedJoin(
            Rename,
            {"Source File"},
            dimSession,
            {"Source File"},
            "Session",
            JoinKind.LeftOuter
        ),

    // Attach session grouping fields from every matching summary row.
    ExpandSession =
        Table.ExpandTableColumn(
            MergeSession,
            "Session",
            {
                "SessionID",
                "Session Number",
                "Session Date",
                "Session Title"
            }
        ),

    // Drop file metadata and Participant ID from the reporting output.
    Result =
        Table.SelectColumns(
            ExpandSession,
            {
                "SessionID",
                "Session Number",
                "Session Date",
                "Session Title",
                "Participant Name",
                "Joined",
                "Left",
                "Attendance Duration",
                "Email",
                "Role",
                "Applause",
                "Laugh",
                "Like",
                "Love",
                "Surprised",
                "Camera On",
                "Raise Hands",
                "Unmute"
            }
        ),

    // Read optional h, m and s components in order; absent units contribute zero.
    AddAttendanceSeconds =
        Table.AddColumn(
            Result,
            "Attendance Duration Seconds",
            each
                let
                    txt = Text.Trim([Attendance Duration]),

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
                                        "InvalidAttendanceDuration",
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
                            "InvalidAttendanceDuration",
                            "Attendance duration must contain at least one h, m or s component.",
                            [Duration = txt]
                        )
                    else if seconds[Remaining] <> "" then
                        error Error.Record(
                            "InvalidAttendanceDuration",
                            "Use h, m and s in order, with a unit after every number.",
                            [Duration = txt, Remaining = seconds[Remaining]]
                        )
                    else
                        hours[Value] * 3600 + minutes[Value] * 60 + seconds[Value],
            Int64.Type
        )

in

    AddAttendanceSeconds
```
