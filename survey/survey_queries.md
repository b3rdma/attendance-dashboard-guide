# Survey Power Query definitions

[Survey guide](../survey_dashboard_guide.md) · [Model and relationships](survey_model.md) · [Validation and source checks](survey_validation.md) · [Glossary](../guide/dashboard_glossary.md)

## Scope and installation order

Power Query contains the repeatable preparation steps that run when the dashboard refreshes. Create the named definitions below in order. Most produce a table; the two functions are reusable preparation instructions, and capabilityFolder supplies a source setting.

For a new build, create the [basePath site parameter](../dashboard_parameters/attendance_parameter_site.md) first and supply the intended SharePoint site address. Then create stgSurveyRaw directly at step 3 below. If the current PBIX already contains the original raw extract named factSurvey, rename that raw extract to stgSurveyRaw before creating the new analytical factSurvey. Reuse an existing basePath when both datasets use the same site. Keep attendance queries and relationships unchanged.

This example reads one workbook containing an Excel Table named tblRawData. It represents one anonymous survey snapshot. The file-count check requires exactly one selected workbook; it does not choose the latest file. IDs identify responses within this snapshot. Use the separate multi-wave design before appending another survey.

The code uses public example headings. Map these names to the exact headings in the intended export before loading real data. Update RenamePairs for profile questions and SourceColumn in the question/tool tables. Keep the output names and stable IDs used by the measures. The analytical build does not require narrative-description fields; raw staging retains every source column.

## Create each definition

1. Open the report in Power BI Desktop and open Transform data to enter Power Query Editor.
2. Create a Blank query. Open its Advanced Editor, replace the starter expression with the complete code block and select Done. Do not paste the Markdown fence lines.
3. Give the query the exact name shown in its heading. Do not create two objects with the same name or add a second Source step around the supplied code.
4. Set Enable load using the query's stated setting. Off means its rows are not loaded as a separate reporting table; the preparation step still runs when another query needs it. Leave the two helper functions unloaded.
5. Repeat in the numbered order so each dependency exists before a later query refers to it. Check the preview and resolve an error before proceeding.
6. Select Close & Apply after creating all definitions. Confirm the eleven loaded tables listed at the end of this page, then create [the model relationships](survey_model.md).

For an existing capabilityFolder parameter with the stated value, keep the existing object. Change source values through the parameter controls when available. Query names, column names and stable question/tool IDs are calculation dependencies; change them only with the corresponding references.

## Query index

| Order | Query | Enable load | Purpose |
| --- | --- | --- | --- |
| 1 | `capabilityFolder` | Parameter | Folder parameter |
| 2 | `src_FilesCapability` | Off | List the Excel files selected from SharePoint |
| 3 | `stgSurveyRaw` | Off | Read every source column from the one selected workbook |
| 4 | `fxSurveyText` | Function; off | Remove surrounding spaces and recognise unanswered text |
| 5 | `dimSurveyConfidenceQuestion` | On | Store the six confidence question names and display labels |
| 6 | `dimSurveyLikert` | On | Store the five agreement labels and their defined codes |
| 7 | `dimSurveyTool` | On | Store the five tool names and display order |
| 8 | `dimSurveyRating` | On | Store neutral labels for numerical ratings 1–5 |
| 9 | `stgSurveyPrepared` | Off | Select 26 required fields, shorten names and check response IDs |
| 10 | `factSurvey` | On | Store one response profile per row |
| 11 | `factSurveyConfidence` | On | Store one row for each response and confidence question |
| 12 | `factSurveyToolRating` | On | Store one row for each response and tool question |
| 13 | `fxSurveyMultiSelect` | Function; off | Separate a list of chosen options without duplicate choices |
| 14 | `bridgeSurveyDomain` | On | Match response IDs to their chosen business domains |
| 15 | `dimSurveyDomain` | On | Store the distinct business-domain labels |
| 16 | `bridgeSurveySupport` | On | Match response IDs to their chosen support options |
| 17 | `dimSurveySupport` | On | Store the distinct support-option labels |

