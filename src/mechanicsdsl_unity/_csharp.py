"""
_csharp.py
----------
A SymPy -> C# code generator for MechanicsDSL.

Core ships C++, Python, Rust, CUDA, ... generators but no C# backend, so this
module implements one. :class:`CSharpPrinter` subclasses SymPy's
:class:`~sympy.printing.c.C99CodePrinter` and remaps math functions to
``System.Math`` (``Math.Sin``, ``Math.Pow`` ...). Two renderers build on it:

* :func:`render_component` - a Unity ``MonoBehaviour`` that integrates the
  dynamics each ``FixedUpdate`` with RK4 (bypassing PhysX), with sub-stepping,
  pause/reset, state get/set and live energy-drift monitoring;
* :func:`render_standalone` - a plain .NET class with no engine dependency,
  usable from Godot C#, MonoGame, Stride, servers or tests. It is written in
  C# 5 syntax so even the compiler bundled with Windows can build it.

All internal identifiers carry an ``mdsl`` prefix so they cannot collide with
user coordinate or parameter names, and C# keywords used as DSL names are
escaped with ``@``.
"""

from __future__ import annotations

from string import Template
from typing import TYPE_CHECKING, List

import sympy as sp
from sympy.printing.c import C99CodePrinter

if TYPE_CHECKING:
    from ._bridge import CompiledSystem


_CS_FUNCS = {
    "sin": "Math.Sin", "cos": "Math.Cos", "tan": "Math.Tan",
    "asin": "Math.Asin", "acos": "Math.Acos", "atan": "Math.Atan",
    "atan2": "Math.Atan2", "sinh": "Math.Sinh", "cosh": "Math.Cosh",
    "tanh": "Math.Tanh", "exp": "Math.Exp", "log": "Math.Log",
    "sqrt": "Math.Sqrt", "Abs": "Math.Abs", "floor": "Math.Floor",
    "ceiling": "Math.Ceiling",
}

CS_KEYWORDS = frozenset("""
abstract as base bool break byte case catch char checked class const continue
decimal default delegate do double else enum event explicit extern false finally
fixed float for foreach goto if implicit in int interface internal is lock long
namespace new null object operator out override params private protected public
readonly ref return sbyte sealed short sizeof stackalloc static string struct
switch this throw true try typeof uint ulong unchecked unsafe ushort using
virtual void volatile while
""".split())


def cs_ident(name: str) -> str:
    """Escape a DSL name that happens to be a C# keyword."""
    return f"@{name}" if name in CS_KEYWORDS else name


class CSharpPrinter(C99CodePrinter):
    """Print SymPy expressions as C# (``System.Math``) expressions."""

    def __init__(self, settings=None):
        super().__init__(settings or {})
        self.known_functions = dict(_CS_FUNCS)

    def _print_Symbol(self, expr):
        return cs_ident(expr.name)

    def _print_Pi(self, expr):
        return "Math.PI"

    def _print_Exp1(self, expr):
        return "Math.E"

    def _print_Pow(self, expr):
        if expr.exp == -1:
            return f"(1.0/({self._print(expr.base)}))"
        if expr.exp == sp.Rational(1, 2):
            return f"Math.Sqrt({self._print(expr.base)})"
        return f"Math.Pow({self._print(expr.base)}, {self._print(expr.exp)})"


def expr_to_csharp(expr: "sp.Expr") -> str:
    """Convert a single SymPy expression to a C# expression string."""
    return CSharpPrinter().doprint(expr)


def _pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace("-", "_").split("_"))


def _cs_float(v: float) -> str:
    text = repr(float(v))
    return text if ("e" in text or "." in text) else text + ".0"


