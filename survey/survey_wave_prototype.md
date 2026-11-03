# Survey wave extraction prototype

[Extension plan](survey_waves.md) · [Maintainer runbook](survey_wave_runbook.md) · [Current single-snapshot model](survey_model.md)

## Status and purpose

This is a separate executable prototype for testing a metadata-driven survey extension. It does not replace any current query, relationship or measure. Use a disposable Power Query file and synthetic inputs. Create a Blank query named fxSurveyWavePrototype and paste its complete expression below into Advanced Editor. Leave the function unloaded.

The function prepares one registered wave at a time. A separate loader must select its exact workbook, read its named Excel Table and supply the correct Wave record. Combine the returned tables across waves only after the wave registry validates unique WaveIDs and one intended source per wave. The function itself does not connect to SharePoint, read workbook bytes or validate that several calls use different WaveIDs.

## Input contract

| Input | Required fields | Meaning |
| --- | --- | --- |
| Raw | ID, Grade and every SourceColumn configured for this question set | One row per anonymous source submission. Grade is retained only as an illustrative profile field. |
| Wave | WaveID, QuestionSetID | Nonblank text. WaveID must not contain a colon because the response key uses that separator. |
| QuestionMap | QuestionSetID, QuestionVersionID, SourceColumn | One source heading per administered question version. The same heading cannot be assigned twice within a set. |
| QuestionVersions | QuestionVersionID, QuestionID, AnswerType, ScaleID, ComparisonGroupID | One version record. AnswerType is exactly Likert, Rating, SingleChoice, MultiChoice or FreeText. |
| ScaleOptions | ScaleID, AnswerLabel, Score, IsFavourable | Allowed answer labels. Score is nullable number and IsFavourable is nullable logical. Label matching ignores surrounding spaces and case. |

FreeText requires no ScaleID. Every other type requires a registered scale with at least one allowed answer. QuestionVersionID identifies exact wording/type/scale; QuestionID identifies the underlying concept. A nonblank ComparisonGroupID must have one QuestionID, AnswerType and ScaleID across its versions. This mechanical check cannot establish that the wording is substantively comparable; that decision still requires review.

Use separate scales for agreement, retrospective change and neutral tool codes even where they all display 1–5. Supply null scores and null favourable flags when numerical interpretation is not approved. Categorical and free-text questions always return null Score and IsFavourable, regardless of unused numeric metadata.

The prototype retains source ID as SourceResponseID and forms SurveyResponseKey as WaveID + colon + its validated positive whole-number ID. IDs can restart in a later wave. Repeated IDs within one wave are rejected, including equivalent forms such as 1 and text 01.

## Outputs and answer states

| Output | Columns |
| --- | --- |
| Responses | SurveyResponseKey, WaveID, SourceResponseID, Grade |
| Answers | SurveyResponseKey, WaveID, QuestionVersionID, AnswerType, ScaleID, ComparisonGroupID, AnswerRaw, Score, IsFavourable, AnswerStatus |
| Choices | SurveyResponseKey, WaveID, QuestionVersionID, Choice |

Answers contains one slot per submission and configured question. A question absent from the set creates no slot. Use the question-set registry to identify that situation as Not asked; do not fabricate Missing answers for it. A missing required source heading is a structural error, rather than an unanswered question.

| AnswerStatus | Meaning |
| --- | --- |
| Missing | The administered answer is null/empty; a MultiChoice list containing only separators is also Missing. |
| Unmapped | The recorded label is not registered, or at least one MultiChoice token is unknown. |
| Unscored | A Likert/Rating answer is recognised, but its scale has no approved numerical score. |
| Valid | A scored Likert/Rating answer or a recognised categorical/free-text answer. This is a preparation status, not proof of objective ability. |

MultiChoice splits on semicolons, removes empty tokens and repeated choices without counting differences in case twice. Choices contains canonical mapped labels and preserves unknown trimmed tokens for investigation. AnswerRaw retains the trimmed original answer. Do not treat an Unmapped question as a valid completed choice simply because it has some recognised tokens.

