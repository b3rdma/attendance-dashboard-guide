# Attendance folder parameter

[Parameter index](attendance_parameters.md)

Create this parameter as **attendanceFolder**. Set it to text found in the full folder path of the intended exports. The example value is a folder label, not a complete SharePoint URL.

## Power Query definition

```powerquery
// Supply the current parameter value and its existing metadata.
"L&L Attendance" meta [IsParameterQuery = true, IsParameterQueryRequired = false, Type = type any]
```

The query uses a substring match. Files in matching subfolders are included. Inspect the full Folder Path column after changing this value and keep duplicate exports outside that scope.