def _accel_lines(system: "CompiledSystem", indent: str, param_ref: str) -> List[str]:
    """Locals + CSE temporaries + qdd assignments for the Accel method body."""
    printer = CSharpPrinter()
    exprs = [system.equations[f"{c}_ddot"] for c in system.coordinates]
    used = set().union(*[{str(s) for s in e.free_symbols} for e in exprs])
    lines = []
    for i, c in enumerate(system.coordinates):
        if c in used:
            lines.append(f"{indent}double {cs_ident(c)} = mdslQ[{i}];")
        if f"{c}_dot" in used:
            lines.append(f"{indent}double {cs_ident(c + '_dot')} = mdslQd[{i}];")
    for p in sorted(system.parameters):
        if p in used:
            lines.append(f"{indent}double {cs_ident(p)} = {param_ref}{cs_ident(p)};")
    temps, reduced = sp.cse(exprs, symbols=sp.numbered_symbols("mdslT"))
    lines += [f"{indent}double {s} = {printer.doprint(v)};" for s, v in temps]
    lines += [f"{indent}mdslQdd[{i}] = {printer.doprint(e)};" for i, e in enumerate(reduced)]
    return lines


def _energy_lines(system: "CompiledSystem", indent: str, param_ref: str) -> List[str]:
    printer = CSharpPrinter()
    n = system.dof
    used = {str(s) for s in system.energy.free_symbols}
    lines = []
    for i, c in enumerate(system.coordinates):
        if c in used:
            lines.append(f"{indent}double {cs_ident(c)} = mdslY[{i}];")
        if f"{c}_dot" in used:
            lines.append(f"{indent}double {cs_ident(c + '_dot')} = mdslY[{n + i}];")
    for p in sorted(system.parameters):
        if p in used:
            lines.append(f"{indent}double {cs_ident(p)} = {param_ref}{cs_ident(p)};")
    temps, (reduced,) = sp.cse([system.energy], symbols=sp.numbered_symbols("mdslE"))
    lines += [f"{indent}double {s} = {printer.doprint(v)};" for s, v in temps]
    lines.append(f"{indent}return {printer.doprint(reduced)};")
    return lines


_RK4 = """
        private void MdslDeriv(double[] mdslY, double[] mdslDydt)
        {
            double[] mdslQdd = new double[Dof];
            double[] mdslQ = new double[Dof];
            double[] mdslQd = new double[Dof];
            Array.Copy(mdslY, 0, mdslQ, 0, Dof);
            Array.Copy(mdslY, Dof, mdslQd, 0, Dof);
            Accel(mdslQ, mdslQd, mdslQdd);
            for (int mdslI = 0; mdslI < Dof; mdslI++)
            {
                mdslDydt[mdslI] = mdslY[Dof + mdslI];
                mdslDydt[Dof + mdslI] = mdslQdd[mdslI];
            }
        }

        /// <summary>Advance the state by one classic RK4 step of size dt.</summary>
        public void Step(double dt)
        {
            double[] k1 = new double[StateDim];
            double[] k2 = new double[StateDim];
            double[] k3 = new double[StateDim];
            double[] k4 = new double[StateDim];
            double[] tmp = new double[StateDim];
            MdslDeriv(_y, k1);
            for (int i = 0; i < StateDim; i++) tmp[i] = _y[i] + 0.5 * dt * k1[i];
            MdslDeriv(tmp, k2);
            for (int i = 0; i < StateDim; i++) tmp[i] = _y[i] + 0.5 * dt * k2[i];
            MdslDeriv(tmp, k3);
            for (int i = 0; i < StateDim; i++) tmp[i] = _y[i] + dt * k3[i];
            MdslDeriv(tmp, k4);
            for (int i = 0; i < StateDim; i++)
                _y[i] += (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
            _simTime += dt;
        }

        /// <summary>Copy of the state vector [q..., qdot...].</summary>
        public double[] GetState() { return (double[])_y.Clone(); }

        /// <summary>Overwrite the state vector [q..., qdot...].</summary>
        public void SetState(double[] state)
        {
            if (state == null || state.Length != StateDim)
                throw new ArgumentException("state must have length " + StateDim);
            Array.Copy(state, _y, StateDim);
        }
"""