## Complete function

```powerquery
// Separate prototype: prepare one registered wave without changing the current model.
(Raw as table, Wave as record, QuestionMap as table,
 QuestionVersions as table, ScaleOptions as table) as record =>
let
    Clean = (Value as any) as nullable text =>
        if Value = null then null
        else let TextValue = Text.Trim(Text.From(Value, "en-US"))
        in if TextValue = "" then null else TextValue,
    ConfigText = (Value as any) as nullable text =>
        if Value = null then null
        else if Value.Is(Value, type text) then Clean(Value)
        else error Error.Record("InvalidSurveyConfiguration", "Configuration labels must be text or null.", null),
    RequireColumns = (Data as table, Names as list, Label as text, Reason as text) as table =>
        let Missing = List.Difference(Names, Table.ColumnNames(Data))
        in if List.IsEmpty(Missing) then Data
        else error Error.Record(Reason, "Required columns are missing.", [Input = Label, Columns = Missing]),
    CleanColumns = (Data as table, Names as list) as table =>
        Table.TransformColumns(Data, List.Transform(Names,
            (Name) => {Name, ConfigText, type nullable text})),
    HasBlank = (Data as table, Names as list) as logical =>
        List.AnyTrue(List.Transform(Names, (Name) => List.Contains(Table.Column(Data, Name), null))),
    HasDuplicates = (Data as table, Names as list) as logical =>
        Table.RowCount(Table.Distinct(Table.SelectColumns(Data, Names))) <> Table.RowCount(Data),

    WaveData =
        if not Record.HasFields(Wave, {"WaveID", "QuestionSetID"}) then
            error Error.Record("InvalidSurveyWave", "WaveID and QuestionSetID are required.", null)
        else if not Value.Is(Wave[WaveID], type text) or not Value.Is(Wave[QuestionSetID], type text) then
            error Error.Record("InvalidSurveyWave", "WaveID and QuestionSetID must be text.", null)
        else [WaveID = Clean(Wave[WaveID]), QuestionSetID = Clean(Wave[QuestionSetID])],
    Map = CleanColumns(
        RequireColumns(QuestionMap, {"QuestionSetID", "QuestionVersionID", "SourceColumn"}, "QuestionMap", "InvalidSurveyConfiguration"),
        {"QuestionSetID", "QuestionVersionID", "SourceColumn"}),
    Versions = CleanColumns(
        RequireColumns(QuestionVersions, {"QuestionVersionID", "QuestionID", "AnswerType", "ScaleID", "ComparisonGroupID"}, "QuestionVersions", "InvalidSurveyConfiguration"),
        {"QuestionVersionID", "QuestionID", "AnswerType", "ScaleID", "ComparisonGroupID"}),
    Options = Table.AddColumn(
        CleanColumns(
            RequireColumns(ScaleOptions, {"ScaleID", "AnswerLabel", "Score", "IsFavourable"}, "ScaleOptions", "InvalidSurveyConfiguration"),
            {"ScaleID", "AnswerLabel"}),
        "MatchKey", each if [AnswerLabel] = null then null else Text.Lower([AnswerLabel], "en-US"), type nullable text),
    SupportedTypes = {"Likert", "Rating", "SingleChoice", "MultiChoice", "FreeText"},
    InvalidTypes = Table.SelectRows(Versions, each not List.Contains(SupportedTypes, [AnswerType])),
    InvalidOptionValues = Table.SelectRows(Options, each
        ([Score] <> null and not Value.Is([Score], type number))
        or ([IsFavourable] <> null and not Value.Is([IsFavourable], type logical))),
    MissingVersions = List.Difference(List.Distinct(Map[QuestionVersionID]), Versions[QuestionVersionID]),
    MissingScales = Table.SelectRows(Versions, each
        if [AnswerType] = "FreeText" then [ScaleID] <> null
        else [ScaleID] = null or not List.Contains(Options[ScaleID], [ScaleID])),
    ComparisonVersions = Table.SelectRows(Versions, each [ComparisonGroupID] <> null),
    ComparisonGroups = Table.Group(ComparisonVersions, {"ComparisonGroupID"}, {
        {"Definitions", each Table.RowCount(Table.Distinct(
            Table.SelectColumns(_, {"QuestionID", "AnswerType", "ScaleID"}))), Int64.Type}
    }),
    SetMap = Table.SelectRows(Map, each [QuestionSetID] = WaveData[QuestionSetID]),
    ConfigurationOK =
        if WaveData[WaveID] = null or WaveData[QuestionSetID] = null then
            error Error.Record("InvalidSurveyWave", "Wave identifiers cannot be blank.", null)
        else if Text.Contains(WaveData[WaveID], ":") then
            error Error.Record("InvalidSurveyWave", "WaveID cannot contain a colon.", null)
        else if HasBlank(Map, {"QuestionSetID", "QuestionVersionID", "SourceColumn"})
            or HasBlank(Versions, {"QuestionVersionID", "QuestionID", "AnswerType"})
            or HasBlank(Options, {"ScaleID", "AnswerLabel"}) then
            error Error.Record("InvalidSurveyConfiguration", "Required configuration labels cannot be blank.", null)
        else if HasDuplicates(Map, {"QuestionSetID", "QuestionVersionID"})
            or HasDuplicates(Map, {"QuestionSetID", "SourceColumn"})
            or HasDuplicates(Versions, {"QuestionVersionID"})
            or HasDuplicates(Options, {"ScaleID", "MatchKey"}) then
            error Error.Record("InvalidSurveyConfiguration", "Configuration keys must be unique.", null)
        else if not Table.IsEmpty(InvalidTypes) or not Table.IsEmpty(InvalidOptionValues)
            or not List.IsEmpty(MissingVersions) or not Table.IsEmpty(MissingScales) then
            error Error.Record("InvalidSurveyConfiguration", "Check answer types, scale references and option value types.", null)
        else if Table.RowCount(Table.SelectRows(ComparisonGroups, each [Definitions] <> 1)) > 0 then
            error Error.Record("InvalidSurveyConfiguration", "A comparison group mixes concepts, types or scales.", null)
        else if Table.IsEmpty(SetMap) then
            error Error.Record("InvalidSurveyConfiguration", "No administered questions are registered for this set.", null)
        else true,
    RequiredRawColumns = List.Distinct({"ID", "Grade"} & SetMap[SourceColumn]),
    CheckedRaw = if ConfigurationOK then
        RequireColumns(Raw, RequiredRawColumns, "Raw", "SurveyColumnsMissing")
        else error Error.Record("InvalidSurveyConfiguration", "Configuration could not be accepted.", null),
    ReadID = (Value as any) as number =>
        let
            TextID = Clean(Value),
            Parsed =
                if TextID = null then
                    error Error.Record("InvalidSurveyID", "A source response ID is required.", null)
                else if Text.Select(TextID, {"0".."9"}) <> TextID then
                    error Error.Record("InvalidSurveyID", "A source response ID must be a positive whole number.", [Value = Value])
                else try Int64.From(TextID, "en-US"),
            Result = if Parsed[HasError] then
                error Error.Record("InvalidSurveyID", "A source response ID is outside the supported integer range.", [Value = Value])
                else Parsed[Value]
        in if Result > 0 then Result
        else error Error.Record("InvalidSurveyID", "A source response ID must be positive.", [Value = Value]),
    Prepared = Table.FromRecords(List.Transform(Table.ToRecords(CheckedRaw), (SourceRow) =>
        let LocalID = ReadID(Record.Field(SourceRow, "ID"))
        in [SurveyResponseKey = WaveData[WaveID] & ":" & Text.From(LocalID, "en-US"),
            WaveID = WaveData[WaveID], SourceResponseID = LocalID,
            Grade = Clean(Record.Field(SourceRow, "Grade")), RawRecord = SourceRow]),
        type table [SurveyResponseKey = text, WaveID = text, SourceResponseID = Int64.Type,
            Grade = nullable text, RawRecord = record]),
    IDs = List.Buffer(Prepared[SourceResponseID]),
    KeysOK = if List.Count(List.Distinct(IDs)) = List.Count(IDs) then true
        else error Error.Record("DuplicateSurveyID", "Source response IDs must be unique within a wave.", [WaveID = WaveData[WaveID]]),
    Questions = List.Transform(Table.ToRecords(SetMap), (Mapping) =>
        Record.Combine({Mapping, Table.SelectRows(Versions,
            each [QuestionVersionID] = Mapping[QuestionVersionID]){0}})),
    ReadAnswer = (Response as record, Question as record) as record =>
        let
            RawText = Clean(Record.Field(Response[RawRecord], Question[SourceColumn])),
            Kind = Question[AnswerType],
            ScaleRows = Table.SelectRows(Options, each [ScaleID] = Question[ScaleID]),
            Found = if RawText = null then Table.FirstN(ScaleRows, 0)
                else Table.SelectRows(ScaleRows, each [MatchKey] = Text.Lower(RawText, "en-US")),
            Recognised = not Table.IsEmpty(Found),
            TokenTexts = if Kind <> "MultiChoice" or RawText = null then {}
                else List.Select(List.Transform(Text.Split(RawText, ";"), each Clean(_)), each _ <> null),
            Tokens = List.Accumulate(TokenTexts, {}, (Kept, Token) =>
                if List.Contains(List.Transform(Kept, each Text.Lower(_, "en-US")), Text.Lower(Token, "en-US"))
                then Kept else Kept & {Token}),
            TokenMatches = List.Transform(Tokens, (Token) =>
                let Match = Table.SelectRows(ScaleRows, each [MatchKey] = Text.Lower(Token, "en-US"))
                in [Known = not Table.IsEmpty(Match),
                    Label = if Table.IsEmpty(Match) then Token else Match{0}[AnswerLabel]]),
            Missing = RawText = null or (Kind = "MultiChoice" and List.IsEmpty(Tokens)),
            ScoredType = List.Contains({"Likert", "Rating"}, Kind),
            ScoreValue = if ScoredType and Recognised then Found{0}[Score] else null,
            Status =
                if Missing then "Missing"
                else if Kind = "FreeText" then "Valid"
                else if Kind = "MultiChoice" then
                    if List.AllTrue(List.Transform(TokenMatches, each [Known])) then "Valid" else "Unmapped"
                else if not Recognised then "Unmapped"
                else if ScoredType and ScoreValue = null then "Unscored"
                else "Valid",
            Favourable = if ScoredType and Recognised and ScoreValue <> null then Found{0}[IsFavourable] else null,
            Answer = [SurveyResponseKey = Response[SurveyResponseKey], WaveID = Response[WaveID],
                QuestionVersionID = Question[QuestionVersionID], AnswerType = Kind,
                ScaleID = Question[ScaleID], ComparisonGroupID = Question[ComparisonGroupID],
                AnswerRaw = RawText, Score = ScoreValue, IsFavourable = Favourable, AnswerStatus = Status]
        in [Answer = Answer, ChoiceValues = List.Transform(TokenMatches, each [Label])],
    Extracted = List.Combine(List.Transform(Table.ToRecords(Prepared), (Response) =>
        List.Transform(Questions, (Question) => ReadAnswer(Response, Question)))),
    Responses = Table.RemoveColumns(Prepared, {"RawRecord"}),
    Answers = Table.FromRecords(List.Transform(Extracted, each [Answer]),
        type table [SurveyResponseKey = text, WaveID = text, QuestionVersionID = text,
            AnswerType = text, ScaleID = nullable text, ComparisonGroupID = nullable text,
            AnswerRaw = nullable text, Score = nullable number, IsFavourable = nullable logical,
            AnswerStatus = text]),
    Choices = Table.FromRecords(List.Combine(List.Transform(Extracted, (Item) =>
        List.Transform(Item[ChoiceValues], (Choice) =>
            [SurveyResponseKey = Item[Answer][SurveyResponseKey], WaveID = Item[Answer][WaveID],
                QuestionVersionID = Item[Answer][QuestionVersionID], Choice = Choice]))),
        type table [SurveyResponseKey = text, WaveID = text, QuestionVersionID = text, Choice = text])
in
    if ConfigurationOK and KeysOK then [Responses = Responses, Answers = Answers, Choices = Choices]
    else error Error.Record("InvalidSurveyConfiguration", "The wave could not be prepared.", null)
```

