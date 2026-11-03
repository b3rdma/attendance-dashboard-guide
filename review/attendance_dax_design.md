# How the attendance calculations work

[Measure catalogue](../dashboard_measures/attendance_rebuild_measures.md) · [Worked tests](attendance_dax_validation.md)

## Visits and people

Count one visit for every person-meeting row. Count each email once for unique people. One person attending three meetings contributes three visits and one person. The overall unique count is recalculated; it is not the sum of meeting-level unique counts.

## Coverage

The primary measure calculates attended seconds divided by the related meeting's seconds for each visit, then averages those fractions. Each visit has equal weight. The time-weighted companion divides total attended seconds by total possible seconds for those visits. Longer meetings have more weight in that companion.

Keep both numeric and label them distinctly. An undefined denominator produces a blank ratio. Do not silently cap a result above 100%; inspect the source and the matching meeting.

## New and returning

First Session Attended finds one person's earliest occurrence across all retained source history. New Attendees counts that event only when it falls within the current selection. Returning Attendance Events is the remaining visit count. New plus returning equals total visits, including combined-meeting totals.

Repeat Participants instead counts people with at least two selected meetings. A person can be a historical returner while attending only one meeting in the current selection. A repeat-person rate and returning-visit share therefore use different denominators.

## Bands and totals

The Attendance Bands table grows with the number of loaded meetings at refresh. Its measure groups visible people by their selected-meeting count. It stays disconnected from the model, and its total should equal Unique Attendees.

Adding an earlier export changes chronology and can change first-attendance classification. That follows the retained-history definition.

## Filters

Meeting and person lookup fields supply shared selections. Fact-only fields need not filter lookup denominators backwards. Preserve the specified relationship direction and test empty, single-meeting, combined-meeting and person contexts using [the synthetic fixture](attendance_dax_validation.md).
