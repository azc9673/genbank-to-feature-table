# GenBank to Feature Table Converter

This is a simple Python script that converts GenBank files to a 5-column tab-delimited feature table. The script uses Biopython to parse GenBank records and scrapes the current INSDC feature table so the allowed feature keys and qualifiers stay up to date.

## Features

- Input a GenBank file (`.gb` or `.gbk`) and output file on the command line
- Fetch the current allowed features and qualifiers from the INSDC feature table
- Cache the most recent successful INSDC scrape for fallback if the live request fails
- Convert the GenBank file to a 5-column tab-delimited format
- Write converted data to the output file

## Technologies

- [Biopython](https://biopython.org/): toolkit for biological computations
- [Requests](https://pypi.org/project/requests/): HTTP client used to fetch the INSDC feature table
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/): HTML parser used to extract feature and qualifier data

## Installation

1. Clone the repository: `git clone https://github.com/azc9673/genbank-to-feature-table.git`
2. Change into the project directory: `cd genbank-to-feature-table`
3. Install the required packages: `pip install -r requirements.txt`

## Usage

1. Run the converter: `python converter-script.py input_file.gb output_file.tab`
2. The script will try to fetch the latest INSDC feature table on each run.
3. If the live fetch fails or returns incomplete data, the script will fall back to the most recent valid cached scrape.

## Project Structure

- `converter-script.py`: main converter application
- `requirements.txt`: project dependencies
- `README.md`: project documentation
- `.gitignore`: ignored files and directories
- `LICENSE`: project license

## Contact

If you have any questions or feedback, please contact Albert Chen at `azc9673@nyu.edu`.
