"""
DAT Data Loader Module
Provides loading and processing functions for DAT (Data) files.
DAT files typically contain frequency domain measurements with amplitude and phase data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DATLoader:
    """
    Loader class for DAT files containing frequency domain measurement data.
    
    Supports tab-separated DAT files with the following expected format:
    - Column 1: Frequency (Hz) - Primary measurement
    - Column 2: Amplitude - Primary measurement
    - Column 3: Phase - Primary measurement
    - Column 4: Frequency (Hz) - Average measurement (optional)
    - Column 5: aveAmplitude - Average amplitude (optional)
    - Column 6: avePhase - Average phase (optional)
    """
    
    def __init__(self):
        """Initialize the DAT loader."""
        self.current_file = None
        self.data = None
        self.metadata = {}
        
        # Default column names for DAT files
        self.expected_columns = [
            'Frequency_Hz', 'Amplitude', 'Phase',
            'Frequency_Hz_Ave', 'aveAmplitude', 'avePhase'
        ]
    
    def load_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load a DAT file and return processed data.
        
        Args:
            file_path: Path to the DAT file
            
        Returns:
            Dictionary containing 'data', 'metadata', and 'summary'
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"DAT file not found: {file_path}")
        
        logger.info(f"Loading DAT file: {file_path.name}")
        
        try:
            # Read the DAT file
            self.data = self._read_dat_file(file_path)
            
            # Process and validate data
            self._process_data()
            
            # Extract metadata
            self.metadata = self._extract_metadata(file_path)
            
            # Create summary statistics
            summary = self._create_summary()
            
            self.current_file = file_path
            
            logger.info(f"Successfully loaded DAT file with {len(self.data)} data points")
            
            return {
                'data': self.data,
                'metadata': self.metadata,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Error loading DAT file {file_path.name}: {e}")
            raise ValueError(f"Failed to load DAT file: {e}")
    
    def _read_dat_file(self, file_path: Path) -> pd.DataFrame:
        """
        Read the DAT file and parse its contents.
        
        Args:
            file_path: Path to the DAT file
            
        Returns:
            pandas DataFrame with the DAT data
        """
        try:
            # Try reading with tab separator
            df = pd.read_csv(file_path, sep='\t', header=0)
            
            # Check if we have the expected number of columns
            if df.shape[1] < 3:
                # Try with different separators
                df = pd.read_csv(file_path, sep=r'\s+', header=0)
            
            # Rename columns to standard names
            if df.shape[1] >= 6:
                # Full format with both primary and average data
                df.columns = self.expected_columns
            elif df.shape[1] >= 3:
                # Primary data only
                df.columns = self.expected_columns[:3]
            else:
                raise ValueError(f"DAT file must have at least 3 columns, found {df.shape[1]}")
            
            # Convert scientific notation and clean data
            for col in df.columns:
                if col in df.columns:
                    # Convert to numeric, handling scientific notation
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove rows with all zeros or NaN values
            if 'Frequency_Hz_Ave' in df.columns:
                # Remove rows where average frequency is 0 (indicates end of average data)
                mask = (df['Frequency_Hz_Ave'] != 0) | df['Frequency_Hz_Ave'].isna()
                # Keep all primary data, but filter average data
                df.loc[~mask, ['Frequency_Hz_Ave', 'aveAmplitude', 'avePhase']] = np.nan
            
            # Remove completely empty rows
            df = df.dropna(subset=['Frequency_Hz', 'Amplitude'])
            
            logger.info(f"Read DAT file: {len(df)} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            raise ValueError(f"Error reading DAT file: {e}")
    
    def _process_data(self):
        """Process and validate the loaded data."""
        if self.data is None or self.data.empty:
            raise ValueError("No data to process")
        
        # Convert frequency to more convenient units
        if 'Frequency_Hz' in self.data.columns:
            # Add frequency in kHz for easier reading
            self.data['Frequency_kHz'] = self.data['Frequency_Hz'] / 1000.0
        
        if 'Frequency_Hz_Ave' in self.data.columns and not self.data['Frequency_Hz_Ave'].isna().all():
            self.data['Frequency_kHz_Ave'] = self.data['Frequency_Hz_Ave'] / 1000.0
        
        # Validate frequency data
        if self.data['Frequency_Hz'].isna().any():
            logger.warning("Found NaN values in frequency data")
        
        # Check for monotonic frequency (should be increasing)
        freq_diff = self.data['Frequency_Hz'].diff()
        if (freq_diff < 0).any():
            logger.warning("Frequency data is not monotonically increasing")
        
        # Calculate frequency step
        if len(self.data) > 1:
            freq_step = self.data['Frequency_Hz'].iloc[1] - self.data['Frequency_Hz'].iloc[0]
            self.metadata['frequency_step_hz'] = freq_step
        
        logger.info("Data processing completed")
    
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from the file and data.
        
        Args:
            file_path: Path to the DAT file
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            'file_name': file_path.name,
            'file_path': str(file_path),
            'file_type': 'DAT',
            'data_format': 'Frequency Domain Measurement',
            'frequency_unit': 'Hz',
            'amplitude_unit': 'V',  # Assuming voltage, could be different
            'phase_unit': 'degrees',
        }
        
        # Extract info from filename if possible
        filename = file_path.stem
        if '-' in filename:
            parts = filename.split('-')
            if len(parts) >= 2:
                metadata['measurement_date'] = parts[0]
                metadata['measurement_id'] = parts[1]
        
        # Data range information
        if 'Frequency_Hz' in self.data.columns:
            metadata['frequency_range_hz'] = (
                float(self.data['Frequency_Hz'].min()),
                float(self.data['Frequency_Hz'].max())
            )
            metadata['frequency_range_khz'] = (
                float(self.data['Frequency_Hz'].min() / 1000),
                float(self.data['Frequency_Hz'].max() / 1000)
            )
        
        if 'Amplitude' in self.data.columns:
            metadata['amplitude_range'] = (
                float(self.data['Amplitude'].min()),
                float(self.data['Amplitude'].max())
            )
        
        if 'Phase' in self.data.columns:
            metadata['phase_range'] = (
                float(self.data['Phase'].min()),
                float(self.data['Phase'].max())
            )
        
        # Check if average data is available
        has_average_data = False
        if 'aveAmplitude' in self.data.columns:
            has_average_data = not self.data['aveAmplitude'].isna().all()
        metadata['has_average_data'] = has_average_data
        
        return metadata
    
    def _create_summary(self) -> Dict[str, Any]:
        """
        Create summary statistics for the loaded data.
        
        Returns:
            Dictionary with summary statistics
        """
        if self.data is None or self.data.empty:
            return {}
        
        summary = {
            'num_points': len(self.data),
            'columns': list(self.data.columns),
        }
        
        # Frequency statistics
        if 'Frequency_Hz' in self.data.columns:
            freq_data = self.data['Frequency_Hz'].dropna()
            summary['frequency_stats'] = {
                'min_hz': float(freq_data.min()),
                'max_hz': float(freq_data.max()),
                'mean_hz': float(freq_data.mean()),
                'step_hz': float(freq_data.diff().mean()) if len(freq_data) > 1 else 0,
                'span_hz': float(freq_data.max() - freq_data.min())
            }
        
        # Amplitude statistics
        if 'Amplitude' in self.data.columns:
            amp_data = self.data['Amplitude'].dropna()
            summary['amplitude_stats'] = {
                'min': float(amp_data.min()),
                'max': float(amp_data.max()),
                'mean': float(amp_data.mean()),
                'std': float(amp_data.std())
            }
        
        # Phase statistics
        if 'Phase' in self.data.columns:
            phase_data = self.data['Phase'].dropna()
            summary['phase_stats'] = {
                'min': float(phase_data.min()),
                'max': float(phase_data.max()),
                'mean': float(phase_data.mean()),
                'std': float(phase_data.std())
            }
        
        # Average data statistics (if available)
        if 'aveAmplitude' in self.data.columns:
            ave_amp_data = self.data['aveAmplitude'].dropna()
            if not ave_amp_data.empty:
                summary['average_amplitude_stats'] = {
                    'min': float(ave_amp_data.min()),
                    'max': float(ave_amp_data.max()),
                    'mean': float(ave_amp_data.mean()),
                    'std': float(ave_amp_data.std()),
                    'count': len(ave_amp_data)
                }
        
        return summary
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for the currently loaded data.
        
        Returns:
            Dictionary with summary statistics
        """
        if self.data is None:
            return {}
        
        return self._create_summary()
    
    def get_frequency_range(self, unit: str = 'Hz') -> Optional[Tuple[float, float]]:
        """
        Get the frequency range of the loaded data.
        
        Args:
            unit: Unit for frequency ('Hz' or 'kHz')
            
        Returns:
            Tuple of (min_freq, max_freq) or None if no data
        """
        if self.data is None or 'Frequency_Hz' not in self.data.columns:
            return None
        
        freq_data = self.data['Frequency_Hz'].dropna()
        if freq_data.empty:
            return None
        
        min_freq = float(freq_data.min())
        max_freq = float(freq_data.max())
        
        if unit.lower() == 'khz':
            return (min_freq / 1000, max_freq / 1000)
        else:
            return (min_freq, max_freq)
    
    def export_to_csv(self, output_path: str) -> bool:
        """
        Export the loaded data to a CSV file.
        
        Args:
            output_path: Path for the output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        if self.data is None:
            logger.error("No data to export")
            return False
        
        try:
            self.data.to_csv(output_path, index=False)
            logger.info(f"Data exported to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False


# Factory function
def load_dat_file(file_path: str) -> Dict[str, Any]:
    """
    Load a DAT file and return the processed data.
    
    Args:
        file_path: Path to the DAT file
        
    Returns:
        Dictionary containing 'data', 'metadata', and 'summary'
    """
    loader = DATLoader()
    return loader.load_file(file_path)


# Test function
def test_dat_loader():
    """Test function to validate DAT loader functionality."""
    import os
    
    # Look for test DAT files
    test_files = []
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    if data_dir.exists():
        test_files = list(data_dir.glob('*.dat'))
    
    if not test_files:
        print("No DAT test files found")
        return
    
    print(f"Testing DAT loader with {len(test_files)} files...")
    
    for test_file in test_files[:1]:  # Test first file only
        try:
            print(f"\nTesting: {test_file.name}")
            result = load_dat_file(str(test_file))
            
            data = result['data']
            metadata = result['metadata']
            
            print(f"✓ Loaded {len(data)} data points")
            print(f"✓ Columns: {list(data.columns)}")
            print(f"✓ Frequency range: {metadata.get('frequency_range_khz', 'Unknown')} kHz")
            print(f"✓ Has average data: {metadata.get('has_average_data', False)}")
            
        except Exception as e:
            print(f"✗ Error loading {test_file.name}: {e}")


if __name__ == "__main__":
    test_dat_loader()