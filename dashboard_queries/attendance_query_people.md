# Prepare the person lookup

[Query index](attendance_queries.md) · [Relationships](../dashboard_relationships/attendance_relationships.md)

Create this query as **dimPerson** with Enable load on. It selects Participant Name and Email from attendance, then removes duplicate pairs.

The model assumes one stable display name for each email. If the same email occurs with two names, both pairs remain and Email is no longer unique in this lookup. Choose one intended label for that address in a reviewed change before creating the one-to-many relationship. Changing the person key is a separate decision.

This table contains people who appear in the selected attendance exports. It does not supply an invitation list or identify people who never attended.

## Advanced Editor code

```powerquery
let

    // Derive the person list from the prepared attendance history.
    Source = factAttendance,

    // Remove duplicate name/email pairs, rather than duplicate emails alone.
    DistinctPeople =
        Table.Distinct(
            Table.SelectColumns(
                Source,
                {
                    "Participant Name",
                    "Email"
                }
            )
        )

in

    DistinctPeople
```
