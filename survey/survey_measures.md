# AI capability survey measure reference

[Survey guide](../survey_dashboard_guide.md) · [Model and relationships](survey_model.md) · [Metric definitions](../guide/dashboard_metrics.md) · [Glossary](../guide/dashboard_glossary.md)

## Status and interpretation

A measure calculates a result for the current selections in the report. For example, selecting a grade should change the response count and the confidence percentages to that grade's responses. The code below keeps these selected groups consistent, including the two questions that allow several choices.

This page contains 31 survey measures. Check them against [the small worked examples](survey_validation.md) before using a new model. Label the population Responses: anonymous IDs do not identify attendance participants or prove that every submission came from a different person. No fixed response count is built into the measures.

The six statements use Strongly disagree = 1, Disagree = 2, Neutral = 3, Agree = 4 and Strongly agree = 5. Neutral is a valid answer. Missing and unrecognised text are separate states, rather than zero agreement. These are self-reported answers, not an objective maturity test. The meanings of tool codes 1 and 5 remain undefined, so tool results keep neutral numerical labels. Terminology measures remain deferred.

## Install the measures

1. Complete [the Power Query build](survey_queries.md) and [the ten relationships](survey_model.md) first.
2. In Power BI Desktop, select factSurvey in the Data pane and choose New measure. Paste one complete expression below, including its measure name and equals sign. Do not paste the Markdown fence lines.
3. Confirm the expression, then repeat in page order. The later measures call the earlier ones. Keep the exact measure names. If a measure already exists under that name, compare and update its expression rather than creating a second version with a different name.
4. Set counts to Whole number, shares to Percentage with one decimal, and the optional mean to Decimal number with two decimals. Format the numeric measure through its properties rather than converting the expression to display text.
5. Test the measures using cards or a simple table. Follow [the expected counts and selections](survey_validation.md), then hide Survey Response Included from the ordinary field list. Keep it in the model because the other measures need it.

Using factSurvey as the measures' home table keeps them together for maintenance; it does not restrict them to calculating only factSurvey rows. No DAX calculated column or calculated table is required. The optional mean and code-5 summaries can remain unused in management pages without being deleted.

| Measure family | Business purpose |
| --- | --- |
| Response counts | Count the submitted records matching the selected group |
| Domain and Support counts/shares | Count responses choosing each option, allowing choices to overlap |
| Confidence counts and completeness | Separate valid, missing and unrecognised answers |
| Confidence distribution and favourable share | Show the agreement answers to each statement and the share Agree/Strongly agree |
| Tool ratings | Describe recorded codes without assuming what their scale means |
| Interest | Keep Yes, No and conditional commission interest distinct |

## Required model and columns

Use dimension fields for statement, answer, tool, business-domain and support-category axes. The expressions expect these names and states:

| Object | Required fields or states |
| --- | --- |
| `factSurvey` | ResponseID; response-level demographic and categorical fields |
| `factSurveyConfidence` | ResponseID, QuestionID, Answer, Score; AnswerStatus = Valid, Missing or Unmapped |
| `dimSurveyConfidenceQuestion` | QuestionID, QuestionText, ShortLabel, SortOrder; IDs C01 to C06 |
| `dimSurveyLikert` | Score, ResponseLabel, SortOrder |
| `factSurveyToolRating` | ResponseID, ToolID, Rating; RatingStatus = Valid, Missing or Invalid |
| `dimSurveyTool` | ToolID, ToolName, SortOrder; IDs T01 to T05 |
| `dimSurveyRating` | Rating, RatingLabel and SortOrder; neutral codes 1 to 5 |
| `bridgeSurveyDomain` | ResponseID, Domain |
| `dimSurveyDomain` | Domain |
| `bridgeSurveySupport` | ResponseID, Support |
| `dimSurveySupport` | Support |

Keep every relationship single-direction. `factSurvey[ResponseID]` filters both answer facts and both response-option bridges. Each option dimension filters its own bridge. These relationships alone do not propagate an option selection backwards into `factSurvey`. The helper below explicitly applies the selected option cohort to every survey measure.

Return zero for an empty count and BLANK for a ratio with no denominator. Keep measures numeric and use model formats: whole number for counts, percentage with one decimal for shares, and two decimals for the optional mean score. No additional calculated column, calculated table or bidirectional relationship is required by this measure layer.

## Shared response-cohort helper

Create this measure first. Hide it from the report field list after creating and testing the other measures.

