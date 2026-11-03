# Maintain later survey waves and question sets

[Architecture and scope](survey_waves.md) · [Compare results](survey_wave_comparisons.md) · [Prototype and fixtures](survey_wave_prototype.md)

## When to use this runbook

Use the operational steps only after the multi-wave extension has been implemented and accepted. The current single-snapshot reader still stops if more than one workbook is selected. This document specifies the intended handover process; it does not assert that the new reader and model are already installed.

Routine additions should change registered data/configuration and require a refresh. They should not require new copies of all model tables or editing DAX for each wave. That objective is achievable for already supported question types and agreed comparison rules. Arbitrary new survey formats cannot be guaranteed to work without an adapter.

## What the handover must include

| Item | Record before handing over |
| --- | --- |
| Working model | Exact accepted PBIX/PBIP location/version and full query/measure/model export |
| Inputs | Approved data folder, configuration workbook/table names, source access and retained snapshots |
| Responsibility | Survey lead, source maintainer, reporting maintainer and technical escalation route |
| Supported contract | Types, multi-choice delimiter, ID format, required profile fields and naming rules |
| Meanings | Question/scale dictionary, approved comparable anchors, valid/unscored/missing treatment |
| Results | Reference first-wave totals and observed multi-wave tests, including the third-set exercise |
| Recovery | Pre-change PBIX and configuration copies, source revision inventory and recovery steps |

Keep credentials in the approved connection mechanism. Arrange source and Power BI access separately from access to this guide.

## Decide whether an addition is routine

| Change | Maintainer action |
| --- | --- |
| Another administration of an existing question set | Add one Waves row and its exact source reference |
| Same meaning but a different export heading | Add a new question-set mapping reusing the approved question version; retain the old set's mapping |
| New question using a supported type | Register the version/scale/options, create a new question-set membership and link the new wave |
| An intentionally removed question | Exclude it from the new set, leaving earlier set definitions intact |
| A new scale or different answer meaning | Register a new version/scale; leave cross-wave comparison unapproved until reviewed |
| Free text changed to a selection | Preserve the text version and register the selection version separately |
| An extra global cohort filter, branching, ranking, matrix or unsupported source format | Stop the routine route and obtain a reviewed model/adapter change |

A source-heading mismatch is not permission to pretend a question was not asked. If the register says a field exists but the export lacks it, resolve that discrepancy before refreshing the reporting copy.

## Register an identical second or later wave

1. Confirm the survey really retained the wording, options, scale direction, required/optional rules and reference meaning of the registered set. Keep the six confidence statements as agreed trend questions.
2. Preserve the completed export as a wave snapshot. Save it under a stable unique filename; keep test data outside every production-selected path.
3. Add a unique WaveID to Waves. Reuse the existing QuestionSetID. Enter the exact folder, filename and Excel Table name, fieldwork dates, reference date and display order. Do not derive WaveID from a refresh index.
4. Check the enabled-wave source preview: exactly one intended file must match each row. Do not globally require one workbook anymore, choose an arbitrary first file or include an unregistered workbook automatically.
5. Refresh the development copy and inspect the response audit by wave: source rows, unique SourceResponseID values and unique SurveyResponseKey values must reconcile. Reused numeric IDs across different waves are expected.
6. Check the question-availability report. The wave must list the existing question versions with the correct scales and families.
7. Check each wave's answer slots and statuses. Compare original-wave results before and after the addition; they must remain equal when its sources and selections are unchanged.
8. Compare the same question and group across the chosen baseline and target. Show valid n, shares and percentage-point difference, together with the response-group mix.
9. Record the source and configuration versions, observed results and recovery copy. Update the reporting model only after the checks pass.

If a live survey remains open, record that status explicitly. Its counts and percentages can change on refresh. Do not describe it as a final baseline snapshot until the survey lead closes and preserves it.

## Register a changed question set

1. Copy the previous set definition to a new QuestionSetID. Do not edit the membership or wording that describes an earlier completed wave.
2. Review each question. Retain its existing version only when the meaning, wording and answer rules are unchanged. A source heading can differ while mapping to the same approved version.
3. Add new versions for changed wording, answer formats or scales. Record full wording and every option, not just a 1–5 range.
4. Add the exact SourceColumn mapping for each administered version. Omit intentionally retired questions from membership. Preserve source/profile availability separately from unanswered responses.
5. Define each new scale's order, nullable scoring and any justified favourable group. A change scale is not Agreement5. Keep known but unscored answers such as Unable to compare explicit.
6. Link the new wave to that set. Preview its registered headings, questions and option mappings before reading all responses.
7. Test one complete response, one blank answer, an unexpected option, repeated multi-choice tokens and an empty file with headers. Every case must follow its documented state or failure rule.
8. Check common unchanged anchors across waves. Show new or changed versions separately. Expect unavailable comparisons to show a reason and a blank difference.
9. Complete the same whole-model checks and release record as an identical-wave addition.

