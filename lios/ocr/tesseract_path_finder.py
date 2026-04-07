#!/usr/bin/env python3
"""
Final Fast Universal Tessdata Path Finder
Optimized for speed and maximum OS compatibility
"""

import os
import shutil
import subprocess
import platform
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Set, Dict
import threading
import time
import glob
import json

try:
    import winreg
except ImportError:
    winreg = None

class FastTessdataFinder:
    """Ultra-fast, OS-independent tessdata finder with smart optimization."""
    
    def __init__(self, timeout: float = 8.0, max_workers: int = 4):
        """
        Initialize the fast tessdata finder.
        
        Args:
            timeout: Maximum time to spend searching (seconds)
            max_workers: Maximum number of concurrent search threads
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.start_time = None
        self.found_paths: Set[str] = set()
        self.lock = threading.Lock()
        self.os_type = platform.system().lower()
        self.cache_file = Path.home() / '.fast_tessdata_cache.json'
        self.cache_max_age = 6 * 3600  # 6 hours
        
    def find_tessdata_paths(self, verbose: bool = False, use_cache: bool = True) -> List[str]:
        """
        Find tessdata paths with maximum speed and compatibility.
        
        Args:
            verbose: Print search progress
            use_cache: Use cached results if available
            
        Returns:
            List of valid tessdata paths, prioritized
        """
        self.start_time = time.time()
        self.found_paths.clear()
        
        if verbose:
            print(f"Fast tessdata search on {self.os_type}...")
        
        # Check cache first
        if use_cache:
            cached = self._load_cache()
            if cached:
                if verbose:
                    print(f"Cache hit: {len(cached)} paths")
                return cached
        
        # Fast method sequence - ordered by speed and success probability
        methods = [
            ("env_vars", self._check_environment_vars),
            ("tesseract_cmd", self._check_tesseract_command),
            ("common_paths", self._check_common_paths_smart),
            ("binary_relative", self._check_binary_relative_paths),
            ("package_locations", self._check_package_locations),
        ]
        
        # Execute methods until we find paths or timeout
        for name, method in methods:
            if self._is_timeout() or len(self.found_paths) >= 3:
                break
                
            try:
                paths = method(verbose)
                if paths:
                    with self.lock:
                        self.found_paths.update(paths)
                    if verbose:
                        print(f"  {name}: +{len(paths)} paths")
            except Exception as e:
                if verbose:
                    print(f"  Warning {name}: {e}")
        
        # Prioritize and validate
        result = self._finalize_paths(list(self.found_paths), verbose)
        
        # Cache results
        if use_cache and result:
            self._save_cache(result)
        
        if verbose:
            elapsed = self._elapsed()
            print(f"Found {len(result)} paths in {elapsed:.2f}s")
            
        return result
    
    def get_primary_path(self, verbose: bool = False) -> Optional[str]:
        """Get the best tessdata path."""
        paths = self.find_tessdata_paths(verbose)
        return paths[0] if paths else None
    
    def _load_cache(self) -> List[str]:
        """Load and validate cache."""
        try:
            if not self.cache_file.exists():
                return []
            
            # Check age
            age = time.time() - self.cache_file.stat().st_mtime
            if age > self.cache_max_age:
                return []
            
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                paths = data.get('paths', [])
                
            # Quick validation
            valid_paths = [p for p in paths if self._is_valid_tessdata_quick(p)]
            return valid_paths if valid_paths else []
            
        except Exception:
            return []
    
    def _save_cache(self, paths: List[str]):
        """Save paths to cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'paths': paths,
                    'timestamp': time.time(),
                    'os': self.os_type
                }, f)
        except Exception:
            pass
    
    def _check_environment_vars(self, verbose: bool = False) -> List[str]:
        """Check environment variables (fastest method)."""
        paths = []
        env_vars = ['TESSDATA_PREFIX', 'TESSERACT_DATA_PATH', 'TESSERACT_PREFIX']
        
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                candidates = [value, os.path.join(value, 'tessdata')]
                for candidate in candidates:
                    if self._is_valid_tessdata_quick(candidate):
                        paths.append(os.path.abspath(candidate))
                        break
        
        return paths
    
    def _check_tesseract_command(self, verbose: bool = False) -> List[str]:
        """Use tesseract command to find tessdata (most reliable)."""
        paths = []
        
        try:
            # Method 1: Try to get tessdata path directly
            result = subprocess.run([
                'tesseract', '--print-parameters'
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                # Parse output for tessdata paths
                for line in result.stdout.split('\n'):
                    if 'tessdata' in line.lower():
                        # Extract path-like strings
                        import re
                        matches = re.findall(r'[/\\][\w/\\.-]*tessdata[/\\]?[\w/\\.-]*', line)
                        for match in matches:
                            clean_path = match.rstrip('/\\')
                            if self._is_valid_tessdata_quick(clean_path):
                                paths.append(os.path.abspath(clean_path))
            
            # Method 2: If tesseract works, find tessdata via binary location
            if not paths:
                tesseract_bin = shutil.which('tesseract')
                if tesseract_bin:
                    bin_paths = self._get_tessdata_from_binary(tesseract_bin)
                    paths.extend(bin_paths)
                    
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        return paths
    
    def _check_common_paths_smart(self, verbose: bool = False) -> List[str]:
        """Smart check of common paths with OS-specific optimizations."""
        paths = []
        
        # Get OS-specific common paths
        common_paths = self._get_smart_common_paths()
        
        # Use ThreadPoolExecutor for parallel checking
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all path checks
            future_to_path = {
                executor.submit(self._check_path_with_glob, path): path
                for path in common_paths
            }
            
            # Collect results with timeout
            timeout_remaining = max(1, self.timeout - self._elapsed())
            for future in as_completed(future_to_path, timeout=timeout_remaining):
                if self._is_timeout():
                    break
                try:
                    found_paths = future.result(timeout=0.5)
                    paths.extend(found_paths)
                except Exception:
                    continue
        
        return paths
    
    def _check_binary_relative_paths(self, verbose: bool = False) -> List[str]:
        """Check paths relative to tesseract binary."""
        paths = []
        
        # Find all tesseract binaries
        binaries = self._find_tesseract_binaries()
        
        for binary in binaries:
            if self._is_timeout():
                break
            found = self._get_tessdata_from_binary(binary)
            paths.extend(found)
        
        return paths
    
    def _check_package_locations(self, verbose: bool = False) -> List[str]:
        """Check package manager specific locations."""
        paths = []
        
        if self.os_type == 'linux':
            # Ubuntu/Debian versioned paths (like your system)
            versioned_patterns = [
                '/usr/share/tesseract-ocr/*/tessdata',
                '/usr/share/tesseract/*/tessdata',
                '/usr/local/share/tesseract-ocr/*/tessdata'
            ]
            
            for pattern in versioned_patterns:
                try:
                    matches = glob.glob(pattern)
                    for match in matches:
                        if self._is_valid_tessdata_quick(match):
                            paths.append(os.path.abspath(match))
                except Exception:
                    continue
                    
        elif self.os_type == 'darwin':
            # Homebrew paths
            brew_paths = [
                '/opt/homebrew/share/tesseract-ocr/tessdata',
                '/usr/local/share/tesseract-ocr/tessdata'
            ]
            for path in brew_paths:
                if self._is_valid_tessdata_quick(path):
                    paths.append(path)
                    
        elif self.os_type == 'windows':
            # Windows registry check
            if winreg:
                paths.extend(self._check_windows_registry())
        
        return paths
    
    def _get_smart_common_paths(self) -> List[str]:
        """Get optimized common paths based on OS."""
        if self.os_type == 'linux':
            return [
                '/usr/share/tesseract-ocr/tessdata',
                '/usr/share/tessdata',
                '/usr/local/share/tesseract-ocr/tessdata',
                '/usr/share/tesseract-ocr/*/tessdata',  # Versioned
                '/snap/tesseract/current/usr/share/tesseract-ocr/tessdata',
                '~/.local/share/tesseract/tessdata',
                '~/miniconda*/share/tesseract-ocr/tessdata',
                '~/anaconda*/share/tesseract-ocr/tessdata'
            ]
        elif self.os_type == 'darwin':
            return [
                '/opt/homebrew/share/tesseract-ocr/tessdata',
                '/usr/local/share/tesseract-ocr/tessdata',
                '/usr/share/tesseract-ocr/tessdata',
                '~/miniconda*/share/tesseract-ocr/tessdata',
                '~/anaconda*/share/tesseract-ocr/tessdata'
            ]
        else:  # Windows
            return [
                'C:/Program Files/Tesseract-OCR/tessdata',
                'C:/Program Files (x86)/Tesseract-OCR/tessdata',
                '~/AppData/Local/Tesseract-OCR/tessdata',
                '~/miniconda*/Library/share/tesseract-ocr/tessdata',
                '~/anaconda*/Library/share/tesseract-ocr/tessdata'
            ]
    
    def _check_path_with_glob(self, path_pattern: str) -> List[str]:
        """Check a path pattern (with glob support)."""
        found = []
        try:
            expanded = os.path.expanduser(os.path.expandvars(path_pattern))
            
            if '*' in expanded:
                matches = glob.glob(expanded)
                for match in matches:
                    if self._is_valid_tessdata_quick(match):
                        found.append(os.path.abspath(match))
            else:
                if self._is_valid_tessdata_quick(expanded):
                    found.append(os.path.abspath(expanded))
        except Exception:
            pass
        
        return found
    
    def _get_tessdata_from_binary(self, binary_path: str) -> List[str]:
        """Get tessdata paths relative to binary."""
        paths = []
        
        try:
            bin_dir = Path(binary_path).parent.resolve()
            
            # Relative paths from binary to tessdata
            if self.os_type == 'windows':
                relatives = ['../tessdata', 'tessdata', '../share/tessdata']
            else:
                relatives = [
                    '../share/tesseract-ocr/tessdata',
                    '../share/tessdata',
                    '../../share/tesseract-ocr/tessdata',
                    '../tessdata'
                ]
            
            for rel in relatives:
                candidate = bin_dir / rel
                if candidate.exists() and self._is_valid_tessdata_quick(str(candidate)):
                    paths.append(str(candidate.resolve()))
                    
        except Exception:
            pass
        
        return paths
    
    def _find_tesseract_binaries(self) -> List[str]:
        """Find tesseract binary locations quickly."""
        binaries = []
        
        # Primary method: shutil.which
        for name in ['tesseract', 'tesseract.exe']:
            binary = shutil.which(name)
            if binary:
                binaries.append(binary)
        
        # Secondary: common locations
        common_bins = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            'C:/Program Files/Tesseract-OCR/tesseract.exe',
            'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
        ]
        
        for path in common_bins:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                if path not in binaries:
                    binaries.append(path)
        
        return binaries
    
    def _check_windows_registry(self) -> List[str]:
        """Check Windows registry for tessdata."""
        paths = []
        
        if not winreg:
            return paths
        
        keys = [
            (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Tesseract-OCR"),
            (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Tesseract-OCR")
        ]
        
        for hkey, subkey in keys:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                    tessdata_path = os.path.join(install_path, "tessdata")
                    if self._is_valid_tessdata_quick(tessdata_path):
                        paths.append(os.path.abspath(tessdata_path))
            except (FileNotFoundError, OSError):
                continue
        
        return paths
    
    def _is_valid_tessdata_quick(self, path: str) -> bool:
        """Fast tessdata validation."""
        try:
            p = Path(path)
            if not p.is_dir():
                return False
            
            # Quick check: look for any .traineddata file
            return any(f.suffix == '.traineddata' for f in p.iterdir())
            
        except (OSError, PermissionError):
            return False
    
    def _finalize_paths(self, paths: List[str], verbose: bool = False) -> List[str]:
        """Validate and prioritize final paths."""
        valid_paths = []
        
        for path in paths:
            if self._is_valid_tessdata_quick(path):
                normalized = os.path.normpath(path)
                if normalized not in valid_paths:
                    valid_paths.append(normalized)
        
        # Priority sort
        def priority_key(path: str) -> tuple:
            path_lower = path.lower()
            score = 0
            
            # Environment variables (highest)
            if any(env in path_lower for env in ['tessdata_prefix', 'tesseract_data']):
                score -= 1000
                
            # System package locations
            if '/usr/share' in path_lower:
                score -= 500
                
            # User installations
            if any(user in path_lower for user in ['home', 'users', '~']):
                score -= 300
            
            # Count language files
            try:
                lang_count = len(list(Path(path).glob('*.traineddata')))
                score -= lang_count * 10
            except:
                pass
            
            return (score, path_lower)
        
        return sorted(valid_paths, key=priority_key)
    
    def _elapsed(self) -> float:
        """Get elapsed time."""
        return time.time() - self.start_time if self.start_time else 0
    
    def _is_timeout(self) -> bool:
        """Check timeout."""
        return self._elapsed() > self.timeout


# Simple API functions
def find_tessdata_paths(verbose: bool = False, timeout: float = 8.0) -> List[str]:
    """
    Find all tessdata paths (optimized version).
    
    Args:
        verbose: Print search progress
        timeout: Maximum search time
        
    Returns:
        List of tessdata paths
    """
    finder = FastTessdataFinder(timeout=timeout)
    return finder.find_tessdata_paths(verbose=verbose)

def get_tessdata_path(verbose: bool = False) -> Optional[str]:
    """
    Get the primary tessdata path (optimized version).
    
    Args:
        verbose: Print search progress
        
    Returns:
        Primary tessdata path or None
    """
    finder = FastTessdataFinder()
    return finder.get_primary_path(verbose=verbose)

def validate_tessdata_path(path: str) -> Dict[str, any]:
    """
    Validate and get info about a tessdata path.
    
    Args:
        path: Path to validate
        
    Returns:
        Dictionary with validation info
    """
    info = {
        'path': path,
        'valid': False,
        'exists': False,
        'readable': False,
        'language_count': 0,
        'languages': [],
        'size_mb': 0
    }
    
    try:
        p = Path(path)
        info['exists'] = p.exists()
        
        if info['exists']:
            info['readable'] = os.access(path, os.R_OK)
            
            if info['readable']:
                traineddata_files = list(p.glob('*.traineddata'))
                info['valid'] = len(traineddata_files) > 0
                info['language_count'] = len(traineddata_files)
                info['languages'] = [f.stem for f in traineddata_files]
                
                total_size = sum(f.stat().st_size for f in traineddata_files)
                info['size_mb'] = round(total_size / (1024 * 1024), 2)
                
    except Exception as e:
        info['error'] = str(e)
    
    return info

def clear_cache():
    """Clear the tessdata finder cache."""
    try:
        cache_file = Path.home() / '.fast_tessdata_cache.json'
        if cache_file.exists():
            cache_file.unlink()
            return True
    except:
        pass
    return False


# Test and demo
if __name__ == "__main__":
    print("Fast Universal Tessdata Finder")
    print(f"   Platform: {platform.system()} {platform.release()}")
    print("=" * 50)
    
    # Quick test
    start_time = time.time()
    primary = get_tessdata_path(verbose=True)
    elapsed = time.time() - start_time
    
    print(f"\nPrimary path: {primary}")
    print(f"Found in: {elapsed:.3f} seconds")
    
    if primary:
        # Validate
        info = validate_tessdata_path(primary)
        print(f"Languages: {info['language_count']} ({', '.join(info['languages'][:5])})")
        print(f"Size: {info['size_mb']} MB")
        
        # Test with tesseract
        try:
            os.environ['TESSDATA_PREFIX'] = primary
            result = subprocess.run(['tesseract', '--list-langs'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                langs = result.stdout.strip().split('\n')[1:]
                print(f"Tesseract test: OK ({len(langs)} languages accessible)")
            else:
                print(f"Tesseract test: Failed")
        except Exception as e:
            print(f"Tesseract test: {e}")
    
    # Comprehensive search
    print(f"\n" + "=" * 50)
    print("Comprehensive search:")
    start_time = time.time()
    all_paths = find_tessdata_paths(verbose=True, timeout=10.0)
    elapsed = time.time() - start_time
    
    print(f"\nAll paths found: {len(all_paths)}")
    for i, path in enumerate(all_paths, 1):
        info = validate_tessdata_path(path)
        print(f"  {i}. {path}")
        print(f"     Languages: {info['language_count']}, Size: {info['size_mb']} MB")
    
    print(f"\nTotal time: {elapsed:.3f} seconds")
    print("Search complete!")