_COMPONENT = Template(
    """// Auto-generated by mechanicsdsl-unity. DO NOT EDIT BY HAND.
//
// Equations of motion derived from the following DSL specification by
// mechanicsdsl-core and transcribed to C# via SymPy:
//
$src_comment
//
using System;
using UnityEngine;

namespace MechanicsDSL.Generated
{
    /// <summary>
    /// $system dynamics ($dof DOF) generated by MechanicsDSL. Integrates the
    /// Lagrangian equations of motion each FixedUpdate with RK4, bypassing
    /// PhysX. Parameters are exposed in the Inspector for live tuning.
    /// </summary>
    [AddComponentMenu("MechanicsDSL/Generated/$cls")]
    [DisallowMultipleComponent]
    public class ${cls}Component : MonoBehaviour
    {
        [Header("Physical Parameters")]
$param_fields

        [Header("Initial Conditions")]
$ic_fields

        [Header("Integrator")]
        [Tooltip("Integration timestep [s]. 0 = use Time.fixedDeltaTime.")]
        public float timestep = 0f;
        [Tooltip("RK4 sub-steps per FixedUpdate (more = more accurate).")]
        [Min(1)] public int substeps = 1;
        [Tooltip("Freeze the simulation without losing state.")]
        public bool paused = false;

        [Header("Diagnostics (read-only)")]
        [Tooltip("Current energy E = sum(qdot dL/dqdot) - L.")]
        public double energy;
        [Tooltip("Relative energy drift since the last reset.")]
        public double energyDrift;

        /// <summary>Fired each FixedUpdate with the full state vector
        /// [q0..q$last, qdot0..qdot$last].</summary>
        public event Action<double[]> OnStateUpdate;

        public const int Dof = $dof;
        public const int StateDim = $state_dim;
        public const bool HasEnergy = $has_energy;
        public static readonly string[] StateNames = { $state_names };

        // Runtime state: [q0..q, qdot0..qdot].
        private readonly double[] _y = new double[StateDim];
        private double _simTime;
        private double _energy0;

        /// <summary>Elapsed simulated time [s] since the last reset.</summary>
        public double SimTime { get { return _simTime; } }

        void Start()
        {
            ResetState();
        }

        public void ResetState()
        {
$reset_body
            _simTime = 0.0;
            _energy0 = Energy();
            energy = _energy0;
            energyDrift = 0.0;
        }

        void FixedUpdate()
        {
            if (paused) return;
            double dt = timestep > 0f ? timestep : Time.fixedDeltaTime;
            int n = Math.Max(1, substeps);
            for (int s = 0; s < n; s++) Step(dt / n);
            energy = Energy();
            energyDrift = Math.Abs(energy - _energy0) / Math.Max(Math.Abs(_energy0), 1e-12);
            var handler = OnStateUpdate;
            if (handler != null) handler((double[])_y.Clone());
        }

        /// <summary>Generalized accelerations from positions q and velocities qd.</summary>
        public void Accel(double[] mdslQ, double[] mdslQd, double[] mdslQdd)
        {
$accel_body
        }

        /// <summary>Energy of the current state (0 if the spec has no Lagrangian).</summary>
        public double Energy() { return EnergyOf(_y); }

        public double EnergyOf(double[] mdslY)
        {
$energy_body
        }
$rk4
    }
}
"""
)


