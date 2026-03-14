#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using MechanicsDSL.Classical;

namespace MechanicsDSL.Classical.Editor
{
    [CustomEditor(typeof(DoublePendulumComponent))]
    public class DoublePendulumComponentEditor : UnityEditor.Editor
    {
        private bool _showState = true;

        public override void OnInspectorGUI()
        {
            var comp = (DoublePendulumComponent)target;
            serializedObject.Update();

            EditorGUILayout.Space(4);
            EditorGUILayout.LabelField("MechanicsDSL — Double Pendulum", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("L = ½ml²(2θ̇₁²+θ̇₂²+2θ̇₁θ̇₂cos Δθ)+mgl(2cosθ₁+cosθ₂)", EditorStyles.miniLabel);
            EditorGUILayout.Space(6);

            DrawPropertiesExcluding(serializedObject, "m_script");

            if (Application.isPlaying)
            {
                EditorGUILayout.Space(8);
                _showState = EditorGUILayout.Foldout(_showState, "Live State", true, EditorStyles.foldoutHeader);
                if (_showState)
                {
                    EditorGUI.indentLevel++;
                    EditorGUILayout.LabelField("θ₁ (rad)", $"{comp.Theta1:F6}");
                    EditorGUILayout.LabelField("θ₂ (rad)", $"{comp.Theta2:F6}");
                    EditorGUILayout.LabelField("ω₁ (rad/s)", $"{comp.Omega1:F6}");
                    EditorGUILayout.LabelField("ω₂ (rad/s)", $"{comp.Omega2:F6}");
                    EditorGUILayout.LabelField("t (s)", $"{comp.SimTime:F3}");
                    EditorGUILayout.LabelField("Energy (J)", $"{comp.Energy:F8}");

                    Color prev = GUI.color;
                    GUI.color = comp.EnergyDrift > comp.driftTolerance
                        ? new Color(1f,0.4f,0.4f) : new Color(0.4f,1f,0.6f);
                    EditorGUILayout.LabelField("|ΔE/E₀|",
                        comp.EnergyDrift < 1e-10f ? "< 1e-10 ✓" : $"{comp.EnergyDrift:E3}");
                    GUI.color = prev;

                    EditorGUI.indentLevel--;
                    EditorGUILayout.Space(4);
                    if (GUILayout.Button("Reset")) comp.Reset();
                }
                Repaint();
            }

            serializedObject.ApplyModifiedProperties();
        }
    }
}
#endif
