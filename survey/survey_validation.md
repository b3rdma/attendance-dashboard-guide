# AI capability survey validation

[Survey model](survey_model.md) · [Survey measures](survey_measures.md)

Use the checks on this page to confirm that a rebuilt model produces the intended numbers. Start with the live checks below. The later invented response records provide a repeatable technical test when query or measure logic changes. Running Python or recreating the test records is not required for an ordinary source update.

## Checks for a new build or refresh

1. Record the selected workbook and refresh date. Compare its tblRawData row count with `[Survey Responses]` before applying selections.
2. Show `[Confidence Answer Slots]`, `[Confidence Valid Answers All Ratings]`, `[Confidence Missing Answers]` and `[Confidence Unmapped Answers]` on separate cards or in a simple table without answer-category rows. The last three counts must add to Answer Slots. Answer Slots must equal six times the response count with all six questions in scope.
3. Show `[Tool Valid Ratings All Ratings]`, `[Tool Missing Ratings]` and `[Tool Invalid Ratings]` without a rating-category filter. Add those three counts: the result must equal five times the response count with all five tools in scope.
4. Restrict the question to C01 using dimSurveyConfidenceQuestion. Compare favourable and valid-answer counts with a small manual count in the source. Check that the percentage divides by valid answers, while coverage divides by expected answers.
5. Select Grade or CostCentre, then Domain and Support. Confirm that response, confidence and tool results all refer to the same matching responses. Use a known small group or the four-response test below when the result is difficult to check manually.
6. Clear the selections and confirm the original totals return. Keep the observed counts and any exception explanation with the handover record.

Check calculations before reproducing a particular chart layout. A different visual is acceptable when it uses the same measure, question filter and selected group.

## Evidence boundary

All records and numbers on this page are invented test controls. The tests use the public example headings. Match those headings and mappings to the intended source, then check its results separately.

Keep generated fixtures outside the selected SharePoint survey folder. Use a separate disposable query or Power BI model for deliberate duplicate, missing-field or invalid-value cases. Record file generation, execution in Microsoft M, execution in DAX and checks of the intended source separately.

## Source and structural checks

| Check | Required result |
| --- | --- |
| Selected workbook | One deliberate current workbook, or an explicit filename choice; no reliance on unspecified first-file order |
| Named source object | `tblRawData`, Kind Table |
| Source inventory | All selected source columns remain available in unloaded raw staging |
| Prepared stage | 26 required fields selected by their exact source headings |
| Response profile | 13 source fields plus five display-order fields, 18 columns; one unique nonblank ResponseID per source row |
| Response count | Equals the source row count before report selections |
| Confidence slots | Six per response when all six statements are selected |
| Tool-rating slots | Five per response when all five tools are selected |
| Domain bridge | One distinct ResponseID and nonblank Domain pair |
| Support bridge | One distinct ResponseID and nonblank Support pair |
| Attendance relationships | None |

Do not hard-code a response count. A correct row count does not establish unique people. Source fields outside the prepared selection are not required by these calculations.

## Four-response cohort fixture

A fixture is a small, fixed set of test records with known answers. This fixture makes it possible to check the selected group, or cohort, by listing its individual response IDs.

Use clearly synthetic Grade labels and option names:

| ResponseID | Grade | Domain choices | Support choices | C01 answer |
| --- | --- | --- | --- | --- |
| 1 | G1 | A; B; | X; | Strongly agree, score 5 |
| 2 | G1 | A; B; | Y; | Agree, score 4 |
| 3 | G2 | B; | X; Y; | Neutral, score 3 |
| 4 | G2 | Blank | Blank | Missing |

C01 is the example work-task confidence statement. The generator uses the public source headings in an in-memory test table. For a separate workbook-reader test, create a synthetic Excel Table named `tblRawData` with those headings. Populate the other required fields with clearly synthetic supported inputs. Retain all six confidence slots and all five tool slots for every response, including unanswered cells.

Expected row counts are four response profiles, 24 confidence slots, 20 tool-rating slots, five Domain pairs and four Support pairs. The Domain pairs are 1/A, 1/B, 2/A, 2/B and 3/B. The Support pairs are 1/X, 2/Y, 3/X and 3/Y. Response 4 has no pair but remains in the unfiltered response population.

The complete confidence fixture is:

