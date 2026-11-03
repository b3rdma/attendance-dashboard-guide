# Convert attendance durations to seconds

[Attendance query](../dashboard_queries/attendance_query_records.md) · [Meeting query](../dashboard_queries/attendance_query_sessions.md)

Durations need a numeric form for averages and percentages. The queries retain the original text and add whole-second values. The participant step and the session's local helper use the same ordered component approach.

## Accepted inputs

The following are invented parser examples, not meeting results.

| Text | Seconds |
| --- | ---: |
| 0s | 0 |
| 45s | 45 |
| 1m | 60 |
| 8m 12s | 492 |
| 1h 2m 3s | 3,723 |
| 1h 3s | 3,603 |
| 75m | 4,500 |

Read h, then m, then s from the remaining text. Missing units contribute zero; at least one labelled component is required. Each present number needs its suffix. Minute-only values remain valid, while 1m 2 is incomplete. Spaces between components are trimmed and compact forms such as 8m12s work.

Reject missing complete input, negative/fractional numbers, repeated or out-of-order units, unsupported suffixes and leftover text. A real 0s differs from missing data. Do not replace malformed input with zero.

## How the code works

1. Trim the raw duration text.
2. Read the number before h when that suffix exists. Validate digits, convert the number and retain the rest.
3. Repeat for m, then s, passing only the remaining text each time.
4. Reject an empty complete value or unconsumed remainder.
5. Calculate hours x 3,600 + minutes x 60 + seconds.

The participant query adds Attendance Duration Seconds. The session query calls ParseDurationSeconds separately for Session Duration and Average attendance time. Keep those two fields independent: a meeting's total duration and its mean attended time answer different questions.

The full expressions and comments are in [factAttendance](../dashboard_queries/attendance_query_records.md#advanced-editor-code) and [dimSession](../dashboard_queries/attendance_query_sessions.md#advanced-editor-code). No separate helper query is required.

## Check a deployment

Test the accepted examples above in a development copy. Also test null, empty text, 45, 1m 2, -1m, 1.5m, 1m 2h and extra trailing text; each should raise a visible error. Compare representative parsed values with the source before using the coverage measures.

Microsoft documents [text operations](https://learn.microsoft.com/en-us/powerquery-m/text-functions) and [Number.FromText](https://learn.microsoft.com/en-us/powerquery-m/number-fromtext). The source's display convention and the parser's accepted grammar should still be checked for the intended export version.