## capabilityFolder

Set the folder token to the intended survey location. Reuse basePath when both models read the same site. Inspect the resulting file list; parameter metadata does not validate a folder.

**Enable load:** Parameter.

```powerquery
// Match the existing folder-parameter convention; retain the controlled folder token.
"04_Capability" meta [IsParameterQuery = true, IsParameterQueryRequired = false, Type = type any]
```

## src_FilesCapability

Retain the supplied site/folder/extension selection. This remains a substring folder match. Inspect the selected inventory when changing the source.

**Enable load:** Off.

```powerquery
let
    // Reuse the established SharePoint site and controlled folder selection.
    Source = SharePoint.Files(basePath, [ApiVersion = 15]),
    Filtered = Table.SelectRows(
        Source,
        each Text.EndsWith([Extension], ".xlsx")
            and Text.Contains([Folder Path], capabilityFolder)
    )
in
    Filtered
```

## stgSurveyRaw

For a new build, create this query as stgSurveyRaw. For the existing raw factSurvey extract, rename that query to stgSurveyRaw before creating the analytical factSurvey below. This definition checks that exactly one workbook was selected and reads tblRawData. If several legitimate workbooks exist, filter by the intended filename in src_FilesCapability before this step. The named Excel Table supplies its own headings.

**Enable load:** Off.

```powerquery
let
    // The supplied example needs this comma before the next binding.
    Source = src_FilesCapability,
    FileCount = Table.RowCount(Source),
    // One maintained workbook is the initial source contract. Do not select an arbitrary first file.
    FileContent =
        if FileCount = 1 then Source[Content]{0}
        else error Error.Record(
            "SurveyWorkbookSelection",
            "Select exactly one current survey workbook in src_FilesCapability.",
            [SelectedFiles = FileCount]
        ),
    // Read the named Excel Table, not a worksheet or the workbook's pivot outputs.
    Workbook = Excel.Workbook(FileContent, null, true),
    RawData = Workbook{[Item = "tblRawData", Kind = "Table"]}[Data]
in
    RawData
```

## fxSurveyText

Use one small text normaliser for profile fields, confidence labels, tool-rating source values and option lists. Preserve non-blank wording; do not infer categories.

**Enable load:** Function; off.

```powerquery
// Trim source text and represent an unanswered value as null.
(value as any) as nullable text =>
    if value = null then null
    else
        let TextValue = Text.Trim(Text.From(value, "en-US"))
        in if TextValue = "" then null else TextValue
```

## dimSurveyConfidenceQuestion

Define the six example questions once. SourceColumn is the exact raw heading; edit it here if the actual Excel heading differs. Keep stable QuestionID values while improving ShortLabel.

**Enable load:** On.

```powerquery
#table(
    type table [QuestionID = text, SourceColumn = text, QuestionText = text, ShortLabel = text, SortOrder = Int64.Type],
    {
        {"C01", "I feel confident using AI tools to support my work tasks", "I feel confident using AI tools to support my work tasks", "Work-task confidence", 1},
        {"C02", "I feel confident using AI tools in my personal life", "I feel confident using AI tools in my personal life", "Personal-life confidence", 2},
        {"C03", "I understand the strengths and limitations of AI tools", "I understand the strengths and limitations of AI tools", "Strengths and limitations", 3},
        {"C04", "I am comfortable with new AI tools or features", "I am comfortable with new AI tools or features", "Comfort with new tools", 4},
        {"C05", "I can judge when AI outputs need to be checked, validated, or adjusted", "I can judge when AI outputs need to be checked, validated, or adjusted", "Checking AI outputs", 5},
        {"C06", "I feel confident explaining or recommending AI tools to others", "I feel confident explaining or recommending AI tools to others", "Explaining and recommending", 6}
    }
)
```

## dimSurveyLikert

Store the five agreement answers in order from Strongly disagree to Strongly agree. Higher codes mean stronger agreement with the statement. These codes support statement-level counts; they do not define an overall maturity score. MatchKey allows the answer mapping to ignore differences in capitalisation.

