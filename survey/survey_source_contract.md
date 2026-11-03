# Survey source assumptions

[Survey guide](../survey_dashboard_guide.md) · [Power Query](survey_queries.md) · [Checks](survey_validation.md)

Check these assumptions before loading a source or interpreting a result. The public example uses generic question headings and invented test records. Map its source headings and answer options to the intended export before building the model.

## Required inputs

| Item | Requirement |
| --- | --- |
| Source location | basePath supplies the SharePoint site. capabilityFolder selects the folder containing the survey workbook. |
| Number of workbooks | Select one workbook for this snapshot. Correct the file selection if zero or several workbooks match. |
| Workbook table | Read the Excel Table named tblRawData. Worksheet order and pivot outputs are not inputs. |
| Survey period | One collection of anonymous responses. Use a wave key before combining another survey. |
| Response ID | A positive whole-number ID, unique within this survey. It need not be consecutive. |
| Identity | Do not use anonymous Email, empty names or response IDs to identify people or join attendance records. |
| Agreement answers | Six statements use Strongly disagree, Disagree, Neutral, Agree and Strongly agree. |
| Tool ratings | Five tool fields contain codes 1–5. Keep neutral labels until the question and scale meanings are defined. |
| Multiple choices | Domain and Support options use semicolon-separated lists. Ignore a trailing separator and empty tokens. |

The file filter matches folder text within the full path. Inspect the file list after changing the site or folder. A count of one does not establish that the correct workbook was chosen; check its name, table and required headings.

A unique response ID identifies a record, not necessarily a different person. It is not a key for joining another anonymous survey. The [multi-wave plan](survey_waves.md) explains the required combined keys and question versions. Do not remove the one-file check and append raw rows without those changes.

## Agreement scale

| Source answer | Score | Favourable? |
| --- | ---: | --- |
| Strongly disagree | 1 | No |
| Disagree | 2 | No |
| Neutral | 3 | No |
| Agree | 4 | Yes |
| Strongly agree | 5 | Yes |

The query removes surrounding spaces and ignores capitalisation. These codes order the answers; they do not establish equal intervals or an overall maturity score.

| Answer state | Meaning | Calculation treatment |
| --- | --- | --- |
| Valid | Matches a defined answer | Include it in the relevant valid-answer calculation |
| Missing | No answer supplied | Preserve the opportunity to answer for completeness checks |
| Unmapped | Nonblank wording not in the map | Retain the wording and leave its score blank |
| Invalid tool rating | Value outside the allowed whole-number codes | Retain it for review and exclude it from valid ratings |

Missing and Unmapped are not Neutral or zero. Do not apply agreement labels to the separate tool scale.

## Example profile options

These are the options used by the example queries. Match the options and display order to the actual questionnaire. Order numbers control presentation only.

| Field | Ordered example options |
| --- | --- |
| ClientCapability | Awareness Only/limited hands-on experience; Comfortable user of AI and digital tools; Experienced practitioner applying AI in delivery; Specialist/subject matter expert |
| ClientAIExposure | None; Limited Exposure; Some involvement; Significant Exposure |
| FormalLearning | None; Introductory; Intermediate; Advanced |
| CommissionInterest | No; Depends on the role; Yes |
| TrainingInterest | No; Yes |

Keep Depends on the role separate from Yes. Commission-interest percentages use recognised Yes, No and Depends on the role answers. Training-interest percentages use recognised Yes/No answers. Missing or unexpected wording is excluded from these denominators, rather than counted as No.

Unexpected profile labels remain visible at display order 99. Review them before changing a fixed-answer measure. Grade, CostCentre, BusinessWorkType, ClientRoleLevel, CurrentAICommission, NonDigitalProductivityUse and PriorAIProject retain the mapped source wording; inspect their distinct values before defining additional measures.

## Example field groups

The public test schema contains 44 fields. The analytical model uses 26 named inputs. Other source fields may remain in unloaded raw staging without being required by the calculations.

| Group | Example columns | Initial handling |
| --- | ---: | --- |
| ID and single-answer profile | 13 | Response profile |
| Multi-select questions | 2 | Separate Domain and Support bridges |
| Agreement statements | 6 | Six answer opportunities per response |
| Tool ratings | 5 | Five rating opportunities per response |
| Timestamps and unused identity fields | 5 | Raw staging only |
| Terminology questions | 6 | Raw staging until question and scale meanings are defined |
| Narrative answers | 7 | Raw staging until a repeatable analysis is agreed |

The two organisation-neutral project headings in [the query mapping](survey_queries.md#stgsurveyprepared) are example source labels. Match them privately to the actual export while retaining the output fields CurrentAICommission and PriorAIProject used elsewhere in the model.

Narrative examples include project descriptions, other tools, technical skills, relevant training and qualifications. The analytical build does not reference their full headings. A truncated narrative heading therefore does not affect this build.

The loaded factSurvey has 13 source fields and five display-order fields. The answer tables and choice bridges are separate outputs. Keep raw staging unloaded instead of loading a second full-width response table.

## Interpretation limits

| Area | Rule |
| --- | --- |
| Tool rating endpoints | Use neutral codes until all labels and meanings are defined. Code 5 alone does not establish expert capability. |
| Terminology answers | Obtain the question wording and scale before adding metrics. |
| Maturity or grouped confidence | Require a stated formula and thresholds. Do not invent groups from pivot titles. |
| Employee response rate | Requires a suitable eligible-population denominator. This model counts submissions. |
| Individual learning impact | Anonymous submissions cannot be matched to attendance or to the same person in another survey. |
| Narrative answers | Use an agreed coding method; do not treat arbitrary text as scored answers. |

Show counts with percentages. Small selected groups can give unstable or identifiable results. Agree an appropriate minimum reporting group before sharing results; the example does not impose a universal threshold.
