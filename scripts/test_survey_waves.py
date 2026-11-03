#!/usr/bin/env python3
"""Check the independent multi-wave controls; these tests do not run M or DAX."""

import base64
from copy import deepcopy
import unittest
import zlib

import build_survey_wave_tests as waves


class SurveyWaveControls(unittest.TestCase):
    def setUp(self):
        self.config = waves.fixture()
        self.output = waves.all_outputs(self.config)

    def evaluate_first(self, config=None):
        data = config or self.config
        return waves.evaluate(data['Sources']['W1'], data['Waves'][0], data['QuestionMap'], data['QuestionVersions'], data['ScaleOptions'])

    def test_restarted_ids_are_distinct_submissions_not_matched_people(self):
        self.assertEqual(len(self.output['Responses']), 16)
        self.assertEqual(len({row['SourceResponseID'] for row in self.output['Responses']}), 4)
        keys = {row['SurveyResponseKey'] for row in self.output['Responses']}
        self.assertEqual(len(keys), 16)
        self.assertIn('W1:1', keys)
        self.assertIn('W2:1', keys)

    def test_repeated_instrument_compares_rates_not_raw_favourable_counts(self):
        result = waves.comparison(self.config, self.output, 'W1', 'W2')
        self.assertEqual(result['Status'], 'Comparable')
        self.assertEqual((result['Baseline']['Valid'], result['Target']['Valid']), (3, 4))
        self.assertAlmostEqual(result['PercentagePointChange'], 100 / 12)
        self.assertAlmostEqual(result['Baseline']['Share'], 2 / 3)
        self.assertAlmostEqual(result['Target']['Share'], 3 / 4)

    def test_pooled_percentage_is_not_an_unweighted_average_of_wave_percentages(self):
        expected = waves.controls(self.config, self.output)
        self.assertAlmostEqual(expected['PooledW1W2FavourableShare'], 5 / 7)
        self.assertAlmostEqual(expected['EqualWaveMeanW1W2FavourableShare'], 17 / 24)
        self.assertNotAlmostEqual(expected['PooledW1W2FavourableShare'], expected['EqualWaveMeanW1W2FavourableShare'])

    def test_intentionally_omitted_question_has_no_false_missing_slots(self):
        self.assertFalse(waves.question_present(self.config, 'W3', 'C02_v1'))
        omitted = [row for row in self.output['Answers'] if row['WaveID'] == 'W3' and row['QuestionVersionID'] == 'C02_v1']
        self.assertEqual(omitted, [])
        change = [row for row in self.output['Answers'] if row['WaveID'] == 'W3' and row['QuestionVersionID'] == 'ChangeConfidence_v1']
        self.assertEqual(len(change), 4)
        self.assertEqual(sum(row['AnswerStatus'] == 'Missing' for row in change), 1)
        self.assertEqual(waves.comparison(self.config, self.output, 'W1', 'W3', 'C02_v1', 'C02_v1')['Status'], 'NotAsked')

    def test_missing_registered_heading_is_a_structural_error(self):
        source = self.config['Sources']['W1']
        source['headers'][source['headers'].index(waves.C01)] = 'Unregistered replacement'
        with self.assertRaises(waves.FixtureError) as error:
            self.evaluate_first()
        self.assertEqual(error.exception.reason, 'SurveyColumnsMissing')

    def test_third_set_is_added_as_configuration_without_changing_old_wave_outputs(self):
        baseline = self.evaluate_first()
        self.assertEqual(len(self.config['Waves']), 4)
        self.assertEqual(len({row['QuestionSetID'] for row in self.config['QuestionMap']}), 3)
        self.assertEqual(len([row for row in self.output['Answers'] if row['WaveID'] == 'W4']), 20)
        rebuilt = {name: [row for row in values if row['WaveID'] == 'W1'] for name, values in self.output.items()}
        self.assertEqual(baseline, rebuilt)

    def test_new_rating_codes_do_not_become_agreement_or_gain_a_favourable_threshold(self):
        change = [row for row in self.output['Answers'] if row['QuestionVersionID'] == 'ChangeConfidence_v1']
        self.assertEqual([row['Score'] for row in change], [4, 3, None, None])
        self.assertTrue(all(row['IsFavourable'] is None for row in change))
        self.assertEqual(waves.comparison(self.config, self.output, 'W3', 'W4', 'ChangeConfidence_v1', 'ChangeAwareness_v1')['Status'], 'NotComparable')

    def test_new_format_has_a_new_version_and_old_free_text_is_not_split_or_scored(self):
        text = [row for row in self.output['Answers'] if row['QuestionVersionID'] == 'Skills_v1']
        selected = [row for row in self.output['Answers'] if row['QuestionVersionID'] == 'Skills_v2']
        self.assertTrue(any(row['AnswerRaw'] == 'Research; preserve this narrative' for row in text))
        self.assertTrue(all(row['Score'] is None for row in text + selected))
        self.assertFalse(any(row['QuestionVersionID'] == 'Skills_v1' for row in self.output['Choices']))
        self.assertEqual(sum(row['AnswerStatus'] == 'Unmapped' for row in selected), 1)

    def test_unknown_scale_endpoints_remain_recognised_but_unscored(self):
        tool = [row for row in self.output['Answers'] if row['QuestionVersionID'] == 'Tool_v1']
        self.assertEqual(sum(row['AnswerStatus'] == 'Unscored' for row in tool), 6)
        self.assertEqual(sum(row['AnswerStatus'] == 'Unmapped' for row in tool), 3)
        self.assertTrue(all(row['Score'] is None and row['IsFavourable'] is None for row in tool))

    def test_multi_select_case_duplicates_and_trailing_tokens_do_not_inflate_choices(self):
        raw = self.config['Sources']['W1']
        raw['rows'][0][raw['headers'].index(waves.DOMAIN)] = ' A; a; B; b;; '
        result = self.evaluate_first()
        selected = [row['Choice'] for row in result['Choices'] if row['SurveyResponseKey'] == 'W1:1' and row['QuestionVersionID'] == 'Domain_v1']
        self.assertEqual(selected, ['A', 'B'])
        self.assertEqual(len(result['Responses']), 4)

    def test_separator_only_list_is_missing_not_a_blank_choice(self):
        raw = self.config['Sources']['W1']
        raw['rows'][0][raw['headers'].index(waves.DOMAIN)] = ';; ;'
        result = self.evaluate_first()
        self.assertFalse(any(row['SurveyResponseKey'] == 'W1:1' and row['QuestionVersionID'] == 'Domain_v1' for row in result['Choices']))
        answer = next(row for row in result['Answers'] if row['SurveyResponseKey'] == 'W1:1' and row['QuestionVersionID'] == 'Domain_v1')
        self.assertEqual(answer['AnswerStatus'], 'Missing')

    def test_unmapped_choice_is_retained_for_investigation(self):
        self.assertTrue(any(row['Choice'] == 'Z' for row in self.output['Choices']))
        answer = next(row for row in self.output['Answers'] if row['SurveyResponseKey'] == 'W3:2' and row['QuestionVersionID'] == 'Support_v1')
        self.assertEqual(answer['AnswerStatus'], 'Unmapped')
        self.assertIsNone(answer['Score'])

    def test_domain_and_support_cohort_uses_or_within_and_across_questions(self):
        self.assertEqual(waves.cohort(self.output, wave_id='W1', domains=['A', 'B'], supports=['X']), ['W1:1', 'W1:3'])
        self.assertEqual(waves.cohort(self.output, wave_id='W1', domains=['A'], supports=['X']), ['W1:1'])
        self.assertEqual(waves.cohort(self.output, wave_id='W2', domains=['B'], supports=['Y']), ['W2:2', 'W2:3'])
        self.assertEqual(waves.cohort(self.output, wave_id='W4', supports=['X']), [])
        self.assertEqual(len(waves.cohort(self.output, wave_id='W4')), 4)

    def test_no_answers_produces_undefined_ratio_and_empty_source_preserves_shapes(self):
        empty = deepcopy(self.config)
        empty['Sources']['W2']['rows'] = []
        output = waves.all_outputs(empty)
        self.assertEqual(waves.comparison(empty, output, 'W1', 'W2')['Status'], 'NoValidAnswers')
        raw = deepcopy(empty['Sources']['W2'])
        result = waves.evaluate(raw, empty['Waves'][1], empty['QuestionMap'], empty['QuestionVersions'], empty['ScaleOptions'])
        self.assertEqual(result, {'Responses': [], 'Answers': [], 'Choices': []})

    def test_baseline_and_target_must_be_explicit_and_different(self):
        for baseline, target in [(None, 'W2'), ('W1', None), ('W1', 'W1')]:
            with self.subTest(baseline=baseline, target=target):
                result = waves.comparison(self.config, self.output, baseline, target)
                self.assertEqual(result['Status'], 'SelectTwoDistinctWaves')
                self.assertIsNone(result['PercentagePointChange'])

    def test_failures_have_declared_contract_reasons(self):
        for case in waves.error_cases(self.config):
            with self.subTest(case=case['Name']):
                data = case['Config']
                with self.assertRaises(waves.FixtureError) as error:
                    self.evaluate_first(data)
                self.assertEqual(error.exception.reason, case['ExpectedReason'])

    def test_zero_and_normalised_duplicate_ids_are_rejected(self):
        for first, second, reason in [(0, 2, 'InvalidSurveyID'), (1, '01', 'DuplicateSurveyID')]:
            with self.subTest(first=first, second=second):
                data = deepcopy(self.config)
                data['Sources']['W1']['rows'][0][0] = first
                data['Sources']['W1']['rows'][1][0] = second
                with self.assertRaises(waves.FixtureError) as error:
                    self.evaluate_first(data)
                self.assertEqual(error.exception.reason, reason)

    def test_native_wrapper_embeds_exact_documented_function_without_executing_it(self):
        function = waves.read_prototype()
        expected = waves.controls(self.config, self.output)
        body, payload, wrapper = waves.build_harness(function, self.config, expected)
        self.assertEqual(zlib.decompress(base64.b64decode(payload), -15).decode(), body)
        self.assertIn(function, body)
        self.assertIn('Expression.Evaluate', wrapper)
        self.assertIn('Value.Is', wrapper)
        self.assertNotIn('SharePoint.Files', body)
        self.assertNotIn('Excel.Workbook', body)


if __name__ == '__main__':
    unittest.main()
