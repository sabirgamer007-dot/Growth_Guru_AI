import pandas as pd
import io
from typing import Tuple

from .column_mapper import (
    build_column_mapping,
    get_aliases_for,
    INTERNAL_PRODUCT_NAME,
    INTERNAL_QUANTITY,
    INTERNAL_TOTAL_REVENUE,
)


class CSVValidationError(Exception):
    pass


# Columns that MUST be present after mapping (using internal canonical names)
REQUIRED_COLUMNS = {INTERNAL_PRODUCT_NAME, INTERNAL_QUANTITY, INTERNAL_TOTAL_REVENUE}


def _missing_column_error(missing_col: str, detected_cols: list[str]) -> str:
    """
    Build a clear, human-friendly error message when a required column is absent.

    Tells the user:
      - Which required column was not found
      - What columns were detected in the CSV
      - Which aliases are accepted for that column
    """
    aliases = get_aliases_for(missing_col)
    aliases_text = ", ".join(f'"{a}"' for a in aliases)
    detected_text = ", ".join(f'"{c}"' for c in detected_cols)

    return (
        f'Required column "{missing_col}" not found.\n\n'
        f"Detected columns:\n  {detected_text}\n\n"
        f"Supported aliases for \"{missing_col}\":\n  {aliases_text}"
    )


def validate_csv_structure(contents: bytes) -> Tuple[bool, str, pd.DataFrame]:
    """
    Stage 1 Local Validation
    Validates the structure and sanity of the CSV contents without any AI.
    Checks for encoding, readability, empty CSV, duplicate headers, missing columns, sparse data.

    Uses intelligent column mapping so that common synonyms (e.g. "Qty" for "Quantity",
    "Sales" for "Total_Revenue", "Item" for "Product_Name") are accepted automatically.
    """
    try:
        # ------------------------------------------------------------------ #
        # 1. Readability & encoding check                                     #
        # ------------------------------------------------------------------ #
        try:
            df = pd.read_csv(io.BytesIO(contents))
        except pd.errors.EmptyDataError:
            return False, "CSV file is completely empty.", pd.DataFrame()
        except pd.errors.ParserError:
            return False, "CSV is malformed or corrupted.", pd.DataFrame()
        except UnicodeDecodeError:
            return False, "Invalid encoding. Please upload a UTF-8 encoded CSV.", pd.DataFrame()

        if df.empty:
            return False, "CSV contains no data rows.", df

        # ------------------------------------------------------------------ #
        # 2. Duplicate headers check                                          #
        # ------------------------------------------------------------------ #
        if len(df.columns) != len(set(df.columns)):
            duplicates = df.columns[df.columns.duplicated()].tolist()
            return False, f"CSV contains duplicate headers: {', '.join(duplicates)}", df

        # ------------------------------------------------------------------ #
        # 3. Intelligent column mapping (synonym normalization)               #
        #    Uses the centralized column_mapper — the ONLY place aliases are  #
        #    defined, so validator and KPI calculator always stay in sync.    #
        # ------------------------------------------------------------------ #
        original_columns = df.columns.tolist()
        col_map = build_column_mapping(original_columns)
        df = df.rename(columns=col_map)

        # ------------------------------------------------------------------ #
        # 4. Required column presence check (with detailed error messages)    #
        # ------------------------------------------------------------------ #
        for required_col in [INTERNAL_PRODUCT_NAME, INTERNAL_QUANTITY, INTERNAL_TOTAL_REVENUE]:
            if required_col not in df.columns:
                error_msg = _missing_column_error(required_col, original_columns)
                return False, error_msg, df

        # ------------------------------------------------------------------ #
        # 5. Sparse data sanity check                                         #
        # ------------------------------------------------------------------ #
        if df[INTERNAL_PRODUCT_NAME].isna().sum() > len(df) * 0.9:
            return False, "Extremely sparse data: Missing Product Names in over 90% of rows.", df

        return True, "Valid", df

    except Exception as e:
        return False, f"Unexpected error during validation: {str(e)}", pd.DataFrame()
