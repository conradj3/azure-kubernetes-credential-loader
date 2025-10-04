# Test configuration for proper imports
import sys
import os

# Add src to Python path for test imports
_src_path = os.path.join(os.path.dirname(__file__), "..", "src")
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)
