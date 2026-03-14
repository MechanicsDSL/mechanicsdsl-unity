# Simple Pendulum Sample

Demonstrates the `PendulumComponent` MonoBehaviour with Inspector parameter tuning, Scene-view Gizmos, and real-time Noether energy monitoring.

## Setup

1. Install the MechanicsDSL package via UPM:
   - Open **Package Manager** → **Add package from git URL**
   - Enter: `https://github.com/MechanicsDSL/mechanicsdsl-unity.git`

2. Import the **Simple Pendulum** sample:
   - In Package Manager, expand **MechanicsDSL** → **Samples** → **Simple Pendulum** → **Import**

3. Open **Assets/Samples/MechanicsDSL/SimplePendulum/SimplePendulumScene.unity**

## Scene Contents

| GameObject | Component | Description |
|------------|-----------|-------------|
| Pivot | `PendulumComponent` | Pendulum dynamics (MechanicsDSL-generated) |
| Bob | `SphereRenderer` | Driven by `PendulumComponent.bobTransform` |
| Monitor | `ConservationMonitor` | Real-time energy drift HUD |

## Parameters (Inspector)

All physical parameters are exposed in the Inspector and can be edited in Play Mode:

- **Mass** (m) — bob mass [kg]
- **Length** (l) — rod length [m]
- **Gravity** — local gravitational acceleration [m/s²]
- **Theta0** — initial angle from vertical [rad]
- **Dt** — integration timestep (default 4 ms = 250 Hz)

## DSL Specification

This sample was generated from:

```
\system{pendulum}
\parameter{m}{1.0}{kg}
\parameter{l}{1.0}{m}
\lagrangian{0.5*m*l^2*\dot{theta}^2 - m*g*l*(1-cos(theta))}
\target{unity}
```
