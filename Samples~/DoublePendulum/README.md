# Double Pendulum Sample

Demonstrates `DoublePendulumComponent` with chaotic dynamics, phase-space trajectory rendering, and sensitivity-to-initial-conditions visualization.

## Setup

1. Install the MechanicsDSL package via UPM (see Simple Pendulum sample)
2. Import the **Double Pendulum** sample from Package Manager
3. Open **Assets/Samples/MechanicsDSL/DoublePendulum/DoublePendulumScene.unity**

## Scene Contents

| GameObject | Component | Description |
|------------|-----------|-------------|
| Pivot | `DoublePendulumComponent` | Double pendulum dynamics |
| Bob1, Bob2 | `SphereRenderer` | Upper and lower bobs |
| TrailRenderer | `TrailRenderer` | Phase space trajectory trace |
| Monitor | `ConservationMonitor` | Energy drift HUD |

## Chaos Demonstration

With the default large initial angles ($\theta_1^0 = 0.8$ rad, $\theta_2^0 = 0.4$ rad), the system is in the chaotic regime. The trajectory never repeats and is highly sensitive to initial conditions.

Try adjusting `theta1_0` by $10^{-4}$ rad and observing how quickly the trajectories diverge — the double pendulum's Lyapunov time is approximately 3–5 seconds.

## DSL Specification

```
\system{double_pendulum}
\parameter{m}{1.0}{kg}
\parameter{l}{1.0}{m}
\lagrangian{
    0.5*m*l^2*(2*\dot{theta1}^2 + \dot{theta2}^2
               + 2*\dot{theta1}*\dot{theta2}*cos(theta1-theta2))
    + m*g*l*(2*cos(theta1) + cos(theta2))
}
\target{unity}
```
