#!/usr/bin/env python3
"""Generate disposable survey fixtures and native-M tests, without executing M or DAX.

Read the exact query blocks in survey/survey_queries.md. Write synthetic inputs,
independent arithmetic controls, eleven DATATABLE declarations and an M wrapper
outside the repository. Only invented records and the public example schema are used.
"""

import argparse
import base64
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re
import tempfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
QUERY_PATH = ROOT / "survey" / "survey_queries.md"
QUERY_ORDER = [
    "capabilityFolder", "src_FilesCapability", "stgSurveyRaw", "fxSurveyText",
    "dimSurveyConfidenceQuestion", "dimSurveyLikert", "dimSurveyTool", "dimSurveyRating",
    "stgSurveyPrepared", "factSurvey", "factSurveyConfidence", "factSurveyToolRating",
    "fxSurveyMultiSelect", "bridgeSurveyDomain", "dimSurveyDomain", "bridgeSurveySupport",
    "dimSurveySupport",
]
MODEL_TABLES = [
    "factSurvey", "factSurveyConfidence", "factSurveyToolRating", "bridgeSurveyDomain",
    "bridgeSurveySupport", "dimSurveyConfidenceQuestion", "dimSurveyLikert", "dimSurveyTool",
    "dimSurveyRating", "dimSurveyDomain", "dimSurveySupport",
]
PROFILE_PAIRS = [
    ("ID", "ResponseID"),
    ("What is your cost centre?", "CostCentre"),
    ("What is your grade?", "Grade"),
    ("Which business domain(s) do you primarily work in? (Select all that apply)", "DomainSelections"),
    ("What type of work do you primarily deliver?", "BusinessWorkType"),
    ("What is your current role level/grade that you are working at within your client work?", "ClientRoleLevel"),
    ("How would you currently rate your AI or digital capability in a client-facing context? (Select one)", "ClientCapability"),
    ("How much exposure to or involvement with AI have you had in your client work?", "ClientAIExposure"),
    ("Have you worked on any digital or AI-focused projects in your organisation?", "CurrentAICommission"),
    ("Outside explicitly digital commissions, have you used AI tools to improve productivity on non-digital projects?", "NonDigitalProductivityUse"),
    ("Before joining your current organisation, did you work on any digital or AI-focused projects or programmes?", "PriorAIProject"),
    ("How would you describe your current level of formal AI learning?", "FormalLearning"),
    ("If the opportunity to work on an AI-focused commission arose, would you be interested?", "CommissionInterest"),
    ("Would you be interested in including AI or digital training in your professional development plan?", "TrainingInterest"),
    ("What type of support or training would be most useful to you?", "SupportSelections"),
]
CONFIDENCE_FIELDS = [
    "I feel confident using AI tools to support my work tasks",
    "I feel confident using AI tools in my personal life",
    "I understand the strengths and limitations of AI tools",
    "I am comfortable with new AI tools or features",
    "I can judge when AI outputs need to be checked, validated, or adjusted",
    "I feel confident explaining or recommending AI tools to others",
]
SHORT_LABELS = [
    "Work-task confidence", "Personal-life confidence", "Strengths and limitations",
    "Comfort with new tools", "Checking AI outputs", "Explaining and recommending",
]
TOOLS = ["Co-pilot", "ChatGPT", "Gemini", "Grammarly", "Claude"]
UNUSED_FIELDS = [
    "Start Time", "Completion Time", "Email", "Name", "Last modified time",
    "If yes, please briefly describe: Type of commission (e.g. advisory, assurance, PM, transformation) - Client sector (no programme names) - Cost centre/business area - Your role and level of invo...",
    "If yes, briefly describe the type of role and how AI was used (e.g. analysis, reporting, planning, risk, automation).",
    "If yes, please briefly describe the type of work and your role (no sensitive details).",
    "Please list any other AI models or tools you have used (if more than 5 please list those most often used)",
    "Artificial Intelligence (AI)", "Machine Learning (ML)", "Natural Language Processing (NLP)",
    "Large Language Model (LLM)", "Generative AI", "Tokenization",
    "List any technical AI skills you have experience with.",
    "Please list any relevant technical or AI training you have undertaken. (Leave blank if not applicable)",
    "Please list any other relevant AI or digital qualifications/certifications you hold. (Formal or informal)",
]
AGREEMENT = {"strongly disagree": 1, "disagree": 2, "neutral": 3, "agree": 4, "strongly agree": 5}
PROFILE_ORDERS = {
    "ClientCapability": ["Awareness Only/limited hands-on experience", "Comfortable user of AI and digital tools", "Experienced practitioner applying AI in delivery", "Specialist/subject matter expert"],
    "ClientAIExposure": ["None", "Limited Exposure", "Some involvement", "Significant Exposure"],
    "FormalLearning": ["None", "Introductory", "Intermediate", "Advanced"],
    "CommissionInterest": ["No", "Depends on the role", "Yes"],
    "TrainingInterest": ["No", "Yes"],
}


