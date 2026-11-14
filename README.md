<p align="center">
  <img src="https://raw.githubusercontent.com/MechanicsDSL/mechanicsdsl/main/docs/images/logo.png" alt="MechanicsDSL Logo" width="360">
</p>

<h1 align="center">mechanicsdsl-unity</h1>

<p align="center">
  <em>Physically accurate simulation components for Unity and Unreal Engine, compiled from DSL notation.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-active-green" alt="Active">
  <img src="https://img.shields.io/badge/Unity-2021.3%2B-black" alt="Unity">
  <img src="https://img.shields.io/badge/components-3-blue" alt="3 Components">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
  <a href="https://github.com/MechanicsDSL/mechanicsdsl"><img src="https://img.shields.io/badge/core-mechanicsdsl-blue" alt="Core Package"></a>
</p>

## Overview

`mechanicsdsl-unity` provides Unity MonoBehaviour components generated from MechanicsDSL DSL specifications. All components bypass PhysX with Lagrangian equations of motion, include Noether-based energy monitoring, and expose parameters in the Unity Inspector for real-time tuning.

---

## Components

### Classical Mechanics

| Component | System | Conserved | Gizmos |
|-----------|--------|-----------|--------|
| `PendulumComponent` | Simple pendulum | Energy (Noether) | Pivot, rod, bob |
| `DoublePendulumComponent` | Double pendulum (chaotic) | Energy (Noether) | Full double pendulum |
| `CoupledPendulumsComponent` | Coupled pendulums | Energy (Noether) | Both pendulums + spring |

### Utilities

| Component | Description |
|-----------|-------------|
| `ConservationMonitor` | On-screen HUD for energy drift across any MechanicsDSL component |
| `PhaseSpaceTrail` | Renders θ vs ω phase portrait as a LineRenderer trail |
| `MechanicsDSLMath` | Generic RK4, symplectic Euler, angle wrap, bob position helpers |

### Editor

| Script | Description |
|--------|-------------|
| `PendulumComponentEditor` | Live state readout (θ, ω, t, E, \|ΔE/E₀\|) + Reset button |
| `DoublePendulumComponentEditor` | Dual-angle live readout + Reset button |

---

## Repository Structure

```
mechanicsdsl-unity/
├── Runtime/
│   ├── Components/
│   │   ├── PendulumComponent.cs
│   │   ├── DoublePendulumComponent.cs
│   │   └── CoupledPendulumsComponent.cs
│   ├── Utilities/
│   │   ├── ConservationMonitor.cs
│   │   ├── PhaseSpaceTrail.cs
│   │   └── MechanicsDSLMath.cs
│   └── com.mechanicsdsl.unity.runtime.asmdef
├── Editor/
│   ├── PendulumComponentEditor.cs
│   ├── DoublePendulumComponentEditor.cs
│   └── com.mechanicsdsl.unity.editor.asmdef
├── Tests/Runtime/
│   ├── TestPendulumEOM.cs
│   ├── TestDoublePendulumEOM.cs
│   └── MechanicsDSL.Tests.Runtime.asmdef
├── Samples~/
│   ├── SimplePendulum/README.md
│   └── DoublePendulum/README.md
├── docs/
│   ├── getting_started.md
│   ├── components_reference.md
│   └── adding_systems.md
└── package.json                (UPM manifest)
```

---

## Installation

**Via UPM (Unity Package Manager):**

1. Open **Window → Package Manager**
2. Click **+** → **Add package from git URL**
3. Enter: `https://github.com/MechanicsDSL/mechanicsdsl-unity.git`

---

## Quick Start

1. Add **MechanicsDSL → Classical → Pendulum** to any GameObject
2. Create a Sphere child and drag to **Bob Transform**
3. Press Play — the sphere is driven by MechanicsDSL-generated Lagrangian equations

The Inspector shows live θ, ω, E, and |ΔE/E₀| during Play Mode. Click **Reset** to return to initial conditions without stopping.

---

## Running Tests

**Window → General → Test Runner → PlayMode → Run All**

Tests cover energy conservation (5–10 s), reset/initial conditions, equilibrium stability, and bob Transform updates.

---

## Generating New Components

```bash
pip install mechanicsdsl-core
mechanicsdsl-unity generate my_system.msl --target unity --out Assets/Physics/
```

The `mechanicsdsl-unity` CLI compiles any `.msl` spec (or core preset) through
`mechanicsdsl-core` and writes engine code that integrates the derived
equations of motion with RK4:

```bash
pip install mechanicsdsl-unity
mechanicsdsl-unity targets
mechanicsdsl-unity generate double_pendulum --target unity  -o Assets/Generated/
mechanicsdsl-unity generate double_pendulum --target godot  -o scripts/
mechanicsdsl-unity generate double_pendulum --target unreal -o Source/MyGame/
mechanicsdsl-unity generate double_pendulum --target csharp -o lib/
mechanicsdsl-unity generate --all-presets --target unity -o Assets/Generated/
mechanicsdsl-unity inspect double_pendulum
```

| Target | Output | What you get |
|--------|--------|--------------|
| `unity` | `<Cls>Component.cs` | `MonoBehaviour`: Inspector parameters, sub-steps, pause, `GetState`/`SetState`, live `energy` and `energyDrift`, `OnStateUpdate` event |
| `csharp` | `<Cls>Dynamics.cs` | engine-free .NET class (C# 5 syntax) for Godot C#, MonoGame, Stride, servers |
| `godot` | `<system>_dynamics.gd` | Godot 4 GDScript `Node`: `@export` parameters, `state_updated` signal, `energy_drift` |
| `unreal` | `<Cls>Dynamics.h`, `<Cls>Component.h/.cpp` | UE5 Blueprint-spawnable `UActorComponent` + engine-free C++17 dynamics |

### How generated code is checked

The standalone C# is compiled (`csc` or the .NET SDK, warnings as errors), run
for 1000 RK4 steps and compared with a Python RK4 reference to 1e-12. The
Unity component is compiled against a minimal `UnityEngine` stub, and the
Unreal component against a minimal Unreal API stub with
`g++ -Wall -Wextra -Werror`, then ticked to check energy drift. GDScript
expressions are evaluated numerically against SymPy. These checks do not
replace testing inside the real editors, which the test suite cannot run.

See [docs/adding_systems.md](docs/adding_systems.md) for the full workflow.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License; see [LICENSE](LICENSE).
