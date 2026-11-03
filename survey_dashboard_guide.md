# Anonymous AI survey guide

[Home](README.md) · [Understand the figures](guide/manager_briefing.md) · [Glossary](guide/dashboard_glossary.md)

The survey model summarises anonymous responses about AI confidence, experience and support preferences. It reads an Excel Table named `tblRawData`; existing Excel charts and pivot tables are not inputs.

## Understand the results

[The metric handbook](guide/dashboard_metrics.md#survey-submissions-and-answers) explains the figures with small examples.

- **Survey responses** counts submitted records matching the selections. It does not verify different people.
- **Favourable agreement** means Agree or Strongly agree as a share of valid answers to the selected statement.
- **Answer coverage** shows how many expected answers can be scored. Missing answers are not Neutral or zero.
- **Domain and Support counts** overlap because a response can select several options. Their bars need not add to the response total.
- **Interest questions** keep Yes separate from a conditional answer such as Depends on the role.

Four submissions with three valid answers and two favourable answers give 66.7% favourable agreement and 75% answer coverage. The two percentages use different bases.

Self-reported confidence is not a tested skill score. Keep tool ratings labelled as numerical codes until their scale meanings are known. Do not invent maturity groups from an unexplained worksheet heading.

## Assumptions

| Requirement | Meaning |
| --- | --- |
| One workbook and one survey snapshot | The current build does not select the latest file or combine survey waves. |
| One unique response ID per row | IDs identify submissions within this snapshot. |
| Defined question headings and answer labels | Preparation maps only the documented inputs. Update the mapping deliberately when a question changes. |
| Semicolon-separated multiple choices | Domain and Support lists can contain several selected answers. |
| No population list | Report submission counts, rather than an employee-wide response rate. |

Read [the source contract](survey/survey_source_contract.md) for the exact fields and scale rules. Keep the survey separate from attendance: anonymous response IDs cannot link the two models.

## Build the model

Use a development Power BI file and follow these steps in order:

1. Identify the SharePoint workbook and its `tblRawData` Excel Table.
2. Create [the site parameter](dashboard_parameters/attendance_parameter_site.md), or reuse it if the intended site is already configured.
3. Create [the Power Query definitions](survey/survey_queries.md) in their stated order and apply the load settings. For a new build, create `stgSurveyRaw` directly. Rename an existing raw query called `factSurvey` before creating the analytical table with that name.
4. Create [the relationships](survey/survey_model.md). Set the category ordering and keep the survey disconnected from attendance.
5. Add [the measures](survey/survey_measures.md) with their exact names, formats and dependencies.
6. Complete [the result checks](survey/survey_validation.md) before creating management charts.

For each response, retain six confidence-question rows and five tool-question rows, including unanswered questions. Check those multiples against the source count. They are answer opportunities, not additional submissions.

Use the supplied measures for Domain and Support selections. Selecting several Domains means any of them; adding a Support selection requires the response also to match that support. A simple row count on an answer table does not apply this extra selection rule.

## Refresh and maintain

1. Save changes in the source Excel Table before refreshing.
2. Compare the response count with the source and check the expected answer-row multiples.
3. Inspect answers marked Unmapped or Invalid. Correct an unintended source entry or agree a mapping before including it in a scored result.
4. Check new Domain and Support spellings before combining labels.
5. Recheck counts, percentages and selections after changes to preparation, relationships or measures.

Change `capabilityFolder` when the source folder moves. Change `basePath` when the site changes, remembering that another model may share that parameter. Inspect the selected file list after either change. `SurveyWorkbookSelection` means zero or several workbooks were selected; correct the selection rather than removing the check.

A new display label does not necessarily need a new technical ID. Preserve QuestionID and ToolID values when the question meaning is unchanged, and review the mapping when its source heading changes.

## Technical references and later extensions

[Validation](survey/survey_validation.md) separates generated test values from results checked in Power BI. Test the actual workbook reader, relationships, measures and selections in the intended model before relying on the report.

[Draft report examples](survey/survey_report_build.md) show possible layouts. Their appearance is optional; their calculation meanings and selection rules are not.

For repeated surveys or changed questionnaires, read [the multi-wave plan](survey/survey_waves.md), [maintainer runbook](survey/survey_wave_runbook.md) and [comparison rules](survey/survey_wave_comparisons.md). The extension is separate from the current one-workbook build. It requires wave-specific response keys and a record of which question versions were asked before data can be combined.
