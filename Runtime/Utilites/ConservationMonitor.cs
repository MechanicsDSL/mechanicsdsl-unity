using UnityEngine;
using UnityEngine.Events;

namespace MechanicsDSL.Utilities
{
    /// <summary>
    /// Monitors conservation law violations across MechanicsDSL components.
    /// Attach to any GameObject alongside a PendulumComponent or
    /// DoublePendulumComponent. Fires events and displays on-screen HUD
    /// when Noether-conserved quantities drift beyond tolerance.
    ///
    /// Author: MechanicsDSL (github.com/MechanicsDSL)
    /// License: MIT
    /// </summary>
    [AddComponentMenu("MechanicsDSL/Utilities/Conservation Monitor")]
    public class ConservationMonitor : MonoBehaviour
    {
        [Header("Monitored Component")]
        [Tooltip("Drag a PendulumComponent or DoublePendulumComponent here")]
        public MonoBehaviour targetComponent;

        [Header("Thresholds")]
        [Tooltip("Warning threshold |ΔE/E0|")]
        public float warningThreshold  = 1e-4f;
        [Tooltip("Critical threshold |ΔE/E0| — triggers OnCriticalDrift event")]
        public float criticalThreshold = 1e-2f;

        [Header("HUD")]
        public bool showOnScreenHUD = true;
        public Color normalColor   = new Color(0.2f, 1f, 0.4f, 0.85f);
        public Color warningColor  = new Color(1f, 0.9f, 0.1f, 0.85f);
        public Color criticalColor = new Color(1f, 0.2f, 0.2f, 0.85f);

        [Header("Events")]
        public UnityEvent<float> OnWarningDrift;
        public UnityEvent<float> OnCriticalDrift;
        public UnityEvent        OnDriftResolved;

        private float _currentDrift;
        private bool  _warningFired;
        private bool  _criticalFired;
        private GUIStyle _hudStyle;

        private void Start()
        {
            if (targetComponent == null)
            {
                // Auto-detect on same GameObject
                targetComponent = GetComponent<MechanicsDSL.Classical.PendulumComponent>() as MonoBehaviour
                               ?? GetComponent<MechanicsDSL.Classical.DoublePendulumComponent>() as MonoBehaviour;
            }
        }

        private void Update()
        {
            if (targetComponent == null) return;

            // Reflection-based drift read — works with any MechanicsDSL component
            var prop = targetComponent.GetType().GetProperty("EnergyDrift");
            if (prop == null) return;
            _currentDrift = (float)prop.GetValue(targetComponent);

            // Fire events
            if (_currentDrift >= criticalThreshold && !_criticalFired)
            {
                _criticalFired = true;
                OnCriticalDrift?.Invoke(_currentDrift);
            }
            else if (_currentDrift >= warningThreshold && !_warningFired)
            {
                _warningFired = true;
                OnWarningDrift?.Invoke(_currentDrift);
            }
            else if (_currentDrift < warningThreshold * 0.5f)
            {
                if (_warningFired || _criticalFired) OnDriftResolved?.Invoke();
                _warningFired = _criticalFired = false;
            }
        }

        private void OnGUI()
        {
            if (!showOnScreenHUD) return;

            _hudStyle ??= new GUIStyle(GUI.skin.box)
            {
                fontSize  = 14,
                alignment = TextAnchor.MiddleLeft,
                padding   = new RectOffset(8, 8, 4, 4),
            };

            Color col = _currentDrift >= criticalThreshold ? criticalColor
                      : _currentDrift >= warningThreshold  ? warningColor
                                                           : normalColor;
            _hudStyle.normal.textColor = col;

            string label = $"MechanicsDSL — Noether Monitor\n" +
                           $"|ΔE/E₀| = {_currentDrift:E3}\n" +
                           $"Status: {(_currentDrift >= criticalThreshold ? "CRITICAL" : _currentDrift >= warningThreshold ? "WARNING" : "OK")}";

            GUI.backgroundColor = new Color(0, 0, 0, 0.6f);
            GUI.Box(new Rect(10, 10, 280, 64), label, _hudStyle);
        }
    }
}
