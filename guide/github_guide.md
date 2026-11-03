# Maintain the documentation

[Home](../README.md) · [Contribution instructions](../CONTRIBUTING.md)

## Keep the reader routes clear

Keep the home page focused on two tasks: understanding the figures and building or maintaining the model. Put exact formulas, test details and proposed extensions in the technical references.

Use relative Markdown links with the destination's exact filename and section anchor. Keep one main heading per page. Do not add YAML front matter or tool-specific navigation syntax.

## Copy code into Power BI

For M, open the named query in Power Query's Advanced Editor and paste the complete code without the Markdown fence. For DAX, use New measure or New table as stated on its reference page.

Keep object names exact. Follow the query order, load settings, relationships, types and sort rules. The site-parameter example is a placeholder; supply the intended SharePoint site in Power BI.

## Check a documentation change

Run from the repository root with Python 3:

```sh
python3 scripts/check_attendance_docs.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The checker validates links, section anchors, formatting and saved code fingerprints. These checks do not refresh Power BI or prove that a formula gives the intended result.

Generate the self-contained test inputs when needed:

```sh
python3 scripts/build_attendance_dax_fixture.py
python3 scripts/build_survey_tests.py
python3 scripts/build_survey_wave_tests.py
```

The generators write synthetic inputs and expected values to temporary folders. They do not execute M or DAX. Follow the relevant validation instructions to run tests in Power BI. The survey-wave suite tests the proposed extension separately from the one-workbook model.

## Change a formula deliberately

1. Explain the intended meaning, included records and percentage base.
2. Test small known examples, totals, empty selections and the affected filters in Power BI.
3. Update the complete reference expression and its explanation together.
4. Review the code change before updating its saved fingerprint.

```sh
python3 scripts/check_attendance_docs.py --update-integrity
python3 scripts/check_attendance_docs.py
```

Updating a fingerprint records a reviewed reference. It does not establish that the calculation is correct.

## Check a public release

Include only the intended guide, generic code and synthetic examples. Keep source files, credentials, local backups and editable reports outside the published material. Review text, images, file metadata and Git history; removing a value from the latest file does not remove earlier committed copies.

After publishing, follow both reader routes and inspect the code blocks, diagrams and images. Check the Documentation checks workflow result in GitHub Actions. Keep deployment access and source connection settings separate from the public guide.
