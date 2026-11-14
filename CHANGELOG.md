# Changelog

All notable changes to mechanicsdsl-unity are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com).

## [0.2.0] - 2026-11-14

### Added
- `unreal` target: a UE5 Blueprint-spawnable `UActorComponent` (.h/.cpp) plus engine-free C++17 dynamics. Replaces the previous "not implemented" exit.
- `godot` target: Godot 4 GDScript `Node` with `@export` parameters, a `state_updated` signal and energy drift.
- `csharp` target: an engine-independent .NET class (C# 5 syntax).
- Unity components gain sub-stepping, pause, `GetState`/`SetState`, `SimTime`, and live `energy`/`energyDrift` readouts.
- `generate --all-presets`, plus `targets`, `presets` and `inspect` commands.
- Shared bridge to core: energy E = sum(qdot dL/dqdot) - L derived from the Lagrangian, a `conservative` flag, `simulate()` (fixed-step RK4 reference), `energy_drift()`, `operation_count()`, `list_presets()`, and `CompiledSystem.describe()`.
- Core's mass-matrix output (`__mass_matrix__`, used for large systems such as the three-body `figure8` preset) is converted to explicit accelerations, so every core preset now generates.

### Changed
- C# printing uses common-subexpression elimination and escapes C# keywords used as DSL names.

### Fixed
- Internal identifiers are prefixed so they cannot collide with coordinate or parameter names.

### Infrastructure
- CI workflow: pytest on Python 3.9-3.12 (Linux) plus Windows and macOS, a syntax/undefined-name lint, and an sdist/wheel build check.
- Dependabot (pip and GitHub Actions), issue and PR templates, pre-commit config, `SECURITY.md`, `CODE_OF_CONDUCT.md`.
- Single-source version (`_version.py`, read by hatch); requires `mechanicsdsl-core>=2.1.4`.

## [Unreleased]

### Added
- `PendulumComponent` — simple pendulum MonoBehaviour with RK4, Noether monitor, Gizmos
- `DoublePendulumComponent` — double pendulum MonoBehaviour with chaos detection
- `MechanicsDSLMath` — shared utilities: generic RK4, symplectic Euler, angle wrapping
- `ConservationMonitor` — on-screen HUD for Noether conservation law monitoring
- `PendulumComponentEditor` — custom Inspector with live state readout and reset button
- UPM `package.json` manifest with sample declarations
- Runtime tests: `TestPendulumEOM`
- Sample documentation: SimplePendulum, DoublePendulum

## [0.1.0] — 2026-03-13

- Initial repository scaffold
