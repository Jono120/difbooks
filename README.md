# CSV/TXT Difference Notebook

## How to use
- Set `file1_path` and `file2_path` to your files.
- If files have headers, set `id_column` to the ID column name and keep `use_header = True`.
- If files do NOT have headers, set `use_header = False` and set `id_index` to the 0-based index of the ID column.
- Delimiters are auto-detected; you can override with `delimiter1`/`delimiter2`.
- Run the cells in order. Reports will be saved within the Outputs folder `id_matches.csv`, `id_only_in_file1.csv`, `id_only_in_file2.csv`, and `id_diff_summary.csv`.

## Purpose of scripts