**Enable load:** On.

```powerquery
#table(
    type table [Score = Int64.Type, ResponseLabel = text, MatchKey = text, SortOrder = Int64.Type],
    {
        {1, "Strongly disagree", "strongly disagree", 1},
        {2, "Disagree", "disagree", 2},
        {3, "Neutral", "neutral", 3},
        {4, "Agree", "agree", 4},
        {5, "Strongly agree", "strongly agree", 5}
    }
)
```

## dimSurveyTool

Preserve the source label Co-pilot for traceability. ToolName is a display name; no rating endpoint meaning is inferred.

**Enable load:** On.

```powerquery
#table(
    type table [ToolID = text, SourceColumn = text, ToolName = text, SortOrder = Int64.Type],
    {
        {"T01", "Co-pilot", "Co-pilot", 1},
        {"T02", "ChatGPT", "ChatGPT", 2},
        {"T03", "Gemini", "Gemini", 3},
        {"T04", "Grammarly", "Grammarly", 4},
        {"T05", "Claude", "Claude", 5}
    }
)
```

## dimSurveyRating

Provide neutral 1–5 legend labels for tool ratings. Do not reuse agreement labels until the original tool question and scale have been defined.

**Enable load:** On.

```powerquery
#table(
    type table [Rating = Int64.Type, RatingLabel = text, SortOrder = Int64.Type],
    {
        {1, "1", 1}, {2, "2", 2}, {3, "3", 3}, {4, "4", 4}, {5, "5", 5}
    }
)
```

## stgSurveyPrepared

Select 26 fields: fifteen identity/profile/option fields, six confidence statements and five tool ratings. Preserve other source columns in unloaded stgSurveyRaw. Match the example source headings to the actual export in the mapping below. Require positive whole-number response IDs that are unique within the survey; the numbers do not need to be consecutive.

**Enable load:** Off.

```powerquery
let
    Source = stgSurveyRaw,
    // Only required analytical headings are referenced. The truncated narrative heading is not needed.
    RenamePairs = {
        {"ID", "ResponseID"},
        {"What is your cost centre?", "CostCentre"},
        {"What is your grade?", "Grade"},
        {"Which business domain(s) do you primarily work in? (Select all that apply)", "DomainSelections"},
        {"What type of work do you primarily deliver?", "BusinessWorkType"},
        {"What is your current role level/grade that you are working at within your client work?", "ClientRoleLevel"},
        {"How would you currently rate your AI or digital capability in a client-facing context? (Select one)", "ClientCapability"},
        {"How much exposure to or involvement with AI have you had in your client work?", "ClientAIExposure"},
        {"Have you worked on any digital or AI-focused projects in your organisation?", "CurrentAICommission"},
        {"Outside explicitly digital commissions, have you used AI tools to improve productivity on non-digital projects?", "NonDigitalProductivityUse"},
        {"Before joining your current organisation, did you work on any digital or AI-focused projects or programmes?", "PriorAIProject"},
        {"How would you describe your current level of formal AI learning?", "FormalLearning"},
        {"If the opportunity to work on an AI-focused commission arose, would you be interested?", "CommissionInterest"},
        {"Would you be interested in including AI or digital training in your professional development plan?", "TrainingInterest"},
        {"What type of support or training would be most useful to you?", "SupportSelections"}
    },
    RequiredColumns = List.Transform(RenamePairs, each _{0})
        & dimSurveyConfidenceQuestion[SourceColumn]
        & dimSurveyTool[SourceColumn],
    MissingColumns = List.Difference(RequiredColumns, Table.ColumnNames(Source)),
    Checked =
        if List.IsEmpty(MissingColumns) then Source
        else error Error.Record(
            "SurveyColumnsMissing",
            "Match the required source headings to the current tblRawData columns.",
            [Columns = MissingColumns]
        ),
    Selected = Table.SelectColumns(Checked, RequiredColumns),
    Renamed = Table.RenameColumns(Selected, RenamePairs),
    // ResponseID is a positive integer within this snapshot, not an employee identity.
    ReadID = (value as any) as number =>
        let
            TextID = fxSurveyText(value),
            Parsed =
                if TextID = null or TextID = "" then
                    error Error.Record("InvalidSurveyID", "Response ID is required.", [Value = value])
                else if Text.Select(TextID, {"0".."9"}) <> TextID then
                    error Error.Record("InvalidSurveyID", "Response ID must be a positive whole number.", [Value = value])
                else Int64.From(TextID, "en-US")
        in
            if Parsed > 0 then Parsed
            else error Error.Record("InvalidSurveyID", "Response ID must be positive.", [Value = value]),
    IDTyped = Table.TransformColumns(Renamed, {{"ResponseID", ReadID, Int64.Type}}),
    // Keep numerical tool inputs unaltered here; their own fact query validates the scale.
    TextColumns = List.RemoveItems(Table.ColumnNames(IDTyped), {"ResponseID"} & dimSurveyTool[SourceColumn]),
    Cleaned = Table.TransformColumns(
        IDTyped,
        List.Transform(TextColumns, (ColumnName) => {ColumnName, fxSurveyText, type nullable text})
    ),
    IDs = Cleaned[ResponseID],
    Result =
        if List.Count(List.Distinct(IDs)) = List.Count(IDs) then Cleaned
        else error Error.Record("DuplicateSurveyID", "Response ID must be unique within this snapshot.", null)
in
    Result
```

