"""
GrowthGuru AI — Intelligent Column Mapper
==========================================
Provides fuzzy-tolerant, synonym-aware column name normalization.

Normalization rules applied before matching:
  - Strip leading/trailing whitespace
  - Lowercase
  - Remove underscores, hyphens, and extra inner spaces

This is the SINGLE SOURCE OF TRUTH for all column aliases.
Both csv_validator.py and main.py calculate_kpis() must use this module.
"""

import re
from typing import Optional

# ---------------------------------------------------------------------------
# Canonical internal column names
# ---------------------------------------------------------------------------
INTERNAL_PRODUCT_NAME  = "Product_Name"
INTERNAL_QUANTITY      = "Quantity"
INTERNAL_TOTAL_REVENUE = "Total_Revenue"
INTERNAL_CATEGORY      = "Category"
INTERNAL_PRICE         = "Price"
INTERNAL_PROFIT_MARGIN = "Profit_Margin"
INTERNAL_STOCK         = "Stock"
INTERNAL_RATING        = "Customer_Rating"

# ---------------------------------------------------------------------------
# Synonym dictionary
# key   -> canonical internal name
# value -> list of accepted alias strings (will be normalized before matching)
#
# Normalization is applied to BOTH the alias definitions below AND the incoming
# CSV header before comparison (see `_normalize`).
# ---------------------------------------------------------------------------
COLUMN_SYNONYMS: dict[str, list[str]] = {
    INTERNAL_PRODUCT_NAME: [
        "product name",
        "product",
        "item",
        "item name",
        "productname",
        "name",
        "sku name",
        "item description",
        "product title",
        "product description",
    ],
    INTERNAL_QUANTITY: [
        "quantity",
        "qty",
        "units",
        "units sold",
        "sold",
        "sales volume",
        "volume",
        "items sold",
        "pieces sold",
        "no sold",
        "quantity sold",
        "total units",
    ],
    INTERNAL_TOTAL_REVENUE: [
        "revenue",
        "sales",
        "sales amount",
        "total sales",
        "total revenue",
        "turnover",
        "total sales amount",
    ],
    INTERNAL_CATEGORY: [
        "category",
        "product category",
        "department",
        "segment",
        "type",
    ],
    INTERNAL_PRICE: [
        "price",
        "selling price",
        "unit price",
        "mrp",
        "retail price",
        "unit cost",
    ],
    INTERNAL_PROFIT_MARGIN: [
        "profit margin",
        "margin",
        "margin %",
        "gross margin",
        "profit %",
        "profit percentage",
        "profit margin (%)"
    ],
    INTERNAL_STOCK: [
        "stock",
        "inventory",
        "current stock",
        "available stock",
        "stock qty",
        "inventory level",
        "stock level",
    ],
    INTERNAL_RATING: [
        "rating",
        "customer rating",
        "reviews",
        "average rating",
        "avg rating",
        "customer reviews",
    ],
}


def _normalize(col: str) -> str:
    """
    Normalize a column name for matching:
      1. Strip surrounding whitespace
      2. Lowercase
      3. Collapse underscores, hyphens, and multiple spaces into a single space
    """
    return re.sub(r"[\s_\-]+", " ", str(col).strip().lower()).strip()


# Build a fast O(1) lookup table: normalized_alias -> internal_column_name
_ALIAS_LOOKUP: dict[str, str] = {}
for _internal, _aliases in COLUMN_SYNONYMS.items():
    for _alias in _aliases:
        _ALIAS_LOOKUP[_normalize(_alias)] = _internal


def map_column(col: str) -> Optional[str]:
    """
    Map a raw CSV column name to its canonical internal name.

    Returns the canonical name if a known synonym is found, otherwise None.
    This function will NEVER guess — only exact normalized alias matches succeed.
    """
    return _ALIAS_LOOKUP.get(_normalize(col))


def build_column_mapping(raw_columns: list[str]) -> dict[str, str]:
    """
    Given a list of raw CSV column names, return a rename dict:
        { raw_col_name: internal_canonical_name }

    Only columns that match a known synonym are included.
    Unrecognized columns are left as-is (not guessed, not dropped).
    """
    mapping: dict[str, str] = {}
    for col in raw_columns:
        internal = map_column(col)
        if internal is not None:
            mapping[col] = internal
    return mapping


def get_aliases_for(internal_col: str) -> list[str]:
    """
    Return the human-readable list of accepted aliases for a canonical column.
    Used to generate detailed error messages when a required column is missing.
    """
    return COLUMN_SYNONYMS.get(internal_col, [])