## What this code changes in the prototype

The function replaces fixed question lists with question-set membership supplied as data. It builds one response key before creating answer or choice rows, checks that metadata joins cannot duplicate questions, and separates allowed scale labels from source headings. Each question version reads its own source column and scale. Missing cells remain answer opportunities; questions absent from the set create none.

The missing-version check uses distinct QuestionVersionIDs because one version may belong to several sets. It checks that each referenced version has a definition. Duplicate membership remains a separate error: the same version cannot be registered twice within one set.

The supported preparation types remain explicit. Adding another set using those types means adding reviewed metadata rows, rather than another set of hard-coded question loops. FreeText remains unscored. Changing a question from text to selection means registering a different version, not interpreting the earlier narrative automatically.

## Errors and acceptance boundary

| Reason | Action |
| --- | --- |
| InvalidSurveyWave | Supply nonblank text WaveID/QuestionSetID and remove colons from WaveID. |
| InvalidSurveyConfiguration | Check required metadata fields, unique keys, supported types, scales, set membership and comparison-group consistency. |
| SurveyColumnsMissing | Reconcile the registered source heading or required ID/Grade columns with the selected file. Do not create false missing answers for an absent required heading. |
| InvalidSurveyID | Supply a positive whole-number source ID within the supported integer range. |
| DuplicateSurveyID | Resolve a repeated source ID within the same wave. Reusing IDs in different waves is valid. |

