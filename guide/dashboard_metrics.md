# Dashboard metric handbook

[Repository home](../README.md) · [Glossary](dashboard_glossary.md) · [Manager briefing](manager_briefing.md)

Use this reference for the exact meaning of each measure. For a quick introduction, read [what the dashboards show](manager_briefing.md). All worked examples below are invented.

## Attendance: meetings, people and visits

A person attending three meetings creates three **attendance visits** and counts as one **unique attendee** across those meetings. Keep these quantities separate.

| Measure | Plain-English meaning | Important selection rule |
| --- | --- | --- |
| Total Sessions | How many meetings are selected | Selecting a person does not reduce the meeting lookup table. |
| Total Attendance Records | How many person-meeting visits are included | Relies on one source summary row per person per meeting. |
| Unique Attendees | How many different Email values appear in those visits | Count a person once across selected meetings. Do not add per-meeting unique counts to obtain the overall total. |
| Sessions Attended | How many different selected meetings have attendance records | For one person, this is that person's selected-session count. |
| Average Attendees per Session | Included attendance visits divided by all selected meetings | A person selection can leave selected meetings with no attendance from that person in the denominator. |
| Average Attendance Minutes | Mean recorded duration of included visits | Uses Teams' in-meeting duration, rather than first join to final leave. |
| Average Attendance Coverage % | Average fraction of a meeting attended, calculated separately for each visit | Every person-meeting visit has equal weight. This is the primary coverage measure. |
| Time-weighted Attendance Coverage % | Recorded participant time divided by the total possible time for those visits | Longer meetings have more weight. Label it distinctly from primary coverage. |
| Total Attendance Hours | Total recorded time across all included participants | Ten people attending one hour produce ten participant-hours. This is not meeting running time. |
| New Attendees | First recorded attendance events falling in the selection | First means first in all retained source history, not first within the selected period. |
| Returning Attendance Events | Included visits after the person's first retained visit | One person can contribute several returning visits. New plus returning visits equals total visits. |
| Returning Attendance Share % | Returning visits divided by all included visits | A share of visits, rather than the percentage of people who return. |
| Repeat Participants | Included people attending at least two selected meetings | Counts each qualifying person once. Earlier visits outside the selection do not qualify them by themselves. |
| Repeat Participant Rate % | Repeat participants divided by unique attendees | This is the people-based repeat rate. |
| Additional Visits in Selection | Visits remaining after allowing one per unique attendee | A separate optional quantity. It does not count returning people. |
| Additional Visit Share in Selection | Additional visits divided by all selected visits | Do not label it the percentage of people who returned. |
| People in Attendance Band | People grouped by the exact number of selected meetings attended | Selecting fewer meetings can move someone into a lower band. Bands grow when more meetings are loaded. |
| Average Session Attendance | Mean Teams-reported participant summary for the selected meetings | A source-summary comparison. A person selection does not turn this into that person's attendance count. |

First Session Attended and Repeat Participant (Selected Period) are person-level helpers. Use them beside one person's details, rather than as whole-audience totals. Copy the complete definitions from the [attendance rebuild measures](../dashboard_measures/attendance_rebuild_measures.md).

### Coverage example

One person attends all 30 minutes of one meeting. Another attends 30 minutes of a 60-minute meeting.

- Visit coverage is 100% and 50%.
- Primary average coverage is (100% + 50%) / 2 = **75%**.
- Time-weighted coverage is 60 attended minutes / 90 possible minutes = **66.7%**.

Both calculations are valid, but they answer different questions. Keep the primary measure's definition fixed even if the chart style changes.

### Returning visits and repeat people example

Across three meetings, A attends meetings 1 and 2, B attends 2 and 3, and C attends 2.

- There are five visits and three unique people.
- First visits are A at meeting 1, then B and C at meeting 2: three new events.
- A at meeting 2 and B at meeting 3 are returning events: two returning visits, or 40% of visits.
- A and B attend repeatedly in the selection: two of three people, or 66.7%.

Select meeting 3 alone. B has attended before, but does not count as a repeat participant within that one-meeting selection. Adding a previously omitted earlier meeting can change which visit counts as first. That correction is intentional.