| ResponseID | C01 | C02 | C03 | C04 | C05 | C06 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Strongly agree | Strongly agree | Agree | Agree | Strongly agree | Agree |
| 2 | Agree | Neutral | Agree | Neutral | Agree | Disagree |
| 3 | Neutral | Disagree | Neutral | `  aGrEe  ` | Not sure | Empty text |
| 4 | null | null | null | null | null | null |

Expected confidence totals: 24 slots, 16 Valid, seven Missing and one Unmapped. Valid scores sum to 59, and ten valid answers are Agree or Strongly agree. The mixed-case C04 answer must become trimmed `aGrEe` with score 4; the unrecognised C05 wording remains Unmapped rather than becoming Neutral.

The tool fixture is:

| ResponseID | Co-pilot | ChatGPT | Gemini | Grammarly | Claude |
| --- | --- | --- | --- | --- | --- |
| 1 | 5 | 4 | 3 | 2 | 1 |
| 2 | Text `5` | null | Text `2.5` | 0 | 6 |
| 3 | Text ` 1 ` | Text `3` | 2 | 4 | 5 |
| 4 | null | null | null | null | null |

Expected tool totals: 20 slots, eleven Valid, six Missing and three Invalid. Valid ratings sum to 35 and three slots have code 5. The invalid source representations are `2.5`, `0` and `6`. These controls verify numerical handling without assigning an unknown substantive meaning to the tool scale.

Use the defined profile option lists to populate client capability, exposure and learning levels 1 through 4 in response order. Those numbers describe expected display positions only. Set CommissionInterest to Yes, Depends on the role, No and null for responses 1 through 4; set TrainingInterest to Yes, Yes, No and null. Expected order fields are commission 3/2/1/99 and training 2/2/1/99. Expected counts are three valid commission answers, one Yes and one conditional response; three valid training answers and two Yes responses. CostCentre is CC1, CC1, CC2 and null, so the loaded profile must retain one `(No answer)` cost centre.

## Cohort expectations

These are independent expected response counts, rather than claimed DAX outputs:

| Selection | Expected ResponseIDs | Count |
| --- | --- | ---: |
| No Domain or Support filter | 1, 2, 3, 4 | 4 |
| Domain A | 1, 2 | 2 |
| Domain B | 1, 2, 3 | 3 |
| Support X | 1, 3 | 2 |
| Domain A and Support X | 1 | 1 |
| Domain B and Support Y | 2, 3 | 2 |
| Domains A or B, and Support X | 1, 3 | 2 |
| Grade G1 and Domain B | 1, 2 | 2 |
| Grade G2 and Support Y | 3 | 1 |
| Explicit option filter matching no pair | None | 0 |
| Clear option filters | 1, 2, 3, 4 | 4 |
| CostCentre `(No answer)` | 4 | 1 |

Clearing a slicer normally restores an unfiltered scope; it does not create the zero-data test. For the no-match case, apply an explicit filter that matches no synthetic option or no retained response.

Repeat these cases on a response-count card, a confidence measure and a tool-rating measure. All must use the same response cohort. A Domain bar and Support selection must combine with AND, while selected choices inside a single field combine with OR. No response should be counted twice merely because it selected several matching options.

Domain A and B bars contain two and three responses respectively. Their sum is five mentions across four response records, including one record without a Domain choice. This is an expected overlap, not a reconciliation failure. The unfiltered distinct Domain-response total is three, while the unfiltered core response count is four. Label these quantities separately.

## Known C01 agreement expectations

For the C01 values above:

| Cohort | Answer slots | Valid | Missing | Unmapped | Favourable | Favourable share of valid answers | Mean agreement code |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All four responses | 4 | 3 | 1 | 0 | 2 | 66.666667% | 4.0 |
| Domain A | 2 | 2 | 0 | 0 | 2 | 100% | 4.5 |
| Support X | 2 | 2 | 0 | 0 | 1 | 50% | 4.0 |
| Domain A and Support X | 1 | 1 | 0 | 0 | 1 | 100% | 5.0 |
| Grade G2 | 2 | 1 | 1 | 0 | 0 | 0% | 3.0 |
| Explicit empty cohort | 0 | 0 | 0 | 0 | 0 | BLANK | BLANK |

The unfiltered C01 valid-answer distribution is one Neutral, one Agree and one Strongly agree. Each is one third of valid answers, and the five response-category shares sum to 100%. Answer coverage is 3/4 = 75%; the missing answer must not become score 0 or Neutral.

