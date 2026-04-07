"""
Multiprocessing Compatibility Wrapper for Python 3.14+

This module provides a clean solution for applications that use multiprocessing
with lambda functions or other non-picklable objects, which break in Python 3.14+
due to the change from 'fork' to 'forkserver' as the default start method.

Usage:
    Simply import this module at the top of your main application file:
    
    import mp_compat  # This line fixes Python 3.14+ compatibility
    
    Or use the decorator for specific functions:
    
    from mp_compat import ensure_fork_context
    
    @ensure_fork_context
    def my_parallel_function():
        # Your multiprocessing code here
        pass
        
License: use freely
"""

import sys
import multiprocessing
from functools import wraps
from typing import Callable, Any


class MultiprocessingCompatibility:
    """
    Handles multiprocessing compatibility across Python versions.
    
    This class manages the multiprocessing start method to ensure compatibility
    with code that uses lambdas or other non-picklable objects in parallel contexts.
    """
    
    _initialized = False
    _python_version = sys.version_info
    
    @classmethod
    def get_python_version_info(cls) -> tuple:
        """Returns (major, minor, micro) Python version tuple."""
        return (cls._python_version.major, 
                cls._python_version.minor, 
                cls._python_version.micro)
    
    @classmethod
    def needs_fork_workaround(cls) -> bool:
        """
        Determines if the current Python version needs the fork workaround.
        
        Returns:
            bool: True if Python >= 3.14, False otherwise
        """
        major, minor, _ = cls.get_python_version_info()
        return major == 3 and minor >= 14 or major > 3
    
    @classmethod
    def initialize(cls, force: bool = False, verbose: bool = False) -> bool:
        """
        Initialize multiprocessing with the appropriate start method.
        
        Args:
            force: If True, reinitialize even if already initialized
            verbose: If True, print status messages
            
        Returns:
            bool: True if initialization was successful or already done
        """
        if cls._initialized and not force:
            if verbose:
                print("[mp_compat] Already initialized")
            return True
        
        major, minor, micro = cls.get_python_version_info()
        
        if verbose:
            print(f"[mp_compat] Python {major}.{minor}.{micro} detected")
        
        if cls.needs_fork_workaround():
            try:
                current_method = multiprocessing.get_start_method(allow_none=True)
                
                if current_method != 'fork':
                    multiprocessing.set_start_method('fork', force=force)
                    if verbose:
                        print(f"[mp_compat] Changed start method from '{current_method}' to 'fork'")
                else:
                    if verbose:
                        print("[mp_compat] Start method already set to 'fork'")
                
                cls._initialized = True
                return True
                
            except RuntimeError as e:
                if "context has already been set" in str(e) and not force:
                    if verbose:
                        print("[mp_compat] Start method already set (cannot change)")
                    cls._initialized = True
                    return True
                elif verbose:
                    print(f"[mp_compat] Warning: Could not set start method: {e}")
                return False
        else:
            if verbose:
                print("[mp_compat] No workaround needed for this Python version")
            cls._initialized = True
            return True
    
    @classmethod
    def get_status(cls) -> dict:
        """
        Get current compatibility status information.
        
        Returns:
            dict: Status information including version, method, and compatibility
        """
        major, minor, micro = cls.get_python_version_info()
        current_method = multiprocessing.get_start_method(allow_none=True)
        
        return {
            'python_version': f"{major}.{minor}.{micro}",
            'python_version_tuple': (major, minor, micro),
            'needs_workaround': cls.needs_fork_workaround(),
            'current_start_method': current_method,
            'initialized': cls._initialized,
            'compatible': current_method == 'fork' if cls.needs_fork_workaround() else True
        }


def ensure_fork_context(func: Callable) -> Callable:
    """
    Decorator that ensures the multiprocessing fork context is set before function execution.
    
    Usage:
        @ensure_fork_context
        def my_parallel_function():
            # Your multiprocessing code here
            pool = multiprocessing.Pool()
            # ...
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function that initializes compatibility before execution
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        MultiprocessingCompatibility.initialize()
        return func(*args, **kwargs)
    return wrapper


# Auto-initialize when the module is imported
MultiprocessingCompatibility.initialize(verbose=False)


# Convenience aliases
mp_compat = MultiprocessingCompatibility
init = MultiprocessingCompatibility.initialize
status = MultiprocessingCompatibility.get_status


def _test_function(x):
    """Helper function for multiprocessing test (must be picklable)"""
    return x * 2


if __name__ == "__main__":
    # Self-test and diagnostics
    print("=" * 70)
    print("Multiprocessing Compatibility Module - Diagnostics")
    print("=" * 70)
    
    status_info = MultiprocessingCompatibility.get_status()
    
    print(f"\nPython Version: {status_info['python_version']}")
    print(f"Needs Workaround: {status_info['needs_workaround']}")
    print(f"Current Start Method: {status_info['current_start_method']}")
    print(f"Initialized: {status_info['initialized']}")
    print(f"Compatible: {status_info['compatible']}")
    
    if status_info['compatible']:
        print("\n✓ System is compatible with multiprocessing lambda functions")
    else:
        print("\n✗ Warning: System may have issues with multiprocessing lambda functions")
    
    # Test with a simple multiprocessing example
    print("\n" + "=" * 70)
    print("Running multiprocessing test with regular function...")
    print("=" * 70)
    
    try:
        # Test with a regular function (always works)
        with multiprocessing.Pool(2) as pool:
            results = pool.map(_test_function, [1, 2, 3, 4, 5])
        print(f"✓ Test passed! Results: {results}")
    except Exception as e:
        print(f"✗ Test failed: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 70)
    print("Note: Lambda functions in multiprocessing require 'fork' method")
    print("      and work when imported as a module (not run as __main__)")
    print("=" * 70)