## Survey: submissions and answers

One anonymous submission is one response record. It can supply six agreement answers, five tool ratings and several Domain or Support choices. The model cannot prove that each submission came from a different employee.

| Measure family | Plain-English meaning | Percentage base |
| --- | --- | --- |
| Survey Responses | Included anonymous submissions | Count only; not an employee response rate. |
| Confidence Valid Answers | Recognised agreement answers for selected statements and submissions | The count of usable answers, including Neutral. |
| Confidence Response % | Distribution across the five agreement answers | Valid answers to the selected statement in the selected group. |
| Confidence Favourable % | Agree or Strongly agree | Valid answers, including Neutral in the denominator. Missing/unrecognised answers are excluded. |
| Confidence Answer Coverage % | How much of the expected answer block can be scored | All expected submission-question slots. This is completeness, not agreement. |
| Confidence Missing / Unmapped Answers | Unanswered slots or unexpected nonblank wording | Separate quality counts. Do not turn them into Neutral or zero. |
| Confidence Mean Agreement Score | Optional mean of recognised 1–5 agreement codes | Answered items only. It is not a validated maturity score. |
| Survey Domain / Support Responses | Submissions choosing an option or option set | Count each submission once within the selected set. Individual option bars can overlap. |
| Survey Domain / Support Share % | Share choosing each option within its comparison population | Remove that option family's own selection, retaining the other cohort filters. Include unanswered lists in the comparison population. |
| Tool Rating Distribution % | Distribution of recorded numerical codes 1–5 | Valid ratings for that tool and group. Endpoint meanings are still unknown. |
| Tool Rating 5 Count / Share % | Number or share of recorded code-5 answers | Valid ratings for that tool. Code 5 is not yet established as high proficiency. |
| Tool Missing / Invalid Ratings | Unanswered slots or values outside the supported codes | Separate quality counts. |
| Commission Yes / Conditional % | Yes or Depends on the role, separately | Recognised Yes, No and Depends on the role answers. |
| Training Yes % | Yes to development-plan training | Recognised Yes/No answers. |

Interest comparison cards deliberately ignore a selection on their own interest question, while retaining the other cohort controls. Use Survey Responses in categorical charts or interest cross-tabulations. The [complete survey measures](../survey/survey_measures.md) specify the exact filter rules for every expression.

### Agreement and completeness example

Four submissions provide three recognised answers to one statement: Neutral, Agree and Strongly agree. The fourth is unanswered.

- Favourable agreement is two / three valid answers = **66.7%**.
- Answer completeness is three / four opportunities = **75%**.
- The missing answer is excluded from agreement, while still reducing completeness.

For six statements and four submissions, there are 24 answer opportunities. A pooled percentage describes answers across statements; it does not count unique people in one confidence category.

### Multiple choices and comparison shares

Four submissions include two choosing Domain A and three choosing Domain B. One submission may choose both.

- A's share is two / four = **50%**.
- B's share is three / four = **75%**.
- Their sum is 125%, which is valid because choices overlap.

Select Domain A. The headline response count becomes two. A's comparison share remains 50% because that share deliberately uses the population before its own Domain selection. Select a Grade or Support preference and the comparison population changes accordingly. This rule is intentional and must be labelled in the tooltip.

Within one option family, several selected choices mean **any of these**. Across Domain and Support, a response must satisfy **both** selections. Ordinary row counts on an answer table do not apply this rule automatically; use the supplied survey measures.

## Rules for every report page

- Show what is counted and which selection applies. Distinguish people, visits, submissions, answers and option selections.
- Keep counts alongside percentages, including their valid-answer base where relevant.
- Leave a percentage blank when there is no denominator. A real zero is a different result.
- Recalculate totals according to each measure. Do not add distinct counts or average displayed percentages to invent an overall result.
- Use a small table of known values to check a calculation before changing its presentation.

Attendance is evidence of participation, not attention or learning achieved. Survey confidence is self-report, not demonstrated competence. Neither dataset supplies an eligible-population denominator, so neither supports an employee-wide participation rate.
