<p align="center">
  <img src="https://raw.githubusercontent.com/MechanicsDSL/mechanicsdsl/main/docs/images/logo.png" alt="MechanicsDSL Logo" width="360">
</p>

<h1 align="center">mechanicsdsl-unity</h1>

<p align="center">
  <em>Physically accurate simulation components for Unity and Unreal Engine, compiled from DSL notation.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-planned-lightgrey" alt="Status: Planned">
  <img src="https://img.shields.io/badge/engines-Unity%20%7C%20Unreal-blue" alt="Unity and Unreal">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
  <a href="https://github.com/MechanicsDSL/mechanicsdsl"><img src="https://img.shields.io/badge/core-mechanicsdsl-blue" alt="Core Package"></a>
</p>

---

## Overview

`mechanicsdsl-unity` brings the MechanicsDSL compiler into game engine workflows. Define a physical system in DSL notation and generate drop-in simulation components for Unity (C#) or Unreal Engine (C++) — bypassing built-in physics engines where analytical accuracy matters more than real-time approximation.

Target applications include physically accurate game mechanics, interactive science museum exhibits, engineering digital twins, robotics simulators, and educational physics visualizations.

---

## Planned Capabilities

### Unity Integration
- **MonoBehaviour components** — Generated C# classes implementing `FixedUpdate` with DSL-derived equations of motion
- **Unity Package Manager** — Installable via UPM git URL; no manual file copying
- **Inspector integration** — DSL parameters exposed as serialized fields, editable in the Unity Inspector at runtime
- **Gizmo visualization** — Automatic drawing of constraint surfaces, phase space trajectories, and conservation law monitors in the Scene view
- **Physics override** — Optional Rigidbody replacement for objects governed by DSL dynamics rather than PhysX

### Unreal Engine Integration
- **Actor components** — Generated C++ `UActorComponent` subclasses with `TickComponent` implementing DSL dynamics
- **Blueprint exposure** — Key parameters and state variables exposed to Blueprint via `UPROPERTY` macros
- **Plugin scaffolding** — Auto-generated Unreal plugin structure with `uplugin` manifest and `Build.cs`
- **Chaos Physics bypass** — Direct position/velocity injection for objects under DSL control

### Shared Capabilities
- **Real-time parameter tuning** — Adjust physical parameters at runtime through engine-native UI without recompiling
- **Constraint visualization** — Render constraint forces and Lagrange multipliers as debug overlays
- **Conservation monitoring** — In-engine HUD elements displaying energy drift and conservation law status
- **Export pipeline** — `mechanicsdsl generate --target unity` and `--target unreal` CLI commands

### Example Projects
- Physically accurate double pendulum with chaos visualization
- Coupled oscillator audio synthesis (string vibration → sound)
- Orbital mechanics sandbox with Keplerian trajectories
- Rigid body gyroscope with Euler angle gimbal lock demonstration
- Interactive Lagrangian mechanics tutorial scene for classroom use

---

## Relationship to Core Package

This repository provides engine-specific scaffolding, CLI tooling, and example projects. Code generation lives in [mechanicsdsl](https://github.com/MechanicsDSL/mechanicsdsl):

```bash
pip install mechanicsdsl-core

# Generate Unity component
mechanicsdsl generate pendulum.msl --target unity --out Assets/Physics/

# Generate Unreal component  
mechanicsdsl generate pendulum.msl --target unreal --out Source/MyProject/Physics/
```

The generated engine code has no Python dependency at runtime — it is self-contained C# or C++.

---

## Status

This repository is in the planning stage. The core package already generates Unity (C#) and Unreal (C++) code; this repository will provide the plugin packaging, Inspector/Blueprint integration, and example projects. Watch this repository for updates.

---

## Contributing

Contributions welcome — particularly from developers with Unreal or Unity plugin experience. See [CONTRIBUTING.md](https://github.com/MechanicsDSL/mechanicsdsl/blob/main/CONTRIBUTING.md).

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <a href="https://github.com/MechanicsDSL/mechanicsdsl">Core Package</a> ·
  <a href="https://mechanicsdsl.readthedocs.io">Documentation</a> ·
  <a href="https://doi.org/10.5281/zenodo.17771040">Zenodo DOI</a>
</p>
