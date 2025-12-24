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
import json
import ast
import os
from datetime import datetime


# Configuration - Project root directory (where the application files are located)
PROJECT_ROOT = Path(__file__).parent

# Configuration - Data source directories
# External data sources (absolute paths - may need updating when moving to new environment)
SOURCE_DIR = Path(r"Q:\DATA\QueryCsvCache")
MAPPING_DIR = Path(r"Y:\PROTECTION\STAFF\Dan Park\PowerFactory\Dan script development\ips_to_pf\mapping_files\relay_maps")
TYPE_MAPPING_DIR = Path(r"Y:\PROTECTION\STAFF\Dan Park\PowerFactory\Dan script development\ips_to_pf\mapping_files\type_mapping")
LOGS_DIR = Path(r"Y:\PROTECTION\STAFF\Dan Park\PowerFactory\Dan script development\ips_to_pf\results_log")

# Project-relative data sources (stored within the project directory)
PF_RELAY_MODELS_DIR = PROJECT_ROOT / "pf_relay_models"
PF_FUSE_MODELS_DIR = PROJECT_ROOT / "pf_fuse_models"
PF_DEVICE_VALIDATION_DIR = PROJECT_ROOT / "pf_device_validation"
MAPPING_VALIDATION_DIR = PROJECT_ROOT / "ips_to_pf_mapping_file_validation"
FUSE_DATASHEET_DIR = PROJECT_ROOT / "fuse_datasheets"

# Legacy constant for backwards compatibility (points to relay models dir)
PF_TYPES_DIR = PF_RELAY_MODELS_DIR


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
    source: str = ''  # 'SEQ' or 'Regional'
    powerfactory_model: str = ''
    mapping_file: str = ''


@dataclass
class TypeMappingEntry:
    """Represents a row from the type_mapping.csv file."""
    ips: str
    pf_model: str
    mapping_file: str


@dataclass
class ScriptRunLog:
    """Represents a summary of a script run from the log file."""
    timestamp: str
    substation: str
    num_transfers: int
    success_percentage: float


@dataclass
class FailedTransfer:
    """Represents a failed device transfer from the log file."""
    timestamp: str
    substation: str
    device_name: str
    result: str


@dataclass
class RelayModel:
    """Represents a PowerFactory relay model."""
    manufacturer: str
    model: str
    used_in_eql: str
    model_validated: str
    ips_mapping_file_exists: str


@dataclass
class FuseModel:
    """Represents a PowerFactory fuse model."""
    fuse: str
    fuse_type: str
    eql_standard: str
    fuse_datasheet: str