```dax
Survey Response Included =
VAR HasOneResponse = HASONEVALUE(factSurvey[ResponseID])
VAR UseDomain = ISFILTERED(dimSurveyDomain)
VAR UseSupport = ISFILTERED(dimSurveySupport)
VAR DomainMatches =
    NOT UseDomain
        || CALCULATE(COUNTROWS(bridgeSurveyDomain)) > 0
VAR SupportMatches =
    NOT UseSupport
        || CALCULATE(COUNTROWS(bridgeSurveySupport)) > 0
RETURN
IF(
    HasOneResponse,
    IF(DomainMatches && SupportMatches, 1, 0),
    0
)
```

This is an internal inclusion check: for each response, test whether its choices match the selected Domain and Support options. Return 1 to include that response and 0 to exclude it. The other measures repeat the check across visible response IDs. Do not place this helper on a management card.

In the DAX, evaluating the measure inside the response iterator applies that response's ID as a filter. Each bridge count then belongs to that response and the current option selection. The single-response guard prevents an entire group from being mistaken for one response.

With no domain filter, a missing domain answer does not exclude a response. With an active domain selection, include responses selecting at least one chosen domain. Apply the same rule to support choices. Choices within one option dimension use OR; simultaneous domain and support filters use AND. Grade, cost centre and other response-level filters remain in force. A domain or support bar uses the same rule as its corresponding slicer.

Every raw count or mean below builds `Cohort`, the list of response IDs included by the current selections. `KEEPFILTERS` restricts the calculation to those IDs while retaining its other intended filters. Keep this pattern when adding measures. An automatic count on an answer table would respond to Grade but ignore the extra Domain/Support inclusion check.

## Response counts and multi-select options

```dax
Survey Responses =
COALESCE(
    SUMX(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included]
    ),
    0
)
```

Count included submissions after the query validates unique, nonblank IDs. Grade, cost centre and the other response-level categories filter the visible IDs directly. Domain and support selections are applied by the helper.

```dax
Survey Domain Responses =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        DISTINCTCOUNT(bridgeSurveyDomain[ResponseID]),
        KEEPFILTERS(Cohort)
    ),
    0
)
```

```dax
Survey Support Responses =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        DISTINCTCOUNT(bridgeSurveySupport[ResponseID]),
        KEEPFILTERS(Cohort)
    ),
    0
)
```

Count each response once for the current option set. A response selecting three domains contributes to three individual bars, while the grand total counts that response once. At an unfiltered card, these bridge-based measures count responses with at least one recorded option; a blank multi-select answer has no bridge row. Never sum the category bars to obtain the survey-response total.

```dax
Survey Domain Share % =
DIVIDE(
    [Survey Domain Responses],
    CALCULATE(
        [Survey Responses],
        REMOVEFILTERS(dimSurveyDomain)
    )
)
```

```dax
Survey Support Share % =
DIVIDE(
    [Survey Support Responses],
    CALCULATE(
        [Survey Responses],
        REMOVEFILTERS(dimSurveySupport)
    )
)
```

The denominator removes both the current option-axis category and any slicer selection on that same option dimension. It retains Grade, cost centre and the other option dimension's cohort. Label these as Share of responses in the comparison population, rather than Share of selected options. A response with no answer to the question remains in that denominator unless another filter excludes it. Multi-select shares can sum above 100% because responses overlap between options.

For example, two Domain A choices among four responses give 50%. If three of the same four responses chose Domain B, its share is 75%; together they total 125% because a response can choose both. Selecting Domain A makes Survey Responses equal two, but the Domain A comparison share stays 50%: that share deliberately compares with the group before the Domain selection. The Support share uses the equivalent rule for Support.

For a domain chart, the comparison population is the selected demographic/support cohort across all domains. For a support chart it is the selected demographic/domain cohort across all support choices. This explicit denominator avoids treating a multi-choice question as mutually exclusive slices of a pie.

## Confidence answer counts and completeness

```dax
Confidence Answer Slots =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        COUNTROWS(factSurveyConfidence),
        KEEPFILTERS(Cohort),
        REMOVEFILTERS(dimSurveyLikert),
        REMOVEFILTERS(factSurveyConfidence[AnswerStatus])
    ),
    0
)
```

```dax
Confidence Valid Answers =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        COUNTROWS(factSurveyConfidence),
        KEEPFILTERS(Cohort),
        KEEPFILTERS(factSurveyConfidence[AnswerStatus] = "Valid")
    ),
    0
)
```

```dax
Confidence Valid Answers All Ratings =
CALCULATE(
    [Confidence Valid Answers],
    REMOVEFILTERS(dimSurveyLikert)
)
```