Show counts and the underlying decimal values in a validation matrix before relying on formatted cards. Use exact equality for integer counts and an explicit tolerance for decimal ratios, for example `0.000000001`. Do not confuse 66.7% display rounding with a different population.

## Transformation cases

Create one deliberate variation at a time:

| Variation | Expected behaviour |
| --- | --- |
| Trailing semicolon after one or several choices | Discard the empty split token; retain each real option |
| Surrounding whitespace | Trim the individual token without changing its meaning |
| Repeated A token in response 1's Domain list | Retain only one 1/A pair |
| Blank Domain or Support list | Create no choice pair, preserve the response profile |
| Null confidence answer | Preserve the response-question slot with Missing status |
| Unrecognised nonblank confidence text | Preserve the raw answer, classify Unmapped and leave Score blank |
| Each defined agreement label | Map to its documented score 1 through 5 |
| Tool rating 1 or 5 | Retain the numerical code as Valid without assigning unknown endpoint meanings |
| Missing tool rating | Preserve the response-tool slot with Missing status |
| Tool rating outside 1 through 5, fractional or nonnumeric | Classify Invalid without rounding it into a valid code |
| Duplicate or blank response ID | Stop or report the key validation failure before relationship processing |
| Several source workbooks with no explicit selection rule | Report ambiguous source selection rather than silently choosing enumeration row 0 |
| Extra unused raw column | Retain it in raw staging; prepared columns and model grains remain stable |
| Unrecognised client-capability label | Preserve its text and assign display order 99; do not invent a capability score |
| No source rows, with required headings retained | Response facts, answer facts, bridges and option dimensions have zero rows; the static question/Likert/tool/rating dimensions retain 6/5/5/5 rows |

Compare the actual query outputs with these expectations in Microsoft's M engine. Generating expected tables in Python alone does not establish Power Query behaviour. If the implementation's status strings differ, reconcile the query and measure contract before loading the model.

## Relationship and DAX checks

1. Create exactly the single-direction relationships in [the model](survey_model.md). Confirm that all one-side keys are unique and no survey object is related to attendance.
2. Apply Grade and CostCentre filters from the response profile. Confirm that both long answer tables and both bridges receive the response restriction.
3. Test the Domain/Support cohort cases above across every core measure family. A bridge-only distinct count does not establish that a confidence card uses the same cohort.
4. For one statement, show all five Likert options. Confirm valid-answer segments sum to 100% and Missing/Unmapped remain separate completeness counts.
5. Select several statements. Confirm that totals describe response-statement answers, not unique people. Retain question context when removing a Likert legend filter.
6. For one tool, compare the full numerical distribution with Rating 5 Count and its valid-rating denominator. Do not label it capability or proficiency until the source scale is defined.
7. Check totals, zero-data contexts, intersecting cohort filters and clearing selections. Empty counts should be zero; ratios without a denominator should be BLANK.
8. After the synthetic checks, compare the actual source response count and six/five slot multiples in the intended model. Record the selected file, source version and refresh date.

Use the defined exact category labels for client capability, exposure, formal learning, commission interest and training interest. Check their display-order columns, including the missing/unknown position 99, without treating those columns as analytical scores. Do not invent further Yes/No maps or maturity thresholds merely to reproduce an undefined Excel pivot title.

## Generate and run the tests

Generate the test files from the repository root:

```sh
python3 scripts/build_survey_tests.py
```

The output directory contains m_survey_tests.pq, its manifest, fixture_data.json, expected_arithmetic.json and eleven DAX table declarations for a separate test model. Expected controls are the four-response values listed above: 24 confidence slots, 20 tool slots, five Domain pairs and four Support pairs.

Paste the complete M wrapper into a blank query in a separate test file and inspect every Pass result. Create the model relationships and measures separately to check the twelve group-selection cases in Power BI. The wrapper uses in-memory tables; it does not test SharePoint credentials or the workbook reader against the intended source.

The generator and Python tests do not run M or DAX. Record the observed Microsoft-engine results and generated fingerprints for the exact public template version being used. Test the real source connection, named table, model relationships, measures and report outputs before relying on a new build.

## Proposed multi-wave extension

Keep the single-snapshot suite above as its own regression baseline. Use [the separate wave prototype](survey_wave_prototype.md) and [maintainer acceptance cases](survey_wave_runbook.md#power-bi-acceptance-before-routine-operation) when evaluating repeat administrations or new question sets. Those fixtures do not replace actual-source checks or establish that the single-snapshot model supports multiple files.
