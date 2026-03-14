# Getting Started with mechanicsdsl-unity

## Installation

### Via UPM (Unity Package Manager)

1. Open **Window → Package Manager**
2. Click **+** → **Add package from git URL**
3. Enter: `https://github.com/MechanicsDSL/mechanicsdsl-unity.git`

### Manual

Clone the repo and copy the `Runtime/`, `Editor/`, and `package.json` into your project's `Packages/` folder.

---

## Quick Start

### Simple Pendulum

1. Create an empty GameObject named `PendulumSystem`
2. Add Component → **MechanicsDSL → Classical → Pendulum**
3. Create a Sphere child GameObject, drag it to **Bob Transform**
4. Press Play

The sphere moves under MechanicsDSL-generated Lagrangian equations of motion, bypassing PhysX entirely.

### Adjusting Parameters at Runtime

All physical parameters are editable in the Inspector during Play Mode:

- Change **Length** to observe period changes ($T = 2\pi\sqrt{l/g}$)
- Change **Theta0** and click **Reset** in the Inspector
- Watch **|ΔE/E₀|** in the live readout — should stay below `1e-4`

---

## Components Reference

| Component | Namespace | Description |
|-----------|-----------|-------------|
| `PendulumComponent` | `MechanicsDSL.Classical` | Simple pendulum |
| `DoublePendulumComponent` | `MechanicsDSL.Classical` | Double pendulum (chaotic) |
| `ConservationMonitor` | `MechanicsDSL.Utilities` | Noether energy drift HUD |
| `MechanicsDSLMath` | `MechanicsDSL.Utilities` | RK4, symplectic Euler, helpers |

---

## Generating New Components

Install `mechanicsdsl-core` and generate Unity components from DSL:

```bash
pip install mechanicsdsl-core
mechanicsdsl generate coupled_oscillators.msl --target unity --out Assets/Physics/
```

This produces a `CoupledOscillatorsComponent.cs` ready to drop into your project.

---

## Running Tests

1. Open **Window → General → Test Runner**
2. Select **Play Mode** tab
3. Click **Run All**

Tests validate energy conservation, reset behaviour, and EOM correctness.
