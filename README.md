# Country GDP ETL Pipeline

A Python script that extracts the list of countries by nominal GDP from an archived Wikipedia page, converts the figures from millions to billions of US dollars, and saves the result to a CSV file and an SQLite database.

## What it does

The script runs a three-stage ETL (Extract, Transform, Load) process:

1. **Extract** – Downloads the archived Wikipedia page *List of countries by GDP (nominal)* and parses it with BeautifulSoup. It reads the IMF GDP table, keeping each country's name and GDP in millions of USD. Rows with no GDP value (shown as `—`) are skipped.
2. **Transform** – Removes the thousands separators from the GDP values, converts them to numbers, divides by 1,000 to get billions of USD, rounds to 2 decimal places, and renames the column from `GDP_USD_millions` to `GDP_USD_billions`.
3. **Load** – Saves the data to a CSV file and to a table in an SQLite database, then runs a query that lists every country with a GDP of at least USD 100 billion.

Each stage is recorded with a timestamp in a log file.

## Requirements

- Python 3.8 or later
- Packages: `requests`, `beautifulsoup4`, `pandas`, `numpy`

`sqlite3` and `datetime` are part of the Python standard library.

Install the packages with:

```bash
pip install requests beautifulsoup4 pandas numpy
```

## Usage

Run the script from the folder that contains it:

```bash
python3 etl_project_gdp.py
```

In the IBM Skills Network lab environment, use:

```bash
python3.11 etl_project_gdp.py
```

The script needs an internet connection to download the source page.

## Output

| File | Contents |
|---|---|
| `Countries_by_GDP.csv` | Country names and GDP in billions of USD |
| `World_Economies.db` | SQLite database with the table `Countries_by_GDP` |
| `etl_project_log.txt` | Timestamped log of each ETL stage |

The query result is also printed to the terminal:

```
SELECT * from Countries_by_GDP WHERE GDP_USD_billions >= 100
          Country  GDP_USD_billions
0   United States          26854.60
1           China          19373.59
...
```

Each run replaces the CSV file and the database table with fresh data. New entries are added to the end of the log file, so earlier runs are kept.

## Configuration

These variables at the top of the script control the source and output locations:

| Variable | Default | Purpose |
|---|---|---|
| `url` | Archived Wikipedia page (2 September 2023) | Source of the GDP data |
| `table_attribs` | `["Country", "GDP_USD_millions"]` | Column names for the extracted data |
| `db_name` | `World_Economies.db` | SQLite database file |
| `table_name` | `Countries_by_GDP` | Database table name |
| `csv_path` | `./Countries_by_GDP.csv` | CSV output path |

## Functions

| Function | Description |
|---|---|
| `extract(url, table_attribs)` | Scrapes the GDP table and returns a DataFrame |
| `transform(df)` | Converts GDP from millions to billions of USD |
| `load_to_csv(df, csv_path)` | Writes the DataFrame to a CSV file |
| `load_to_db(df, sql_connection, table_name)` | Writes the DataFrame to an SQLite table, replacing any existing table |
| `run_query(query_statement, sql_connection)` | Runs an SQL query and prints the result |
| `log_progress(message)` | Appends a timestamped message to the log file |

## Notes

- The script uses an archived copy of the Wikipedia page from the Wayback Machine, so the data reflects GDP figures as of September 2023. Using the archive keeps the page layout fixed, because the extraction depends on the table's position on the page (`tables[2]`). If the source URL is changed, the table index may need to be updated.
- GDP figures come from the IMF estimates column of the source table.
