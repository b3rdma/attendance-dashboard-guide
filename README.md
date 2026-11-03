# Attendance and AI survey dashboards

This guide explains two Power BI examples:

- **Meeting attendance:** how many people attend, how much of a meeting they attend and whether they return.
- **Anonymous AI survey:** what responses say about confidence, experience and support preferences.

## Understand the figures

Start with [what the dashboards show](guide/manager_briefing.md). Then read the [metric handbook](guide/dashboard_metrics.md) for definitions and worked examples.

Check the assumptions before drawing conclusions: [attendance](guide/attendance_assumptions.md) and [survey](survey/survey_source_contract.md). Use the [glossary](guide/dashboard_glossary.md) when a technical term is unfamiliar.

## Build or maintain a dashboard

| Task | Guide |
| --- | --- |
| Build the attendance model | [Attendance build](guide/attendance_rebuild.md) |
| Build the survey model | [Survey build](survey_dashboard_guide.md) |
| Add a meeting and refresh the report | [Attendance update](guide/attendance_refresh.md) |
| Investigate an attendance problem | [Troubleshooting](guide/attendance_troubleshooting.md) |
| Find the queries, relationships and formulas | [Attendance reference](guide/attendance_technical_reference.md) or [survey guide](survey_dashboard_guide.md) |

Keep the attendance and anonymous survey models separate. Survey response IDs do not identify meeting participants.

The guide provides instructions and formulas. Source data and an editable Power BI report are not included. Check the calculations with your own source files before using the results. Report layouts are examples; the data and calculation definitions determine the figures.

[Maintain the guide](CONTRIBUTING.md) · [MIT licence](LICENSE)
