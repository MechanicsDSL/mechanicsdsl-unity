"""
mechanicsdsl-unity
------------------
Unity and Unreal Engine plugin packages for MechanicsDSL.
Generates physically accurate simulation components compiled from DSL notation.

Quick start:
    pip install mechanicsdsl-unity
    mechanicsdsl-unity generate pendulum.msl --target unity --out Assets/Physics/
    mechanicsdsl-unity generate pendulum.msl --target unreal --out Source/Physics/
    mechanicsdsl-unity generate pendulum.msl --target godot --out scripts/
    mechanicsdsl-unity generate pendulum.msl --target csharp --out lib/

    # Documentation and UPM install:
    # https://github.com/MechanicsDSL/mechanicsdsl-unity
"""

from mechanicsdsl_unity._version import __version__
from mechanicsdsl_unity._components import list_components, list_targets
from mechanicsdsl_unity._bridge import (
    CompiledSystem,
    CoreNotInstalled,
    DSLCompileError,
    compile_spec,
    energy_drift,
    list_presets,
    numeric_energy,
    simulate,
)
from mechanicsdsl_unity._csharp import expr_to_csharp, render_component, render_standalone
from mechanicsdsl_unity._gdscript import expr_to_gdscript, render_gdscript
from mechanicsdsl_unity._unreal import render_unreal, write_unreal

__all__ = [
    "__version__",
    "list_components",
    "list_targets",
    "compile_spec",
    "render_component",
    "render_standalone",
    "render_gdscript",
    "render_unreal",
    "write_unreal",
    "expr_to_csharp",
    "expr_to_gdscript",
    "list_presets",
    "simulate",
    "numeric_energy",
    "energy_drift",
    "CompiledSystem",
    "CoreNotInstalled",
    "DSLCompileError",
]
