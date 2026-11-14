"""
test_csharp.py
--------------
Verifies the real SymPy -> C# generator.

The headline test evaluates every generated C# acceleration expression (with
``Math.*`` mapped back to Python ``math.*``) against the original SymPy
equation of motion at many random states, asserting machine-precision
agreement. This proves the C# is a faithful transcription of the derived
dynamics without needing a C# compiler in CI.

Run with: pytest tests/test_csharp.py -v
"""
import math
import random
import re

import pytest

pytest.importorskip(
    "mechanics_dsl", reason="mechanicsdsl-core required for generation tests"
)

import sympy as sp

from mechanicsdsl_unity import compile_spec, render_component
from mechanicsdsl_unity._csharp import CSharpPrinter
from mechanicsdsl_unity.cli import main as cli_main


def _cs_to_py(expr_str: str) -> str:
    s = expr_str.replace("Math.Pow", "math.pow").replace("Math.Sqrt", "math.sqrt")
    return re.sub(r"Math\.([A-Z][a-z]+)", lambda m: "math." + m.group(1).lower(), s)


@pytest.mark.parametrize("preset", ["pendulum", "double_pendulum", "coupled_oscillators"])
def test_generated_csharp_matches_sympy(preset):
    system = compile_spec(preset)
    printer = CSharpPrinter()
    all_syms = set()
    for expr in system.equations.values():
        all_syms |= {str(s) for s in expr.free_symbols}

    rng = random.Random(1234)
    for _ in range(200):
        vals = {}
        for name in all_syms:
            vals[name] = system.parameters.get(name, rng.uniform(-2.0, 2.0))
        env = {"math": math, **vals}
        for coord in system.coordinates:
            expr = system.equations[f"{coord}_ddot"]
            cs = printer.doprint(expr)
            got = eval(_cs_to_py(cs), {"__builtins__": {}}, env)  # noqa: S307
            ref = float(expr.subs({s: vals[str(s)] for s in expr.free_symbols}))
            assert abs(got - ref) < 1e-9, f"{preset}/{coord}: {cs}"


def test_math_functions_are_remapped():
    system = compile_spec("pendulum")
    cs = render_component(system)
    assert "Math.Sin" in cs
    assert "sin(" not in cs.replace("Math.Sin", "")  # no bare sin( left


def test_component_is_well_formed():
    system = compile_spec("double_pendulum")
    cs = render_component(system)
    assert cs.count("{") == cs.count("}"), "unbalanced braces in generated C#"
    assert "class DoublePendulumComponent : MonoBehaviour" in cs
    assert "void FixedUpdate()" in cs
    assert "public const int Dof = 2;" in cs


def test_cli_generates_file(tmp_path):
    rc = cli_main(["generate", "pendulum", "-o", str(tmp_path)])
    assert rc == 0
    produced = list(tmp_path.glob("*.cs"))
    assert produced, "no .cs file generated"


def test_unreal_target_generates_component(tmp_path):
    rc = cli_main(["generate", "pendulum", "--target", "unreal", "-o", str(tmp_path)])
    assert rc == 0
    names = sorted(p.name for p in tmp_path.iterdir())
    assert names == ["SimplePendulumComponent.cpp", "SimplePendulumComponent.h",
                     "SimplePendulumDynamics.h"]