```dax
Confidence Missing Answers =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        COUNTROWS(factSurveyConfidence),
        KEEPFILTERS(Cohort),
        REMOVEFILTERS(dimSurveyLikert),
        factSurveyConfidence[AnswerStatus] = "Missing"
    ),
    0
)
```

```dax
Confidence Unmapped Answers =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        COUNTROWS(factSurveyConfidence),
        KEEPFILTERS(Cohort),
        REMOVEFILTERS(dimSurveyLikert),
        factSurveyConfidence[AnswerStatus] = "Unmapped"
    ),
    0
)
```

```dax
Confidence Answer Coverage % =
DIVIDE(
    [Confidence Valid Answers All Ratings],
    [Confidence Answer Slots]
)
```

A slot is one response's opportunity to answer one statement. N responses create 6 x N slots for all six statements, or N slots for one statement. Four invented responses therefore create 24 slots across the block. Missing answers remain in that count.

For example, if four responses contain three recognised answers to one statement, answer coverage is 3/4 = 75%. It describes completeness. It does not indicate whether those answers agree with the statement.

The slots measure removes the Likert category and answer-status filters while preserving question and cohort filters. Missing and unmapped counts likewise ignore a Likert colour legend. With no direct fact-answer filter, Valid Answers All Ratings + Missing Answers + Unmapped Answers must equal Answer Slots. Answer Coverage measures valid mapped answers divided by those opportunities; it is not the proportion of invited people responding.

Use the Likert dimension for the distribution legend. Do not use direct fact Score, Answer or AnswerStatus columns as management-page slicers; their local filters are not the response-cohort controls. Missing and unmapped records belong in the quality checks rather than a fabricated zero score.

## Statement response distribution

```dax
Confidence Response % =
DIVIDE(
    [Confidence Valid Answers],
    [Confidence Valid Answers All Ratings]
)
```

Use statement ShortLabel on the axis and Likert ResponseLabel on the legend. Sort the answer dimension by SortOrder and statements by their SortOrder. The numerator responds to the legend category. The denominator removes only that Likert category and retains the current question and response cohort, so a statement's five segments sum to 100% when it has valid answers. Use Valid Answers All Ratings in the tooltip for the statement's base n. An unanswered statement has a BLANK percentage rather than an invented distribution.

Across several statements without a question axis, this describes submission-statement answers. It is not the percentage of unique people in one confidence category. One submission can give different answers to different statements.

## Agree or strongly agree

```dax
Confidence Favourable Answers =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        COUNTROWS(factSurveyConfidence),
        KEEPFILTERS(Cohort),
        REMOVEFILTERS(dimSurveyLikert),
        factSurveyConfidence[AnswerStatus] = "Valid",
        factSurveyConfidence[Score] >= 4
    ),
    0
)
```

```dax
Confidence Favourable % =
DIVIDE(
    [Confidence Favourable Answers],
    [Confidence Valid Answers All Ratings]
)
```

Count codes 4 and 5 using the defined statement mapping. Neutral remains in the valid-answer denominator. Missing and unmapped answers are excluded from both parts; show Answer Coverage when incomplete. The favourable measures ignore the Likert legend deliberately. Use them in a separate statement chart or KPI rather than adding them as another segment of the Likert stack.

If two of three valid answers are Agree or Strongly agree, the favourable share is 2/3 = 66.7%. A fourth response with a missing answer reduces completeness but does not become disagreement. Report the valid-answer count alongside the percentage so that its size is clear.

For the Work confidence card, add visual filter `dimSurveyConfidenceQuestion[QuestionID] = C01`. For the Output judgement card use C05. The same measure then uses the correct statement-specific valid-answer denominator. Use the real visual labels Agree or strongly agree: work confidence and Agree or strongly agree: output judgement. Do not label either as observed AI skill.

For one selected statement, the percentage describes valid submissions agreeing with that statement. Across several statements, it weights each valid answer equally. Do not label the latter as the share of people who are confident or use it to assign maturity categories.

```dax
Confidence Mean Agreement Score =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
CALCULATE(
    AVERAGE(factSurveyConfidence[Score]),
    KEEPFILTERS(Cohort),
    REMOVEFILTERS(dimSurveyLikert),
    factSurveyConfidence[AnswerStatus] = "Valid"
)
```

This optional descriptive score averages valid 1-to-5 answer codes. It treats the coded steps as equally spaced for the summary. Keep the distribution as primary evidence and label the number Mean agreement score. Across several statements, it is a mean of answered items, not a validated multi-item scale or an objective maturity score. Do not convert it to a percentage of capability.

## Neutral tool-rating summaries

