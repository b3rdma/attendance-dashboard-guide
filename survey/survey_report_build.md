# Draft AI survey report examples

[Survey build guide](../survey_dashboard_guide.md) · [Survey measure definitions](survey_measures.md) · [Metric meanings](../guide/dashboard_metrics.md)

**Optional presentation reference.** These two page designs are examples, rather than the required dashboard appearance. Rebuild and check the data model and measures first. Change layouts, chart types, colours and titles to suit the audience while preserving the measure definitions, question filters and selection behaviour described below. The same data under the same selections must give the same metrics.

## Reporting purpose and current status

The examples use two pages for the separate anonymous survey model. They describe submitted responses about confidence, experience and development preferences. Keep survey filters and relationships independent of the Teams attendance model.

The example model reads one survey snapshot. Label its counts Responses or Submissions, rather than People. It cannot establish the number of different employees or an employee response rate without a suitable population and identity source.

Use the five defined agreement labels for the six confidence statements. Do not describe agreement as an objective assessment of skill. Keep tool scores labelled as recorded rating codes until the original scale wording is defined. Defer the terminology block and any undefined maturity or confidence groups. Do not invent thresholds to reproduce those groups.

Complete the queries, relationships and measure checks before adding these optional visuals. Verify the actual source counts and filter behaviour in the model being built.

## Common canvas and cohort controls

The draft layouts use **Type = 16:9; Size = 1920 x 1080 (Full HD)**. When reproducing this layout, enter the listed positions and sizes in pixels. The exact positions, fonts and styling do not define the calculations. Clearly label the pages as survey analysis.

Use these controls on both pages:

| Object | X | Y | Width | Height | Field or content |
| --- | ---: | ---: | ---: | ---: | --- |
| Page title | 36 | 24 | 1,848 | 72 | Static text identifying the survey page |
| Grade slicer | 36 | 120 | 444 | 84 | `factSurvey[Grade]` |
| Cost centre slicer | 504 | 120 | 444 | 84 | `factSurvey[CostCentre]` |
| Domain slicer | 972 | 120 | 444 | 84 | `dimSurveyDomain[Domain]` |
| Support preference slicer | 1,440 | 120 | 444 | 84 | `dimSurveySupport[Support]` |
| Scope caption | 36 | 1,008 | 1,536 | 48 | Anonymous survey responses; percentage bases are shown in tooltips |
| Other-page button | 1,596 | 1,008 | 288 | 48 | Native Page navigation button |

Use dropdown slicers for long option labels and enable multiple selection. Keep the supplied `(No answer)` profile category visible. Use View > Sync slicers to synchronise all four controls between these two survey pages, with Visible enabled on both. Keep them independent of attendance pages.

Within each multi-select field, a response qualifies through any selected option. Across Domain and Support selections, it must satisfy both families. Grade and Cost centre further restrict the same cohort. Use only the explicit cohort-aware measures from [the measure guide](survey_measures.md). Implicit row counts or sums do not implement the Domain/Support cohort behaviour.

Leave Domain and Support clear initially so the first view shows the complete retained survey. A cleared slicer normally removes its filter; it does not mean no responses. Use a filter matching no rows when testing a genuinely empty cohort.

### Apply the defined category order

The prepared `factSurvey` has 18 columns: thirteen response/profile fields and five display-order columns. Before adding categorical charts, select each label column and use Column tools > Sort by column with its corresponding order field:

| Label column | Sort column |
| --- | --- |
| `factSurvey[ClientCapability]` | `factSurvey[ClientCapabilityOrder]` |
| `factSurvey[ClientAIExposure]` | `factSurvey[ClientAIExposureOrder]` |
| `factSurvey[FormalLearning]` | `factSurvey[FormalLearningOrder]` |
| `factSurvey[CommissionInterest]` | `factSurvey[CommissionInterestOrder]` |
| `factSurvey[TrainingInterest]` | `factSurvey[TrainingInterestOrder]` |

Hide the five order fields from the ordinary report field list after applying these settings. They are display metadata, not numeric capability, learning or interest scores. Unknown labels and `(No answer)` have order 99 and remain visible after the defined choices. Do not sum or average the order columns.

## Page 1: Response profile and confidence

Use the title `AI survey | Response profile and confidence`.

This page answers which response groups are represented and how respondents describe their confidence across the six statements. Compare the agreement distributions before comparing optional mean scores.

### Layout

| Visual | X | Y | Width | Height |
| --- | ---: | ---: | ---: | ---: |
| Response count card | 36 | 228 | 444 | 108 |
| Valid confidence coverage card | 504 | 228 | 444 | 108 |
| Work confidence card | 972 | 228 | 444 | 108 |
| Output judgement card | 1,440 | 228 | 444 | 108 |
| Six-statement agreement distribution | 36 | 360 | 1,848 | 360 |
| Grade profile | 36 | 744 | 600 | 240 |
| Cost centre profile | 660 | 744 | 600 | 240 |
| Business-domain profile | 1,284 | 744 | 600 | 240 |

