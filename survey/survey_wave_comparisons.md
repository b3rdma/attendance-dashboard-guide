# Compare future survey waves

[Survey guide](../survey_dashboard_guide.md) · [Current measures](survey_measures.md) · [Current model](survey_model.md) · [Metric handbook](../guide/dashboard_metrics.md)

## Proposal status and scope

This page specifies a future comparison layer. It is not part of the current one-workbook model and has not been executed in Power BI. Do not paste its DAX into the current model before implementing and testing the future tables, unique response keys and adapted base measures described below. Keep the current 31 survey measures and single-snapshot source unchanged while evaluating the proposal.

The immediate purpose is to compare one unchanged agreement question between two survey waves. A wave is one dated collection of responses. A question set is the questionnaire used for that collection; several waves can reuse one question set.

## What an anonymous comparison means

Compare the responses collected in each wave. The same local ID in two files does not establish the same person. A combined count is a count of submissions across waves, rather than a count of different employees. Do not join the two answer tables by local response ID to calculate individual improvement.

A valid headline is: `Agreement among valid answers was 66.7% in the baseline wave and 75.0% in the later wave.` It does not establish that the same people became more confident, that all employees changed, or that Lunch & Learn attendance caused the difference.

Matched individual change would require a deliberately designed repeated-person study and a suitable persistent identity. That is a separate change to this anonymous survey process, rather than a key that can be inferred from grade, cost centre or repeated response numbers. Pew Research Center explains the distinction between [cross-sectional and panel surveys](https://www.pewresearch.org/writing-survey-questions/).

## Decide whether a comparison is meaningful

| Situation | Default treatment |
| --- | --- |
| Same question wording, answer scale, reference period and intended meaning | Reuse the approved question version and allow a like-for-like comparison. |
| Source column heading corrected but the question shown to respondents is unchanged | Update the source-heading mapping after checking the questionnaire. A file-header change alone does not require a new meaning. |
| New question added | Give it its own question/version identity. Report it from its first asked wave onward. |
| Wording, meaning or reference period materially changed | Create a new question version. Do not automatically connect its trend to the old version. |
| Free text replaced by a selection | Treat as a new version and response type. Historical theme coding may support a separately labelled analysis, but does not make the measurements identical. |
| Answer options, labels or scale direction changed | Register the changed scale/version and review comparability. Equal numerical ranges do not establish equal meanings. |
| Tool or terminology question still has unknown scale meanings | Keep interpretation deferred. These agreement templates do not approve those fields for comparison. |
| Two versions share a broad topic | Show separately unless a documented, tested comparison rule explicitly permits combining them. The templates below require the exact same version. |

Keep unchanged core questions as trend anchors. Adding a new question need not break comparisons for the unchanged questions. Record relevant changes in question order, response method and target audience. [Pew's question-design guidance](https://www.pewresearch.org/writing-survey-questions/) explains why wording and context matter for trends; [AAPOR's best practices](https://aapor.org/standards-and-ethics/best-practices/) discusses evaluating measurement changes.

### Distinguish not asked from unanswered

Register which question versions belong to each wave. Create answer opportunities only for questions actually asked in that wave. If a new question first appears in Wave 2, Wave 1 has no opportunities for that question. It must display `Not asked`, rather than a zero score, disagreement or missing-answer problem.

If an asked question has an empty answer cell, retain its opportunity as Missing. If a question is registered as asked but its required source column is absent, stop or report a structural import error. Do not silently treat a broken file as a wave that omitted the question.

The current Confidence Answer Slots measure counts its retained fact rows. Extending it by manufacturing rows for every possible question in every wave would inflate its denominator. Adapt the preparation and measures together so their retained rows represent genuine opportunities.

## Read percentage changes correctly

All numerical examples below use invented records.

| Wave | Valid answers | Agree or Strongly agree | Favourable share |
| --- | ---: | ---: | ---: |
| W1, baseline | 3 | 2 | 66.666667% |
| W2, target | 4 | 3 | 75.000000% |

The difference is **+8.333333 percentage points**. It is calculated as 75% minus 66.666667%, rather than described as an 8.333333% relative increase. Display the wave-specific valid counts with the percentages.

Combining both waves gives five favourable answers out of seven valid answers, or **71.428571%**. Taking the simple mean of the two percentages gives **70.833333%**. These differ because the waves have different answer counts. Use the combined numerator and denominator when reporting a pooled answer share. Do not label pooled submissions as distinct people or present the pooled result as the latest wave's result.

### Check who replied in each wave

A changed response mix can change the overall percentage even when each group's percentage remains the same:

| Group | W1 valid answers | W1 favourable | W2 valid answers | W2 favourable |
| --- | ---: | ---: | ---: | ---: |
| G1 | 20 | 16, or 80% | 80 | 64, or 80% |
| G2 | 80 | 16, or 20% | 20 | 4, or 20% |
| Total | 100 | 32, or 32% | 100 | 68, or 68% |

The aggregate difference is +36 percentage points, although neither group's favourable rate changed. Show the grade, cost-centre and other relevant response mix beside the comparison. Selecting the same recorded groups improves interpretability but does not establish that the same individuals replied or remove every difference between waves.

## Future model interface required by the DAX

Implement this exact interface, or adapt and review every expression before installation. It describes the proposed comparison contract, rather than tables already included in the current model.

| Object | Required fields and rule |
| --- | --- |
| dimSurveyWave | Unique nonblank text WaveID, with the wave's label and dates as attributes. Active single-direction relationship to the future response profile. |
| Survey Baseline | Disconnected table containing the available WaveID values. Use it for the baseline selector; select exactly one. |
| Survey Target | Disconnected table containing the available WaveID values. Use it for the target selector; select exactly one. |
| dimSurveyQuestionVersion | Unique QuestionVersionID; ScaleID, ComparisonGroupID and logical ComparisonApproved. An active single-direction relationship filters the future answer fact. |
| factSurveyWaveQuestion | One unique WaveID/QuestionVersionID pair for each asked question. Active single-direction relationships from dimSurveyWave and dimSurveyQuestionVersion filter this availability table. It has no outgoing relationship. |
| Comparable Valid Answers | Future numeric base measure counting valid answers for the selected question, wave and response cohort. Return zero for an empty valid count. |
| Comparable Favourable Share | Future numeric base measure dividing Agree/Strongly agree by valid answers for the selected question, wave and cohort. Return BLANK when its denominator is zero. |

The two base measures are prerequisites, not existing measures renamed by this page. Adapt them after migrating all response relationships and the cohort logic from local ResponseID to the future cross-wave response key. Confirm that their Domain/Support inclusion checks run under the wave filter supplied to each calculation. Missing answers, unrecognised answers and recognised but unscored options stay outside the valid scored denominator.

Use ScaleID `Agreement5` only for the defined Strongly disagree = 1 through Strongly agree = 5 scale, with favourable answers 4 and 5. ComparisonApproved must be a true/false field set deliberately after review. ComparisonGroupID records the approved comparison purpose. It must not be inferred merely from similar titles or equal code ranges.

These templates require one exact QuestionVersionID common to both waves. They do not implement an approved cross-version mapping, a tool-rating comparison, a free-text theme comparison or the proposed retrospective change scale. Those need separate definitions and tests.

Use dimSurveyWave fields for ordinary wave/date filters. Hide duplicate wave fields on detail tables from ordinary report use. There is no separate calendar table in this interface: dates are attributes of dimSurveyWave. Clearing the wave dimension therefore clears its ordinary date filters too. If a calendar relationship is added later, update both comparison calculations and their guards to replace that calendar context consistently.

Keep the availability table independent of response cohorts. It records that a question was asked even when a selected grade supplies zero responses. Never derive question availability solely from nonblank answers or from the current response count.

### Required preflight for active cohort questions

Outcome availability is not enough. A selection such as Grade, CostCentre, Domain or Support is meaningful across two waves only when the source question behind that selection was administered in both, with compatible wording and approved category/option mappings. A wave that never asked about Support cannot supply an empty Support choice and be treated as evidence of no demand.

Before making a comparison available, check every active cohort filter against the two waves' profile/cohort availability and mapping records:

| Preflight result | Required behaviour |
| --- | --- |
| Every active filter comes from a question administered comparably in both waves | Permit the selected cohort to reach the comparison measures. |
| An active filter's question was not asked in either selected wave | Stop the comparison and display, for example, `Support was not asked in the baseline wave`. Do not display zero valid answers as its explanation. |
| An active filter's meaning or options changed without an approved mapping | Stop the comparison and explain the incompatible cohort definition. |
| An administered, comparable cohort genuinely has no matching responses | Permit the ordinary zero-valid-answer status below. This is different from an unavailable question. |

For the first implementation, expose only cohort filters explicitly defined as comparable in both selected instruments. Record that restriction and check it whenever the baseline/target pair changes. If arbitrary wave pairs and profile filters are later exposed, implement and test an automatic availability/mapping check before enabling them. A manual preflight is an implementation prerequisite, rather than a permanent substitute for that automatic check in an unrestricted report.

The seven DAX templates below **do not implement this cohort preflight**. Their declared interface has no complete map from each active profile/choice filter to its administered question version, so inventing that logic here would conceal a missing model requirement. They assume the active cohort has already passed this check. `Ready` means the selected outcome passes the specified guards under that prevalidated cohort contract. Do not present it as an unconditional whole-model readiness check or enable the templates for unrestricted wave/filter combinations without completing the missing preflight.

## Proposed DAX, in dependency order

Create the two disconnected selectors and required future base measures before these expressions. Hide technical helpers after validation. Keep the final status available in the report so a blank difference has an explanation.

### 1. Check the selected waves and question

```dax
Wave Comparison Structure Status =
VAR BaselineWave = SELECTEDVALUE('Survey Baseline'[WaveID])
VAR TargetWave = SELECTEDVALUE('Survey Target'[WaveID])
VAR HasBaseline = HASONEVALUE('Survey Baseline'[WaveID])
VAR HasTarget = HASONEVALUE('Survey Target'[WaveID])
VAR BaselineExists =
    COUNTROWS(
        FILTER(ALL(dimSurveyWave), dimSurveyWave[WaveID] = BaselineWave)
    ) = 1
VAR TargetExists =
    COUNTROWS(
        FILTER(ALL(dimSurveyWave), dimSurveyWave[WaveID] = TargetWave)
    ) = 1
VAR HasQuestion =
    HASONEVALUE(dimSurveyQuestionVersion[QuestionVersionID])
VAR IsApproved =
    SELECTEDVALUE(dimSurveyQuestionVersion[ComparisonApproved], FALSE())
VAR ComparisonGroup =
    SELECTEDVALUE(dimSurveyQuestionVersion[ComparisonGroupID])
VAR Scale = SELECTEDVALUE(dimSurveyQuestionVersion[ScaleID])
VAR BaselineAvailability =
    CALCULATE(
        COUNTROWS(factSurveyWaveQuestion),
        REMOVEFILTERS(dimSurveyWave),
        TREATAS({BaselineWave}, dimSurveyWave[WaveID])
    )
VAR TargetAvailability =
    CALCULATE(
        COUNTROWS(factSurveyWaveQuestion),
        REMOVEFILTERS(dimSurveyWave),
        TREATAS({TargetWave}, dimSurveyWave[WaveID])
    )
RETURN
SWITCH(
    TRUE(),
    NOT HasBaseline || ISBLANK(BaselineWave), "Select one baseline wave",
    NOT HasTarget || ISBLANK(TargetWave), "Select one target wave",
    BaselineWave = TargetWave, "Select two different waves",
    NOT BaselineExists, "Baseline wave is unavailable",
    NOT TargetExists, "Target wave is unavailable",
    NOT HasQuestion, "Select exactly one question version",
    NOT IsApproved, "Question is not approved for comparison",
    ISBLANK(ComparisonGroup) || LEN(TRIM(ComparisonGroup)) = 0,
        "Question comparison group is missing",
    Scale <> "Agreement5", "Comparison requires the confirmed Agreement5 scale",
    BaselineAvailability = 0, "Question was not asked in the baseline wave",
    TargetAvailability = 0, "Question was not asked in the target wave",
    BaselineAvailability <> 1 || TargetAvailability <> 1,
        "Question availability registry is invalid",
    "Ready"
)
```

The existence checks use all visible wave rows, rather than an ordinary wave/date slicer's restricted list. The availability checks replace that ordinary wave context, retain the exact question version and count its registered opportunity. They do not depend on whether the selected response cohort supplied any answers. The registry must also pass uniqueness checks during preparation; this guard is not a substitute for those checks.

### 2. Count valid baseline answers

```dax
Wave Baseline Valid Answers =
VAR BaselineWave = SELECTEDVALUE('Survey Baseline'[WaveID])
RETURN
IF(
    [Wave Comparison Structure Status] = "Ready",
    COALESCE(
        CALCULATE(
            [Comparable Valid Answers],
            REMOVEFILTERS(dimSurveyWave),
            TREATAS({BaselineWave}, dimSurveyWave[WaveID])
        ),
        0
    )
)
```

### 3. Count valid target answers

```dax
Wave Target Valid Answers =
VAR TargetWave = SELECTEDVALUE('Survey Target'[WaveID])
RETURN
IF(
    [Wave Comparison Structure Status] = "Ready",
    COALESCE(
        CALCULATE(
            [Comparable Valid Answers],
            REMOVEFILTERS(dimSurveyWave),
            TREATAS({TargetWave}, dimSurveyWave[WaveID])
        ),
        0
    )
)
```

Each base measure is evaluated inside its new CALCULATE context. Do not calculate a reusable response cohort outside that operation and then carry it into both waves; that could retain the original wave's response keys. Keep the question and grade/cost-centre/Domain/Support filters in force for each wave separately.

The counts return zero for an asked question with no valid answers in the selected cohort. They return BLANK when the structure is unsuitable. This distinction allows the status below to distinguish an unasked question from a zero-denominator comparison.

### 4. Explain whether a numerical comparison is available

```dax
Wave Comparison Status =
VAR StructureStatus = [Wave Comparison Structure Status]
VAR BaselineN = [Wave Baseline Valid Answers]
VAR TargetN = [Wave Target Valid Answers]
RETURN
SWITCH(
    TRUE(),
    StructureStatus <> "Ready", StructureStatus,
    BaselineN <= 0 && TargetN <= 0, "No valid answers in either selected wave",
    BaselineN <= 0, "No valid answers in the baseline wave",
    TargetN <= 0, "No valid answers in the target wave",
    "Ready"
)
```

### 5. Calculate baseline agreement

```dax
Wave Baseline Favourable Share =
VAR BaselineWave = SELECTEDVALUE('Survey Baseline'[WaveID])
RETURN
IF(
    [Wave Comparison Status] = "Ready",
    CALCULATE(
        [Comparable Favourable Share],
        REMOVEFILTERS(dimSurveyWave),
        TREATAS({BaselineWave}, dimSurveyWave[WaveID])
    )
)
```

### 6. Calculate target agreement

```dax
Wave Target Favourable Share =
VAR TargetWave = SELECTEDVALUE('Survey Target'[WaveID])
RETURN
IF(
    [Wave Comparison Status] = "Ready",
    CALCULATE(
        [Comparable Favourable Share],
        REMOVEFILTERS(dimSurveyWave),
        TREATAS({TargetWave}, dimSurveyWave[WaveID])
    )
)
```

### 7. Calculate the difference in percentage points

```dax
Wave Favourable Difference pp =
IF(
    [Wave Comparison Status] = "Ready",
    100 * (
        [Wave Target Favourable Share]
            - [Wave Baseline Favourable Share]
    )
)
```

Format the two shares as percentages with one decimal, the counts as whole numbers and the difference using a numeric format such as `+0.0 "pp";-0.0 "pp";0.0 "pp"`. Do not format the already multiplied difference as Percentage. A value of 8.333333 means 8.333333 percentage points; Percentage formatting would multiply its display by another 100.

Use Wave Comparison Status beside the result or in its tooltip. A zero difference means two defined shares were equal. A blank difference means the comparison was unavailable or unsuitable, rather than no change.

Microsoft documents [TREATAS](https://learn.microsoft.com/en-us/dax/treatas-function-dax) for applying selector values to an unrelated table, and [REMOVEFILTERS](https://learn.microsoft.com/en-us/dax/removefilters-function-dax) for clearing the ordinary wave context. These functions describe the mechanics; metadata and questionnaire review determine whether the resulting comparison is meaningful.

## Optional retrospective change question

Keep the unchanged work-confidence statement in every repeated core survey. An additional question can collect a respondent's view of change:

`Compared with [fixed baseline period], how has your confidence in using AI tools for work tasks changed?`

| Code | Suggested answer |
| --- | --- |
| 1 | Much lower |
| 2 | Slightly lower |
| 3 | About the same |
| 4 | Slightly higher |
| 5 | Much higher |
| Unscored option | Unable to compare |

Choose and record the actual baseline reference before issuing the questionnaire. Pilot the wording and scale with the intended audience. This is a proposed question, rather than a validated assessment scale. Ask awareness in a separate question if needed; awareness and confidence describe different things. Balanced answers permit a decrease as well as an increase.

Give this question its own version and scale. Do not append its 1–5 codes to Agreement5 or pool them with the six confidence statements. Label its result Self-reported confidence change. It supplements repeated current-confidence answers; it does not establish individual measured improvement or attribute change to Lunch & Learn.

Recognise Unable to compare explicitly and keep it unscored. It is an answer, rather than Missing or Unmapped. A future answered-completeness measure may count it as answered, while scored-answer coverage excludes it. The baseline wave's absent retrospective question remains Not asked. These states require documented preparation and measure handling before installation.

## Acceptance checks before enabling comparisons

1. Reuse local response IDs in two synthetic waves and confirm their cross-wave response keys remain distinct. Check the response profile, both answer tables and both multi-select bridges.
2. Test W1 with two favourable answers out of three valid answers and W2 with three out of four. Expect 66.666667%, 75%, three/four valid answers and +8.333333 percentage points. Use decimal tolerance rather than formatted text for the numerical comparison.
3. Reverse the baseline and target. Expect the same counts in the opposite roles and a difference of -8.333333 percentage points.
4. Test no selection, several waves in either selector, the same wave in both selectors, an unavailable wave and several question versions. Expect an explanatory status and blank shares/difference.
5. Add a question only in W2. Its W1 comparison must report Not asked. An asked but unanswered W1 question must instead report no valid baseline answers.
6. First select a grade or Domain/Support question that was not asked in one wave. The prerequisite cohort preflight must stop the comparison and show that availability reason, rather than report no valid answers. Then select a comparable, administered cohort that genuinely has zero valid answers in one wave. Preserve the metadata's asked status, show the zero valid count and leave the difference blank.
7. Change the scale, revoke comparison approval or remove the comparison group. Confirm the guard prevents a numerical comparison. Different versions remain separate even if assigned the same broad comparison group.
8. Select an ordinary wave/date filter that includes only one wave, then select another baseline/target pair. Confirm both comparison calculations replace the ordinary wave context while preserving the selected response characteristics.
9. Verify that the future base measures use the intended valid-answer and favourable definitions. Missing, unmapped and recognised unscored answers must not become Neutral, zero or automatically favourable.
10. Compare response-group composition and confirm totals are labelled submissions or answers. Do not present a pooled wave count as distinct employees or a percentage-point difference as proved individual or programme impact.

Record native DAX outputs, the tested relationships and metadata versions separately from Python arithmetic or generated fixtures. No completed native execution of these future expressions is claimed by this page.
