# =============================================================================
# Project  : Inventory_Stock_Project
# Product  : Purchase
# File     : tests/common/test_udfs.py
# Purpose  : Unit tests for src/common/udfs.py — pure Python functions only.
#            No SparkSession required; UDFs are tested as plain callables.
# Rules    : NFR-009, CX-P003
# Task     : TASK-021
# =============================================================================
"""
Unit tests for the two UDFs defined in src/common/udfs.py:

  * format_date_key — ISO date string derivation (CX-P003)
  * safe_trim       — whitespace normalisation with NULL guard (NFR-009)

Each UDF is tested with four boundary cases:
  1. None input         → returns None (NULL guard — NFR-009)
  2. Empty / edge input → correct return value
  3. Boundary value     → correct return value
  4. Representative valid input → correct return value

These tests exercise the plain Python functions directly, which is sufficient
because the Spark UDF registration wrappers (udf(...)) are thin adapters that
do not alter the return value of the underlying callable.
"""

import datetime

import pytest

from src.common.udfs import format_date_key, safe_trim


# ===========================================================================
# format_date_key
# ===========================================================================

class TestFormatDateKey:
    """Tests for format_date_key (CX-P003, NFR-009).

    Contract:
      - None       → None
      - date obj   → "YYYY-MM-DD"
      - datetime   → "YYYY-MM-DD"  (time component discarded)
    """

    # --- NULL guard (NFR-009) -----------------------------------------------

    def test_format_date_key_none_returns_none(self):
        """None input must propagate as None rather than raise an exception.

        This guards against source rows with NULL last_modified_when values
        aborting the pipeline (NFR-009).
        """
        result = format_date_key(None)
        assert result is None, f"Expected None, got {result!r}"

    # --- date object ---------------------------------------------------------

    def test_format_date_key_date_object(self):
        """A datetime.date object is formatted as an ISO date string.

        Boundary case: first day of a month.
        Expected: "2024-01-15"
        """
        result = format_date_key(datetime.date(2024, 1, 15))
        assert result == "2024-01-15", f"Expected '2024-01-15', got {result!r}"

    # --- datetime object (time component must be discarded) ------------------

    def test_format_date_key_datetime_object_truncates_time(self):
        """A datetime.datetime value must return only the date portion.

        The time component (10:30) must be discarded — only "YYYY-MM-DD"
        should be returned (NFR-011 — deterministic, timezone-neutral).
        Expected: "2024-01-15"
        """
        result = format_date_key(datetime.datetime(2024, 1, 15, 10, 30))
        assert result == "2024-01-15", f"Expected '2024-01-15', got {result!r}"

    # --- Boundary: leap-year date -------------------------------------------

    def test_format_date_key_leap_year_date(self):
        """Leap-year date (Feb 29) is formatted correctly without error.

        Boundary value: 2024-02-29 (2024 is a leap year).
        Expected: "2024-02-29"
        """
        result = format_date_key(datetime.date(2024, 2, 29))
        assert result == "2024-02-29", f"Expected '2024-02-29', got {result!r}"


# ===========================================================================
# safe_trim
# ===========================================================================

class TestSafeTrim:
    """Tests for safe_trim (NFR-009, CX-P003, NM-001).

    Contract:
      - None         → None
      - ""           → ""        (empty string is a valid value; returned as-is)
      - "  text  "   → "text"    (leading and trailing whitespace stripped)
      - "   "        → ""        (whitespace-only → empty string after strip)
    """

    # --- NULL guard (NFR-009) -----------------------------------------------

    def test_safe_trim_none_returns_none(self):
        """None input must propagate as None rather than raise an exception.

        Source package names may arrive as NULL from legacy SSAS extracts;
        propagating NULL avoids aborting the pipeline (NFR-009).
        """
        result = safe_trim(None)
        assert result is None, f"Expected None, got {result!r}"

    # --- Empty string --------------------------------------------------------

    def test_safe_trim_empty_string_returns_empty_string(self):
        """An empty string input must return an empty string unchanged.

        Empty string is a valid value that should not be coerced to NULL.
        Expected: ""
        """
        result = safe_trim("")
        assert result == "", f"Expected '', got {result!r}"

    # --- Representative valid input -----------------------------------------

    def test_safe_trim_strips_surrounding_whitespace(self):
        """A string with leading and trailing spaces must be trimmed.

        "  Carton  " represents a padded package name from the legacy source.
        Expected: "Carton"
        """
        result = safe_trim("  Carton  ")
        assert result == "Carton", f"Expected 'Carton', got {result!r}"

    # --- Boundary: whitespace-only string -----------------------------------

    def test_safe_trim_whitespace_only_returns_empty_string(self):
        """A string containing only whitespace characters must return "".

        After stripping, "   " has no remaining characters; the result must
        be "" not None (consistent with the empty-string contract above).
        Expected: ""
        """
        result = safe_trim("   ")
        assert result == "", f"Expected '' for whitespace-only input, got {result!r}"
