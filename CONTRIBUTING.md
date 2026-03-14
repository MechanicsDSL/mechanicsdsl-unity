# Contributing to mechanicsdsl-unity

## Contribution Types

### New Physics Components

Generate a new component from DSL notation:

```bash
mechanicsdsl generate my_system.msl --target unity --out Runtime/Components/
mechanicsdsl generate my_system.msl --target unity_editor --out Editor/
```

Include:
- The originating `.msl` specification as a header comment
- An `AddComponentMenu` attribute for discoverability
- A custom Inspector Editor script with live state readout
- Runtime tests in `Tests/Runtime/`
- Entry in `CHANGELOG.md`

### Sample Scenes

Well-documented sample scenes demonstrating MechanicsDSL components are especially valuable for new users. Add samples to `Samples~/YourSampleName/` and declare them in `package.json`.

### Bug Reports

Include:
- Unity version
- How to reproduce (minimal scene setup)
- Expected vs actual behaviour
- Whether the issue is in the EOM, integrator, or Unity integration layer

## Testing

Run tests via **Window → General → Test Runner → PlayMode → Run All**.

All physics components must have:
- Energy conservation test (5+ seconds simulation)
- Reset/initial-conditions test
- Equilibrium stability test

## Code Style

- Use `[AddComponentMenu("MechanicsDSL/...")]` for all MonoBehaviours
- All MechanicsDSL-generated code must be clearly labelled with the originating DSL spec
- Inspector properties should have `[Tooltip]` attributes
- Use `[Range]` attributes for physical parameters to prevent unphysical values