The four-card row fits as `4 x 444 + 3 x 24 = 1848`. The three profile visuals fit as `3 x 600 + 2 x 24 = 1848`. Content ends at Y 984, leaving 24 pixels before navigation. Keep 36-pixel side margins and 24 pixels below the footer.

### Cards and local filters

| Card | Measure | Display title | Local visual filter | Format |
| --- | --- | --- | --- | --- |
| Response count | `[Survey Responses]` | Survey responses | None | Whole number |
| Valid confidence coverage | `[Confidence Answer Coverage %]` | Confidence answers scored | None | Percentage, 1 decimal |
| Work confidence | `[Confidence Favourable %]` | Confident using AI at work | `dimSurveyConfidenceQuestion[QuestionID]` = `C01` | Percentage, 1 decimal |
| Output judgement | `[Confidence Favourable %]` | Self-reported output judgement | `dimSurveyConfidenceQuestion[QuestionID]` = `C05` | Percentage, 1 decimal |

For the two item cards, add `[Confidence Valid Answers All Ratings]` to Tooltips, labelled `Valid answers`. Add it as a native Card reference label only if it fits legibly within the allocated card bounds. The local question filter must also apply to that denominator. Do not put the C01 or C05 restriction on the whole page.

Favourable means Agree or Strongly agree among valid answers to that item. Neutral is a valid answer. Missing or unmapped answers do not become Disagree or zero. Preserve BLANK when no valid answers exist. Confidence answers scored measures valid scored answers against the expected response/question slots, not the share favourable.

### Six-item Likert distribution

Create a native **100% stacked bar chart**:

| Field well or setting | Assignment |
| --- | --- |
| Y-axis | `dimSurveyConfidenceQuestion[ShortLabel]` |
| Legend | `dimSurveyLikert[ResponseLabel]` |
| X-axis | `[Confidence Valid Answers]` |
| Tooltips | `[Confidence Valid Answers]`, `[Confidence Valid Answers All Ratings]`, `[Confidence Response %]` |
| Title | Self-reported confidence and agreement |
| Sort | Question ShortLabel sorted by the question dimension's SortOrder |
| Legend ordering | Strongly disagree, Disagree, Neutral, Agree, Strongly agree; use the Likert dimension's sort order |
| Visual filter | `[Confidence Valid Answers]` greater than 0 |

The chart normalises the valid counts to 100% separately for each statement. The tooltip's first count is the segment count; All Ratings is the statement's valid-answer denominator, unchanged by its current legend segment. Do not feed a mean score into this chart. A missing answer does not contribute to a coloured agreement segment.

Use a stable ordered palette for the five responses, with Neutral in a neutral colour. Keep the same five-label ordering and colour mapping when a selected cohort has no segment in one category; an omitted empty legend category must not change the meaning of the remaining colours. Show percentage labels when legible and retain the count/denominator tooltip. Expand the question text in the tooltip or a temporary validation table if the short label alone is insufficient.

A normal 100% stacked chart is sufficient for the first build. It does not need a custom diverging axis or an overall maturity gauge. The six distributions can show a gap between work confidence and self-reported judgement without claiming that one causes the other.

### Response-profile charts

Use clustered horizontal bars:

| Visual | Y-axis | X-axis | Tooltip | Title |
| --- | --- | --- | --- | --- |
| Grade | `factSurvey[Grade]` | `[Survey Responses]` | `[Survey Responses]` | Responses by grade |
| Cost centre | `factSurvey[CostCentre]` | `[Survey Responses]` | `[Survey Responses]` | Responses by cost centre |
| Domain | `dimSurveyDomain[Domain]` | `[Survey Domain Responses]` | `[Survey Domain Responses]`, `[Survey Domain Share %]` | Responses selecting each domain |

Sort by count descending until an approved business order is supplied. Keep categorical text exact; do not derive a numerical hierarchy from grade labels. Allow vertical category scrolling where required instead of silently dropping categories with an undocumented Top N filter. Keep Display units None and counts at zero decimal places.

Domain counts are overlapping selections. One submission can count in several domain bars, so the sum can exceed Survey responses. The optional domain share uses the denominator defined in the measure guide: remove the Domain dimension's own selections, but retain the other cohort filters. Label it `Share before domain selection` in the tooltip. This is not necessarily the same denominator as the headline response card after a Domain slicer selection. Use counts as the main profile display.

## Page 2: Experience and development

Use the title `AI survey | Experience and development`.

This page connects self-reported work confidence with reported client exposure and shows the recorded demand for support. Treat relationships as descriptive associations, not evidence that training or exposure caused a confidence level.

