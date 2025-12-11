# CSV/TXT Difference Notebook

## How to use
- Change `file1_path` and `file2_path` to your files, they should be in the same folder as the notebook.
- If files have headers, set `id_column` to the ID column name and keep `use_header = True`.
- If files do NOT have headers, set `use_header = False` and set `id_index` to the 0-based index of the ID column.
- Delimiters are auto-detected; you can override with `delimiter1`/`delimiter2`.
- Run the cells in order. Reports will be saved within the Outputs folder `id_matches.csv`, `id_only_in_file1.csv`, `id_only_in_file2.csv`, and `id_diff_summary.csv`.

## Purpose of Scripts

This was created based on a request from a team member wanting to compare and understand two CSV files and compare the ID's of each one.

It was also developed as an experiment and learning understanding for myself.

### ID Comparison Notebook (`id_diff.ipynb`)

This Jupyter notebook provides a **CSV/TXT file comparison tool** that analyzes and compares ID values between two files.

#### Core Functionality

**:one: Loads Two Files** :open_file_folder:
   - Supports CSV and TXT formats
   - Auto-detects delimiters (comma, tab, pipe, semicolon)
   - Handles files with or without headers
   - Flexible ID column selection (by name or index)

**:two: ID Comparison & Analysis** :card_index:
   - Extracts and deduplicates IDs from both files
   - Optional fuzzy matching (normalises IDs by removing separators, whitespace, and case differences)
   - Identifies three categories:
     - **Matching IDs** (present in both files)
     - **Only in File 1** (missing from File 2)
     - **Only in File 2** (missing from File 1)

**:three: Visual Results** :bar_chart:
   - Displays a styled table with:
     - Green highlighting for matches
     - Red highlighting for non-matching IDs
     - Color-coded status labels

**:four: Report Generation** :file_cabinet:
   - Saves four CSV reports to an `./Outputs` folder:
     - `id_matches.csv` - IDs found in both files
     - `id_only_in_file1.csv` - IDs unique to File 1
     - `id_only_in_file2.csv` - IDs unique to File 2
     - `id_diff_summary.csv` - Statistical summary of counts

#### :key: Key Features

- **Robust delimiter detection** with validation and fallback logic
- **Data cleaning**: strips whitespace, removes blank IDs
- **Duplicate handling**: removes duplicates within each file
- **Error handling**: validates file paths, column names, and data integrity
- **Pre-validation testing** to ensure proper file parsing before main comparison

#### :briefcase: Use Cases

Perfect for data reconciliation tasks like:
- Account number verification between systems
- Customer ID matching across databases
- Order/transaction ID validation
- Any scenario requiring ID-level file comparison and reporting

> :arrow_right: Some components were aided based on help from GitHub Copilot and a secondary dev :arrow_left:

:new_zealand: :test_tube: :arrow_up_small: