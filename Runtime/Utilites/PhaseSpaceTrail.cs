using System.Collections.Generic;
using UnityEngine;

namespace MechanicsDSL.Utilities
{
    /// <summary>
    /// Renders a phase space trajectory (θ, ω) as a trail in 3D space.
    /// Attach alongside any MechanicsDSL component to visualise
    /// the Hamiltonian level set in the Inspector and Game view.
    ///
    /// The trail maps (θ → X, ω → Y, time → Z) for 3D trajectories,
    /// or (θ → X, ω → Y, 0) for flat 2D phase portraits.
    ///
    /// Author: MechanicsDSL (github.com/MechanicsDSL)
    /// License: MIT
    /// </summary>
    [AddComponentMenu("MechanicsDSL/Utilities/Phase Space Trail")]
    [RequireComponent(typeof(LineRenderer))]
    public class PhaseSpaceTrail : MonoBehaviour
    {
        [Header("Target")]
        [Tooltip("MechanicsDSL component to track (PendulumComponent etc.)")]
        public MonoBehaviour targetComponent;

        [Header("Display")]
        [Tooltip("Coordinate index to use as X axis (θ₁=0, θ₂=1, etc.)")]
        public int coordIndex = 0;
        [Tooltip("Velocity index to use as Y axis")]
        public int velocityIndex = 0;
        [Tooltip("Scale factor for position axis")]
        public float thetaScale = 1.0f;
        [Tooltip("Scale factor for momentum/velocity axis")]
        public float omegaScale = 0.1f;
        [Tooltip("Add time as Z offset to separate trajectory loops")]
        public bool useTimeAsZ = false;
        [Tooltip("Z scale for time axis")]
        public float timeScale = 0.02f;

        [Header("Buffer")]
        [Tooltip("Maximum trail points")]
        [Range(100, 10000)]
        public int maxPoints = 3000;
        [Tooltip("Minimum distance before adding a new point")]
        public float minDistance = 0.002f;

        [Header("Style")]
        public Gradient trailGradient;

        private LineRenderer _line;
        private List<Vector3> _points = new List<Vector3>();
        private System.Reflection.PropertyInfo _thetaProp;
        private System.Reflection.PropertyInfo _omegaProp;
        private System.Reflection.PropertyInfo _timeProp;

        private void Start()
        {
            _line = GetComponent<LineRenderer>();
            _line.useWorldSpace = false;
            _line.colorGradient = trailGradient;
            _line.startWidth = 0.015f;
            _line.endWidth   = 0.005f;

            if (targetComponent == null)
            {
                targetComponent = GetComponent<PendulumComponent>() as MonoBehaviour
                               ?? GetComponent<DoublePendulumComponent>() as MonoBehaviour;
            }

            if (targetComponent != null)
            {
                var t = targetComponent.GetType();
                // Try indexed properties first (DoublePendulum), then scalar (Pendulum)
                _thetaProp = t.GetProperty(coordIndex == 0 ? "Theta" : $"Theta{coordIndex+1}");
                _omegaProp = t.GetProperty(velocityIndex == 0 ? "Omega" : $"Omega{velocityIndex+1}");
                _timeProp  = t.GetProperty("SimTime");
            }
        }

        private void Update()
        {
            if (_thetaProp == null || _omegaProp == null) return;

            float theta = (float)_thetaProp.GetValue(targetComponent);
            float omega = (float)_omegaProp.GetValue(targetComponent);
            float time  = _timeProp != null ? (float)_timeProp.GetValue(targetComponent) : Time.time;

            Vector3 pt = new Vector3(
                theta * thetaScale,
                omega * omegaScale,
                useTimeAsZ ? time * timeScale : 0f
            );

            if (_points.Count == 0 || Vector3.Distance(pt, _points[_points.Count - 1]) >= minDistance)
            {
                _points.Add(pt);
                if (_points.Count > maxPoints)
                    _points.RemoveAt(0);

                _line.positionCount = _points.Count;
                _line.SetPositions(_points.ToArray());
            }
        }

        public void ClearTrail()
        {
            _points.Clear();
            _line.positionCount = 0;
        }
    }
}
