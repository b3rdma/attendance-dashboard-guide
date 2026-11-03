# Additional attendance questions

[Attendance guide](../attendance_dashboard_guide.md) · [Metric handbook](dashboard_metrics.md)

Start with the defined attendance counts, coverage and return measures. Add a new calculation only when its management question, included records and denominator are clear.

| Question | Possible measure | Additional requirement |
| --- | --- | --- |
| Which meetings reach new people? | First appearances and unique attendees by meeting | Retained history must be consistent |
| How often do people return? | Selected-period repeat people and attendance bands | Keep people distinct from visits |
| Which meetings have shorter attendance? | Coverage distributions and participant minutes | Compare each visit with its own meeting duration |
| How many visits include an action? | Attendance rows with at least one positive action count | Complete numeric action fields and an explicit unknown-data policy |
| How much action is recorded? | Total reactions or activations | Label counts as actions, not people or time |
| Which topics work best? | Compare attendance measures by topic | Add a maintained session/topic mapping |

## Engagement measures

Prepare types using [the engagement addition](attendance_engagement_typing.md). Keep these concepts separate:

- **Breadth:** attendance visits with at least one action.
- **Volume:** total actions across visits.
- **People:** distinct emails associated with those visits.

One visit can contribute to several action categories. Their counts cannot be added to obtain the number of people with any action. A synthetic example with one person giving two reactions contributes two actions and one person.

## Optional report detail

Use [the Session Explorer example](../dashboard_report_pages/attendance_session_explorer.md) to inspect visit-level coverage and selected meetings. Styling and position are optional. Check the measures in a simple table before adding more charts.

A new topic, speaker or invitation-rate question needs its own reliable source. Teams permission roles do not identify who actually delivered a session, and attendance exports do not supply the eligible population.
