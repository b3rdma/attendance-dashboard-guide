#!/usr/bin/env python3
"""Generate synthetic multi-wave survey controls, without executing M or DAX.

Read the exact proposed fxSurveyWavePrototype from survey/survey_wave_prototype.md.
Write JSON fixtures, independent Python expectations and a native-M test wrapper
outside the repository. All source records are invented; no workbook or SharePoint connection is read.
"""

import argparse
import base64
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re
import tempfile
import zlib

import build_survey_tests as snapshot

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE = ROOT / 'survey' / 'survey_wave_prototype.md'
MAP_FIELDS = ['QuestionSetID', 'QuestionVersionID', 'SourceColumn']
VERSION_FIELDS = ['QuestionVersionID', 'QuestionID', 'AnswerType', 'ScaleID', 'ComparisonGroupID']
OPTION_FIELDS = ['ScaleID', 'AnswerLabel', 'Score', 'IsFavourable']
RESPONSE_FIELDS = ['SurveyResponseKey', 'WaveID', 'SourceResponseID', 'Grade']
ANSWER_FIELDS = ['SurveyResponseKey', 'WaveID', 'QuestionVersionID', 'AnswerType', 'ScaleID', 'ComparisonGroupID', 'AnswerRaw', 'Score', 'IsFavourable', 'AnswerStatus']
CHOICE_FIELDS = ['SurveyResponseKey', 'WaveID', 'QuestionVersionID', 'Choice']
TYPES = {'Likert', 'Rating', 'SingleChoice', 'MultiChoice', 'FreeText'}
C01 = snapshot.CONFIDENCE_FIELDS[0]
C02 = snapshot.CONFIDENCE_FIELDS[1]
DOMAIN = snapshot.PROFILE_PAIRS[3][0]
SUPPORT = snapshot.PROFILE_PAIRS[-1][0]
GRADE = snapshot.PROFILE_PAIRS[2][0]
SKILLS = 'List any technical AI skills you have experience with.'


