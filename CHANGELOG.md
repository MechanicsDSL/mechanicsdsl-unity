# Changelog

All notable changes to mechanicsdsl-unity are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com).

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
