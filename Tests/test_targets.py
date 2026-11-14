"""
test_targets.py
---------------
Every generation target, checked by *building and running* where a toolchain
exists and by numeric re-evaluation everywhere else.

* C#: compiled with ``csc`` (bundled with Windows' .NET Framework) or the .NET
  SDK. The standalone class is run and its RK4 state compared with the
  bridge's Python RK4; the Unity component is compiled against a minimal
  ``UnityEngine`` stub so syntax and types are checked without Unity.
* Unreal: the engine-free dynamics header is compiled and run with g++/clang;
  the component is compiled against a minimal stub of the Unreal API.
* GDScript: expressions are translated back to Python and compared with SymPy.
"""
import glob
import math
import os
import random
import re
import shutil
import subprocess
import textwrap

import pytest

pytest.importorskip("mechanics_dsl", reason="mechanicsdsl-core required")

from mechanicsdsl_unity import (  # noqa: E402
    compile_spec,
    expr_to_gdscript,
    numeric_energy,
    render_component,
    render_gdscript,
    render_standalone,
    render_unreal,
    simulate,
)
from mechanicsdsl_unity._csharp import _pascal  # noqa: E402
from mechanicsdsl_unity.cli import main as cli_main  # noqa: E402

PRESETS = ["pendulum", "double_pendulum", "coupled_oscillators", "damped_oscillator",
           "projectile", "figure8"]


def _find_csc():
    on_path = shutil.which("csc")
    if on_path:
        return [on_path]
    windir = os.environ.get("WINDIR", r"C:\Windows")
    hits = sorted(glob.glob(os.path.join(windir, "Microsoft.NET", "Framework64", "v4*",
                                         "csc.exe")))
    return [hits[-1]] if hits else None


def _dotnet_sdk():
    exe = shutil.which("dotnet")
    if not exe:
        return None
    out = subprocess.run([exe, "--list-sdks"], capture_output=True, text=True).stdout
    return exe if out.strip() else None


CSC = _find_csc()
DOTNET = _dotnet_sdk()
CXX = shutil.which("g++") or shutil.which("clang++")
needs_cs = pytest.mark.skipif(CSC is None and DOTNET is None, reason="no C# compiler")
needs_cxx = pytest.mark.skipif(CXX is None, reason="no C++ compiler")


@pytest.fixture(scope="module", params=PRESETS)
def system(request):
    return compile_spec(request.param)