## factSurvey

Load one row per response with thirteen source fields and five display-order columns. Keep Grade and ClientRoleLevel separate because they describe different contexts. Match source categories to the example option maps before loading. Order columns control display, rather than capability or maturity scores. Email, Name, timestamps, narrative answers and terminology answers are not loaded into this model.

**Enable load:** On.

```powerquery
let
    Source = stgSurveyPrepared,
    Selected = Table.SelectColumns(Source, {
        "ResponseID",
        "CostCentre",
        "Grade",
        "BusinessWorkType",
        "ClientRoleLevel",
        "ClientCapability",
        "ClientAIExposure",
        "CurrentAICommission",
        "NonDigitalProductivityUse",
        "PriorAIProject",
        "FormalLearning",
        "CommissionInterest",
        "TrainingInterest"
    }),
    ProfileColumns = List.RemoveItems(Table.ColumnNames(Selected), {"ResponseID"}),
    // Retain unanswered profiles visibly without assigning a substantive survey category.
    Profiles = Table.TransformColumns(
        Selected,
        List.Transform(ProfileColumns,
            (ColumnName) => {ColumnName, (Value) => if Value = null then "(No answer)" else Value, type text})
    ),
    // Keep confirmed response wording and store its display order separately.
    Orders = {
        [Column = "ClientCapability", Values = {
            "Awareness Only/limited hands-on experience",
            "Comfortable user of AI and digital tools",
            "Experienced practitioner applying AI in delivery",
            "Specialist/subject matter expert"
        }],
        [Column = "ClientAIExposure", Values = {
            "None", "Limited Exposure", "Some involvement", "Significant Exposure"
        }],
        [Column = "FormalLearning", Values = {
            "None", "Introductory", "Intermediate", "Advanced"
        }],
        [Column = "CommissionInterest", Values = {"No", "Depends on the role", "Yes"}],
        [Column = "TrainingInterest", Values = {"No", "Yes"}]
    },
    // New or unanswered labels remain visible, sorted after the known choices.
    Result = List.Accumulate(Orders, Profiles, (State, Mapping) =>
        Table.AddColumn(State, Mapping[Column] & "Order", (Response as record) =>
            let Position = List.PositionOf(Mapping[Values], Record.Field(Response, Mapping[Column]))
            in if Position < 0 then 99 else Position + 1,
            Int64.Type)
    )
in
    Result
```

## factSurveyConfidence

Create one row for each of the six questions for every response, even when an answer is missing. This is an answer slot: a record that the response had an opportunity to answer that question. Keep unrecognised nonblank wording as Unmapped with no score. Map only the five defined agreement labels, after removing surrounding spaces and ignoring capitalisation. Table.Unpivot omits null values; creating the rows explicitly avoids losing unanswered questions from completeness checks.

