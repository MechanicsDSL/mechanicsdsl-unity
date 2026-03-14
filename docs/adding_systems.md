# Adding New Systems

This guide walks through generating a new MechanicsDSL Unity component from a DSL specification.

---

## Step 1: Write the DSL Specification

Create a `.msl` file describing your physical system:

```
\system{spring_mass}
\parameter{m}{1.0}{kg}
\parameter{k}{10.0}{N/m}
\lagrangian{0.5*m*\dot{x}^2 - 0.5*k*x^2}
\initial{x: 0.5, x_dot: 0.0}
\target{unity}
```

---

## Step 2: Generate the Component

```bash
pip install mechanicsdsl-core

mechanicsdsl generate spring_mass.msl --target unity \
    --out Assets/MechanicsDSL/Runtime/Components/
```

This produces `SpringMassComponent.cs` with:
- MechanicsDSL-generated EOM: $\ddot{x} = -(k/m)x$
- MechanicsDSL-generated Hamiltonian: $H = p^2/(2m) + kx^2/2$
- RK4 integrator
- Noether energy monitor
- Inspector-exposed parameters
- Scene-view Gizmos

---

## Step 3: Add to Scene

1. Create a GameObject
2. Add Component → **MechanicsDSL → [Your System Name]**
3. Set parameters in Inspector
4. Optionally attach a Transform to visualise the moving part

---

## Step 4: Generate Editor Inspector (optional)

```bash
mechanicsdsl generate spring_mass.msl --target unity_editor \
    --out Assets/MechanicsDSL/Editor/
```

Produces `SpringMassComponentEditor.cs` with live state readout.

---

## Manual Implementation Template

If generating manually, every MechanicsDSL Unity component follows this pattern:

```csharp
// 1. Derive EOM via Euler-Lagrange (include DSL spec as comment)
private float EOM_dAcceleration(float q, float dq) => /* generated */;

// 2. Derive Hamiltonian (Noether conserved quantity)
private float Hamiltonian(float q, float dq) => /* generated */;

// 3. RK4 step (or symplectic for long simulations)
private void RK4Step(float h) { /* standard 4-stage */ }

// 4. FixedUpdate: integrate, monitor drift, drive visualisation
private void FixedUpdate() {
    _accumulator += Time.fixedDeltaTime;
    while (_accumulator >= dt) { RK4Step(dt); _accumulator -= dt; }
    Energy = Hamiltonian(Q, DQ);
    EnergyDrift = Mathf.Abs((Energy - _E0) / _E0);
    if (EnergyDrift > driftTolerance) Debug.LogWarning(...);
}
```
