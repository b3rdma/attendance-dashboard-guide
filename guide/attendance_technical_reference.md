# Attendance technical reference

[Attendance guide](../attendance_dashboard_guide.md) · [Build in order](attendance_rebuild.md)

Use this index to trace a source value through preparation, relationships and calculations. Start with the build sequence when creating a new model.

| Area | Reference |
| --- | --- |
| Ordered build | [Attendance model](attendance_rebuild.md) |
| Input conditions | [Assumptions](attendance_assumptions.md) |
| Export sections and headings | [Source contract](attendance_source_contract.md) |
| Table and measure dependencies | [Data flow](attendance_data_flow.md) |
| Columns, types and units | [Data dictionary](attendance_data_dictionary.md) |
| Source configuration | [Parameters](../dashboard_parameters/attendance_parameters.md) |
| Complete preparation code | [Queries](../dashboard_queries/attendance_queries.md) |
| Engagement field types | [Typing addition](attendance_engagement_typing.md) |
| Duration conversion rules | [Duration parsing](attendance_duration_parsing.md) |
| Relationship keys and directions | [Model relationships](../dashboard_relationships/attendance_relationships.md) |
| Measure formulas and growing bands | [Measure catalogue](../dashboard_measures/attendance_rebuild_measures.md) |
| Expected values and selection checks | [Calculation tests](../review/attendance_dax_validation.md) |
| Calculation choices | [Design explanation](../review/attendance_dax_design.md) |
| Updates and recovery | [Maintenance](attendance_maintenance.md) |
| Official function documentation | [Reference sources](attendance_reference_sources.md) |
| Optional page layout | [Session Explorer](../dashboard_report_pages/attendance_session_explorer.md) |
| Possible later analysis | [Insights roadmap](attendance_insights_roadmap.md) |

The build uses the complete fact query plus its separate engagement typing addition. Configure the relationships and model types before adding measures. The guide supplies templates, rather than an editable Power BI report; check all results in the model where they will be used.
