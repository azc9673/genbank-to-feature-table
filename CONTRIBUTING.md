# Contributing

Thanks for contributing to `genbank-to-feature-table`.

This project is a small Python utility for converting GenBank files into a 5-column feature table while validating feature keys and qualifiers against the current INSDC feature table. Contributions are welcome for bug fixes, documentation improvements, validation logic, and workflow improvements.

## Before You Start

- Read [README.md](README.md) for the current installation and usage flow.
- Check existing issues and pull requests before starting overlapping work.
- Prefer small, focused pull requests over large mixed changes.
- Consult the [Code of Conduct](CODE_OF_CONDUCT.md)

## Development Setup

1. Clone the repository and move into it:

```powershell
git clone https://github.com/azc9673/genbank-to-feature-table.git
cd genbank-to-feature-table
```

2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Making Changes

- Keep changes targeted to a single problem or improvement.
- Preserve the command-line interface unless the change intentionally updates user-facing behavior.
- If you change how feature or qualifier validation works, make sure the fallback cache behavior still makes sense.
- Update [README.md](README.md) when usage, installation, or expected behavior changes.
- Do not commit generated local cache files such as `.insdc_feature_table_cache.json`.

## Code Style

- Follow standard Python style conventions and keep the script readable.
- Prefer clear function boundaries and descriptive names over clever shortcuts.
- Add comments only where they improve understanding of non-obvious logic.
- Keep dependencies minimal unless a new dependency clearly improves maintainability or correctness.

## Testing and Validation

Recommended checks for creating tests on new features:

1. Run the script against a known `.gb` or `.gbk` file:

```powershell
python converter-script.py input_file.gb output_file.tab
```

2. Confirm that:

- the output file is created successfully
- valid features are preserved in the output
- unsupported features or qualifiers are skipped as expected
- live INSDC fetches still work when network access is available
- cached fallback behavior still works when the live fetch is unavailable

3. If your change affects parsing or formatting, include a short example in the pull request description showing the expected behavior.

## Pull Requests

When opening a pull request, please include:

- a short summary of the change
- the reason for the change
- any manual validation you performed
- example input/output notes if behavior changed

## Reporting Issues

Bug reports are most helpful when they include:

- the command you ran
- a sample input file
- the error message or unexpected output
- your Python version and operating system

## Questions

If you are unsure whether a change fits the project, please feel free to open an issue or contact the owner.
