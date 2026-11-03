# Source parameters

[Attendance build](../guide/attendance_rebuild.md) · [Source setup](../guide/attendance_setup.md)

A parameter is a saved setting used by a query. Create these exact names before the attendance queries:

| Parameter | Purpose |
| --- | --- |
| [basePath](attendance_parameter_site.md) | SharePoint site address |
| [attendanceFolder](attendance_parameter_folder.md) | Text used to select the attendance folder |

The survey can reuse basePath when it uses the same site. Its capabilityFolder parameter selects the survey source separately.

## Optional metadata clarity

The examples retain IsParameterQueryRequired = false and Type = type any. Those settings do not make an empty value usable. Supply text values for both parameters. Required/Text metadata can make the intended input clearer, but it does not validate the site, folder boundary or access rights.
