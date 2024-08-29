"""
Tap configuration related stuff
"""

from __future__ import annotations

from voluptuous import Optional, Required, Schema

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
            Optional("set_empty_values_null"): bool,
        }
    ]
)