def _build_cs(sources, tmp_path, exe_name="prog", library=False):
    """Compile C# sources; return a command that runs the result (or None for libraries)."""
    if CSC:
        target = "/target:library" if library else "/target:exe"
        out = tmp_path / (exe_name + (".dll" if library else ".exe"))
        r = subprocess.run(CSC + ["/nologo", "/warnaserror+", target, f"/out:{out}"]
                           + [str(s) for s in sources], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        return None if library else [str(out)]
    proj = tmp_path / "proj"
    proj.mkdir()
    for s in sources:
        shutil.copy(s, proj)
    kind = "Library" if library else "Exe"
    (proj / "p.csproj").write_text(textwrap.dedent(f"""\
        <Project Sdk="Microsoft.NET.Sdk">
          <PropertyGroup><OutputType>{kind}</OutputType>
          <TargetFramework>net8.0</TargetFramework>
          <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
          <Nullable>disable</Nullable></PropertyGroup>
        </Project>"""))
    r = subprocess.run([DOTNET, "build", "-nologo", "-o", str(proj / "bin")], cwd=proj,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return None if library else [DOTNET, str(proj / "bin" / "p.dll")]


# ------------------------------------------------------------- standalone C#
@needs_cs
def test_standalone_csharp_runs_and_matches_reference(system, tmp_path):
    cls = _pascal(system.name)
    dt = 1e-3
    (tmp_path / f"{cls}.cs").write_text(render_standalone(system), encoding="utf-8")
    (tmp_path / "Main.cs").write_text(textwrap.dedent(f"""\
        using System; using System.Globalization; using MechanicsDSL.Generated;
        class Program {{ static void Main() {{
            var d = new {cls}Dynamics();
            for (int k = 0; k < 1000; k++) d.Step({dt!r});
            foreach (var v in d.GetState())
                Console.Write(v.ToString("R", CultureInfo.InvariantCulture) + " ");
            Console.WriteLine(d.Energy().ToString("R", CultureInfo.InvariantCulture));
        }} }}"""), encoding="utf-8")
    cmd = _build_cs([tmp_path / f"{cls}.cs", tmp_path / "Main.cs"], tmp_path)
    vals = [float(v) for v in subprocess.run(cmd, capture_output=True, text=True,
                                             check=True).stdout.split()]
    _, Y = simulate(system, t_end=1000 * dt, dt=dt)
    scale = max(1.0, max(abs(v) for v in Y[-1]))
    assert max(abs(a - b) for a, b in zip(vals, Y[-1])) / scale < 1e-12
    E = numeric_energy(system)(Y[-1])
    assert abs(vals[-1] - E) / max(1.0, abs(E)) < 1e-12


# ------------------------------------------------------- Unity (stubbed API)
UNITY_STUB = """
namespace UnityEngine {
    public class MonoBehaviour {}
    public static class Time { public static float fixedDeltaTime = 0.02f; }
    [System.AttributeUsage(System.AttributeTargets.All)] public class HeaderAttribute : System.Attribute { public HeaderAttribute(string s) {} }
    [System.AttributeUsage(System.AttributeTargets.All)] public class TooltipAttribute : System.Attribute { public TooltipAttribute(string s) {} }
    [System.AttributeUsage(System.AttributeTargets.All)] public class MinAttribute : System.Attribute { public MinAttribute(float f) {} }
    [System.AttributeUsage(System.AttributeTargets.All)] public class AddComponentMenu : System.Attribute { public AddComponentMenu(string s) {} }
    [System.AttributeUsage(System.AttributeTargets.All)] public class DisallowMultipleComponent : System.Attribute {}
}
"""


@needs_cs
def test_unity_component_compiles_against_unity_api(system, tmp_path):
    (tmp_path / "UnityStub.cs").write_text(UNITY_STUB, encoding="utf-8")
    (tmp_path / "Comp.cs").write_text(render_component(system), encoding="utf-8")
    _build_cs([tmp_path / "UnityStub.cs", tmp_path / "Comp.cs"], tmp_path,
              exe_name="unity", library=True)


def test_unity_component_has_diagnostics():
    cs = render_component(compile_spec("double_pendulum"))
    for needle in ("public int substeps", "public bool paused", "public double energyDrift",
                   "public void SetState(double[] state)", "public double EnergyOf("):
        assert needle in cs


# --------------------------------------------------------------------- Godot
def _gd_to_py(src: str) -> str:
    return re.sub(r"\b(sin|cos|tan|asin|acos|atan|atan2|sinh|cosh|tanh|exp|log|sqrt|pow|"
                  r"floor|ceil)\(", r"math.\1(", src).replace("absf(", "abs(").replace(
                      "PI", "math.pi")


def test_gdscript_expressions_match_sympy(system):
    rng = random.Random(7)
    exprs = list(system.equations.values()) + [system.energy]
    for e in exprs:
        py = _gd_to_py(expr_to_gdscript(e))
        syms = list(e.free_symbols)
        for _ in range(10):
            vals = {str(s): rng.uniform(0.3, 2.0) for s in syms}
            want = float(e.subs({s: vals[str(s)] for s in syms}))
            got = eval(py, {"math": math}, vals)  # noqa: S307 - generated by us
            assert abs(got - want) <= 1e-12 * max(1.0, abs(want))


def test_gdscript_never_uses_integer_division(system):
    gd = render_gdscript(system)
    body = gd.split("func accel", 1)[1]
    # every literal in the physics is a float: no bare integers next to an operator
    assert not re.search(r"(?<![\w.\[])\d+(?![\w.\]])\s*[/*]", body.split("func _deriv")[0])
    assert "extends Node" in gd and "signal state_updated" in gd
    assert "\t" in gd and "    var" not in gd  # GDScript indentation is tabs here


# -------------------------------------------------------------------- Unreal
UE_STUB = """
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>
#define UCLASS(...)
#define UPROPERTY(...)
#define UFUNCTION(...)
#define GENERATED_BODY()
using int32 = std::int32_t;
enum ELevelTick { LEVELTICK_All };
struct FActorComponentTickFunction {};
struct FTickStub { bool bCanEverTick = false; };
template <typename T> struct TArray {
    std::vector<T> v;
    TArray(const T* p, int n) : v(p, p + n) {}
};
struct FMath {
    template <typename T> static T Max(T a, T b) { return std::max(a, b); }
    static double Abs(double a) { return std::fabs(a); }
};
class UActorComponent {
public:
    virtual ~UActorComponent() = default;
    FTickStub PrimaryComponentTick;
    virtual void BeginPlay() {}
    virtual void TickComponent(float, ELevelTick, FActorComponentTickFunction*) {}
};
"""


@needs_cxx
def test_unreal_component_compiles_against_stub_api(system, tmp_path):
    files = render_unreal(system)
    cls = _pascal(system.name)
    for name, text in files.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    (tmp_path / "CoreMinimal.h").write_text(UE_STUB, encoding="utf-8")
    (tmp_path / "Components").mkdir()
    (tmp_path / "Components" / "ActorComponent.h").write_text("#pragma once\n")
    (tmp_path / f"{cls}Component.generated.h").write_text("#pragma once\n")
    # Unreal's Super:: typedef comes from GENERATED_BODY; supply it for the stub build.
    cpp = (tmp_path / f"{cls}Component.cpp").read_text()
    cpp = cpp.replace("Super::", "UActorComponent::")
    (tmp_path / f"{cls}Component.cpp").write_text(cpp, encoding="utf-8")
    driver = tmp_path / "drive.cpp"
    driver.write_text(textwrap.dedent(f"""\
        #include "{cls}Component.h"
        #include <cstdio>
        int main() {{
            U{cls}Component c; c.Substeps = 10; c.FixedTimestep = 0.01;
            c.ResetState();
            for (int i = 0; i < 100; ++i) c.TickComponent(0.01f, LEVELTICK_All, nullptr);
            std::printf("%.17g %.17g\\n", c.GetSimTime(), c.EnergyDrift);
        }}"""), encoding="utf-8")
    exe = tmp_path / "drive.bin"
    r = subprocess.run([CXX, "-std=c++17", "-Wall", "-Wextra", "-Werror", "-I", str(tmp_path),
                        str(tmp_path / f"{cls}Component.cpp"), str(driver), "-o", str(exe)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    sim_time, drift = map(float, subprocess.run([str(exe)], capture_output=True, text=True,
                                                check=True).stdout.split())
    assert sim_time == pytest.approx(1.0)
    if system.conservative:
        assert drift < 1e-8


# ----------------------------------------------------------------------- CLI
@pytest.mark.parametrize("target,suffix", [("unity", ".cs"), ("csharp", ".cs"),
                                           ("godot", ".gd"), ("unreal", ".h")])
def test_cli_every_target(tmp_path, target, suffix):
    assert cli_main(["generate", "double_pendulum", "-t", target, "-o", str(tmp_path)]) == 0
    assert any(p.suffix == suffix for p in tmp_path.iterdir())


def test_cli_all_presets(tmp_path):
    assert cli_main(["generate", "--all-presets", "-t", "csharp", "-o", str(tmp_path)]) == 0
    assert len(list(tmp_path.glob("*Dynamics.cs"))) >= 8


def test_cli_inspect(capsys):
    assert cli_main(["inspect", "double_pendulum"]) == 0
    assert "theta2_ddot" in capsys.readouterr().out
