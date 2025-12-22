"""
Data Manager Module
Centralized data loading and caching for all application data sources.
Handles relationships between different data sets.
"""

import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import re


# Configuration - Data source directories
SOURCE_DIR = Path(r"E:\Programming\_python_work\protection-device-management\Data sources\Queries")
MAPPING_DIR = Path(r"E:\Programming\_python_work\protection-device-management\Data sources\mapping")
TYPE_MAPPING_DIR = Path(r"E:\Programming\_python_work\protection-device-management\Data sources\type mapping")


@dataclass
class MappingFile:
    """Represents a mapping file with associated IPS patterns and PF models."""
    filename: str
    ips_patterns: List[str] = field(default_factory=list)  # Multiple IPS patterns
    pf_models: List[str] = field(default_factory=list)  # Multiple PF models
    validated: str = ''


@dataclass
class RelayPattern:
    """Represents an IPS relay pattern summary."""
    pattern: str
    asset: str
    eql_population: int
    powerfactory_model: str = ''
    mapping_file: str = ''


@dataclass
class TypeMappingEntry:
    """Represents a row from the type_mapping.csv file."""
    ips: str
    pf_model: str
    mapping_file: str


@dataclass
class DataCache:
    """Container for all cached application data."""
    relay_patterns: List[RelayPattern] = field(default_factory=list)
    mapping_files: List[MappingFile] = field(default_factory=list)
    type_mapping_entries: List[TypeMappingEntry] = field(default_factory=list)

    # Lookup dictionaries for fast access
    mapping_by_ips_pattern: Dict[str, str] = field(default_factory=dict)  # IPS pattern -> mapping filename

    # Statistics
    ips_total_records: int = 0
    mapping_parse_stats: Dict[str, int] = field(default_factory=lambda: {'total': 0, 'success': 0})


