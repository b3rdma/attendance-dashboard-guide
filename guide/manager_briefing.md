# What the dashboards show

[Home](../README.md) · [Metric handbook](dashboard_metrics.md) · [Attendance assumptions](attendance_assumptions.md) · [Survey assumptions](../survey/survey_source_contract.md)

The two dashboards answer different questions. Attendance describes recorded participation in meetings. The anonymous survey describes the answers submitted about AI confidence, experience and support.

## Meeting attendance

Teams exports provide the meeting and participant records. Refreshing the model reads the retained files again and recalculates the results.

| Question | Figure to use |
| --- | --- |
| How many meetings are included? | Selected meetings |
| How many different people attended? | Unique attendees |
| How many attendances were recorded? | Visits |
| Are people attending repeatedly? | Repeat participants within the selected meetings |
| How much of each meeting was attended? | Average attendance coverage |

One person attending two meetings and another attending one creates three visits by two people. One of the two people attended repeatedly, so the repeat-person rate is 50%. The second visit is one returning visit out of three, so the returning-visit share is 33.3%.

The figures differ because one counts people and the other counts visits.

## Anonymous AI survey

The survey shows how submissions describe confidence, experience, learning and support preferences. Use the full answer distribution and the number of valid answers when comparing groups.

Suppose four submissions include two agreeing with a statement, one neutral and one unanswered:

- Favourable agreement is two of three valid answers: **66.7%**.
- Answer coverage is three of four expected answers: **75%**.

The unanswered submission reduces coverage. It is not counted as disagreement or Neutral.

Multiple-choice bars can overlap. A submission choosing two support options appears in both option counts, but remains one submission overall.

These are invented examples for explaining the calculations.

## Check the assumptions

The attendance design relies on each person using the same unique email across meetings, complete participant records, one intended export per meeting and a consistent export layout. Session numbering follows date order. Adding an earlier meeting can change which visit is counted as a person's first.

The survey design uses one workbook and one anonymous snapshot. A response ID identifies a submission, rather than a verified person. Agreement questions use a defined scale; other rating codes need their own confirmed meanings before interpretation.

The [attendance assumptions](attendance_assumptions.md) and [survey source contract](../survey/survey_source_contract.md) explain the full rules.

## Interpret the limits

Attendance time is not evidence of attention, learning or improved productivity. Survey confidence is self-report, rather than tested ability. Neither model includes a population list for calculating an overall invitation or response rate.

The anonymous survey cannot identify who attended a meeting. Separate survey charts also cannot show that the same people gave a particular combination of answers without a response-level calculation.

Check the selected meetings or response group before reading a figure. Keep counts and percentage bases visible. Different report layouts are acceptable when the same data and selections give the same results.