### Layout

| Visual | X | Y | Width | Height |
| --- | ---: | ---: | ---: | ---: |
| Response count card | 36 | 228 | 600 | 84 |
| Support-selection card | 660 | 228 | 600 | 84 |
| Training-interest card | 1,284 | 228 | 600 | 84 |
| Exposure and work-confidence distribution | 36 | 336 | 912 | 300 |
| Support preferences | 972 | 336 | 912 | 300 |
| Formal learning profile | 36 | 660 | 600 | 324 |
| Commission/training interest matrix | 660 | 660 | 600 | 324 |
| Recorded tool-rating distribution | 1,284 | 660 | 600 | 324 |

The top chart pair fits as `912 + 24 + 912 = 1848`. The lower three use `3 x 600 + 2 x 24 = 1848`. The common footer and four cohort slicers use the coordinates above.

### Cards

| Card | Measure | Display title | Local filter |
| --- | --- | --- | --- |
| Response count | `[Survey Responses]` | Survey responses | None |
| Support selection | `[Survey Support Responses]` | Responses selecting support | None |
| Training interest | `[Training Yes %]` | Yes to development-plan training | None |

Support selection counts submissions with at least one relevant support choice in the current cohort, not total selections and not attendance. A blank support answer does not contribute to that count. For Training interest, add `[Training Interest Valid Responses]` to Tooltips, labelled `Valid answers`; use an additional reference label only if it fits legibly inside the allocated card. The percentage is Yes divided by recognised Yes/No answers in the cohort; missing or unrecognised answers are excluded. It ignores a filter on its own interest field while retaining the other cohort controls, as specified in the measure guide. This is an expressed preference among submissions, not an employee-wide training uptake rate.

### Exposure versus work confidence

Create a 100% stacked bar chart with `factSurvey[ClientAIExposure]` on Y-axis, `dimSurveyLikert[ResponseLabel]` in Legend and `[Confidence Valid Answers]` on X-axis. Add a visual-level question filter for `C01`. Use `[Confidence Valid Answers All Ratings]` and `[Confidence Response %]` in Tooltips. Title it `Work confidence by reported client AI exposure`.

Use the defined exposure order: `None`, `Limited Exposure`, `Some involvement`, `Significant Exposure`. Keep `(No answer)` visible after the substantive categories if present. Sort ClientAIExposure by ClientAIExposureOrder rather than alphabetically. Show each category's valid n. A small group can have a high percentage from few submissions; inspect its count before comparing groups. The axis is reported exposure, not a numerical capability score.

### Support-preference bars

Create a clustered bar chart with `dimSurveySupport[Support]` on Y-axis and `[Survey Support Responses]` on X-axis. Add `[Survey Support Share %]` to Tooltips and label that tooltip quantity `Share before support selection`. Sort counts descending. Use the title `Requested support and training`.

These are multi-select counts. Count a response once within each option, even if the source cell repeats the same option. Do not sum option counts to obtain the number of submissions. The optional share removes the Support dimension's own axis and slicer selection while retaining the other cohort filters. It can therefore use a different base from the current headline response card. Several option percentages can sum to more than 100%.

### Formal learning and interest

For formal learning, use a clustered bar chart with `factSurvey[FormalLearning]` on Y-axis and `[Survey Responses]` on X-axis. Title it `Reported formal AI learning`. Use the defined order `None`, `Introductory`, `Intermediate`, `Advanced`, with `(No answer)` after those categories if present. Sort FormalLearning by FormalLearningOrder.

For interest, use a Matrix with `factSurvey[CommissionInterest]` in Rows, `factSurvey[TrainingInterest]` in Columns and `[Survey Responses]` in Values. Title it `Commission interest and development-plan training`. The defined commission options are `No`, `Depends on the role`, `Yes`; the training options are `No`, `Yes`. Sort CommissionInterest by CommissionInterestOrder and TrainingInterest by TrainingInterestOrder, and keep row and column totals on for reconciliation. Use counts, not an invented combined willingness score. Keep `Depends on the role` as its own answer rather than treating it as Yes or No.

The matrix counts each submission once. Its grand total should match Survey responses in the same cohort. `(No answer)` remains a visible category rather than an inferred negative answer.

### Tool ratings without an assumed scale meaning

Create a 100% stacked bar chart with `dimSurveyTool[ToolName]` on Y-axis, `dimSurveyRating[RatingLabel]` in Legend and `[Tool Valid Ratings]` on X-axis. Add `[Tool Valid Ratings All Ratings]` and `[Tool Rating Distribution %]` to Tooltips. Sort ToolName by its dimension order and RatingLabel by its numeric SortOrder. Apply `[Tool Valid Ratings] > 0` to the visual.