```dax
Tool Valid Ratings =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        COUNTROWS(factSurveyToolRating),
        KEEPFILTERS(Cohort),
        KEEPFILTERS(factSurveyToolRating[RatingStatus] = "Valid")
    ),
    0
)
```

```dax
Tool Valid Ratings All Ratings =
CALCULATE(
    [Tool Valid Ratings],
    REMOVEFILTERS(dimSurveyRating)
)
```

```dax
Tool Rating 5 Count =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        COUNTROWS(factSurveyToolRating),
        KEEPFILTERS(Cohort),
        REMOVEFILTERS(dimSurveyRating),
        factSurveyToolRating[RatingStatus] = "Valid",
        factSurveyToolRating[Rating] = 5
    ),
    0
)
```

```dax
Tool Rating 5 Share % =
DIVIDE(
    [Tool Rating 5 Count],
    [Tool Valid Ratings All Ratings]
)
```

```dax
Tool Rating Distribution % =
DIVIDE(
    [Tool Valid Ratings],
    [Tool Valid Ratings All Ratings]
)
```

```dax
Tool Missing Ratings =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        COUNTROWS(factSurveyToolRating),
        KEEPFILTERS(Cohort),
        REMOVEFILTERS(dimSurveyRating),
        factSurveyToolRating[RatingStatus] = "Missing"
    ),
    0
)
```

```dax
Tool Invalid Ratings =
VAR Cohort =
    FILTER(
        VALUES(factSurvey[ResponseID]),
        [Survey Response Included] = 1
    )
RETURN
COALESCE(
    CALCULATE(
        COUNTROWS(factSurveyToolRating),
        KEEPFILTERS(Cohort),
        REMOVEFILTERS(dimSurveyRating),
        factSurveyToolRating[RatingStatus] = "Invalid"
    ),
    0
)
```

Use ToolName on the axis. Rating 5 Count counts answers with code 5 without assuming what it means. Rating 5 Share divides by the valid ratings for that tool, allowing comparison when completion differs. For the complete distribution, use `dimSurveyRating[RatingLabel]` on the legend, sorted by SortOrder, and Tool Rating Distribution %. Tool Valid Ratings is the segment count; Tool Valid Ratings All Ratings is the tool's base n. Missing and invalid entries remain separate quality counts. Preserve RatingRaw for tracing a rejected value. Use the rating dimension for the legend rather than a direct fact-Rating field filter.

Do not call code 5 high capability, expert proficiency or frequent usage until the source question and endpoints establish that meaning. Do not compare tool ratings with Likert agreement codes as if both measured the same construct. Across several tools, totals count submission-tool ratings, not unique users. No tool mean, adoption rate or normalised proficiency score is proposed while its scale semantics are unknown.

## Categorical responses and cross-tabs

Use Survey Responses with the exact response-level categories as axes, rows, columns or slicers. This supports Grade responses, Cost centre responses, client capability by Grade, formal learning by Grade and the two interest questions without inventing new classifications. The cohort helper continues to apply domain/support selections to those counts.

For a Grade-by-ClientCapability count matrix, use `factSurvey[Grade]` on rows, `factSurvey[ClientCapability]` on columns and Survey Responses as Values. For work-confidence by exposure, use `factSurvey[ClientAIExposure]` on the axis, apply confidence QuestionID C01 and use Likert ResponseLabel on the legend with Confidence Valid Answers as Values. The valid-answer base then belongs to that statement within each exposure group.

The example interest labels are Yes, No and Depends on the role for CommissionInterest, and Yes/No for TrainingInterest. Match these definitions to the source before using the targeted measures below. Count other questions by their original categories until their response options have been defined; do not assume every question is Yes/No.

## Defined commission and training interest

Create these after Survey Responses. They reuse its complete domain/support and response-profile cohort handling. The interest filters belong inside CALCULATE so Survey Responses builds its cohort after the intended question context has been set.

```dax
Commission Valid Responses =
CALCULATE(
    [Survey Responses],
    REMOVEFILTERS(factSurvey[CommissionInterest], factSurvey[CommissionInterestOrder]),
    factSurvey[CommissionInterest] IN {"Yes", "No", "Depends on the role"}
)
```

```dax
Commission Yes Responses =
CALCULATE(
    [Survey Responses],
    REMOVEFILTERS(factSurvey[CommissionInterest], factSurvey[CommissionInterestOrder]),
    factSurvey[CommissionInterest] = "Yes"
)
```

```dax
Commission Yes % =
DIVIDE([Commission Yes Responses], [Commission Valid Responses])
```

