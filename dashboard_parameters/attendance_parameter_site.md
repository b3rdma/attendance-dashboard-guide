# SharePoint site parameter

[Parameter index](attendance_parameters.md)

Create this parameter as **basePath**. Replace the placeholder with the authorised SharePoint site address in Power BI. Use the site URL, rather than a sharing link, page or individual file address.

The parameter is shared by attendance and survey queries when both use it. Changing it can therefore affect both datasets. Inspect each selected file list after a change.

## Power Query definition

```powerquery
// Supply the current parameter value and its existing metadata.
"https://YOUR-TENANT.sharepoint.com/sites/YOUR-SITE" meta [IsParameterQuery = true, IsParameterQueryRequired = false, Type = type any]
```

The parameter metadata does not validate the address or provide credentials. Keep deployment-specific values and credentials outside the shared guide.
