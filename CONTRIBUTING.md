# Maintain the dashboard guide

[Home](README.md) · [Documentation checks](guide/github_guide.md)

Keep the guide clear for someone who did not build the model. Explain what changes, why it matters, which records it includes and how the result was checked.

## Update the relevant reference

| Change | Update |
| --- | --- |
| Source rules | Attendance assumptions/source contract or survey source contract, then affected setup and checks |
| Data preparation | Complete query reference, dependencies and validation |
| Calculation | Measure reference, metric explanation and affected result checks |
| Relationship or column type | Model reference, build steps and acceptance checks |
| Routine update or recovery | Refresh, maintenance or troubleshooting instructions |
| Report appearance | Optional report examples, preserving calculation meanings and selections |

## Write plainly

- Use British English and short, factual sentences. Explain a technical term before relying on it.
- Use one main heading per page and descriptive section headings.
- Use relative Markdown links with .md extensions and valid heading anchors. Encode spaces in image paths as %20.
- Start pages with their heading. Do not add YAML front matter.
- Use powerquery or dax code fences. State whether code is a complete expression or an addition to an existing query.
- State assumptions and the action required if one no longer holds.
- Keep query preparation, calculation meaning and presentation choices distinct.

## Review a change

1. Keep a recovery copy of the model and record the test inputs.
2. Update the smallest relevant set of pages and check the route from the home page.
3. Run the documentation checker and unit tests using the linked instructions.
4. For code or model changes, run the relevant known examples and selection/total checks in Power BI.
5. Record test results separately from generated expected values. Review changed code before updating the integrity manifest.

Use clear commit messages with a prefix such as docs: or fix:.

Publish only generic instructions and synthetic examples. Keep original source records, identifying information, credentials, connection addresses and editable reports outside documentation changes.
