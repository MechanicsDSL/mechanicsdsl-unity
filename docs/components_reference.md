# Components Reference

## Classical Mechanics

### PendulumComponent
**Namespace:** `MechanicsDSL.Classical`
**Path:** `Runtime/Components/PendulumComponent.cs`

Simple pendulum dynamics derived from $L = \frac{1}{2}ml^2\dot{\theta}^2 - mgl(1-\cos\theta)$.

| Property | Type | Description |
|----------|------|-------------|
| `mass` | float | Bob mass [kg] |
| `length` | float | Rod length [m] |
| `gravity` | float | Local gravity [m/s²] |
| `theta0` | float | Initial angle [rad] |
| `omega0` | float | Initial angular velocity [rad/s] |
| `dt` | float | Integration timestep [s] |
| `driftTolerance` | float | Noether monitor threshold |
| `bobTransform` | Transform | Optional bob visualisation target |
| **`Theta`** | float (read) | Current angle [rad] |
| **`Omega`** | float (read) | Current angular velocity [rad/s] |
| **`Energy`** | float (read) | Total mechanical energy [J] |
| **`EnergyDrift`** | float (read) | \|ΔE/E₀\| |
| **`SimTime`** | float (read) | Simulation time [s] |

**Methods:** `ResetToInitialConditions()`, `SetState(theta, omega)`

---

### DoublePendulumComponent
**Namespace:** `MechanicsDSL.Classical`
**Path:** `Runtime/Components/DoublePendulumComponent.cs`

Double pendulum with chaotic dynamics. Same parameter structure as `PendulumComponent` with additional `theta2_0`, `omega2_0`, `bob2Transform`, `Theta2`, `Omega2`.

---

### CoupledPendulumsComponent
**Namespace:** `MechanicsDSL.Classical`
**Path:** `Runtime/Components/CoupledPendulumsComponent.cs`

Two identical pendulums coupled by spring $k$. Exposes `spring` parameter and read-only `NormalMode1`, `NormalMode2` mode coordinates.

---

## Utilities

### ConservationMonitor
**Namespace:** `MechanicsDSL.Utilities`
**Path:** `Runtime/Utilities/ConservationMonitor.cs`

Monitors energy drift across any MechanicsDSL component via reflection. Displays on-screen HUD and fires `OnWarningDrift`, `OnCriticalDrift`, `OnDriftResolved` Unity Events.

---

### MechanicsDSLMath
**Namespace:** `MechanicsDSL.Utilities`
**Path:** `Runtime/Utilities/MechanicsDSLMath.cs`

Static utilities: generic `RK4Step2D`, `SymplecticEulerStep`, `EnergyDrift`, `WrapAngle`, `PendulumBobPosition`.

---

## Editor

### PendulumComponentEditor
Custom Inspector for `PendulumComponent`. Shows live θ, ω, t, E, |ΔE/E₀| readout and Reset button during Play Mode.

### DoublePendulumComponentEditor
Custom Inspector for `DoublePendulumComponent` with dual-angle live state readout.
