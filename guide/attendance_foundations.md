# Attendance purpose and scope

[Attendance guide](../attendance_dashboard_guide.md) · [Assumptions](attendance_assumptions.md) · [Build steps](attendance_rebuild.md)

## Purpose

The model summarises attendance from Teams exports. Keep the original files in SharePoint and refresh Power BI to rebuild the included meeting history. The guide covers preparation, calculations, routine updates and result interpretation.

The exports are the input. A manually maintained register, its formulas and its charts are not required.

## The three main tables

| Table | Role | Meaning of one row |
| --- | --- | --- |
| dimSession | Meeting details and selection | One retained meeting |
| factAttendance | Recorded visits | One person attending one meeting |
| dimPerson | Person details and selection | One stable name/Email pair |

Email identifies a person. SessionID identifies a meeting using its complete start timestamp to the second. Session Number is the meeting's current chronological position. Adding an earlier meeting deliberately changes that order.

Power Query prepares the tables during refresh. Relationships connect meeting and person selections to attendance rows. Measures calculate results for those selections. Each stage must be checked.

## The main figures

| Figure | Meaning |
| --- | --- |
| Attendance visits | Person-meeting records; one person at three meetings contributes three visits |
| Unique attendees | Different Email values in selected attendance; that person contributes one |
| Selected meetings | Meeting lookup rows selected, including meetings without attendance from selected people |
| Average attendance coverage | Mean of each visit's attendance time divided by its own meeting duration |
| New attendance | A person's first appearance in retained history, when it is in the selection |
| Returning attendance | Selected visits after that first appearance |
| Repeat participants | People attending at least two selected meetings |
| Attendance bands | People grouped by the number of selected meetings attended |

Read [the plain-English metric guide](attendance_reading_report.md) and [exact formulas](../dashboard_measures/attendance_rebuild_measures.md) together when checking results.

## Assumptions and limits

The design assumes complete, stable email identities and names, unique filenames, one intended export per meeting and the documented English export layout. [The assumptions](attendance_assumptions.md) explain the effect of each condition. Preparation does not enforce every source-management rule automatically.

Refresh reads the files currently selected. It does not preserve a separate copy of removed history. Deleting or replacing an older export can change counts and first-attendance classifications.

No invitation list, eligible population or learning assessment is included. Attendance establishes recorded participation, rather than attention, understanding, learning or an invitation response rate. A Teams role describes permissions, not who presented. Anonymous survey responses cannot be linked to attendance using their response IDs.

## Operating the model

Use [the build procedure](attendance_rebuild.md) and check the results with the intended source. Record report/source locations, responsible maintainer, retained period, update routine and recovery copy.

Desktop and Power BI Service have separate refresh and connection settings. Follow [setup](attendance_setup.md) and [maintenance](attendance_maintenance.md) when using either environment.