The prototype does not supply the registered-file loader, the full current profile, all production dimensions, migrated relationships, generic multi-question cohort logic or replacement DAX. It does not prove that existing 31 measures work unchanged. Native M, real workbook selection and Power BI model tests are separate evidence. Do not install it in the reporting PBIX merely because its synthetic inputs can be generated.

## Synthetic test expectations

Generate the fixed test inputs and an M wrapper with:

```sh
python3 scripts/build_survey_wave_tests.py
```

The invented inputs contain four waves and three question sets. IDs 1–4 restart in each wave. Expected results are 16 distinct response keys, 92 administered answer slots and 29 option rows. Expected answer states are 55 Valid, 25 Missing, six Unmapped and six Unscored. The third set uses configuration only, and the first wave's output should remain unchanged.

The first two waves have agreement shares of 2/3 and 3/4: a difference of +8.333333 percentage points. Their pooled share is 5/7. These fixed values make calculation errors easier to identify than randomised records.

The generator prints its output directory. Paste the complete m_survey_wave_tests.pq file into a blank query in a separate test file. All eight output rows must show Pass = true. Record the observed result and generated fingerprints for the version being tested. Generating the files or running the Python tests does not execute M or DAX.

This test uses in-memory tables, not workbook bytes or SharePoint. Test the file loader, full profile and option model, relationships and DAX separately. The example source headings are test labels, not a recommended final questionnaire.

Unknown choice tokens remain in Choices for investigation. Production choice counts must apply their agreed validity rules rather than count every raw row as a valid answer.
