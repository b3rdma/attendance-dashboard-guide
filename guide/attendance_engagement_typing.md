# Prepare engagement counts

[Attendance build](attendance_rebuild.md) · [Attendance query](../dashboard_queries/attendance_query_records.md)

Apply this addition after creating factAttendance. It converts the eight action columns into whole-number counts. The core attendance measures do not depend on these fields, but later engagement calculations need consistent numeric inputs.

## Add the final query block

Add a comma after the existing AddAttendanceSeconds binding. Replace the final in AddAttendanceSeconds return with the bindings and return below. Keep them in the outer query, outside the duration parser's inner let.

```powerquery
    EngagementColumns = {
        "Applause", "Laugh", "Like", "Love", "Surprised",
        "Camera On", "Raise Hands", "Unmute"
    },

    // Normalise exported no-action text and validate whole-number counts.
    ToEngagementCount = (value as any) as nullable number =>
        if value = null then
            null
        else
            let
                txt = Text.Trim(Text.From(value, "en-US"))
            in
                if txt = "" then
                    0
                else if Text.Select(txt, {"0".."9"}) = txt then
                    Int64.From(txt, "en-US")
                else
                    error Error.Record(
                        "InvalidEngagementCount",
                        "Expected a non-negative whole-number count.",
                        [Value = value]
                    ),

    TypedEngagement =
        Table.TransformColumns(
            AddAttendanceSeconds,
            List.Transform(
                EngagementColumns,
                (columnName) =>
                    {columnName, ToEngagementCount, Int64.Type}
            )
        )
in
    TypedEngagement
```

## Conversion rules

| Input | Result |
| --- | --- |
| Empty text or whitespace | 0, under the template's no-action rule |
| null | null, retained as unknown |
| A non-negative whole-number value | That count |
| Fraction, negative value or other text | Error |

The digits-only check prevents integer conversion from rounding a fractional count. Table.TransformColumns applies the same conversion and Int64.Type to every listed field. The final return changes to TypedEngagement; no attendance rows, keys or durations should change.

Check that blank-to-zero matches the source meaning before adopting it. Unknown data should not silently become no action.

## Check the result

Test empty text, null, 0, 3, 1.5, -1 and arbitrary text in a disposable query. Confirm the whole-number type and compare row counts, keys, non-engagement fields and attendance seconds before and after the addition.

Actions and people are different measures. One person can react several times or use several actions. Camera On counts activations, not camera-on duration; Unmute counts actions, not speaking time. Do not infer engagement quality from these counts alone.