```dax
Commission Conditional Responses =
CALCULATE(
    [Survey Responses],
    REMOVEFILTERS(factSurvey[CommissionInterest], factSurvey[CommissionInterestOrder]),
    factSurvey[CommissionInterest] = "Depends on the role"
)
```

```dax
Commission Conditional % =
DIVIDE([Commission Conditional Responses], [Commission Valid Responses])
```

```dax
Training Interest Valid Responses =
CALCULATE(
    [Survey Responses],
    REMOVEFILTERS(factSurvey[TrainingInterest], factSurvey[TrainingInterestOrder]),
    factSurvey[TrainingInterest] IN {"Yes", "No"}
)
```

```dax
Training Yes Responses =
CALCULATE(
    [Survey Responses],
    REMOVEFILTERS(factSurvey[TrainingInterest], factSurvey[TrainingInterestOrder]),
    factSurvey[TrainingInterest] = "Yes"
)
```

```dax
Training Yes % =
DIVIDE([Training Yes Responses], [Training Interest Valid Responses])
```

Commission valid responses are the three defined source options. Training valid responses are the two defined options. Exclude the no-answer label and any future unrecognised label from these denominators, rather than treating either as No. Counts return zero through Survey Responses, and a percentage with no valid answers is BLANK. Show the relevant valid-response count in card tooltips.

These are stable comparison cards: all commission measures deliberately clear CommissionInterest and CommissionInterestOrder before applying their own option. Clear both fields because a sorted axis can include the order column in its filter context. Clearing only the visible label could leave a conflicting order restriction. Training measures clear TrainingInterest and TrainingInterestOrder in the same way. This removes both the own-question slicer and its sorted chart-axis context. Grade, cost centre, domain, support and the other interest question remain in force. Therefore a commission card can compare the full commission-answer distribution within a training-interest cohort, while a training card can compare the full training distribution within a commission-interest cohort. State that scope in the tooltip. Use Survey Responses, rather than these fixed-option measures, for charts or matrices whose axis is the interest question itself.

In plain terms, a Commission Yes card answers how many of the selected group's valid commission answers are Yes. A selection on the commission question itself does not redefine that comparison. A selection on grade, Domain, Support or the training question still narrows the group. Use Survey Responses to count each answer category in a table; use the named Yes/Conditional measures for their fixed comparisons.

Keep Yes and Depends on the role separate. The conditional category is not an unconditional commitment to an AI commission. No combined interested percentage or employee-wide participation rate is introduced.

The example category fields use these labels:

| Field | Defined options |
| --- | --- |
| ClientCapability | Awareness Only/limited hands-on experience; Comfortable user of AI and digital tools; Experienced practitioner applying AI in delivery; Specialist/subject matter expert |
| ClientAIExposure | None; Limited Exposure; Some involvement; Significant Exposure |
| FormalLearning | None; Introductory; Intermediate; Advanced |

Use explicit source/order metadata for those categorical axes. They are self-reported descriptions and retain their own meanings. They do not supply the missing formula for the workbook's Maturity Category or Confidence Rating.

## Totals, interaction and acceptance

Use Filter interactions from the four cohort slicers to the management visuals. For the initial [two-page build](survey_report_build.md), set chart-to-chart interactions to None and change the cohort through the visible slicers. The domain/support dimensions are single-direction bridge filters, so every displayed metric must use the cohort-aware expressions above. Avoid naked COUNTROWS, SUM or AVERAGE values in visual field wells. Test any later option-chart filtering explicitly before enabling it.

Check one statement, all statements, one tool, all tools, one Grade, multiple domain choices and overlapping support choices. Choices within a question use OR; Domain and Support together use AND. Confirm Grade and cost centre continue to intersect those selections. Check a response missing one multi-select answer remains in the population when no filter is active on that dimension and is excluded when selecting an actual option it did not choose.

Category sums can exceed survey responses for multi-select questions. Likert shares per statement must sum to 100% over valid answers. A zero-response cohort gives zero counts and BLANK shares/means. Do not sum distinct option counts or averages to create a total.

Define any maturity, grouped confidence or learning-category calculation before adding it. Do not substitute arbitrary thresholds, percentile splits or Grade-based labels. Define the terminology question wording and scales before adding those measures.

Microsoft documents context modification and measure context transition in [CALCULATE](https://learn.microsoft.com/en-us/dax/calculate-function-dax), scoped removal in [REMOVEFILTERS](https://learn.microsoft.com/en-us/dax/removefilters-function-dax), and undefined ratios in [DIVIDE](https://learn.microsoft.com/en-us/dax/divide-function-dax). These establish function behaviour; they do not validate the survey questions or execute this proposal.
