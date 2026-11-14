"""
cli.py
------
Command-line interface for ``mechanicsdsl-unity``.

Performs *real* code generation: compiles a DSL spec through
``mechanicsdsl-core`` and emits a Unity ``MonoBehaviour`` C# component that
integrates the derived equations of motion.

Usage
-----
    mechanicsdsl-unity components
    mechanicsdsl-unity generate pendulum -o Assets/Generated
    mechanicsdsl-unity generate my_system.msl -o Assets/Generated
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from ._bridge import CoreNotInstalled, DSLCompileError, compile_spec
from ._components import _COMPONENTS
from ._csharp import render_component, _pascal


def _generate(args: argparse.Namespace) -> int:
    try:
        system = compile_spec(args.spec)
    except CoreNotInstalled as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except DSLCompileError as exc:
        print(f"DSL compilation failed: {exc}", file=sys.stderr)
        return 1

    if args.target == "unreal":
        print(
            "Unreal C++ generation is not yet implemented; only 'unity' is "
            "supported. Track progress at "
            "https://github.com/MechanicsDSL/mechanicsdsl-unity/issues",
            file=sys.stderr,
        )
        return 3

    os.makedirs(args.out, exist_ok=True)
    cls = _pascal(system.name)
    out_path = os.path.join(args.out, f"{cls}Component.cs")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_component(system))

    print(
        f"Compiled '{system.name}' "
        f"({len(system.coordinates)} DOF: {', '.join(system.coordinates)})"
    )
    print(f"Generated Unity component -> {out_path}")
    return 0


def _components(_: argparse.Namespace) -> int:
    print("Available MechanicsDSL game engine components:")
    for name, info in _COMPONENTS.items():
        print(f"  {name:<30} [{info['target']}] {info['description']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mechanicsdsl-unity",
        description="Generate Unity C# components from MechanicsDSL specs.",
    )
    sub = parser.add_subparsers(dest="command")

    p_comp = sub.add_parser("components", help="List bundled components")
    p_comp.set_defaults(func=_components)

    p_gen = sub.add_parser("generate", help="Generate a component from a DSL spec")
    p_gen.add_argument(
        "spec",
        help="Path to a .msl file, a raw DSL string, or a core preset name.",
    )
    p_gen.add_argument(
        "--target", "-t", default="unity", choices=["unity", "unreal"],
        help="Game engine target (unreal not yet implemented)",
    )
    p_gen.add_argument("--out", "-o", default=".", help="Output directory")
    p_gen.set_defaults(func=_generate)
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
