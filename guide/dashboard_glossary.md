# Dashboard glossary in plain English

[Repository home](../README.md) · [Metric handbook](dashboard_metrics.md)

Look up a term when it appears in the build instructions or metric explanations. The definitions describe how it is used in this guide.

| Term | Meaning in this guide |
| --- | --- |
| Source | The original Teams CSV exports or survey Excel Table. Charts and Excel pivot tables are outputs, rather than the source used here. |
| Parameter | A saved setting, such as the SharePoint site address or folder name. Change the setting rather than searching through every query. |
| Refresh | Read the current source files again and recalculate the prepared data. Refresh replaces the model's view of that source; it does not preserve a deleted export automatically. |
| Power Query | The part of Power BI that reads and prepares data during refresh. Its code language is M. |
| Query | A named set of instructions for reading or preparing data. A query can produce a table, a parameter or a reusable function. |
| Applied step | One named stage inside a query, such as renaming columns or calculating duration seconds. |
| Staging query | A preparation table used by later queries. It usually does not need to appear as a separate report table. |
| Enable load | Whether a query's result becomes a table in the Power BI model. Turning this off for staging does not stop later queries from using it. |
| Model | The prepared tables, their connections and the calculations used by reports. The same model can support different report layouts. |
| Semantic model | The Power BI Service name for the shared data model that a report uses. |
| Row | One record in a table. Always ask what one row represents before counting it. |
| Grain | What one row represents. The attendance detail has one row per person per meeting. A survey answer table has one row per submission per question. |
| Fact table | A table of detailed records to count or summarise, such as attendance visits or survey answers. |
| Dimension or lookup table | A table with one row for each item used to select or describe the detail, such as each meeting or person. |
| Key | The value used to identify an item and connect tables. Email identifies an attendance person; SessionID identifies a meeting. |
| Relationship | A connection between matching keys in two tables. It tells Power BI how a selection affects related records. It does not combine the source files. |
| One-to-many | One lookup row can match several detail rows. One meeting can have many attendance rows. The one-side key must be unique. |
| Single-direction filtering | A lookup selection selects matching detail rows. A detail selection does not automatically travel backwards through that connection. |
| Bridge | A small membership table for a question allowing several choices. Each row says that one survey submission selected one option. |
| Disconnected table | A table intentionally left without a relationship. Attendance Bands supplies the available session-count categories; its measure performs the counting. |
| DAX | The formula language used for model calculations. Paste a measure into New measure, not into Power Query. |
| Measure | A calculation evaluated for the records selected when a report is used. A count, percentage or average is usually a measure. |
| Calculated column | A value stored for each table row when data is processed. The initial survey build needs none in DAX. |
| Calculated table | A table created by a model formula, such as Attendance Bands. Use New table rather than New measure. |
| Filter or selection | A restriction on the included records, from a slicer, chart category, page setting or other control. |
| Filter context | All the selections that apply to a calculation at that moment, including a chart's row or category. |
| Slicer | A visible report control used to choose meetings, grades or other categories. |
| Cohort | The group currently included, for example submissions from a chosen grade that selected a particular business domain. |
| Denominator or base | The quantity a percentage divides by. For agreement, it is valid answers; for completeness, it is all expected answer opportunities. |
| Distinct count | Count each different value once. One person attending three meetings contributes three visits but one distinct attendee. |
| Answer slot | One submission's opportunity to answer one question, retained even if unanswered. Four submissions and six statements create 24 slots. |
| Valid answer | An answer recognised by the documented mapping or numerical range. This means usable for that calculation, not proof that a self-assessment is objectively correct. |
| Missing answer | No answer was supplied. It is not a negative answer or a numerical zero. |
| Unmapped or invalid answer | A recorded value does not match the supported labels or range. Preserve it for investigation rather than silently changing its meaning. |
| Null or BLANK | A missing or undefined value. Power Query uses null; DAX uses BLANK. A percentage with no valid denominator stays blank. |
| Zero | A real count or value of none. Zero seconds attended differs from missing duration data. |
| Metadata | Information describing how data is used or displayed, such as a column type, label or sort order. |
| Sort by column | A Power BI setting that orders labels using another column, such as None, Introductory, Intermediate, Advanced. |
| Snapshot | The source state used by one survey. Replacing that workbook's contents does not create a history of earlier snapshots. |
| Retained history | All meeting exports currently included. A person's first appearance means their first in those files. |
| PBIX / PBIP | Power BI report/project files. This repository contains build instructions and formulas, rather than a complete editable report file. |
| Native execution | A test run in Microsoft's actual M or DAX engine, rather than a result calculated independently in Python or described in a document. |

Technical names such as factAttendance and dimSession are retained because formulas refer to them exactly. Their prefixes describe their purpose; do not rename a Power BI object just to make the guide's filenames look consistent.
