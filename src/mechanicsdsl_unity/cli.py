"""
cli.py
------
Command-line interface for ``mechanicsdsl-unity``.

Compiles a DSL spec through ``mechanicsdsl-core`` and emits game-engine code
that integrates the derived equations of motion.

Usage
-----
    mechanicsdsl-unity targets
    mechanicsdsl-unity components
    mechanicsdsl-unity presets
    mechanicsdsl-unity generate pendulum -o Assets/Generated
    mechanicsdsl-unity generate double_pendulum --target godot -o scripts/
    mechanicsdsl-unity generate double_pendulum --target unreal -o Source/MyGame/
    mechanicsdsl-unity generate my_system.msl --target csharp -o lib/
    mechanicsdsl-unity generate --all-presets --target unity -o Assets/Generated
    mechanicsdsl-unity inspect double_pendulum
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from ._bridge import CompiledSystem, CoreNotInstalled, DSLCompileError, compile_spec, list_presets
from ._components import _COMPONENTS, TARGET_DESCRIPTIONS, list_targets
from ._csharp import _pascal, render_component, render_standalone


def _write(path: str, text: str) -> str:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


def emit(system: CompiledSystem, target: str, out_dir: str) -> List[str]:
    """Generate ``target`` code for ``system`` into ``out_dir``; return written paths."""
    os.makedirs(out_dir, exist_ok=True)
    cls = _pascal(system.name)
    if target == "unity":
        return [_write(os.path.join(out_dir, f"{cls}Component.cs"), render_component(system))]
    if target == "csharp":
        return [_write(os.path.join(out_dir, f"{cls}Dynamics.cs"), render_standalone(system))]
    if target == "godot":
        from ._gdscript import render_gdscript

        name = f"{system.name}_dynamics.gd"
        return [_write(os.path.join(out_dir, name), render_gdscript(system))]
    if target == "unreal":
        from ._unreal import write_unreal

        return list(write_unreal(system, out_dir).values())
    raise ValueError(f"unknown target '{target}'")


def _compile(spec: str) -> Optional[CompiledSystem]:
    try:
        return compile_spec(spec)
    except CoreNotInstalled as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
    except DSLCompileError as exc:
        print(f"DSL compilation failed for '{spec[:60]}': {exc}", file=sys.stderr)
        return None


def _generate(args: argparse.Namespace) -> int:
    if args.all_presets:
        specs = sorted({compile_spec(p).name: p for p in list_presets()}.values())
    elif args.spec:
        specs = [args.spec]
    else:
        print("give a spec, or --all-presets", file=sys.stderr)
        return 1

    failures = 0
    for spec in specs:
        system = _compile(spec)
        if system is None:
            failures += 1
            continue
        try:
            paths = emit(system, args.target, args.out)
        except (NotImplementedError, ValueError) as exc:
            print(f"'{system.name}': cannot generate {args.target}: {exc}", file=sys.stderr)
            failures += 1
            continue
        print(f"Compiled '{system.name}' ({system.dof} DOF: {', '.join(system.coordinates)})")
        for p in paths:
            print(f"  {args.target} -> {p}")
    return 1 if failures else 0


def _components(_: argparse.Namespace) -> int:
    print("Bundled MechanicsDSL game engine components:")
    for name, info in _COMPONENTS.items():
        print(f"  {name:<30} [{info['target']}] {info['description']}")
    return 0


def _targets(_: argparse.Namespace) -> int:
    print("Generation targets:")
    for name in list_targets():
        print(f"  {name:<8} {TARGET_DESCRIPTIONS[name]}")
    return 0


def _presets(_: argparse.Namespace) -> int:
    print("Presets shipped with mechanicsdsl-core:")
    for name in list_presets():
        print(f"  {name}")
    return 0


def _inspect(args: argparse.Namespace) -> int:
    system = _compile(args.spec)
    if system is None:
        return 1
    print(system.describe())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mechanicsdsl-unity",
        description="Generate Unity, Godot, Unreal and .NET code from MechanicsDSL specs.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("components", help="List bundled components").set_defaults(func=_components)
    sub.add_parser("targets", help="List generation targets").set_defaults(func=_targets)
    sub.add_parser("presets", help="List core presets").set_defaults(func=_presets)

    spec_help = "Path to a .msl file, a raw DSL string, or a core preset name."
    p_gen = sub.add_parser("generate", help="Generate engine code from a DSL spec")
    p_gen.add_argument("spec", nargs="?", help=spec_help)
    p_gen.add_argument("--target", "-t", default="unity", choices=list_targets(),
                       help="Engine target (default: unity)")
    p_gen.add_argument("--out", "-o", default=".", help="Output directory")
    p_gen.add_argument("--all-presets", action="store_true",
                       help="Generate every core preset instead of one spec")
    p_gen.set_defaults(func=_generate)

    p_ins = sub.add_parser("inspect", help="Print coordinates, parameters, EOM and energy")
    p_ins.add_argument("spec", help=spec_help)
    p_ins.set_defaults(func=_inspect)
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
