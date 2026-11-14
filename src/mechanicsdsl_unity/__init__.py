"""
mechanicsdsl-unity
------------------
Unity and Unreal Engine plugin packages for MechanicsDSL.
Generates physically accurate simulation components compiled from DSL notation.

Quick start:
    pip install mechanicsdsl-unity
    mechanicsdsl-unity generate pendulum.msl --target unity --out Assets/Physics/
    mechanicsdsl-unity generate pendulum.msl --target unreal --out Source/Physics/

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
)
from mechanicsdsl_unity._csharp import expr_to_csharp, render_component

__all__ = [
    "__version__",
    "list_components",
    "list_targets",
    "compile_spec",
    "render_component",
    "expr_to_csharp",
    "CompiledSystem",
    "CoreNotInstalled",
    "DSLCompileError",
]