Use the title `Recorded tool ratings: codes 1 to 5`. Use neutral ordered colours and show valid n per tool. A value of 5 is a recorded code; it is not yet a verified high-capability, frequent-use or favourable response. Do not call this chart an AI tool proficiency ranking.

Use `[Tool Rating 5 Count]` for an optional count of code-5 answers. Show `[Tool Rating 5 Share %]` beside that count to expose its valid-answer base. Keep this out of the main card row until the original question and endpoint meanings are defined.

## Interactions and navigation

Use explicit cohort controls first:

| Source | Target | Interaction |
| --- | --- | --- |
| Each Grade, Cost centre, Domain and Support slicer | All data visuals and the other cohort slicers, where supported | Filter |
| Every chart and matrix | Other charts, cards, matrices and cohort slicers | None |
| Cards | Other visuals, where controls are available | None |

Select each visual and use Format > Edit interactions. These settings are directional, so test the source and target separately. Microsoft documents the controls in [Change visual interactions](https://learn.microsoft.com/en-us/power-bi/create-reports/service-reports-visual-interactions).

The list of available slicer choices does not have to shrink after every Domain or Support selection. The measures still restrict their results to matching responses. Selecting a confidence segment or tool-rating segment does not automatically select the corresponding response profiles because the model relationships work in one direction. Keep chart-to-chart interactions off for this initial example so a chart click cannot leave different measures describing different groups. Use the visible slicers to change the selected group consistently. Test any later change to chart interactions against the same counts and percentages before accepting it.

Add a native Page navigation button at the shared footer position. Link page 1 to `Experience and development` and page 2 to `Response profile and confidence`. Keep the four slicers visible and synchronised on both pages. Add no cross-report attendance drillthrough or identity matching.

## Useful decisions and later additions

Use the pages to identify where support demand is concentrated, compare reported confidence with exposure, and inspect differences between confidence in use and confidence in checking outputs. Compare group distributions and their n before choosing training priorities.

Keep these additions for a later increment after the core outputs reconcile:

- A paired work-confidence versus limitations/judgement cross-tab at response level. The six marginal distributions alone do not establish that the same submissions supplied each pattern.
- Self-rated client-facing capability by grade, ordered as `Awareness Only/limited hands-on experience`, `Comfortable user of AI and digital tools`, `Experienced practitioner applying AI in delivery`, `Specialist/subject matter expert`. Use the defined source categories; add a maturity grouping only after its rule has been agreed.
- Reported AI productivity use by grade or work type, using its original categories and an answered-response denominator.
- Free-text theme coding with an explicit category dictionary and response-level counts. Do not publish raw response IDs or verbatim free text by default.
- Terminology ratings, once the overarching question and scale meanings are available.
- Maturity or learning groups with agreed calculation rules and thresholds.

Do not join the survey to attendance using anonymous Email, response ID, grade or cost centre. Additions to the separate survey model must preserve that independence.

## Report acceptance checks

1. Begin without cohort selections. Compare `[Survey Responses]` with the source table's row count and distinct valid ResponseID count. Use the actual source count; no fixed response total belongs in a measure.
2. Confirm the six confidence statement rows and five tool rows per submission are retained by the transformation, including missing or unrecognised answers. Four responses create 24 confidence slots and 20 tool slots; valid-answer counts can be lower.
3. For each confidence statement, confirm the five valid segment counts sum to `[Confidence Valid Answers All Ratings]`; their percentages sum to 100% when n is positive. Missing and unmapped answers are excluded from the agreement denominator and remain visible in quality measures.
4. Confirm the C01 and C05 cards use their local question filters. They must not both display a pooled six-item average.
5. Select one Grade, then one Cost centre. Check that profile, confidence, support, interest and tool outputs all use that cohort. Add Domain and Support selections and confirm the intersection rule with a small known fixture.
6. Confirm the five ordered profile fields follow their supplied source order, including the conditional commission-interest label. Keep the order fields hidden. Verify duplicated options and the trailing semicolon do not create duplicate counts or an empty domain/support category. Compare domain/support totals with their distinct-response definitions, not with summed selections.
7. Check the Domain and Support share denominators against their explicitly labelled pre-selection bases. Do not interpret those shares as a partition summing to 100%.
8. Select a cohort with no valid answers. Counts should be zero; undefined ratios should remain BLANK. Test a genuinely empty response cohort separately from clearing slicers.
9. Confirm the interest matrix totals to the cohort response count and each tool's valid rating segments total to its valid n. Preserve invalid/missing counts outside those distributions.
10. Click charts and matrix cells. Confirm they do not change the other cohort measures. Change each visible slicer and confirm all relevant visuals update on both pages.
11. Review at Fit to page. Keep complete category labels accessible through wrapping, scrolling or tooltips and preserve the Full HD layout. Record the exact field wells, filters and observed counts after building.