class FixtureError(ValueError):
    """An independently specified validation outcome, not a native M result."""
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def clean(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def fixture():
    """Four waves, three question sets and anonymous IDs restarting at one."""
    versions = [
        ['C01_v1', 'C01', 'Likert', 'Agreement5', 'WorkConfidence'],
        ['C02_v1', 'C02', 'Likert', 'Agreement5', 'PersonalConfidence'],
        ['Skills_v1', 'Skills', 'FreeText', None, None],
        ['Domain_v1', 'Domain', 'MultiChoice', 'Domains', None],
        ['Support_v1', 'Support', 'MultiChoice', 'Supports', None],
        ['Tool_v1', 'Tool', 'Rating', 'ToolCodes', None],
        ['Skills_v2', 'Skills', 'SingleChoice', 'SkillChoices', None],
        ['ChangeConfidence_v1', 'ChangeConfidence', 'Rating', 'Change5', 'PerceivedConfidenceChange'],
        ['ChangeAwareness_v1', 'ChangeAwareness', 'Rating', 'Change5', 'PerceivedAwarenessChange'],
        ['Interest_v1', 'Interest', 'SingleChoice', 'InterestChoices', None],
        ['Comment_v1', 'Comment', 'FreeText', None, None],
    ]
    question_map = [
        ['Set1', 'C01_v1', C01], ['Set1', 'C02_v1', C02], ['Set1', 'Skills_v1', SKILLS],
        ['Set1', 'Domain_v1', DOMAIN], ['Set1', 'Support_v1', SUPPORT], ['Set1', 'Tool_v1', 'Co-pilot'],
        ['Set2', 'C01_v1', C01], ['Set2', 'Skills_v2', 'Technical skill selection'],
        ['Set2', 'Domain_v1', DOMAIN], ['Set2', 'Support_v1', SUPPORT], ['Set2', 'Tool_v1', 'Co-pilot'],
        ['Set2', 'ChangeConfidence_v1', 'Reported increase in AI confidence'],
        ['Set3', 'C01_v1', C01], ['Set3', 'Domain_v1', DOMAIN],
        ['Set3', 'ChangeAwareness_v1', 'Reported increase in AI awareness'],
        ['Set3', 'Interest_v1', 'Interest in learning'], ['Set3', 'Comment_v1', 'Comment'],
    ]
    options = [['Agreement5', label.title() if label != 'neutral' else 'Neutral', score, score >= 4]
               for label, score in snapshot.AGREEMENT.items()]
    options += [['Change5', str(score), score, None] for score in range(1, 6)]
    options += [['ToolCodes', str(score), None, None] for score in range(1, 6)]
    options += [[scale, label, None, None] for scale, labels in [
        ('Domains', ['A', 'B']), ('Supports', ['X', 'Y']),
        ('SkillChoices', ['None', 'Some', 'Extensive']), ('InterestChoices', ['Yes', 'No', 'Depends'])]
        for label in labels]
    waves = [
        {'WaveID': 'W1', 'QuestionSetID': 'Set1', 'WaveLabel': 'Synthetic baseline', 'FieldworkEnd': '2026-10-01'},
        {'WaveID': 'W2', 'QuestionSetID': 'Set1', 'WaveLabel': 'Synthetic repeat', 'FieldworkEnd': '2026-11-01'},
        {'WaveID': 'W3', 'QuestionSetID': 'Set2', 'WaveLabel': 'Synthetic revised set', 'FieldworkEnd': '2026-12-01'},
        {'WaveID': 'W4', 'QuestionSetID': 'Set3', 'WaveLabel': 'Synthetic third set', 'FieldworkEnd': '2027-01-01'},
    ]
    base = snapshot.fixture()
    sources = {}
    for wave_id, c01, c02, skills, domains, supports, tools in [
        ('W1', ['Strongly agree', 'Agree', 'Neutral', None], ['Strongly agree', 'Neutral', 'Disagree', None],
         ['Drafting', None, 'Research; preserve this narrative', ''], ['A; B; A; ', 'A;B;', 'B;', None], ['X;', 'Y;', 'X; Y; X;;', ''], [5, 4, '2.5', None]),
        ('W2', ['Agree', ' aGrEe ', 'Strongly agree', 'Disagree'], ['Agree', 'Agree', None, 'Neutral'],
         ['Reporting', 'Planning', None, ' '], ['A;', 'B;', 'B;', ''], ['X;', 'X;Y;', 'Y;', None], [1, 5, 0, None]),
    ]:
        source = deepcopy(base)
        for index, row in enumerate(source['rows']):
            updates = {C01: c01[index], C02: c02[index], SKILLS: skills[index], DOMAIN: domains[index], SUPPORT: supports[index], 'Co-pilot': tools[index]}
            for field, value in updates.items():
                row[source['headers'].index(field)] = value
        # The prototype's profile contract uses Grade as a short, explicitly prepared input.
        source['headers'][source['headers'].index(GRADE)] = 'Grade'
        sources[wave_id] = source
    sources['W3'] = {'headers': ['ID', 'Grade', C01, 'Technical skill selection', DOMAIN, SUPPORT, 'Co-pilot', 'Reported increase in AI confidence'],
                     'rows': [[1, 'G1', 'Strongly agree', 'Some', 'A;B;', 'Y;', 5, 4],
                              [2, 'G1', 'Agree', 'None', 'A;', 'X; Z;', 3, 3],
                              [3, 'G2', None, 'Unexpected', 'B;', 'X;Y;', 'oops', None],
                              [4, 'G2', 'Strongly disagree', None, None, None, None, 6]]}
    sources['W4'] = {'headers': ['ID', 'Grade', C01, DOMAIN, 'Reported increase in AI awareness', 'Interest in learning', 'Comment'],
                     'rows': [[1, 'G1', 'Agree', 'B;', 1, 'Yes', 'Preserve free text; do not split'],
                              [2, 'G1', 'Strongly agree', 'A;B;', 2, 'No', 'Check source outputs'],
                              [3, 'G2', 'Disagree', 'A;', 4, 'Depends', None],
                              [4, 'G2', None, '', None, None, '']]}
    return {'Method': 'Invented configuration and JSON/in-memory source tables; no Excel files',
            'Waves': waves, 'QuestionMap': [dict(zip(MAP_FIELDS, row)) for row in question_map],
            'QuestionVersions': [dict(zip(VERSION_FIELDS, row)) for row in versions],
            'ScaleOptions': [dict(zip(OPTION_FIELDS, row)) for row in options], 'Sources': sources}


def _unique(rows, fields):
    keys = [tuple(row[field] for field in fields) for row in rows]
    if len(keys) != len(set(keys)):
        raise FixtureError('InvalidSurveyConfiguration')


def evaluate(raw, wave, question_map, versions, options):
    """Independent, deliberately small Python oracle for the proposed contract."""
    wave_id, set_id = clean(wave.get('WaveID')), clean(wave.get('QuestionSetID'))
    if not wave_id or ':' in wave_id or not set_id:
        raise FixtureError('InvalidSurveyWave')
    _unique(versions, ['QuestionVersionID'])
    _unique(question_map, ['QuestionSetID', 'QuestionVersionID'])
    _unique(question_map, ['QuestionSetID', 'SourceColumn'])
    normalised_options = [(row['ScaleID'], clean(row['AnswerLabel']).casefold()) for row in options]
    if len(normalised_options) != len(set(normalised_options)):
        raise FixtureError('InvalidSurveyConfiguration')
    by_version = {row['QuestionVersionID']: row for row in versions}
    groups = {}
    for version in versions:
        if version['AnswerType'] not in TYPES:
            raise FixtureError('InvalidSurveyConfiguration')
        if version['AnswerType'] != 'FreeText' and not any(option['ScaleID'] == version['ScaleID'] for option in options):
            raise FixtureError('InvalidSurveyConfiguration')
        group = clean(version['ComparisonGroupID'])
        if group:
            groups.setdefault(group, set()).add((version['QuestionID'], version['AnswerType'], version['ScaleID']))
    if any(len(shapes) != 1 for shapes in groups.values()):
        raise FixtureError('InvalidSurveyConfiguration')
    mappings = [row for row in question_map if row['QuestionSetID'] == set_id]
    if not mappings or any(row['QuestionVersionID'] not in by_version for row in question_map):
        raise FixtureError('InvalidSurveyConfiguration')
    required = {'ID', 'Grade'} | {row['SourceColumn'] for row in mappings}
    if not required <= set(raw['headers']):
        raise FixtureError('SurveyColumnsMissing')
    responses, answers, choices, seen = [], [], [], set()
    for values in raw['rows']:
        source = dict(zip(raw['headers'], values))
        text_id = clean(source['ID'])
        if not text_id or not re.fullmatch(r'[0-9]+', text_id) or int(text_id) <= 0:
            raise FixtureError('InvalidSurveyID')
        local_id = int(text_id)
        if local_id in seen:
            raise FixtureError('DuplicateSurveyID')
        seen.add(local_id)
        response_key = wave_id + ':' + str(local_id)
        responses.append(dict(zip(RESPONSE_FIELDS, [response_key, wave_id, local_id, clean(source['Grade'])])))
        for mapping in mappings:
            version = by_version[mapping['QuestionVersionID']]
            answer_type, scale_id = version['AnswerType'], version['ScaleID']
            value = clean(source[mapping['SourceColumn']])
            scale_options = {clean(row['AnswerLabel']).casefold(): row for row in options if row['ScaleID'] == scale_id}
            score = favourable = None
            if answer_type == 'MultiChoice':
                tokens = [] if value is None else [token.strip() for token in value.split(';') if token.strip()]
                selected, token_keys = {}, set()
                for token in tokens:
                    if token.casefold() in token_keys:
                        continue
                    token_keys.add(token.casefold())
                    option = scale_options.get(token.casefold())
                    label = option['AnswerLabel'] if option else token
                    selected.setdefault(label, option)
                for label in selected:
                    choices.append(dict(zip(CHOICE_FIELDS, [response_key, wave_id, version['QuestionVersionID'], label])))
                status = 'Missing' if not selected else 'Valid' if all(option is not None for option in selected.values()) else 'Unmapped'
            elif value is None:
                status = 'Missing'
            elif answer_type == 'FreeText':
                status = 'Valid'
            else:
                option = scale_options.get(value.casefold())
                status = 'Unmapped' if option is None else 'Valid'
                if option is not None and answer_type in {'Likert', 'Rating'}:
                    score, favourable = option['Score'], option['IsFavourable']
                    if score is None:
                        favourable = None
                        status = 'Unscored'
            answers.append(dict(zip(ANSWER_FIELDS, [response_key, wave_id, version['QuestionVersionID'], answer_type,
                scale_id, version['ComparisonGroupID'], value, score, favourable, status])))
    return {'Responses': responses, 'Answers': answers, 'Choices': choices}


def all_outputs(config):
    output = {name: [] for name in ['Responses', 'Answers', 'Choices']}
    for wave in config['Waves']:
        result = evaluate(config['Sources'][wave['WaveID']], wave, config['QuestionMap'], config['QuestionVersions'], config['ScaleOptions'])
        for name in output:
            output[name].extend(result[name])
    return output


def question_present(config, wave_id, question_version):
    wave = next((wave for wave in config['Waves'] if wave['WaveID'] == wave_id), None)
    return bool(wave and any(row['QuestionSetID'] == wave['QuestionSetID'] and row['QuestionVersionID'] == question_version for row in config['QuestionMap']))


def cohort(output, wave_id=None, grade=None, domains=None, supports=None):
    result = []
    for response in output['Responses']:
        if wave_id is not None and response['WaveID'] != wave_id:
            continue
        if grade is not None and response['Grade'] != grade:
            continue
        key = response['SurveyResponseKey']
        if any(selected is not None and not any(row['SurveyResponseKey'] == key and row['QuestionVersionID'] == question and row['Choice'] in selected for row in output['Choices'])
               for question, selected in [('Domain_v1', domains), ('Support_v1', supports)]):
            continue
        result.append(key)
    return result


def favourable(output, wave_id, question_version, keys=None):
    selected = [row for row in output['Answers'] if row['WaveID'] == wave_id and row['QuestionVersionID'] == question_version
                and row['AnswerStatus'] == 'Valid' and row['AnswerType'] == 'Likert' and row['ScaleID'] == 'Agreement5'
                and (keys is None or row['SurveyResponseKey'] in keys)]
    valid = len(selected)
    count = sum(row['IsFavourable'] is True for row in selected)
    return {'Valid': valid, 'Favourable': count, 'Share': float(Fraction(count, valid)) if valid else None}


def comparison(config, output, baseline, target, baseline_question='C01_v1', target_question='C01_v1'):
    if not baseline or not target or baseline == target:
        return {'Status': 'SelectTwoDistinctWaves', 'PercentagePointChange': None}
    if baseline_question != target_question:
        return {'Status': 'NotComparable', 'PercentagePointChange': None}
    versions = {row['QuestionVersionID']: row for row in config['QuestionVersions']}
    version = versions[baseline_question]
    if version['AnswerType'] != 'Likert' or version['ScaleID'] != 'Agreement5' or not version['ComparisonGroupID']:
        return {'Status': 'NotComparable', 'PercentagePointChange': None}
    if not question_present(config, baseline, baseline_question) or not question_present(config, target, target_question):
        return {'Status': 'NotAsked', 'PercentagePointChange': None}
    first, second = favourable(output, baseline, baseline_question), favourable(output, target, target_question)
    if first['Share'] is None or second['Share'] is None:
        return {'Status': 'NoValidAnswers', 'PercentagePointChange': None}
    return {'Status': 'Comparable', 'Baseline': first, 'Target': second,
            'PercentagePointChange': (second['Share'] - first['Share']) * 100}


def controls(config, output):
    w1, w2 = favourable(output, 'W1', 'C01_v1'), favourable(output, 'W2', 'C01_v1')
    cohorts = [
        ('W1 all', {'wave_id': 'W1'}), ('W2 all', {'wave_id': 'W2'}), ('All waves', {}),
        ('W1 Domain A', {'wave_id': 'W1', 'domains': ['A']}),
        ('W2 Domain A', {'wave_id': 'W2', 'domains': ['A']}),
        ('W1 Support X', {'wave_id': 'W1', 'supports': ['X']}),
        ('W1 Domain A and Support X', {'wave_id': 'W1', 'domains': ['A'], 'supports': ['X']}),
        ('W2 Domain B and Support Y', {'wave_id': 'W2', 'domains': ['B'], 'supports': ['Y']}),
        ('W1 Grade G1 and Domain B', {'wave_id': 'W1', 'grade': 'G1', 'domains': ['B']}),
        ('W2 Grade G1 and Domain B', {'wave_id': 'W2', 'grade': 'G1', 'domains': ['B']}),
        ('W1 Domains A or B and Support X', {'wave_id': 'W1', 'domains': ['A', 'B'], 'supports': ['X']}),
        ('W4 Support X not asked', {'wave_id': 'W4', 'supports': ['X']}),
    ]
    return {'Method': 'Independent Python arithmetic and contract controls, not executed M/DAX results',
            'Shapes': {'Waves': 4, 'QuestionSets': 3, 'Responses': len(output['Responses']), 'Answers': len(output['Answers']), 'Choices': len(output['Choices'])},
            'AnswerStatuses': dict(Counter(row['AnswerStatus'] for row in output['Answers'])),
            'PerWave': {wave['WaveID']: {name: sum(row['WaveID'] == wave['WaveID'] for row in rows) for name, rows in output.items()} for wave in config['Waves']},
            'BaselineTarget': comparison(config, output, 'W1', 'W2'),
            'PooledW1W2FavourableShare': float(Fraction(w1['Favourable'] + w2['Favourable'], w1['Valid'] + w2['Valid'])),
            'EqualWaveMeanW1W2FavourableShare': (w1['Share'] + w2['Share']) / 2,
            'Availability': {'W1_ChangeConfidence': question_present(config, 'W1', 'ChangeConfidence_v1'),
                             'W3_C02': question_present(config, 'W3', 'C02_v1'),
                             'W4_Support': question_present(config, 'W4', 'Support_v1')},
            'Cohorts': [{'Name': name, 'Filter': filters, 'ExpectedKeys': cohort(output, **filters), 'ExpectedCount': len(cohort(output, **filters))} for name, filters in cohorts]}


def error_cases(config):
    """Each mutation represents an operational failure with an explicit contract."""
    cases = []
    def add(name, reason, mutate):
        data = deepcopy(config)
        mutate(data)
        cases.append({'Name': name, 'ExpectedReason': reason, 'Config': data})
    add('Blank wave key', 'InvalidSurveyWave', lambda data: data['Waves'][0].update(WaveID=' '))
    add('Ambiguous wave key delimiter', 'InvalidSurveyWave', lambda data: data['Waves'][0].update(WaveID='W:1'))
    add('Duplicate local response ID', 'DuplicateSurveyID', lambda data: data['Sources']['W1']['rows'][1].__setitem__(0, 1))
    add('Missing response ID', 'InvalidSurveyID', lambda data: data['Sources']['W1']['rows'][0].__setitem__(0, None))
    add('Fractional response ID', 'InvalidSurveyID', lambda data: data['Sources']['W1']['rows'][0].__setitem__(0, 1.5))
    add('Expected question heading missing', 'SurveyColumnsMissing', lambda data: data['Sources']['W1']['headers'].__setitem__(data['Sources']['W1']['headers'].index(C01), 'Unexpected renamed question'))
    add('Unsupported answer type', 'InvalidSurveyConfiguration', lambda data: data['QuestionVersions'][0].update(AnswerType='Ranking'))
    add('Unknown question version', 'InvalidSurveyConfiguration', lambda data: data['QuestionMap'][0].update(QuestionVersionID='AbsentVersion'))
    add('Duplicate question registration', 'InvalidSurveyConfiguration', lambda data: data['QuestionMap'].append(deepcopy(data['QuestionMap'][0])))
    add('Duplicate scale label', 'InvalidSurveyConfiguration', lambda data: data['ScaleOptions'].append(deepcopy(data['ScaleOptions'][0])))
    add('Incompatible shared comparison group', 'InvalidSurveyConfiguration', lambda data: data['QuestionVersions'][7].update(ComparisonGroupID='WorkConfidence'))
    add('Unknown scale', 'InvalidSurveyConfiguration', lambda data: data['QuestionVersions'][0].update(ScaleID='AbsentScale'))
    return cases


def read_prototype():
    blocks = re.findall(r'^```powerquery\s*\n(.*?)^```\s*$', PROTOTYPE.read_text(), re.M | re.S)
    if len(blocks) != 1:
        raise ValueError('Expected exactly one proposed prototype M function')
    return blocks[0]


def m_text(text):
    return '"' + text.replace('"', '""').replace('\n', '#(lf)').replace('\r', '#(cr)').replace('\t', '#(tab)') + '"'


def m_value(value):
    if value is None:
        return 'null'
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if isinstance(value, str):
        return m_text(value)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return '{' + ', '.join(m_value(item) for item in value) + '}'
    if isinstance(value, dict):
        return '[' + ', '.join(key + ' = ' + m_value(item) for key, item in value.items()) + ']'
    raise TypeError(type(value))


def m_table(fields, records):
    return '#table(' + m_value(fields) + ', ' + m_value([[row.get(field) for field in fields] for row in records]) + ')'


def m_raw(raw):
    return '#table(' + m_value(raw['headers']) + ', ' + m_value(raw['rows']) + ')'


def build_harness(function, config, expected):
    """Embed the exact proposed function and ordinary in-memory source tables."""
    # M record fields share a scope. Count-suffixed observation fields must not
    # shadow the outer Responses/Answers/Choices tables used by later fields.
    # Catch test expressions inline so a native error remains a failed test.
    bindings = ['fxSurveyWavePrototype = (\n' + function + '\n)',
                'QuestionMap = ' + m_table(MAP_FIELDS, config['QuestionMap']),
                'QuestionVersions = ' + m_table(VERSION_FIELDS, config['QuestionVersions']),
                'ScaleOptions = ' + m_table(OPTION_FIELDS, config['ScaleOptions']),
                'Waves = ' + m_value(config['Waves']),
                'Sources = [' + ', '.join(wave['WaveID'] + ' = ' + m_raw(config['Sources'][wave['WaveID']]) for wave in config['Waves']) + ']',
                'Run = (Wave as record) as record => fxSurveyWavePrototype(Record.Field(Sources, Wave[WaveID]), Wave, QuestionMap, QuestionVersions, ScaleOptions)',
                'Runs = List.Transform(Waves, each Run(_))',
                'Responses = Table.Combine(List.Transform(Runs, each _[Responses]))',
                'Answers = Table.Combine(List.Transform(Runs, each _[Answers]))',
                'Choices = Table.Combine(List.Transform(Runs, each _[Choices]))',
                'AsText = (Value as any) as text => Text.FromBinary(Json.FromValue(Value), TextEncoding.Utf8)',
                'SafeText = (Value as any) as text => let Attempt = try AsText(Value) in if Attempt[HasError] then AsText([NativeError = true, Reason = try Attempt[Error][Reason] otherwise "Unknown", Message = try Attempt[Error][Message] otherwise "Unknown"]) else Attempt[Value]',
                'Count = (Rows as table, WaveID as text, QuestionVersionID as text, Status as nullable text) as number => Table.RowCount(Table.SelectRows(Rows, each [WaveID] = WaveID and [QuestionVersionID] = QuestionVersionID and (Status = null or [AnswerStatus] = Status)))',
                'Shapes = [ResponseCount = Table.RowCount(Responses), UniqueKeys = List.Count(List.Distinct(Responses[SurveyResponseKey])), AnswerCount = Table.RowCount(Answers), ChoiceCount = Table.RowCount(Choices), RowsPerWave = List.Transform(Runs, each Table.RowCount(_[Responses]))]',
                'ShapesPass = Shapes[ResponseCount] = 16 and Shapes[UniqueKeys] = 16 and Shapes[AnswerCount] = ' + str(expected['Shapes']['Answers']) + ' and Shapes[ChoiceCount] = ' + str(expected['Shapes']['Choices']) + ' and Shapes[RowsPerWave] = {4,4,4,4}',
                'C01 = Table.SelectRows(Answers, each [QuestionVersionID] = "C01_v1")',
                'Summary = (WaveID as text) as record => let Rows = Table.SelectRows(C01, each [WaveID] = WaveID and [AnswerStatus] = "Valid"), N = Table.RowCount(Rows), F = Table.RowCount(Table.SelectRows(Rows, each [IsFavourable] = true)) in [Valid = N, Favourable = F, Share = if N = 0 then null else F / N]',
                'W1Summary = Summary("W1")', 'W2Summary = Summary("W2")',
                'ComparisonObserved = [W1 = W1Summary, W2 = W2Summary, DifferencePP = (W2Summary[Share] - W1Summary[Share]) * 100, Pooled = (W1Summary[Favourable] + W2Summary[Favourable]) / (W1Summary[Valid] + W2Summary[Valid])]',
                'ComparisonPass = W1Summary[Valid] = 3 and W1Summary[Favourable] = 2 and W2Summary[Valid] = 4 and W2Summary[Favourable] = 3 and Number.Abs(ComparisonObserved[DifferencePP] - (100 / 12)) < 0.000000001 and Number.Abs(ComparisonObserved[Pooled] - (5 / 7)) < 0.000000001',
                'Availability = [W1ChangeSlots = Count(Answers,"W1","ChangeConfidence_v1",null), W3C02Slots = Count(Answers,"W3","C02_v1",null), W4SupportSlots = Count(Answers,"W4","Support_v1",null), W3ChangeSlots = Count(Answers,"W3","ChangeConfidence_v1",null), W3ChangeMissing = Count(Answers,"W3","ChangeConfidence_v1","Missing")]',
                'AvailabilityPass = Availability[W1ChangeSlots] = 0 and Availability[W3C02Slots] = 0 and Availability[W4SupportSlots] = 0 and Availability[W3ChangeSlots] = 4 and Availability[W3ChangeMissing] = 1',
                'Statuses = [Valid = Table.RowCount(Table.SelectRows(Answers, each [AnswerStatus] = "Valid")), Missing = Table.RowCount(Table.SelectRows(Answers, each [AnswerStatus] = "Missing")), Unmapped = Table.RowCount(Table.SelectRows(Answers, each [AnswerStatus] = "Unmapped")), Unscored = Table.RowCount(Table.SelectRows(Answers, each [AnswerStatus] = "Unscored")), UnknownChoicePreserved = Table.RowCount(Table.SelectRows(Choices, each [WaveID] = "W3" and [Choice] = "Z")) = 1, UnscoredToolSlots = Table.RowCount(Table.SelectRows(Answers, each [QuestionVersionID] = "Tool_v1" and [AnswerStatus] = "Unscored"))]',
                'StatusesPass = ' + ' and '.join('Statuses[' + name + '] = ' + str(expected['AnswerStatuses'].get(name, 0)) for name in ['Valid', 'Missing', 'Unmapped', 'Unscored']) + ' and Statuses[UnknownChoicePreserved] and Statuses[UnscoredToolSlots] = 6',
                'ThirdSet = [Set = Waves{3}[QuestionSetID], AnswerCount = Table.RowCount(Runs{3}[Answers]), ValidComments = Count(Answers,"W4","Comment_v1","Valid"), FirstWaveStable = AsText(Runs{0}) = AsText(Run(Waves{0}))]',
                'ThirdSetPass = ThirdSet[Set] = "Set3" and ThirdSet[AnswerCount] = 20 and ThirdSet[ValidComments] = 2 and ThirdSet[FirstWaveStable]',
                'Empty = fxSurveyWavePrototype(Table.FirstN(Sources[W1],0), Waves{0}, QuestionMap, QuestionVersions, ScaleOptions)',
                'EmptyObserved = [Responses = Table.RowCount(Empty[Responses]), Answers = Table.RowCount(Empty[Answers]), Choices = Table.RowCount(Empty[Choices])]',
                'EmptyPass = EmptyObserved[Responses] = 0 and EmptyObserved[Answers] = 0 and EmptyObserved[Choices] = 0']
    native_errors = []
    for case in error_cases(config):
        mutated = case['Config']
        wave = mutated['Waves'][0]
        expression = 'fxSurveyWavePrototype(' + ', '.join([m_raw(mutated['Sources']['W1']), m_value(wave), m_table(MAP_FIELDS, mutated['QuestionMap']), m_table(VERSION_FIELDS, mutated['QuestionVersions']), m_table(OPTION_FIELDS, mutated['ScaleOptions'])]) + ')'
        native_errors.append('[Name = ' + m_text(case['Name']) + ', Expected = ' + m_text(case['ExpectedReason']) + ', Observed = (try Table.RowCount((' + expression + ')[Answers]))]')
    bindings += ['ErrorCases = {' + ',\n'.join(native_errors) + '}',
                 'ErrorObserved = List.Transform(ErrorCases, each [Name = _[Name], Expected = _[Expected], HasError = _[Observed][HasError], Reason = if _[Observed][HasError] then _[Observed][Error][Reason] else null, Pass = _[Observed][HasError] and _[Observed][Error][Reason] = _[Expected]])',
                 'ErrorPass = List.AllTrue(List.Transform(ErrorObserved, each _[Pass]))',
                 'AllPass = (try ShapesPass otherwise false) and (try ComparisonPass otherwise false) and (try AvailabilityPass otherwise false) and (try StatusesPass otherwise false) and (try ThirdSetPass otherwise false) and (try EmptyPass otherwise false) and (try ErrorPass otherwise false)',
                 'Output = #table(type table [Test = text, Pass = logical, Observed = text], {'
                 '{"All survey wave prototype regressions",(try AllPass otherwise false),SafeText([Groups=7,ErrorCases=List.Count(ErrorCases),Pass=AllPass])},'
                 '{"Wave keys and appended shapes",(try ShapesPass otherwise false),SafeText(Shapes)},'
                 '{"Identical question repeated-wave arithmetic",(try ComparisonPass otherwise false),SafeText(ComparisonObserved)},'
                 '{"Not asked versus missing answer slots",(try AvailabilityPass otherwise false),SafeText(Availability)},'
                 '{"Answer types and unmapped/unscored values",(try StatusesPass otherwise false),SafeText(Statuses)},'
                 '{"Third question set through configuration",(try ThirdSetPass otherwise false),SafeText(ThirdSet)},'
                 '{"Empty source with retained headings",(try EmptyPass otherwise false),SafeText(EmptyObserved)},'
                 '{"Expected configuration and source errors",(try ErrorPass otherwise false),SafeText(ErrorObserved)}})']
    body = '// Disposable synthetic survey-wave tests. Generation is not native execution.\nlet\n    ' + ',\n    '.join(bindings) + '\nin\n    Output\n'
    compressor = zlib.compressobj(level=9, wbits=-15)
    payload = base64.b64encode(compressor.compress(body.encode()) + compressor.flush()).decode()
    prefixes = {'Binary', 'BinaryEncoding', 'Compression', 'Comparer', 'Error', 'Int64', 'JoinKind', 'Json', 'List', 'Number', 'Order', 'Record', 'Table', 'Text', 'TextEncoding', 'Value'}
    builtins = sorted({name for name in re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*\b', body) if name.split('.', 1)[0] in prefixes})
    environment = 'Record.SelectFields(#shared, {' + ', '.join(m_text(name) for name in builtins) + '})'
    wrapper = 'Expression.Evaluate(Text.FromBinary(Binary.Decompress(Binary.FromText(' + m_text(payload) + ', BinaryEncoding.Base64), Compression.Deflate), TextEncoding.Utf8), ' + environment + ')\n'
    assert zlib.decompress(base64.b64decode(payload), -15).decode() == body
    return body, payload, wrapper


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, help='A disposable directory outside the repository')
    args = parser.parse_args(argv)
    directory = (args.output_dir or Path(tempfile.mkdtemp(prefix='survey-wave-tests-'))).resolve()
    if directory == ROOT or ROOT in directory.parents:
        parser.error('Choose a disposable output directory outside the repository')
    directory.mkdir(parents=True, exist_ok=True)
    config = fixture()
    outputs = all_outputs(config)
    expected = controls(config, outputs)
    function = read_prototype()
    body, payload, wrapper = build_harness(function, config, expected)
    (directory / 'survey_wave_configuration.json').write_text(json.dumps({key: value for key, value in config.items() if key != 'Sources'}, indent=2) + '\n')
    (directory / 'survey_wave_source_tables.json').write_text(json.dumps(config['Sources'], indent=2) + '\n')
    (directory / 'survey_wave_expected.json').write_text(json.dumps({'Controls': expected, 'Tables': outputs}, indent=2) + '\n')
    (directory / 'm_survey_wave_tests_body.pq').write_text(body)
    (directory / 'm_survey_wave_tests.pq').write_text(wrapper)
    manifest = {'Method': 'Generated tests only; Microsoft M and Power BI DAX have not been executed by this generator',
                'PrototypeDocument': str(PROTOTYPE.relative_to(ROOT)), 'FunctionSHA256': sha256(function.encode()).hexdigest(),
                'WrapperSHA256': sha256(wrapper.encode()).hexdigest(), 'PayloadCharacters': len(payload),
                'NativeResultRows': 8, 'SemanticGroups': 7, 'ExpectedErrorCases': len(error_cases(config)),
                'CohortCases': len(expected['Cohorts']), 'Shapes': expected['Shapes'],
                'Boundary': 'JSON and in-memory M tables; no Excel workbook bytes, SharePoint access, production query replacement, native DAX or employee identity linkage',
                'EntryPoint': str(directory / 'm_survey_wave_tests.pq')}
    (directory / 'survey_wave_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Generated synthetic survey-wave tests, not executed M or DAX')
    print('M query:', directory / 'm_survey_wave_tests.pq')
    print('Shapes:', json.dumps(expected['Shapes'], sort_keys=True))
    print('Native groups: 7; expected errors:', manifest['ExpectedErrorCases'], '; cohort arithmetic cases:', manifest['CohortCases'])
    print('Wrapper SHA-256:', manifest['WrapperSHA256'])
    return directory


if __name__ == '__main__':
    main()