**Enable load:** On.

```powerquery
let
    Source = stgSurveyPrepared,
    Questions = Table.ToRecords(dimSurveyConfidenceQuestion),
    // Explicitly construct all six slots. A null answer must not disappear during unpivoting.
    Nested = Table.AddColumn(Source, "Answers", (Response as record) =>
        Table.FromRecords(List.Transform(Questions, (Question as record) => [
            QuestionID = Question[QuestionID],
            Answer = Record.Field(Response, Question[SourceColumn])
        ])), type table [QuestionID = text, Answer = nullable text]),
    Slots = Table.ExpandTableColumn(
        Table.SelectColumns(Nested, {"ResponseID", "Answers"}),
        "Answers", {"QuestionID", "Answer"}
    ),
    MatchKeys = Table.AddColumn(Slots, "MatchKey",
        each if [Answer] = null then null else Text.Lower([Answer], "en-US"), type nullable text),
    Matched = Table.NestedJoin(MatchKeys, {"MatchKey"}, dimSurveyLikert, {"MatchKey"}, "Likert", JoinKind.LeftOuter),
    Scored = Table.ExpandTableColumn(Matched, "Likert", {"Score"}, {"Score"}),
    Status = Table.AddColumn(Scored, "AnswerStatus", each
        if [Answer] = null then "Missing"
        else if [Score] = null then "Unmapped"
        else "Valid", type text),
    Result = Table.TransformColumnTypes(
        Table.SelectColumns(Status, {"ResponseID", "QuestionID", "Answer", "Score", "AnswerStatus"}),
        {{"ResponseID", Int64.Type}, {"QuestionID", type text}, {"Answer", type text}, {"Score", Int64.Type}, {"AnswerStatus", type text}}
    )
in
    Result
```

## factSurveyToolRating

Create five slots per response. Accept only numeric values exactly equal to 1, 2, 3, 4 or 5. Preserve missing and invalid values without rounding fractions or treating them as zero. Rating 5 is a numerical category; its substantive meaning remains undefined.

**Enable load:** On.

```powerquery
let
    Source = stgSurveyPrepared,
    Tools = Table.ToRecords(dimSurveyTool),
    Nested = Table.AddColumn(Source, "Ratings", (Response as record) =>
        Table.FromRecords(List.Transform(Tools, (Tool as record) =>
            let
                RawText = fxSurveyText(Record.Field(Response, Tool[SourceColumn])),
                Parsed = if RawText = null then null else try Number.FromText(RawText, "en-US") otherwise null,
                Valid = if Parsed = null then false else List.Contains({1, 2, 3, 4, 5}, Parsed)
            in [
                ToolID = Tool[ToolID],
                RatingRaw = RawText,
                Rating = if Valid then Int64.From(Parsed) else null,
                RatingStatus = if RawText = null then "Missing" else if Valid then "Valid" else "Invalid"
            ])),
        type table [ToolID = text, RatingRaw = nullable text, Rating = nullable number, RatingStatus = text]),
    Flat = Table.ExpandTableColumn(
        Table.SelectColumns(Nested, {"ResponseID", "Ratings"}),
        "Ratings", {"ToolID", "RatingRaw", "Rating", "RatingStatus"}
    ),
    Result = Table.TransformColumnTypes(Flat, {{"ResponseID", Int64.Type}, {"Rating", Int64.Type}})
in
    Result
```

## fxSurveyMultiSelect

Separate each semicolon-delimited question into its own list of response/option pairs. Remove surrounding spaces, empty choices after a trailing semicolon and repeated identical choices in one response. Keep source spelling and capitalisation. For example, `A; B; A;` becomes the two pairs ResponseID/A and ResponseID/B. A blank list contributes no choice pair, while its response remains in factSurvey.

**Enable load:** Function; off.