@dataclass
class DataCache:
    """Container for all cached application data."""
    relay_patterns_seq: List[RelayPattern] = field(default_factory=list)
    relay_patterns_regional: List[RelayPattern] = field(default_factory=list)
    mapping_files: List[MappingFile] = field(default_factory=list)
    type_mapping_entries: List[TypeMappingEntry] = field(default_factory=list)
    script_run_logs: List[ScriptRunLog] = field(default_factory=list)
    failed_transfers: List[FailedTransfer] = field(default_factory=list)
    relay_models: List[RelayModel] = field(default_factory=list)
    fuse_models: List[FuseModel] = field(default_factory=list)

    # Lookup dictionaries for fast access
    mapping_by_ips_pattern: Dict[str, str] = field(default_factory=dict)  # IPS pattern -> mapping filename
    mapping_by_pf_model: Dict[str, List[str]] = field(default_factory=dict)  # PF_MODEL -> list of mapping filenames

    # Validation lookup sets
    validated_pf_devices: Set[str] = field(default_factory=set)  # Set of validated PowerFactory device models
    validated_mapping_files: Set[str] = field(default_factory=set)  # Set of validated mapping file names
    fuse_datasheets: Set[str] = field(default_factory=set)  # Set of fuses with datasheets

    # Statistics
    ips_total_records_seq: int = 0
    ips_total_records_regional: int = 0
    mapping_parse_stats: Dict[str, int] = field(default_factory=lambda: {'total': 0, 'success': 0})
    script_log_stats: Dict[str, int] = field(default_factory=lambda: {'total_runs': 0, 'total_failures': 0})

    # File modification dates
    relay_models_last_modified: str = ''
    fuse_models_last_modified: str = ''


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
        # Load validation log files first (needed for populating validation fields)
        self._load_validation_logs()

        # Load type mapping file first (needed for linking)
        self._load_type_mapping()

        # Load mapping files from directory and link with type_mapping data
        self._load_mapping_files()

        # Build lookup dictionary for IPS pattern -> mapping file
        self._build_mapping_lookup()

        # Load relay patterns and link to mapping files
        self._load_relay_patterns()

        # Load script run logs
        self._load_script_logs()

        # Load PowerFactory relay models
        self._load_relay_models()

        # Load PowerFactory fuse models
        self._load_fuse_models()

    def _load_validation_logs(self):
        """Load all validation log CSV files."""
        # Load PowerFactory device validation log
        self._load_pf_device_validation_log()

        # Load IPS to PF mapping file validation log
        self._load_mapping_validation_log()

        # Load Fuse datasheet log
        self._load_fuse_datasheet_log()

    def _load_pf_device_validation_log(self):
        """Load PowerFactory device validation log CSV file."""
        self.cache.validated_pf_devices = set()

        validation_log_path = PF_DEVICE_VALIDATION_DIR / "PowerFactory device validation log.csv"

        try:
            if not validation_log_path.exists():
                print(f"PowerFactory device validation log not found: {validation_log_path}")
                return

            df = pd.read_csv(validation_log_path, encoding='utf-8')

            if len(df.columns) > 0:
                # Get values from the first column
                first_col = df.columns[0]
                for value in df[first_col].dropna():
                    value_str = str(value).strip()
                    if value_str:
                        self.cache.validated_pf_devices.add(value_str)

            print(f"  - Loaded {len(self.cache.validated_pf_devices)} validated PowerFactory devices")

        except Exception as e:
            print(f"Error loading PowerFactory device validation log: {e}")

    def _load_mapping_validation_log(self):
        """Load IPS to PF mapping file validation log CSV file."""
        self.cache.validated_mapping_files = set()

        validation_log_path = MAPPING_VALIDATION_DIR / "IPS to PF mapping file validation log.csv"

        try:
            if not validation_log_path.exists():
                print(f"Mapping file validation log not found: {validation_log_path}")
                return

            df = pd.read_csv(validation_log_path, encoding='utf-8')

            if len(df.columns) > 0:
                # Get values from the first column
                first_col = df.columns[0]
                for value in df[first_col].dropna():
                    value_str = str(value).strip()
                    if value_str:
                        self.cache.validated_mapping_files.add(value_str)

            print(f"  - Loaded {len(self.cache.validated_mapping_files)} validated mapping files")

        except Exception as e:
            print(f"Error loading mapping file validation log: {e}")

    def _load_fuse_datasheet_log(self):
        """Load Fuse datasheet log CSV file."""
        self.cache.fuse_datasheets = set()

        datasheet_log_path = FUSE_DATASHEET_DIR / "Fuse datasheet log.csv"

        try:
            if not datasheet_log_path.exists():
                print(f"Fuse datasheet log not found: {datasheet_log_path}")
                return

            df = pd.read_csv(datasheet_log_path, encoding='utf-8')

            if len(df.columns) > 0:
                # Get values from the first column
                first_col = df.columns[0]
                for value in df[first_col].dropna():
                    value_str = str(value).strip()
                    if value_str:
                        self.cache.fuse_datasheets.add(value_str)

            print(f"  - Loaded {len(self.cache.fuse_datasheets)} fuses with datasheets")

        except Exception as e:
            print(f"Error loading fuse datasheet log: {e}")

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

                # Check if this mapping file is validated (match against filename without extension)
                validated = 'Yes' if filename_no_ext in self.cache.validated_mapping_files else ''

                self.cache.mapping_files.append(MappingFile(
                    filename=filename,
                    ips_patterns=ips_patterns,
                    pf_models=pf_models,
                    validated=validated
                ))

        except Exception as e:
            print(f"Error loading mapping files: {e}")

        # Sort by filename
        self.cache.mapping_files.sort(key=lambda x: x.filename.lower())
        self.cache.mapping_parse_stats = {'total': total_files, 'success': files_with_mappings}

    def _build_mapping_lookup(self):
        """Build lookup dictionaries for fast access."""
        self.cache.mapping_by_ips_pattern = {}
        self.cache.mapping_by_pf_model = {}

        for entry in self.cache.type_mapping_entries:
            # Map IPS pattern to its mapping file (add .csv extension for display)
            if entry.ips and entry.mapping_file:
                self.cache.mapping_by_ips_pattern[entry.ips] = entry.mapping_file + '.csv'

            # Map PF_MODEL to its mapping files (can have multiple)
            if entry.pf_model and entry.mapping_file:
                mapping_filename = entry.mapping_file + '.csv'
                if entry.pf_model not in self.cache.mapping_by_pf_model:
                    self.cache.mapping_by_pf_model[entry.pf_model] = []
                # Avoid duplicates
                if mapping_filename not in self.cache.mapping_by_pf_model[entry.pf_model]:
                    self.cache.mapping_by_pf_model[entry.pf_model].append(mapping_filename)

    def _load_relay_patterns(self):
        """Load relay patterns from both SEQ and Regional CSV files and link to mapping files."""
        self.cache.relay_patterns_seq = []
        self.cache.relay_patterns_regional = []

        # Load SEQ data source
        seq_csv_path = SOURCE_DIR / "Report-Cache-ProtectionSettingIDs-EX.csv"
        self._load_relay_patterns_from_file(seq_csv_path, 'SEQ')

        # Load Regional data source
        regional_csv_path = SOURCE_DIR / "Report-Cache-ProtectionSettingIDs-EE.csv"
        self._load_relay_patterns_from_file(regional_csv_path, 'Regional')

    def _load_relay_patterns_from_file(self, csv_path: Path, source: str):
        """Load relay patterns from a specific CSV file."""
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            total_records = len(df)

            # Update total records for the appropriate source
            if source == 'SEQ':
                self.cache.ips_total_records_seq = total_records
            else:
                self.cache.ips_total_records_regional = total_records

            # Get unique pattern names
            unique_patterns = df['patternname'].unique()

            patterns_list = []
            for pattern in unique_patterns:
                pattern_rows = df[df['patternname'] == pattern]
                first_asset = pattern_rows['assetname'].iloc[0]
                count = len(pattern_rows)

                # Check for matching mapping file using type_mapping lookup
                mapping_file_name = self.cache.mapping_by_ips_pattern.get(pattern, '')

                patterns_list.append(RelayPattern(
                    pattern=pattern,
                    asset=first_asset,
                    eql_population=count,
                    source=source,
                    powerfactory_model='',  # Placeholder for future
                    mapping_file=mapping_file_name
                ))

            # Sort by EQL Population descending
            patterns_list.sort(key=lambda x: x.eql_population, reverse=True)

            # Add to appropriate cache list
            if source == 'SEQ':
                self.cache.relay_patterns_seq = patterns_list
            else:
                self.cache.relay_patterns_regional = patterns_list

            print(f"  - Loaded {len(patterns_list)} {source} relay patterns from {total_records} records")

        except FileNotFoundError:
            print(f"{source} IPS data file not found: {csv_path}")
        except Exception as e:
            print(f"Error loading {source} relay patterns: {e}")

    def _load_script_logs(self):
        """
        Load script run logs from the JSON log file.

        Processing rules:
        1. Only top-level dictionaries (Dicts) with "message": "Data capture list: [...]" are processed
        2. Each Dict contains an embedded list of dictionaries in the message string
        3. For "Log of All Script Runs" table - one row per Dict:
           - Timestamp: Dict["timestamp"]
           - Substation: First 'SUBSTATION' value from the embedded list
           - Number of Transfers: Length of the embedded list
           - Percentage Successful Transfers: (items without 'RESULT' key / total) * 100
        4. For "Log of All Failed Device Transfers" table:
           - Convert embedded list to table rows
           - Add Timestamp column from Dict["timestamp"]
           - Remove rows with blank/missing RESULT (keep only rows WITH 'RESULT' key)
           - Concatenate all Dict tables into one
        """
        self.cache.script_run_logs = []
        self.cache.failed_transfers = []

        log_file_path = LOGS_DIR / "ips_to_pf.log"

        try:
            if not log_file_path.exists():
                print(f"Log file not found: {log_file_path}")
                self.cache.script_log_stats = {'total_runs': 0, 'total_failures': 0}
                return

            # Read the JSON log file (one JSON object per line)
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()

            for line in log_lines:
                line = line.strip()
                if not line:
                    continue

                try:
                    # Parse each line as a top-level dictionary (Dict)
                    dict_entry = json.loads(line)
                    message = dict_entry.get('message', '')

                    # Rule 1: Only process Dicts that have "message": "Data capture list: [...]"
                    if not message.startswith('Data capture list:'):
                        continue

                    # Get timestamp from Dict
                    timestamp = dict_entry.get('timestamp', '')
                    formatted_timestamp = self._format_timestamp(timestamp)

                    # Rule 2: Parse the embedded list of dictionaries from the message string
                    # Message format: "Data capture list: [{'SUBSTATION': 'BHL', ...}, ...]"
                    list_start = message.find('[')
                    list_end = message.rfind(']') + 1

                    if list_start == -1 or list_end <= list_start:
                        continue

                    list_str = message[list_start:list_end]

                    try:
                        # Parse the Python-style list using ast.literal_eval
                        embedded_list = ast.literal_eval(list_str)

                        if not isinstance(embedded_list, list) or len(embedded_list) == 0:
                            continue

                        # === Build "Log of All Script Runs" table row ===
                        # Substation: first 'SUBSTATION' value from embedded list
                        substation = embedded_list[0].get('SUBSTATION', 'Unknown')

                        # Number of Transfers: length of embedded list
                        num_transfers = len(embedded_list)

                        # Percentage Successful Transfers: items WITHOUT 'RESULT' key / total * 100
                        successful_count = sum(1 for item in embedded_list if 'RESULT' not in item)
                        success_percentage = (successful_count / num_transfers * 100) if num_transfers > 0 else 0

                        self.cache.script_run_logs.append(ScriptRunLog(
                            timestamp=formatted_timestamp,
                            substation=substation,
                            num_transfers=num_transfers,
                            success_percentage=success_percentage
                        ))

                        # === Build "Log of All Failed Device Transfers" table rows ===
                        # Rule 4: Only keep rows that HAVE a 'RESULT' key (remove blank/NaN Result rows)
                        for item in embedded_list:
                            # Check if 'RESULT' key exists and has a non-empty value
                            if 'RESULT' in item:
                                result_value = item.get('RESULT', '')
                                # Skip if RESULT is blank/empty/None
                                if result_value is None or (isinstance(result_value, str) and result_value.strip() == ''):
                                    continue

                                # Rule 3: Add Timestamp column from Dict["timestamp"]
                                self.cache.failed_transfers.append(FailedTransfer(
                                    timestamp=formatted_timestamp,
                                    substation=item.get('SUBSTATION', 'Unknown'),
                                    device_name=item.get('DEVICE NAME', 'Unknown'),
                                    result=result_value
                                ))

                    except (ValueError, SyntaxError) as e:
                        print(f"Error parsing data capture list: {e}")
                        continue

                except json.JSONDecodeError as e:
                    print(f"Error parsing log line: {e}")
                    continue

            # Rule 5: All Dict tables are concatenated (done via appending to self.cache.failed_transfers)

            # Update statistics
            self.cache.script_log_stats = {
                'total_runs': len(self.cache.script_run_logs),
                'total_failures': len(self.cache.failed_transfers)
            }

            print(f"  - Loaded {len(self.cache.script_run_logs)} script run logs")
            print(f"  - Loaded {len(self.cache.failed_transfers)} failed transfers")

        except Exception as e:
            print(f"Error loading script logs: {e}")
            self.cache.script_log_stats = {'total_runs': 0, 'total_failures': 0}

    def _load_relay_models(self):
        """Load PowerFactory relay models from CSV file."""
        self.cache.relay_models = []
        self.cache.relay_models_last_modified = ''

        relay_models_path = PF_RELAY_MODELS_DIR / "pf_relay_models.csv"

        try:
            if not relay_models_path.exists():
                print(f"Relay models file not found: {relay_models_path}")
                return

            # Get file modification date
            mod_timestamp = os.path.getmtime(relay_models_path)
            mod_date = datetime.fromtimestamp(mod_timestamp)
            self.cache.relay_models_last_modified = mod_date.strftime('%d/%m/%Y')

            df = pd.read_csv(relay_models_path, encoding='utf-8')

            for _, row in df.iterrows():
                manufacturer = str(row.get('Manufacturer', '')).strip() if pd.notna(row.get('Manufacturer', '')) else ''
                model = str(row.get('Model', '')).strip() if pd.notna(row.get('Model', '')) else ''
                used_in_eql = str(row.get('Used in EQL', '')).strip() if pd.notna(row.get('Used in EQL', '')) else ''

                # Check if this model is validated based on the validation log
                model_validated = 'Yes' if model in self.cache.validated_pf_devices else ''

                # Look up IPS mapping files from type_mapping based on PF_MODEL match
                mapping_files = self.cache.mapping_by_pf_model.get(model, [])
                ips_mapping_file_exists = ', '.join(mapping_files) if mapping_files else ''

                self.cache.relay_models.append(RelayModel(
                    manufacturer=manufacturer,
                    model=model,
                    used_in_eql=used_in_eql,
                    model_validated=model_validated,
                    ips_mapping_file_exists=ips_mapping_file_exists
                ))

            print(f"  - Loaded {len(self.cache.relay_models)} relay models")

        except Exception as e:
            print(f"Error loading relay models: {e}")

    def _load_fuse_models(self):
        """Load PowerFactory fuse models from CSV file."""
        self.cache.fuse_models = []
        self.cache.fuse_models_last_modified = ''

        fuse_models_path = PF_FUSE_MODELS_DIR / "pf_fuse_models.csv"

        try:
            if not fuse_models_path.exists():
                print(f"Fuse models file not found: {fuse_models_path}")
                return

            # Get file modification date
            mod_timestamp = os.path.getmtime(fuse_models_path)
            mod_date = datetime.fromtimestamp(mod_timestamp)
            self.cache.fuse_models_last_modified = mod_date.strftime('%d/%m/%Y')

            df = pd.read_csv(fuse_models_path, encoding='utf-8')

            for _, row in df.iterrows():
                fuse = str(row.get('Fuse', '')).strip() if pd.notna(row.get('Fuse', '')) else ''
                fuse_type = str(row.get('Type', '')).strip() if pd.notna(row.get('Type', '')) else ''
                eql_standard = str(row.get('EQL Standard', '')).strip() if pd.notna(row.get('EQL Standard', '')) else ''

                # Check if this fuse has a datasheet based on the datasheet log
                fuse_datasheet = 'Yes' if fuse in self.cache.fuse_datasheets else ''

                self.cache.fuse_models.append(FuseModel(
                    fuse=fuse,
                    fuse_type=fuse_type,
                    eql_standard=eql_standard,
                    fuse_datasheet=fuse_datasheet
                ))

            print(f"  - Loaded {len(self.cache.fuse_models)} fuse models")

        except Exception as e:
            print(f"Error loading fuse models: {e}")

    def _format_timestamp(self, timestamp_str: str) -> str:
        """Format ISO timestamp for display."""
        try:
            # Parse ISO format timestamp
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            # Format for display: YYYY-MM-DD HH:MM:SS
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return timestamp_str

    def get_relay_patterns(self, include_seq: bool = True, include_regional: bool = True) -> List[RelayPattern]:
        """Get relay patterns filtered by source."""
        patterns = []
        if include_seq:
            patterns.extend(self.cache.relay_patterns_seq)
        if include_regional:
            patterns.extend(self.cache.relay_patterns_regional)
        # Sort combined list by EQL Population descending
        patterns.sort(key=lambda x: x.eql_population, reverse=True)
        return patterns

    def get_seq_patterns(self) -> List[RelayPattern]:
        """Get SEQ relay patterns only."""
        return self.cache.relay_patterns_seq

    def get_regional_patterns(self) -> List[RelayPattern]:
        """Get Regional relay patterns only."""
        return self.cache.relay_patterns_regional

    def get_mapping_files(self) -> List[MappingFile]:
        """Get all mapping files."""
        return self.cache.mapping_files

    def get_mapping_parse_stats(self) -> Dict[str, int]:
        """Get mapping file parse statistics."""
        return self.cache.mapping_parse_stats

    def get_ips_total_records(self, include_seq: bool = True, include_regional: bool = True) -> int:
        """Get total number of IPS records."""
        total = 0
        if include_seq:
            total += self.cache.ips_total_records_seq
        if include_regional:
            total += self.cache.ips_total_records_regional
        return total

    def get_script_run_logs(self) -> List[ScriptRunLog]:
        """Get all script run logs."""
        return self.cache.script_run_logs

    def get_failed_transfers(self) -> List[FailedTransfer]:
        """Get all failed transfers."""
        return self.cache.failed_transfers

    def get_script_log_stats(self) -> Dict[str, int]:
        """Get script log statistics."""
        return self.cache.script_log_stats

    def get_relay_models(self) -> List[RelayModel]:
        """Get all PowerFactory relay models."""
        return self.cache.relay_models

    def get_fuse_models(self) -> List[FuseModel]:
        """Get all PowerFactory fuse models."""
        return self.cache.fuse_models

    def get_relay_models_last_modified(self) -> str:
        """Get the last modified date of the relay models file."""
        return self.cache.relay_models_last_modified

    def get_fuse_models_last_modified(self) -> str:
        """Get the last modified date of the fuse models file."""
        return self.cache.fuse_models_last_modified

    def _calculate_relay_mapping_percentage(self, patterns: List[RelayPattern]) -> float:
        """Calculate percentage of devices (EQL population) that have mapping files."""
        if not patterns:
            return 0.0
        total_relays = sum(p.eql_population for p in patterns)
        if total_relays == 0:
            return 0.0
        relays_with_mapping = sum(p.eql_population for p in patterns if p.mapping_file)
        return (relays_with_mapping / total_relays) * 100

    def get_ips_summary_stats(self) -> str:
        """Get summary statistics string for IPS relay patterns (SEQ and Regional separately)."""
        try:
            seq_patterns = self.cache.relay_patterns_seq
            regional_patterns = self.cache.relay_patterns_regional

            if not seq_patterns and not regional_patterns:
                return "No data loaded"

            # Calculate percentage of SEQ relays with mapping files
            seq_percentage = self._calculate_relay_mapping_percentage(seq_patterns)

            # Calculate percentage of Regional relays with mapping files
            regional_percentage = self._calculate_relay_mapping_percentage(regional_patterns)

            return (
                f"{seq_percentage:.1f}% of SEQ IPS devices have mapping files\n"
                f"{regional_percentage:.1f}% of Regional IPS devices have mapping files"
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

    def get_script_maintenance_summary_stats(self) -> str:
        """Get summary statistics string for script maintenance."""
        try:
            total_runs = len(self.cache.script_run_logs)

            if total_runs == 0:
                return "No script runs logged"

            # Calculate weighted % successful transfers
            # Weight each run's success percentage by its number of transfers
            total_transfers = sum(log.num_transfers for log in self.cache.script_run_logs)

            if total_transfers > 0:
                # Weighted sum: sum of (success_percentage * num_transfers) / total_transfers
                weighted_success = sum(
                    (log.success_percentage / 100) * log.num_transfers
                    for log in self.cache.script_run_logs
                ) / total_transfers * 100
            else:
                weighted_success = 0

            return (
                f"{total_runs} script run(s) logged\n"
                f"{weighted_success:.1f}% Successful Transfers"
            )
        except Exception:
            return "Under Construction"

    def get_relay_models_summary_stats(self) -> str:
        """Get summary statistics string for PowerFactory relay models."""
        try:
            if not self.cache.relay_models:
                return "No relay models loaded"

            # Count models where "Model Validated" is not blank AND "Used in EQL" is not blank
            validated_eql_count = sum(
                1 for rm in self.cache.relay_models
                if rm.model_validated and rm.used_in_eql
            )

            return f"{validated_eql_count} EQL PowerFactory relay models validated"
        except Exception:
            return "Under Construction"

    def get_fuse_models_summary_stats(self) -> str:
        """Get summary statistics string for PowerFactory fuse models."""
        try:
            if not self.cache.fuse_models:
                return "No fuse models loaded"

            # Count models where "EQL Standard" is not blank
            eql_standard_count = sum(
                1 for fm in self.cache.fuse_models
                if fm.eql_standard
            )

            return f"{eql_standard_count} EQL Standard PowerFactory fuse models"
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