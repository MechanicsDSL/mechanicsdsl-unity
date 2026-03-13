#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

namespace MechanicsDSL.Classical.Editor
{
    /// <summary>
    /// Custom Inspector for PendulumComponent.
    /// Adds a live state readout, reset button, and energy drift gauge
    /// directly in the Inspector during Play Mode.
    /// </summary>
    [CustomEditor(typeof(PendulumComponent))]
    public class PendulumComponentEditor : UnityEditor.Editor
    {
        private bool _showState    = true;
        private bool _showPhysics  = true;
        private bool _showEvents   = false;

        public override void OnInspectorGUI()
        {
            var comp = (PendulumComponent)target;
            serializedObject.Update();

            // ------------------------------------------------------------------
            // Header
            // ------------------------------------------------------------------
            EditorGUILayout.Space(4);
            EditorGUILayout.LabelField("MechanicsDSL — Simple Pendulum",
                EditorStyles.boldLabel);
            EditorGUILayout.LabelField(
                "Lagrangian: L = ½ml²ω² − mgl(1−cosθ)",
                EditorStyles.miniLabel);
            EditorGUILayout.Space(6);

            // ------------------------------------------------------------------
            // Physical parameters
            // ------------------------------------------------------------------
            _showPhysics = EditorGUILayout.Foldout(_showPhysics,
                "Physical Parameters", true, EditorStyles.foldoutHeader);
            if (_showPhysics)
            {
                EditorGUI.indentLevel++;
                EditorGUILayout.PropertyField(serializedObject.FindProperty("mass"));
                EditorGUILayout.PropertyField(serializedObject.FindProperty("length"));
                EditorGUILayout.PropertyField(serializedObject.FindProperty("gravity"));
                EditorGUILayout.Space(4);
                EditorGUILayout.PropertyField(serializedObject.FindProperty("theta0"));
                EditorGUILayout.PropertyField(serializedObject.FindProperty("omega0"));
                EditorGUI.indentLevel--;
            }

            EditorGUILayout.Space(4);
            EditorGUILayout.PropertyField(serializedObject.FindProperty("dt"));
            EditorGUILayout.PropertyField(serializedObject.FindProperty("driftTolerance"));
            EditorGUILayout.PropertyField(serializedObject.FindProperty("bobTransform"));
            EditorGUILayout.PropertyField(serializedObject.FindProperty("drawGizmos"));

            // ------------------------------------------------------------------
            // Live state readout (Play Mode only)
            // ------------------------------------------------------------------
            if (Application.isPlaying)
            {
                EditorGUILayout.Space(8);
                _showState = EditorGUILayout.Foldout(_showState,
                    "Live State", true, EditorStyles.foldoutHeader);

                if (_showState)
                {
                    EditorGUI.indentLevel++;

                    EditorGUILayout.LabelField("θ (rad)",
                        $"{comp.Theta:F6}");
                    EditorGUILayout.LabelField("ω (rad/s)",
                        $"{comp.Omega:F6}");
                    EditorGUILayout.LabelField("t (s)",
                        $"{comp.SimTime:F3}");
                    EditorGUILayout.LabelField("Energy (J)",
                        $"{comp.Energy:F8}");

                    // Energy drift gauge
                    float drift = comp.EnergyDrift;
                    Color prevColor = GUI.color;
                    GUI.color = drift > comp.driftTolerance
                        ? new Color(1f, 0.4f, 0.4f)
                        : new Color(0.4f, 1f, 0.6f);
                    EditorGUILayout.LabelField("|ΔE/E₀|",
                        drift < 1e-10f ? "< 1e-10 ✓" : $"{drift:E3}");
                    GUI.color = prevColor;

                    EditorGUI.indentLevel--;

                    EditorGUILayout.Space(4);
                    if (GUILayout.Button("Reset to Initial Conditions"))
                        comp.ResetToInitialConditions();
                }

                // Repaint every frame during play to keep live readout updated
                Repaint();
            }

            // ------------------------------------------------------------------
            // Events (collapsed by default — keep Inspector clean)
            // ------------------------------------------------------------------
            EditorGUILayout.Space(4);
            _showEvents = EditorGUILayout.Foldout(_showEvents,
                "Events", true, EditorStyles.foldoutHeader);
            if (_showEvents)
            {
                EditorGUI.indentLevel++;
                EditorGUILayout.PropertyField(
                    serializedObject.FindProperty("OnStateUpdate"));
                EditorGUILayout.PropertyField(
                    serializedObject.FindProperty("OnEnergyDrift"));
                EditorGUI.indentLevel--;
            }

            serializedObject.ApplyModifiedProperties();
        }
    }
}
#endif
