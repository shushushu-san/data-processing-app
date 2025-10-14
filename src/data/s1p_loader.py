"""
S1P File Loader for Network Analyzer Data
Handles loading and parsing of S-parameter files from network analyzers.
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)


class S1PLoader:
    """
    Loader for S1P (single-port S-parameter) files.
    
    S1P files contain frequency response data from network analyzers,
    typically including frequency, magnitude, and phase information.
    """
    
    def __init__(self):
        """Initialize the S1P loader."""
        self.supported_extensions = ['.s1p', '.S1P']
        self.data = None
        self.metadata = {}
        
    def load_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load an S1P file and return parsed data.
        
        Args:
            file_path (str): Path to the S1P file
            
        Returns:
            Dict containing parsed data and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if file_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file extension: {file_path.suffix}")
            
        logger.info(f"Loading S1P file: {file_path}")
        
        # Parse the file
        header_info, data_lines = self._parse_file(file_path)
        
        # Process header information
        self.metadata = self._parse_header(header_info)
        
        # Process data
        self.data = self._parse_data(data_lines)
        
        # Create result dictionary
        result = {
            'data': self.data,
            'metadata': self.metadata,
            'file_path': str(file_path),
            'file_type': 'S1P',
            'columns': list(self.data.columns) if self.data is not None else []
        }
        
        logger.info(f"Successfully loaded S1P file with {len(self.data)} data points")
        
        return result
    
    def _parse_file(self, file_path: Path) -> Tuple[List[str], List[str]]:
        """
        Parse the S1P file into header and data sections.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (header_lines, data_lines)
        """
        header_lines = []
        data_lines = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith('#') or line.startswith('!'):
                        # Header or comment line
                        header_lines.append(line)
                    else:
                        # Data line
                        data_lines.append(line)
                        
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith('#') or line.startswith('!'):
                        header_lines.append(line)
                    else:
                        data_lines.append(line)
                        
        return header_lines, data_lines
    
    def _parse_header(self, header_lines: List[str]) -> Dict[str, Any]:
        """
        Parse header information from S1P file.
        
        Args:
            header_lines: List of header lines
            
        Returns:
            Dictionary with parsed metadata
        """
        metadata = {
            'format': 'S1P',
            'frequency_unit': 'Hz',
            'parameter_format': 'DB',  # Default
            'data_format': 'MA',  # Magnitude and Angle (Phase)
            'reference_impedance': 50.0,  # Default
            'instrument': 'Unknown',
            'comments': []
        }
        
        for line in header_lines:
            if line.startswith('#'):
                # Format line: # HZ S DB R 50.00
                parts = line[1:].strip().split()
                if len(parts) >= 5:
                    metadata['frequency_unit'] = parts[0].upper()
                    metadata['parameter_type'] = parts[1].upper()  # S-parameters
                    metadata['parameter_format'] = parts[2].upper()  # DB, MA, RI
                    metadata['data_format'] = parts[3].upper()  # R (Real/Imaginary) or MA (Mag/Angle)
                    try:
                        metadata['reference_impedance'] = float(parts[4])
                    except (ValueError, IndexError):
                        pass
                        
            elif line.startswith('!'):
                # Comment line
                comment = line[1:].strip()
                if comment:
                    metadata['comments'].append(comment)
                    
                    # Try to extract instrument name
                    if any(keyword in comment.lower() for keyword in ['rohde', 'schwarz', 'keysight', 'agilent']):
                        metadata['instrument'] = comment
        
        return metadata
    
    def _parse_data(self, data_lines: List[str]) -> pd.DataFrame:
        """
        Parse data lines into a pandas DataFrame.
        
        Args:
            data_lines: List of data lines
            
        Returns:
            DataFrame with frequency, magnitude, and phase data
        """
        if not data_lines:
            raise ValueError("No data lines found in S1P file")
            
        frequencies = []
        magnitudes = []
        phases = []
        
        for line_num, line in enumerate(data_lines, 1):
            try:
                parts = line.split()
                if len(parts) < 3:
                    logger.warning(f"Line {line_num}: Insufficient data columns")
                    continue
                    
                frequency = float(parts[0])
                magnitude = float(parts[1])
                phase = float(parts[2])
                
                frequencies.append(frequency)
                magnitudes.append(magnitude)
                phases.append(phase)
                
            except (ValueError, IndexError) as e:
                logger.warning(f"Line {line_num}: Error parsing data: {e}")
                continue
        
        if not frequencies:
            raise ValueError("No valid data points found")
            
        # Create DataFrame
        df = pd.DataFrame({
            'Frequency_Hz': frequencies,
            'S11_Magnitude_dB': magnitudes,
            'S11_Phase_deg': phases
        })
        
        # Sort by frequency
        df = df.sort_values('Frequency_Hz').reset_index(drop=True)
        
        # Add derived columns
        df['Frequency_GHz'] = df['Frequency_Hz'] / 1e9
        
        # Convert magnitude from dB to linear if needed
        df['S11_Magnitude_Linear'] = 10**(df['S11_Magnitude_dB'] / 20)
        
        # Convert phase to radians
        df['S11_Phase_rad'] = np.radians(df['S11_Phase_deg'])
        
        return df
    
    def get_frequency_range(self) -> Tuple[float, float]:
        """
        Get the frequency range of loaded data.
        
        Returns:
            Tuple of (min_freq, max_freq) in Hz
        """
        if self.data is None:
            return (0, 0)
            
        return (self.data['Frequency_Hz'].min(), self.data['Frequency_Hz'].max())
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics of the loaded data.
        
        Returns:
            Dictionary with summary statistics
        """
        if self.data is None:
            return {}
            
        summary = {
            'num_points': len(self.data),
            'frequency_range_hz': self.get_frequency_range(),
            'frequency_range_ghz': (
                self.data['Frequency_GHz'].min(),
                self.data['Frequency_GHz'].max()
            ),
            'magnitude_range_db': (
                self.data['S11_Magnitude_dB'].min(),
                self.data['S11_Magnitude_dB'].max()
            ),
            'phase_range_deg': (
                self.data['S11_Phase_deg'].min(),
                self.data['S11_Phase_deg'].max()
            ),
            'frequency_step_hz': self._calculate_frequency_step()
        }
        
        return summary
    
    def _calculate_frequency_step(self) -> Optional[float]:
        """Calculate the frequency step if data is uniformly spaced."""
        if self.data is None or len(self.data) < 2:
            return None
            
        # Calculate differences
        freq_diffs = np.diff(self.data['Frequency_Hz'].values)
        
        # Check if uniformly spaced (within 1% tolerance)
        mean_diff = np.mean(freq_diffs)
        if np.all(np.abs(freq_diffs - mean_diff) / mean_diff < 0.01):
            return mean_diff
        else:
            return None  # Non-uniform spacing
    
    def export_data(self, output_path: str, format: str = 'csv') -> None:
        """
        Export loaded data to a file.
        
        Args:
            output_path: Output file path
            format: Export format ('csv', 'xlsx')
        """
        if self.data is None:
            raise ValueError("No data loaded to export")
            
        output_path = Path(output_path)
        
        if format.lower() == 'csv':
            self.data.to_csv(output_path, index=False)
        elif format.lower() == 'xlsx':
            self.data.to_excel(output_path, index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
        logger.info(f"Data exported to: {output_path}")


# Factory function for creating loaders
def create_s1p_loader() -> S1PLoader:
    """Create and return an S1P loader instance."""
    return S1PLoader()


# Utility function for quick loading
def load_s1p_file(file_path: str) -> Dict[str, Any]:
    """
    Quick utility function to load an S1P file.
    
    Args:
        file_path: Path to the S1P file
        
    Returns:
        Dictionary with loaded data and metadata
    """
    loader = S1PLoader()
    return loader.load_file(file_path)