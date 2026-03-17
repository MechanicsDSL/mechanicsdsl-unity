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


def main() -> None:
    """Entry point for mechanicsdsl-unity CLI."""
    import argparse
    parser = argparse.ArgumentParser(
        prog="mechanicsdsl-unity",
        description="MechanicsDSL Unity/Unreal Engine code generation tools"
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("components", help="List available components")

    gen = sub.add_parser("generate", help="Generate game engine code from DSL spec")
    gen.add_argument("spec", help="Path to .msl DSL specification file")
    gen.add_argument("--target", "-t", required=True,
                     choices=_TARGETS, help="Game engine target")
    gen.add_argument("--out", "-o", default=".", help="Output directory")

    args = parser.parse_args()

    if args.command == "components":
        print("Available MechanicsDSL game engine components:")
        for c, info in _COMPONENTS.items():
            print(f"  {c:<30} [{info['target']}] {info['description']}")

    elif args.command == "generate":
        try:
            import mechanicsdsl
            mechanicsdsl.generate(args.spec, target=args.target, out=args.out)
        except ImportError:
            print("mechanicsdsl-core is required for code generation.")
            print("Install with: pip install mechanicsdsl-core")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
