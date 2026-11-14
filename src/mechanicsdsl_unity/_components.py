"""
_components.py
--------------
Component registry and code generation utilities for mechanicsdsl-unity.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List


_COMPONENTS: Dict[str, Dict] = {
    "PendulumComponent": {
        "system": "simple_pendulum",
        "target": "unity",
        "description": "Simple pendulum MonoBehaviour with Noether energy monitoring",
    },
    "DoublePendulumComponent": {
        "system": "double_pendulum",
        "target": "unity",
        "description": "Double pendulum MonoBehaviour with chaotic dynamics",
    },
    "CoupledPendulumsComponent": {
        "system": "coupled_pendulums",
        "target": "unity",
        "description": "Coupled pendulums MonoBehaviour with normal mode detection",
    },
    "ConservationMonitor": {
        "system": "any",
        "target": "unity",
        "description": "On-screen HUD for energy drift monitoring",
    },
    "PhaseSpaceTrail": {
        "system": "any",
        "target": "unity",
        "description": "Phase space portrait renderer as LineRenderer trail",
    },
}

_TARGETS = ["unity", "unreal"]


def list_components() -> List[str]:
    """Return all available Unity/Unreal components."""
    return sorted(_COMPONENTS.keys())


def list_targets() -> List[str]:
    """Return supported game engine targets."""
    return _TARGETS