_STANDALONE = Template(
    """// Auto-generated by mechanicsdsl-unity. DO NOT EDIT BY HAND.
//
// Engine-independent .NET dynamics (C# 5 syntax, no dependencies) derived by
// mechanicsdsl-core from:
//
$src_comment
//
using System;

namespace MechanicsDSL.Generated
{
    /// <summary>Physical parameters for $system.</summary>
    public sealed class ${cls}Params
    {
$param_props
    }

    /// <summary>
    /// $system ($dof DOF): RK4 integration of the DSL-derived equations of motion.
    /// Usable from Godot C#, MonoGame, Stride, servers and tests.
    /// </summary>
    public sealed class ${cls}Dynamics
    {
        public const int Dof = $dof;
        public const int StateDim = $state_dim;
        public static readonly string[] StateNames = { $state_names };

        public ${cls}Params P = new ${cls}Params();
        private readonly double[] _y = new double[StateDim];
        private double _simTime;

        public ${cls}Dynamics() { Reset(); }

        public double SimTime { get { return _simTime; } }

        /// <summary>Restore the DSL initial conditions.</summary>
        public void Reset()
        {
$reset_body
            _simTime = 0.0;
        }

        public void Accel(double[] mdslQ, double[] mdslQd, double[] mdslQdd)
        {
$accel_body
        }

        public double Energy() { return EnergyOf(_y); }

        public double EnergyOf(double[] mdslY)
        {
$energy_body
        }
$rk4
    }
}
"""
)


def _common(system: "CompiledSystem", param_ref: str) -> dict:
    coords = system.coordinates
    n = len(coords)
    accel = _accel_lines(system, " " * 12, param_ref)
    if system.energy is not None:
        energy = _energy_lines(system, " " * 12, param_ref)
    else:
        energy = [" " * 12 + "return 0.0;"]
    return {
        "src_comment": "\n".join(f"//     {ln}" for ln in system.source.splitlines()),
        "system": system.name,
        "cls": _pascal(system.name),
        "dof": str(n),
        "last": str(n - 1),
        "state_dim": str(2 * n),
        "state_names": ", ".join(f'"{s}"' for s in system.state_names),
        "accel_body": "\n".join(accel),
        "energy_body": "\n".join(energy),
        "has_energy": "true" if system.energy is not None else "false",
        "rk4": _RK4,
    }


def render_component(system: "CompiledSystem") -> str:
    """Render a Unity MonoBehaviour C# component for ``system``."""
    coords = system.coordinates
    n = len(coords)
    param_names = sorted(system.parameters)
    param_fields = "\n".join(
        f'        [Tooltip("Parameter {p} [{system.units.get(p, "")}]")]'
        f"\n        public float {cs_ident(p)} = {float(system.parameters[p])}f;"
        for p in param_names
    )
    ic_fields = []
    for c in coords:
        q0 = float(system.initial_conditions.get(c, 0.0))
        v0 = float(system.initial_conditions.get(f"{c}_dot", 0.0))
        ic_fields.append(f'        [Tooltip("Initial {c}")]'
                         f"\n        public float {c}0 = {q0}f;")
        ic_fields.append(f'        [Tooltip("Initial {c} rate")]'
                         f"\n        public float {c}0_dot = {v0}f;")
    reset = [f"            _y[{i}] = {c}0;" for i, c in enumerate(coords)]
    reset += [f"            _y[{n + i}] = {c}0_dot;" for i, c in enumerate(coords)]

    subs = _common(system, "this.")
    subs.update(param_fields=param_fields, ic_fields="\n".join(ic_fields),
                reset_body="\n".join(reset))
    return _COMPONENT.substitute(subs)


def render_standalone(system: "CompiledSystem") -> str:
    """Render an engine-independent .NET dynamics class for ``system``."""
    props = "\n".join(
        f"        /// <summary>{system.units.get(p) or 'dimensionless'}</summary>\n"
        f"        public double {cs_ident(p)} = {_cs_float(system.parameters[p])};"
        for p in sorted(system.parameters)
    )
    reset = [f"            _y[{i}] = {_cs_float(v)};  // {s}"
             for i, (s, v) in enumerate(zip(system.state_names, system.initial_state()))]
    subs = _common(system, "P.")
    subs.update(param_props=props, reset_body="\n".join(reset))
    return _STANDALONE.substitute(subs)