Review the intake report of mapped headings, deliberately ignored source fields and unregistered additions. An unexpected new question should prompt a register update and meaning review, rather than being imported automatically or silently omitted from an assumed complete analysis. The prototype checks required headings; the complete intake audit is part of the registered-file implementation.

Adding a third question set requires the same registry edits when it stays within the accepted answer-type contract. No new relationship or per-wave measure should be needed. This remains a design objective until the installed model has passed that exact configuration-only test.

Standard answer distributions should reuse generic type-aware measures. A new management calculation with its own definition still needs a separately reviewed measure; supporting a question format does not automatically define every possible KPI about it.

## Test with the supplied synthetic demonstration

Generate deterministic fixtures outside the repository:

```sh
python3 scripts/build_survey_wave_tests.py
python3 -m unittest discover -s scripts -p 'test_survey_waves.py'
```

The generator supplies configuration/source JSON and an M wrapper using the exact proposed function in the prototype reference. These are invented records for four waves and three question sets. They are not Excel workbooks and do not exercise SharePoint or Excel.Workbook. Follow the generator's printed paths and the prototype instructions for native M tests. Python expectations are not native M or DAX results.

The core first/second-wave controls are:

| Control | Expected result |
| --- | --- |
| Local source IDs | Both waves reuse 1, 2, 3, 4 |
| Combined response keys | Eight different keys; no person matching |
| First-wave C01 scores | 5, 4, 3, missing: three valid, two favourable, 66.6667% |
| Second-wave C01 scores | 4, 4, 5, 2: four valid, three favourable, 75% |
| Difference | +8.3333 percentage points |
| Pooled favourable answers | Five / seven valid answers = 71.4286% |
| Equal-weight mean of wave percentages | 70.8333%; a different measure |

Later sets demonstrate a retained anchor, a retired question, a newly introduced change item, a text-to-selection version change and a third set using registered types. Use these fixed cases before randomising values. Randomisation can generate plausible charts while hiding an incorrect expected result.

For a manual workbook test, copy only clearly synthetic data into new lab workbooks and create the registered Excel Tables/headings. Preserve IDs restarting between waves. Keep a small hand-calculated answer sample and never use those workbooks as production survey evidence.

## Power BI acceptance before routine operation

- Confirm each source is read once for its intended enabled wave and unregistered files do not become waves.
- Confirm duplicate IDs within a wave fail, while repeated local IDs across waves are retained with different combined keys.
- Check missing configured headings, duplicate mappings and unsupported types produce clear failures.
- Confirm Not asked creates no slot, whereas a blank administered question retains one Missing slot.
- Confirm known unscored options differ from missing/unmapped answers and stay out of scored percentages.
- Reconcile profile, answer and choice counts by wave; check trailing semicolons and repeated options.
- Apply Grade, Domain and Support selections consistently to wave counts and answer measures. Check questions absent from an instrument do not create zero-demand or fabricated No answer categories.
- Test one wave, all waves, one question, selected questions, no valid answers and an empty response cohort.
- Test missing/equal baseline and target selections, noncomparable versions and a zero-valid target. Return a blank difference with a reason, not a spurious change.
- Confirm corrected exports replace their existing wave rather than duplicate it, and adding a new wave leaves earlier results unchanged.
- Complete a third-question-set addition through configuration alone with the future maintainer, recording every action and observed result.

The generated prototype does not implement all these model/source acceptance checks. In particular, file registration, the full profile/cohort model and native DAX filtering must be tested in the actual development model.

## Recover from a failed addition

Keep the failed source and configuration available for diagnosis. Restore the previous configuration or disable the new wave in the development copy, then refresh against the preceding accepted inventory. Restore the preceding PBIX if model objects changed. Confirm the earlier wave's totals, versions and source dates before returning to routine reporting.

For a corrected historical source, preserve the prior revision outside the enabled inventory, update the existing wave's source reference and recheck affected comparisons. Keep its WaveID and question-set identity unchanged unless the actual administered questionnaire changed. Record the correction and its effect on published figures.
