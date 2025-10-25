"""Backward compatibility - logger moved to utils."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import log_event

__all__ = ["log_event"]
