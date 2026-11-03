# Technical checks

[Guide home](../README.md)

Use small invented examples to check counts, percentages and selections before building report pages. These checks do not require private source data.

| Area | Reference |
| --- | --- |
| Attendance metric reasoning | [How the attendance calculations work](attendance_dax_design.md) |
| Attendance model tests | [Synthetic attendance fixtures](attendance_dax_validation.md) |
| Survey extraction and model tests | [Survey validation](../survey/survey_validation.md) |
| Proposed survey-wave extension | [Plan and prototype](../survey/survey_waves.md) |

Generating fixtures or passing Python tests does not execute a Power BI model. Run the stated M/DAX checks in a separate development file and record the results for the intended source and model settings.
