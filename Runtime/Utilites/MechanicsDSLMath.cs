using UnityEngine;

namespace MechanicsDSL.Utilities
{
    /// <summary>
    /// Mathematical utilities shared across MechanicsDSL Unity components.
    /// Includes RK4 integrators, symplectic integrators, and numerical helpers.
    /// </summary>
    public static class MechanicsDSLMath
    {
        /// <summary>
        /// Generic Runge-Kutta 4 step for a 2D state [q, p].
        /// Delegate signature: (q, p) -> (dq/dt, dp/dt)
        /// </summary>
        public delegate (float dq, float dp) EOM2D(float q, float p);

        public static (float q, float p) RK4Step2D(float q, float p, float h, EOM2D eom)
        {
            var (k1q, k1p) = eom(q,           p          );
            var (k2q, k2p) = eom(q+0.5f*h*k1q, p+0.5f*h*k1p);
            var (k3q, k3p) = eom(q+0.5f*h*k2q, p+0.5f*h*k2p);
            var (k4q, k4p) = eom(q+h*k3q,      p+h*k3p      );
            return (
                q + (h/6f)*(k1q + 2*k2q + 2*k3q + k4q),
                p + (h/6f)*(k1p + 2*k2p + 2*k3p + k4p)
            );
        }

        /// <summary>
        /// Symplectic Euler (Störmer-Verlet) step — preserves phase space volume.
        /// Preferred over RK4 for long Hamiltonian simulations.
        /// </summary>
        public static (float q, float p) SymplecticEulerStep(
            float q, float p, float h,
            System.Func<float, float> dH_dp,   // = dq/dt
            System.Func<float, float, float> dH_dq) // = -dp/dt
        {
            float p_new = p - h * dH_dq(q, p);
            float q_new = q + h * dH_dp(p_new);
            return (q_new, p_new);
        }

        /// <summary>
        /// Relative energy drift |ΔE/E0|. Returns 0 if E0 is near-zero.
        /// </summary>
        public static float EnergyDrift(float E, float E0)
        {
            if (Mathf.Abs(E0) < 1e-10f) return 0f;
            return Mathf.Abs((E - E0) / E0);
        }

        /// <summary>
        /// Wrap angle to [-π, π].
        /// </summary>
        public static float WrapAngle(float theta)
        {
            while (theta >  Mathf.PI) theta -= 2f * Mathf.PI;
            while (theta < -Mathf.PI) theta += 2f * Mathf.PI;
            return theta;
        }

        /// <summary>
        /// Convert pendulum state (theta, omega) to Cartesian bob position
        /// relative to pivot, given rod length l.
        /// </summary>
        public static Vector2 PendulumBobPosition(float theta, float l)
            => new Vector2(l * Mathf.Sin(theta), -l * Mathf.Cos(theta));
    }
}