class DataManager:
    """
    Centralized data manager for loading and accessing application data.
    Singleton pattern ensures data is loaded once and shared across all windows.
    """

    _instance: Optional['DataManager'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not DataManager._initialized:
            self.cache = DataCache()
            self._load_all_data()
            DataManager._initialized = True

    def _load_all_data(self):
        """Load all data sources and build relationships."""
        # Load type mapping file first (needed for linking)
        self._load_type_mapping()

        # Load mapping files from directory and link with type_mapping data
        self._load_mapping_files()

        # Build lookup dictionary for IPS pattern -> mapping file
        self._build_mapping_lookup()

        # Load relay patterns and link to mapping files
        self._load_relay_patterns()

    def _load_type_mapping(self):
        """Load the type_mapping.csv file."""
        self.cache.type_mapping_entries = []

        type_mapping_path = TYPE_MAPPING_DIR / "type_mapping.csv"

        try:
            if not type_mapping_path.exists():
                print(f"Type mapping file not found: {type_mapping_path}")
                return

            df = pd.read_csv(type_mapping_path, encoding='utf-8')

            # Expected columns: IPS, PF_MODEL, MAPPING_FILE
            for _, row in df.iterrows():
                ips = str(row.get('IPS', '')).strip() if pd.notna(row.get('IPS', '')) else ''
                pf_model = str(row.get('PF_MODEL', '')).strip() if pd.notna(row.get('PF_MODEL', '')) else ''
                mapping_file = str(row.get('MAPPING_FILE', '')).strip() if pd.notna(row.get('MAPPING_FILE', '')) else ''

                if mapping_file:  # Only add entries with a mapping file
                    self.cache.type_mapping_entries.append(TypeMappingEntry(
                        ips=ips,
                        pf_model=pf_model,
                        mapping_file=mapping_file
                    ))

            print(f"  - Loaded {len(self.cache.type_mapping_entries)} type mapping entries")

        except Exception as e:
            print(f"Error loading type mapping file: {e}")

    def _load_mapping_files(self):
        """Load mapping files from directory and link with type_mapping data."""
        self.cache.mapping_files = []
        total_files = 0
        files_with_mappings = 0

        try:
            if not MAPPING_DIR.exists():
                self.cache.mapping_parse_stats = {'total': 0, 'success': 0}
                return

            # Get all CSV files in the mapping directory
            csv_files = list(MAPPING_DIR.glob('*.csv'))
            total_files = len(csv_files)

            for csv_file in csv_files:
                filename = csv_file.name
                # Get filename without extension for matching with type_mapping
                filename_no_ext = csv_file.stem  # filename without .csv extension

                # Find all type_mapping entries that reference this mapping file
                # Match against filename without extension since type_mapping doesn't include .csv
                matching_entries = [
                    entry for entry in self.cache.type_mapping_entries
                    if entry.mapping_file == filename_no_ext
                ]

                # Collect unique IPS patterns and PF models
                ips_patterns = list(dict.fromkeys(
                    entry.ips for entry in matching_entries if entry.ips
                ))
                pf_models = list(dict.fromkeys(
                    entry.pf_model for entry in matching_entries if entry.pf_model
                ))

                if ips_patterns or pf_models:
                    files_with_mappings += 1

                self.cache.mapping_files.append(MappingFile(
                    filename=filename,
                    ips_patterns=ips_patterns,
                    pf_models=pf_models
                ))

        except Exception as e:
            print(f"Error loading mapping files: {e}")

        # Sort by filename
        self.cache.mapping_files.sort(key=lambda x: x.filename.lower())
        self.cache.mapping_parse_stats = {'total': total_files, 'success': files_with_mappings}

    def _build_mapping_lookup(self):
        """Build lookup dictionary for fast access: IPS pattern -> mapping filename."""
        self.cache.mapping_by_ips_pattern = {}

        for entry in self.cache.type_mapping_entries:
            if entry.ips and entry.mapping_file:
                # Map IPS pattern to its mapping file (add .csv extension for display)
                self.cache.mapping_by_ips_pattern[entry.ips] = entry.mapping_file + '.csv'

    def _load_relay_patterns(self):
        """Load relay patterns from CSV and link to mapping files."""
        self.cache.relay_patterns = []

        csv_path = SOURCE_DIR / "Report-Cache-ProtectionSettingIDs-EX.csv"

        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            self.cache.ips_total_records = len(df)

            # Get unique pattern names
            unique_patterns = df['patternname'].unique()

            for pattern in unique_patterns:
                pattern_rows = df[df['patternname'] == pattern]
                first_asset = pattern_rows['assetname'].iloc[0]
                count = len(pattern_rows)

                # Check for matching mapping file using type_mapping lookup
                mapping_file_name = self.cache.mapping_by_ips_pattern.get(pattern, '')

                self.cache.relay_patterns.append(RelayPattern(
                    pattern=pattern,
                    asset=first_asset,
                    eql_population=count,
                    powerfactory_model='',  # Placeholder for future
                    mapping_file=mapping_file_name
                ))

            # Sort by EQL Population descending
            self.cache.relay_patterns.sort(key=lambda x: x.eql_population, reverse=True)

        except FileNotFoundError:
            print(f"IPS data file not found: {csv_path}")
        except Exception as e:
            print(f"Error loading relay patterns: {e}")

    def get_relay_patterns(self) -> List[RelayPattern]:
        """Get all relay patterns."""
        return self.cache.relay_patterns

    def get_mapping_files(self) -> List[MappingFile]:
        """Get all mapping files."""
        return self.cache.mapping_files

    def get_mapping_parse_stats(self) -> Dict[str, int]:
        """Get mapping file parse statistics."""
        return self.cache.mapping_parse_stats

    def get_ips_total_records(self) -> int:
        """Get total number of IPS records."""
        return self.cache.ips_total_records

    def get_ips_summary_stats(self) -> str:
        """Get summary statistics string for IPS relay patterns."""
        try:
            total_patterns = len(self.cache.relay_patterns)
            if total_patterns == 0:
                return "No data loaded"

            # Count patterns with mapping files
            patterns_with_mapping = sum(
                1 for p in self.cache.relay_patterns if p.mapping_file
            )

            # Calculate percentage of patterns with mapping files
            pattern_percentage = (patterns_with_mapping / total_patterns) * 100

            # Sum total EQL population
            total_eql = sum(p.eql_population for p in self.cache.relay_patterns)

            # Sum EQL population for patterns with mapping files
            eql_with_mapping = sum(
                p.eql_population for p in self.cache.relay_patterns if p.mapping_file
            )

            # Calculate percentage of EQL population with mapping files
            eql_percentage = (eql_with_mapping / total_eql) * 100 if total_eql > 0 else 0

            return (
                f"{pattern_percentage:.1f}% of IPS patterns have mapping files\n"
                f"{eql_percentage:.1f}% of IPS relays have mapping files"
            )
        except Exception:
            return "Under Construction"

    def get_mapping_summary_stats(self) -> str:
        """Get summary statistics string for mapping files."""
        try:
            total_files = len(self.cache.mapping_files)
            if total_files == 0:
                return "No mapping files found"

            # Count mapping files with non-blank validated field
            validated_count = sum(
                1 for mf in self.cache.mapping_files if mf.validated
            )

            return f"{validated_count} of {total_files} mapping files validated"
        except Exception:
            return "Under Construction"

    def refresh_data(self):
        """Reload all data from sources."""
        DataManager._initialized = False
        self.cache = DataCache()
        self._load_all_data()
        DataManager._initialized = True


# Global function to get the data manager instance
def get_data_manager() -> DataManager:
    """Get the singleton DataManager instance."""
    return DataManager()