# Read the attendance metrics

[Attendance guide](../attendance_dashboard_guide.md) · [Exact rebuild formulas](../dashboard_measures/attendance_rebuild_measures.md)

## Start with the selection

Check which meetings and people are selected before reading any figure. A card, table or chart can also have its own filters and respond to selections elsewhere. The defined meaning depends on the measure and the fields supplying those selections, not on the appearance of the visual.

The full-history view means all matching exports currently retained at source. It does not prove that the source includes every meeting ever held. Use dimSession fields to select meetings and dimPerson fields to select people. A copied meeting field inside factAttendance does not necessarily filter the meeting table in the same way.

Use [the measure catalogue](../dashboard_measures/attendance_rebuild_measures.md) for the formulas. If a result differs, compare the included records, fields, filters and source values before changing the calculation.

## Meetings, visits and different people

One person attending three meetings contributes three attendance visits and one different person across those meetings. Do not add session-level unique-attendee counts to calculate unique people for the whole programme: the same person can appear in several sessions.

| Measure | Read it as |
| --- | --- |
| Total Sessions | Selected meetings, even if the selected people did not attend every one |
| Total Attendance Records | Selected attendance visits |
| Unique Attendees | Different email values among selected visits |
| Sessions Attended | Different meetings represented by selected attendance; for one person, their selected meeting count |
| Average Attendees per Session | Selected visits divided by all selected meetings |
| Average Session Attendance | Mean participant count from selected Teams meeting summaries |

Average Session Attendance follows the meeting summaries, while Average Attendees per Session follows extracted visits. Person selections can make these figures differ because the summary count remains the whole meeting's count. Keep both labels clear if both are shown.

## Recorded time and coverage

Average Attendance Minutes gives the mean length of a selected visit. Total Attendance Hours adds all selected participant time: ten people attending one hour contributes ten hours. Neither establishes how much was learned.

The primary Average Attendance Coverage % calculates a percentage for every selected visit using that visit's own meeting duration, then averages those percentages. A 30-minute attendance at a 60-minute meeting contributes 50%. A full attendance at a 30-minute meeting contributes 100%. Their equal-weight mean is 75%.

Time-weighted Attendance Coverage % is a companion calculation that gives longer attendance opportunities more weight. It divides total attended time by the matching possible participant time. It can differ from the primary average without either being wrong. Use its complete label.

A blank ratio means no usable denominator or selected attendance, rather than measured 0%. A real zero-second attendance contributes zero. Investigate an actual result above 100% in source durations; do not silently cap it. No duration measure is an invitee attendance rate.

## New, returning and repeat are different questions

**New Attendees** counts selected visits that are the person's first appearance in all retained history. A first visit hidden by the current selection still determines whether a later visit is returning. An overlooked earlier export can legitimately change that classification.

**Returning Attendance Events** counts selected visits after that historical first appearance. A person can contribute several returning visits. New Attendees plus Returning Attendance Events equals Total Attendance Records, including at combined-meeting totals.

**Repeat Participants** counts people attending at least two selected meetings. It ignores earlier visits outside the selection for that particular test. A historically returning person can attend only once in the selection and therefore not be a repeat participant in it.

**Additional Visits in Selection** counts visits beyond one per selected person. A person attending three selected meetings contributes two additional visits. This is a visit count, not two different returning people.

| Percentage | Numerator | Denominator |
| --- | --- | --- |
| Returning Attendance Share % | Historically returning visits in the selection | All selected visits |
| Repeat Participant Rate % | People attending at least two selected meetings | Different people in selected visits |
| Additional Visit Share in Selection | Visits beyond one per selected person | All selected visits |

Do not use one of these percentages as a substitute for another. The per-person Repeat Participant (Selected Period) text label belongs in a person table and is blank for a multi-person total.

## Attendance bands

Attendance bands group people by exactly how many selected meetings they attended. Band five means exactly five, not five or more. The rebuild table grows with loaded meetings at refresh. The measure recalculates people's counts as the report selection changes.

If a person attended six meetings and only five of those are selected, that person belongs in band five. At the unfiltered band total, each visible attendee is counted once. The result should match Unique Attendees in the same selection. People with no selected attendance are outside this attended-audience distribution; an eligible-population source would be needed to analyse non-attendees.

## Check before reporting

Reconcile a known meeting with its original export, then test combined meetings and person selections using [the acceptance cases](../review/attendance_dax_validation.md). Retain the source period, source inventory, PBIX version and selections with the reported output. The report layout can change while these definitions remain fixed.