```powerquery
// Expand one question at a time; never combine the two option lists into a Cartesian product.
(Responses as table, SourceColumn as text, OutputColumn as text) as table =>
let
    Selected = Table.SelectColumns(Responses, {"ResponseID", SourceColumn}),
    Lists = Table.TransformColumns(Selected, {{SourceColumn, (Value) =>
        let
            TextValue = fxSurveyText(Value),
            Parts = if TextValue = null then {} else Text.Split(TextValue, ";"),
            Cleaned = List.Transform(Parts, each Text.Trim(_)),
            NonEmpty = List.Select(Cleaned, each _ <> "")
        in List.Distinct(NonEmpty), type list}}),
    Expanded = Table.ExpandListColumn(Lists, SourceColumn),
    NonEmptyRows = Table.SelectRows(Expanded, each
        Record.Field(_, SourceColumn) <> null and Record.Field(_, SourceColumn) <> ""),
    Renamed = Table.RenameColumns(NonEmptyRows, {{SourceColumn, OutputColumn}}),
    // A repeated token in one response must not count the same choice twice.
    DistinctPairs = Table.Distinct(Renamed, {"ResponseID", OutputColumn}),
    Result = Table.TransformColumnTypes(DistinctPairs, {{"ResponseID", Int64.Type}, {OutputColumn, type text}})
in
    Result
```

## bridgeSurveyDomain

Create one row per response/domain membership, not one row per respondent in the whole model.

**Enable load:** On.

```powerquery
fxSurveyMultiSelect(stgSurveyPrepared, "DomainSelections", "Domain")
```

## dimSurveyDomain

Create the distinct source domain choices. Keep it independent of attendance domains or organisational mappings.

**Enable load:** On.

```powerquery
let
    Values = Table.SelectColumns(bridgeSurveyDomain, {"Domain"}),
    Result = Table.Sort(Table.Distinct(Values), {{"Domain", Order.Ascending}})
in
    Result
```

## bridgeSurveySupport

Create one row per response/support preference. Multiple choices legitimately create overlapping category counts.

**Enable load:** On.

```powerquery
fxSurveyMultiSelect(stgSurveyPrepared, "SupportSelections", "Support")
```

## dimSurveySupport

Create distinct support/training preferences from the supplied question, without inferring preference priority.

**Enable load:** On.

```powerquery
let
    Values = Table.SelectColumns(bridgeSurveySupport, {"Support"}),
    Result = Table.Sort(Table.Distinct(Values), {{"Support", Order.Ascending}})
in
    Result
```

## Preparation and maintenance

The reader checks that one workbook was selected. Preparation shortens source headings, checks response IDs and represents unanswered profile fields consistently. factSurvey adds five display-order columns; these are not scores. Confidence extraction creates six answer slots per response and maps the defined agreement labels. Tool extraction creates five rating slots. The option function splits Domain and Support separately. No DAX calculated columns or calculated tables are needed for this build.

Keep staging queries, helper functions and the file inventory unloaded. Load only the eleven analytical tables: factSurvey, the two answer facts, the two option bridges and the six dimensions. Hide IDs, source-heading metadata, bridge tables and helper fields in report view after configuring relationships. Use the explicit measures in [Survey measures](survey_measures.md) rather than implicit sums or bridge row counts.

Update SourceColumn metadata for a genuinely renamed confidence/tool heading, and update RenamePairs for a profile heading. Do not replace a scale mapping merely because a new answer appears: retain Unmapped or Invalid status until the intended wording is known. Refresh the named raw table when workbook rows grow; pivot pages are not inputs. Retain the SharePoint folder controls. Add terminology scores or maturity categories only after their questions and calculation rules are defined.

Microsoft references: [Excel.Workbook](https://learn.microsoft.com/en-us/powerquery-m/excel-workbook), [Table.Unpivot](https://learn.microsoft.com/en-us/powerquery-m/table-unpivot), [Table.ExpandListColumn](https://learn.microsoft.com/en-us/powerquery-m/table-expandlistcolumn). Test synthetic fixtures and the actual working refresh separately; successful test generation alone is not M or DAX execution.