def query_blocks():
    text = QUERY_PATH.read_text()
    pairs = re.findall(r"^## ([A-Za-z_][A-Za-z0-9_]*)\s*\n.*?^```powerquery\s*\n(.*?)^```\s*$", text, re.M | re.S)
    queries = dict(pairs)
    if list(queries) != QUERY_ORDER or len(pairs) != 17:
        raise ValueError("Expected the seventeen documented query blocks in installation order")
    return queries


def clean(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def choices(value):
    text = clean(value)
    return sorted({part.strip() for part in text.split(";") if part.strip()}) if text else []


def fixture():
    headers = [name for name, _ in PROFILE_PAIRS] + CONFIDENCE_FIELDS + TOOLS + UNUSED_FIELDS
    assert len(headers) == len(set(headers)) == 44
    confidence = [
        ["Strongly agree", "Strongly agree", "Agree", "Agree", "Strongly agree", "Agree"],
        ["Agree", "Neutral", "Agree", "Neutral", "Agree", "Disagree"],
        ["Neutral", "Disagree", "Neutral", "  aGrEe  ", "Not sure", ""],
        [None] * 6,
    ]
    tool_values = [[5, 4, 3, 2, 1], ["5", None, "2.5", 0, 6], [" 1 ", "3", 2, 4, 5], [None] * 5]
    profile_values = [
        [1, "CC1", "G1", "A; B; A; ", "Example work A", "Example client role A", "Awareness Only/limited hands-on experience", "None", "Yes", "Yes", "No", "None", "Yes", "Yes", "X;"],
        [2, "CC1", "G1", "A;B;", "Example work B", "Example client role B", "Comfortable user of AI and digital tools", "Limited Exposure", "No", "Yes", "Yes", "Introductory", "Depends on the role", "Yes", "Y;"],
        [3, "CC2", "G2", "B;", "Example work A", "Example client role A", "Experienced practitioner applying AI in delivery", "Some involvement", "No", "No", "No", "Intermediate", "No", "No", "X; Y; X;;"],
        [4, None, "G2", None, None, None, "Specialist/subject matter expert", "Significant Exposure", None, None, None, "Advanced", None, None, ""],
    ]
    rows = []
    for i in range(4):
        unused = [None] * 18
        unused[2] = "anonymous"
        rows.append(profile_values[i] + confidence[i] + tool_values[i] + unused)
    assert all(len(row) == 44 for row in rows)
    return {"headers": headers, "rows": rows}


def expected_tables(data):
    """Independent Python expectations, not a replacement for either M or DAX."""
    facts, answers, ratings, domains, support = [], [], [], [], []
    for values in data["rows"]:
        record = dict(zip(data["headers"], values))
        prepared = {alias: clean(record[source]) for source, alias in PROFILE_PAIRS}
        response_id = int(prepared["ResponseID"])
        prepared["ResponseID"] = response_id
        core = {alias: prepared[alias] if alias == "ResponseID" else prepared[alias] or "(No answer)"
                for _, alias in PROFILE_PAIRS if alias not in {"DomainSelections", "SupportSelections"}}
        for name, ordered in PROFILE_ORDERS.items():
            core[name + "Order"] = ordered.index(core[name]) + 1 if core[name] in ordered else 99
        facts.append(core)
        domains.extend({"ResponseID": response_id, "Domain": option} for option in choices(prepared["DomainSelections"]))
        support.extend({"ResponseID": response_id, "Support": option} for option in choices(prepared["SupportSelections"]))
        for i, field in enumerate(CONFIDENCE_FIELDS, 1):
            answer = clean(record[field])
            score = AGREEMENT.get(answer.lower()) if answer is not None else None
            answers.append({"ResponseID": response_id, "QuestionID": f"C{i:02d}", "Answer": answer,
                            "Score": score, "AnswerStatus": "Missing" if answer is None else "Valid" if score is not None else "Unmapped"})
        for i, field in enumerate(TOOLS, 1):
            raw = clean(record[field])
            try:
                parsed = float(raw) if raw is not None else None
            except ValueError:
                parsed = None
            valid = parsed in (1, 2, 3, 4, 5)
            ratings.append({"ResponseID": response_id, "ToolID": f"T{i:02d}", "RatingRaw": raw,
                            "Rating": int(parsed) if valid else None,
                            "RatingStatus": "Missing" if raw is None else "Valid" if valid else "Invalid"})
    result = {
        "factSurvey": facts, "factSurveyConfidence": answers, "factSurveyToolRating": ratings,
        "bridgeSurveyDomain": domains, "bridgeSurveySupport": support,
        "dimSurveyConfidenceQuestion": [{"QuestionID": f"C{i:02d}", "SourceColumn": text, "QuestionText": text,
                                          "ShortLabel": SHORT_LABELS[i - 1], "SortOrder": i} for i, text in enumerate(CONFIDENCE_FIELDS, 1)],
        "dimSurveyLikert": [{"Score": score, "ResponseLabel": label.capitalize(), "MatchKey": label, "SortOrder": score}
                            for label, score in AGREEMENT.items()],
        "dimSurveyTool": [{"ToolID": f"T{i:02d}", "SourceColumn": name, "ToolName": name, "SortOrder": i} for i, name in enumerate(TOOLS, 1)],
        "dimSurveyRating": [{"Rating": i, "RatingLabel": str(i), "SortOrder": i} for i in range(1, 6)],
        "dimSurveyDomain": [{"Domain": option} for option in sorted({row["Domain"] for row in domains})],
        "dimSurveySupport": [{"Support": option} for option in sorted({row["Support"] for row in support})],
    }
    assert len(facts) == 4 and all(len(row) == 18 for row in facts)
    assert len(answers) == 24 and Counter(row["AnswerStatus"] for row in answers) == {"Valid": 16, "Missing": 7, "Unmapped": 1}
    assert sum(row["Score"] or 0 for row in answers) == 59
    assert sum((row["Score"] or 0) >= 4 for row in answers) == 10
    assert len(ratings) == 20 and Counter(row["RatingStatus"] for row in ratings) == {"Valid": 11, "Missing": 6, "Invalid": 3}
    assert sum(row["Rating"] or 0 for row in ratings) == 35
    assert sum(row["Rating"] == 5 for row in ratings) == 3
    assert len(domains) == 5 and len(support) == 4
    return result


def arithmetic_cases(tables):
    cases = [
        ("all_responses", None, None, None), ("domain_A", ["A"], None, None),
        ("domain_B", ["B"], None, None), ("support_X", None, ["X"], None),
        ("domain_A_and_support_X", ["A"], ["X"], None),
        ("domain_B_and_support_Y", ["B"], ["Y"], None),
        ("domain_A_or_B_and_support_X", ["A", "B"], ["X"], None),
        ("grade_G1_and_domain_B", ["B"], None, ["G1"]),
        ("grade_G2_and_support_Y", None, ["Y"], ["G2"]),
        ("explicit_no_matching_domain", ["No matching option"], None, None),
        ("cleared_option_filters", None, None, None),
        ("no_answer_cost_centre", None, None, None),
    ]
    result = []
    for name, domains, supports, grades in cases:
        selected = []
        for row in tables["factSurvey"]:
            key = row["ResponseID"]
            domain_match = domains is None or any(p["ResponseID"] == key and p["Domain"] in domains for p in tables["bridgeSurveyDomain"])
            support_match = supports is None or any(p["ResponseID"] == key and p["Support"] in supports for p in tables["bridgeSurveySupport"])
            grade_match = grades is None or row["Grade"] in grades
            cost_match = name != "no_answer_cost_centre" or row["CostCentre"] == "(No answer)"
            if domain_match and support_match and grade_match and cost_match:
                selected.append(key)
        c01 = [r for r in tables["factSurveyConfidence"] if r["ResponseID"] in selected and r["QuestionID"] == "C01"]
        valid = [r for r in c01 if r["AnswerStatus"] == "Valid"]
        favourable = sum(r["Score"] >= 4 for r in valid)
        result.append({"Case": name, "Domains": domains, "Support": supports, "Grades": grades,
                       "CostCentre": "(No answer)" if name == "no_answer_cost_centre" else None,
                       "ExpectedResponseIDs": selected, "ExpectedResponses": len(selected),
                       "Interest": {
                           "CommissionValid": sum(r["CommissionInterest"] in PROFILE_ORDERS["CommissionInterest"] for r in tables["factSurvey"] if r["ResponseID"] in selected),
                           "CommissionYes": sum(r["CommissionInterest"] == "Yes" for r in tables["factSurvey"] if r["ResponseID"] in selected),
                           "CommissionConditional": sum(r["CommissionInterest"] == "Depends on the role" for r in tables["factSurvey"] if r["ResponseID"] in selected),
                           "TrainingValid": sum(r["TrainingInterest"] in PROFILE_ORDERS["TrainingInterest"] for r in tables["factSurvey"] if r["ResponseID"] in selected),
                           "TrainingYes": sum(r["TrainingInterest"] == "Yes" for r in tables["factSurvey"] if r["ResponseID"] in selected),
                       },
                       "C01": {"Slots": len(c01), "Valid": len(valid), "Missing": sum(r["AnswerStatus"] == "Missing" for r in c01),
                               "Unmapped": sum(r["AnswerStatus"] == "Unmapped" for r in c01), "Favourable": favourable,
                               "FavourableShare": float(Fraction(favourable, len(valid))) if valid else None,
                               "AnswerCoverage": float(Fraction(len(valid), len(c01))) if c01 else None,
                               "MeanAgreementCode": sum(r["Score"] for r in valid) / len(valid) if valid else None}})
    assert [row["ExpectedResponses"] for row in result] == [4, 2, 3, 2, 1, 2, 2, 2, 1, 0, 4, 1]
    assert result[0]["C01"]["FavourableShare"] == float(Fraction(2, 3))
    return result


def m_text(value):
    return '"' + value.replace('#(', '#(#)(').replace('"', '""').replace('\r', '#(cr)').replace('\n', '#(lf)').replace('\t', '#(tab)') + '"'


def m_value(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return m_text(value)


M_TESTS = r'''
    AsText = (Value as any) as text => Text.FromBinary(Json.FromValue(Value), TextEncoding.Utf8),
    Fixture = Run(Raw),
    Tables = Fixture[Tables],
    Profile = Table.Buffer(Tables[factSurvey]),
    Confidence = Table.Buffer(Tables[factSurveyConfidence]),
    Tools = Table.Buffer(Tables[factSurveyToolRating]),
    Domains = Table.Buffer(Tables[bridgeSurveyDomain]),
    Support = Table.Buffer(Tables[bridgeSurveySupport]),
    ExpectedDomains = #table(type table [ResponseID = Int64.Type, Domain = text], {{1,"A"},{1,"B"},{2,"A"},{2,"B"},{3,"B"}}),
    ExpectedSupport = #table(type table [ResponseID = Int64.Type, Support = text], {{1,"X"},{2,"Y"},{3,"X"},{3,"Y"}}),
    Shapes = [RawColumns = Table.ColumnCount(Raw), PreparedColumns = Table.ColumnCount(Fixture[Prepared]),
        Responses = Table.RowCount(Profile), ProfileColumns = Table.ColumnCount(Profile),
        ConfidenceSlots = Table.RowCount(Confidence), ToolSlots = Table.RowCount(Tools),
        DomainPairs = Table.RowCount(Domains), SupportPairs = Table.RowCount(Support),
        DomainLabels = Table.RowCount(Tables[dimSurveyDomain]), SupportLabels = Table.RowCount(Tables[dimSurveySupport]),
        Questions = Table.RowCount(Tables[dimSurveyConfidenceQuestion]), Likert = Table.RowCount(Tables[dimSurveyLikert]),
        ToolLabels = Table.RowCount(Tables[dimSurveyTool]), RatingLabels = Table.RowCount(Tables[dimSurveyRating]),
        MissingCostCentre = Table.RowCount(Table.SelectRows(Profile, each [CostCentre] = "(No answer)")),
        DomainPairsEqual = AsText(Table.Sort(Domains, {{"ResponseID",Order.Ascending},{"Domain",Order.Ascending}})) = AsText(ExpectedDomains),
        SupportPairsEqual = AsText(Table.Sort(Support, {{"ResponseID",Order.Ascending},{"Support",Order.Ascending}})) = AsText(ExpectedSupport)],
    ShapesPass = Shapes[RawColumns] = 44 and Shapes[PreparedColumns] = 26 and Shapes[Responses] = 4
        and Shapes[ProfileColumns] = 18 and Shapes[ConfidenceSlots] = 24 and Shapes[ToolSlots] = 20
        and Shapes[DomainPairs] = 5 and Shapes[SupportPairs] = 4 and Shapes[DomainLabels] = 2 and Shapes[SupportLabels] = 2
        and Shapes[Questions] = 6 and Shapes[Likert] = 5 and Shapes[ToolLabels] = 5 and Shapes[RatingLabels] = 5
        and Shapes[MissingCostCentre] = 1 and Shapes[DomainPairsEqual] and Shapes[SupportPairsEqual],
    UnknownCategoryRaw = #table(SourceHeaders, List.ReplaceRange(SourceRows, 0, 1, {List.ReplaceRange(SourceRows{0}, 6, 1, {"Unmapped capability"})})),
    UnknownProfile = Run(UnknownCategoryRaw)[Tables][factSurvey]{0},
    ProfileObserved = [CapabilityOrders = Profile[ClientCapabilityOrder], ExposureOrders = Profile[ClientAIExposureOrder],
        LearningOrders = Profile[FormalLearningOrder], CommissionOrders = Profile[CommissionInterestOrder], TrainingOrders = Profile[TrainingInterestOrder],
        CommissionValid = Table.RowCount(Table.SelectRows(Profile, each List.Contains({"No","Depends on the role","Yes"}, [CommissionInterest]))),
        CommissionYes = Table.RowCount(Table.SelectRows(Profile, each [CommissionInterest] = "Yes")),
        CommissionConditional = Table.RowCount(Table.SelectRows(Profile, each [CommissionInterest] = "Depends on the role")),
        TrainingValid = Table.RowCount(Table.SelectRows(Profile, each List.Contains({"No","Yes"}, [TrainingInterest]))),
        TrainingYes = Table.RowCount(Table.SelectRows(Profile, each [TrainingInterest] = "Yes")),
        UnknownLabel = UnknownProfile[ClientCapability], UnknownOrder = UnknownProfile[ClientCapabilityOrder]],
    ProfilePass = AsText(ProfileObserved[CapabilityOrders]) = AsText({1,2,3,4}) and AsText(ProfileObserved[ExposureOrders]) = AsText({1,2,3,4})
        and AsText(ProfileObserved[LearningOrders]) = AsText({1,2,3,4}) and AsText(ProfileObserved[CommissionOrders]) = AsText({3,2,1,99})
        and AsText(ProfileObserved[TrainingOrders]) = AsText({2,2,1,99}) and ProfileObserved[CommissionValid] = 3 and ProfileObserved[CommissionYes] = 1
        and ProfileObserved[CommissionConditional] = 1 and ProfileObserved[TrainingValid] = 3 and ProfileObserved[TrainingYes] = 2
        and ProfileObserved[UnknownLabel] = "Unmapped capability" and ProfileObserved[UnknownOrder] = 99,
    C01 = Table.SelectRows(Confidence, each [QuestionID] = "C01"),
    C04Third = Table.SelectRows(Confidence, each [ResponseID] = 3 and [QuestionID] = "C04"){0},
    ConfidenceObserved = [Slots = Table.RowCount(Confidence), Valid = Table.RowCount(Table.SelectRows(Confidence, each [AnswerStatus] = "Valid")),
        Missing = Table.RowCount(Table.SelectRows(Confidence, each [AnswerStatus] = "Missing")),
        Unmapped = Table.RowCount(Table.SelectRows(Confidence, each [AnswerStatus] = "Unmapped")),
        ScoreSum = List.Sum(List.RemoveNulls(Confidence[Score])),
        Favourable = Table.RowCount(Table.SelectRows(Confidence, each [Score] <> null and [Score] >= 4)),
        C01Valid = Table.RowCount(Table.SelectRows(C01, each [AnswerStatus] = "Valid")),
        C01Missing = Table.RowCount(Table.SelectRows(C01, each [AnswerStatus] = "Missing")),
        C01Favourable = Table.RowCount(Table.SelectRows(C01, each [Score] <> null and [Score] >= 4)),
        C01ScoreSum = List.Sum(List.RemoveNulls(C01[Score])),
        TrimmedCaseMatch = C04Third[Answer] = "aGrEe" and C04Third[Score] = 4,
        SlotsPerResponse = List.Transform({1..4}, (ID) => Table.RowCount(Table.SelectRows(Confidence, each [ResponseID] = ID)))],
    ConfidencePass = ConfidenceObserved[Slots] = 24 and ConfidenceObserved[Valid] = 16 and ConfidenceObserved[Missing] = 7
        and ConfidenceObserved[Unmapped] = 1 and ConfidenceObserved[ScoreSum] = 59 and ConfidenceObserved[Favourable] = 10
        and ConfidenceObserved[C01Valid] = 3 and ConfidenceObserved[C01Missing] = 1 and ConfidenceObserved[C01Favourable] = 2
        and ConfidenceObserved[C01ScoreSum] = 12 and ConfidenceObserved[TrimmedCaseMatch]
        and List.AllTrue(List.Transform(ConfidenceObserved[SlotsPerResponse], each _ = 6)),
    ToolObserved = [Slots = Table.RowCount(Tools), Valid = Table.RowCount(Table.SelectRows(Tools, each [RatingStatus] = "Valid")),
        Missing = Table.RowCount(Table.SelectRows(Tools, each [RatingStatus] = "Missing")),
        Invalid = Table.RowCount(Table.SelectRows(Tools, each [RatingStatus] = "Invalid")),
        RatingSum = List.Sum(List.RemoveNulls(Tools[Rating])), Rating5Count = Table.RowCount(Table.SelectRows(Tools, each [Rating] = 5)),
        InvalidRaw = List.Sort(Table.SelectRows(Tools, each [RatingStatus] = "Invalid")[RatingRaw]),
        SlotsPerResponse = List.Transform({1..4}, (ID) => Table.RowCount(Table.SelectRows(Tools, each [ResponseID] = ID)))],
    ToolPass = ToolObserved[Slots] = 20 and ToolObserved[Valid] = 11 and ToolObserved[Missing] = 6 and ToolObserved[Invalid] = 3
        and ToolObserved[RatingSum] = 35 and ToolObserved[Rating5Count] = 3 and AsText(ToolObserved[InvalidRaw]) = AsText({"0","2.5","6"})
        and List.AllTrue(List.Transform(ToolObserved[SlotsPerResponse], each _ = 5)),
    Empty = Run(#table(SourceHeaders, {})),
    EmptyTables = Empty[Tables],
    EmptyObserved = [PreparedRows = Table.RowCount(Empty[Prepared]), PreparedColumns = Table.ColumnCount(Empty[Prepared]),
        Responses = Table.RowCount(EmptyTables[factSurvey]), ConfidenceSlots = Table.RowCount(EmptyTables[factSurveyConfidence]),
        ToolSlots = Table.RowCount(EmptyTables[factSurveyToolRating]), DomainPairs = Table.RowCount(EmptyTables[bridgeSurveyDomain]),
        SupportPairs = Table.RowCount(EmptyTables[bridgeSurveySupport]), DomainLabels = Table.RowCount(EmptyTables[dimSurveyDomain]),
        SupportLabels = Table.RowCount(EmptyTables[dimSurveySupport]), Questions = Table.RowCount(EmptyTables[dimSurveyConfidenceQuestion]),
        Likert = Table.RowCount(EmptyTables[dimSurveyLikert]), ToolLabels = Table.RowCount(EmptyTables[dimSurveyTool]),
        RatingLabels = Table.RowCount(EmptyTables[dimSurveyRating])],
    EmptyPass = EmptyObserved[PreparedRows] = 0 and EmptyObserved[PreparedColumns] = 26 and EmptyObserved[Responses] = 0
        and EmptyObserved[ConfidenceSlots] = 0 and EmptyObserved[ToolSlots] = 0 and EmptyObserved[DomainPairs] = 0
        and EmptyObserved[SupportPairs] = 0 and EmptyObserved[DomainLabels] = 0 and EmptyObserved[SupportLabels] = 0
        and EmptyObserved[Questions] = 6 and EmptyObserved[Likert] = 5 and EmptyObserved[ToolLabels] = 5 and EmptyObserved[RatingLabels] = 5,
    ChangedID = (NewID as any) as table => #table(SourceHeaders, List.ReplaceRange(SourceRows, 3, 1, {List.ReplaceRange(SourceRows{3}, 0, 1, {NewID})})),
    CheckError = (Input as table, ExpectedReason as text) as record =>
        let Attempt = try Table.RowCount(Table.Buffer(Run(Input)[Tables][factSurvey])),
            Reason = if Attempt[HasError] then Attempt[Error][Reason] else null
        in [Expected = ExpectedReason, HasError = Attempt[HasError], Reason = Reason,
            Pass = Attempt[HasError] and Reason = ExpectedReason],
    ErrorObserved = [DuplicateID = CheckError(ChangedID(2), "DuplicateSurveyID"),
        MissingID = CheckError(ChangedID(null), "InvalidSurveyID"), NonIntegerID = CheckError(ChangedID(1.5), "InvalidSurveyID"),
        MissingHeading = CheckError(Table.RemoveColumns(Raw, {ConfidenceFirstHeading}), "SurveyColumnsMissing")],
    ErrorPass = List.AllTrue(List.Transform(Record.FieldValues(ErrorObserved), each [Pass])),
    CheckSourceCount = (Count as number) as record =>
        let Files = #table(type table [Content = binary], List.Repeat({{#binary({})}}, Count)),
            Attempt = try Table.RowCount(ReadSource(Files)),
            Reason = if Attempt[HasError] then Attempt[Error][Reason] else null
        in [SelectedFiles = Count, HasError = Attempt[HasError], Reason = Reason,
            Pass = Attempt[HasError] and Reason = "SurveyWorkbookSelection"],
    SourceObserved = [ZeroFiles = CheckSourceCount(0), TwoFiles = CheckSourceCount(2)],
    SourcePass = SourceObserved[ZeroFiles][Pass] and SourceObserved[TwoFiles][Pass],
    AllPass = ShapesPass and ProfilePass and ConfidencePass and ToolPass and EmptyPass and ErrorPass and SourcePass,
    Output = #table(type table [Test = text, Pass = logical, Observed = text], {
        {"All survey M regressions", AllPass, AsText([Tests = 7, ErrorCases = 6, Pass = AllPass])},
        {"Fixture shapes and split choices", ShapesPass, AsText(Shapes)},
        {"Confirmed category order and interest", ProfilePass, AsText(ProfileObserved)},
        {"Confidence mapping and retained slots", ConfidencePass, AsText(ConfidenceObserved)},
        {"Neutral tool ratings and retained slots", ToolPass, AsText(ToolObserved)},
        {"Empty extraction and constant dimensions", EmptyPass, AsText(EmptyObserved)},
        {"Response-key and required-heading errors", ErrorPass, AsText(ErrorObserved)},
        {"Source-count guards only", SourcePass, AsText(SourceObserved)}
    })
in
    Output
'''


def build_harness(queries, data):
    semantic = [name for name in QUERY_ORDER if name not in {"capabilityFolder", "src_FilesCapability", "stgSurveyRaw"}]
    run_bindings = ["stgSurveyRaw = Raw"] + [name + " = (\n" + queries[name] + "\n        )" for name in semantic]
    tables = ", ".join(name + " = " + name for name in MODEL_TABLES)
    run = "Run = (Raw as table) as record =>\n        let\n            " + ",\n            ".join(run_bindings)
    run += "\n        in [Prepared = stgSurveyPrepared, Tables = [" + tables + "]]"
    reader = "ReadSource = (Files as table) as table =>\n        let src_FilesCapability = Files\n        in (\n" + queries["stgSurveyRaw"] + "\n        )"
    rows = ["{" + ", ".join(m_value(value) for value in row) + "}" for row in data["rows"]]
    bindings = [run, reader,
                "SourceHeaders = {" + ", ".join(m_text(h) for h in data["headers"]) + "}",
                "SourceRows = {\n        " + ",\n        ".join(rows) + "\n    }",
                "Raw = #table(SourceHeaders, SourceRows)",
                "ConfidenceFirstHeading = " + m_text(CONFIDENCE_FIELDS[0])]
    body = "// Disposable synthetic survey regression. Generation does not execute M or DAX.\nlet\n    " + ",\n    ".join(bindings) + ",\n" + M_TESTS
    compressor = zlib.compressobj(level=9, wbits=-15)
    payload = base64.b64encode(compressor.compress(body.encode()) + compressor.flush()).decode()
    assert zlib.decompress(base64.b64decode(payload), -15).decode() == body
    prefixes = {"Binary", "BinaryEncoding", "Compression", "Error", "Excel", "Int64", "JoinKind", "Json", "List", "Number", "Order", "Record", "Table", "Text", "TextEncoding"}
    builtins = sorted({name for name in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\b", body)
                       if name.split(".", 1)[0] in prefixes})
    environment = "Record.SelectFields(#shared, {" + ", ".join(m_text(n) for n in builtins) + "})"
    wrapper = 'Expression.Evaluate(Text.FromBinary(Binary.Decompress(Binary.FromText("' + payload + '", BinaryEncoding.Base64), Compression.Deflate), TextEncoding.Utf8), ' + environment + ')\n'
    return body, payload, wrapper


def dax_table(name, rows):
    columns = list(rows[0])
    integer_columns = {"ResponseID", "Score", "Rating"} | {c for c in columns if c.endswith("Order")}
    q = lambda value: '"' + value.replace('"', '""') + '"'
    schema = ",\n    ".join(q(c) + ", " + ("INTEGER" if c in integer_columns else "STRING") for c in columns)
    def value(item, column):
        if item is None:
            return "BLANK()"
        return str(item) if column in integer_columns else q(item)
    body = ",\n        ".join("{" + ", ".join(value(row[c], c) for c in columns) + "}" for row in rows)
    return name + " =\nDATATABLE(\n    " + schema + ",\n    {\n        " + body + "\n    }\n)\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="A disposable output directory outside the repository")
    args = parser.parse_args()
    output = (args.output_dir or Path(tempfile.mkdtemp(prefix="survey-tests-"))).resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("Choose an output directory outside the repository")
    output.mkdir(parents=True, exist_ok=True)
    queries = query_blocks()
    data = fixture()
    tables = expected_tables(data)
    cases = arithmetic_cases(tables)
    body, payload, wrapper = build_harness(queries, data)
    (output / "m_survey_tests.pq").write_text(wrapper)
    (output / "m_survey_tests_body.pq").write_text(body)
    (output / "fixture_data.json").write_text(json.dumps({"Method": "Invented source data using the public example schema", **data}, indent=2) + "\n")
    (output / "expected_arithmetic.json").write_text(json.dumps({"Method": "Independent Python expectations, not native M or DAX execution", "Tables": tables, "CohortCases": cases}, indent=2) + "\n")
    directory = output / "dax_tables"
    directory.mkdir(exist_ok=True)
    for name in MODEL_TABLES:
        (directory / (name + ".dax")).write_text(dax_table(name, tables[name]))
    manifest = {
        "method": "Generated tests only; execute m_survey_tests.pq separately in Microsoft's M engine",
        "fixture": "Four synthetic responses with 44 raw columns, overlapping semicolon choices, missing/unmapped confidence and invalid tool ratings",
        "source_query_document": str(QUERY_PATH.relative_to(ROOT)),
        "query_sha256": {name: sha256(code.encode()).hexdigest() for name, code in queries.items()},
        "wrapper_sha256": sha256(wrapper.encode()).hexdigest(),
        "payload_characters": len(payload), "payload_crc32": zlib.crc32(payload.encode()),
        "native_test_rows": 8, "semantic_groups": 7, "expected_error_cases": 6,
        "cohort_arithmetic_cases": len(cases), "disposable_dax_tables": len(MODEL_TABLES),
        "workbook_boundary": "Source-count guards invoke the real reader with 0/2 dummy file records. No Excel workbook bytes or SharePoint authentication are tested.",
        "dax_boundary": "Table declarations and arithmetic controls are generated. DAX and relationship filtering are not executed.",
        "entry_point": str(output / "m_survey_tests.pq"),
    }
    (output / "m_survey_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Generated tests, not executed M or DAX")
    print("M query:", output / "m_survey_tests.pq")
    print("Rows: 8; semantic groups: 7; expected error cases: 6")
    print("Arithmetic cohort cases:", len(cases), "; DATATABLE declarations:", len(MODEL_TABLES))
    print("Payload characters:", len(payload), "; payload CRC32:", manifest["payload_crc32"])
    print("Wrapper SHA-256:", manifest["wrapper_sha256"])


if __name__ == "__main__":
    main()
