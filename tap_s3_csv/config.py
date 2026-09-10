"""
Tap configuration related stuff
"""

from __future__ import annotations

from voluptuous import Any, Optional, Required, Schema

CONFIG_CONTRACT = Schema(
    [
        {
            Required("table_name"): str,
            Required("search_pattern"): str,
            Optional("key_properties"): [str],
            Optional("search_prefix"): str,
            Optional("date_overrides"): [str],
            Optional("string_overrides"): [str],
            Optional("datatype_overrides"): object,
            Optional("guess_types"): bool,
            Optional("delimiter"): str,
            Optional("table_suffix"): str,
            Optional("remove_character"): str,
            Optional("s3_proxies"): object,
            Optional("encoding"): str,
            # "csv" (default) or "jsonl", one JSON object per line.
            Optional("format"): Any("csv", "jsonl"),
            Optional("set_empty_values_null"): bool,
        }
    ]
)
