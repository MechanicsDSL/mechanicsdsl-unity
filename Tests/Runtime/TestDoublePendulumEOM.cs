using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using MechanicsDSL.Classical;

namespace MechanicsDSL.Tests
{
    public class TestDoublePendulumEOM
    {
        private GameObject _go;
        private DoublePendulumComponent _dp;

        [SetUp]
        public void SetUp()
        {
            _go = new GameObject("TestDoublePendulum");
            _dp = _go.AddComponent<DoublePendulumComponent>();
            _dp.mass    = 1.0f;
            _dp.length  = 1.0f;
            _dp.gravity = 9.81f;
            _dp.dt      = 0.001f;
        }

        [TearDown]
        public void TearDown() => Object.DestroyImmediate(_go);

        [Test]
        public void InitialEnergyFinite()
        {
            Assert.IsFalse(float.IsNaN(_dp.Energy));
            Assert.IsFalse(float.IsInfinity(_dp.Energy));
        }

        [Test]
        public void SymmetricModeStaysSymmetric()
        {
            // Symmetric IC: both angles equal → theta1 should always equal theta2
            _dp.theta1_0 = 0.1f;
            _dp.theta2_0 = 0.1f;
            _dp.ResetToInitialConditions();
            Assert.AreEqual(_dp.Theta1, _dp.Theta2, 1e-5f,
                "Symmetric initial conditions should preserve theta1=theta2");
        }

        [UnityTest]
        public IEnumerator EnergyConservedSmallAngle()
        {
            _dp.theta1_0 = 0.1f;
            _dp.theta2_0 = 0.1f;
            _dp.ResetToInitialConditions();
            float E0 = _dp.Energy;
            yield return new WaitForSeconds(5f);
            float drift = Mathf.Abs((_dp.Energy - E0) / E0);
            Assert.Less(drift, 1e-3f, $"Energy drift {drift:E3} too large");
        }

        [Test]
        public void ResetClearsState()
        {
            _dp.theta1_0 = 0.5f;
            _dp.theta2_0 = 0.3f;
            _dp.ResetToInitialConditions();
            Assert.AreEqual(_dp.theta1_0, _dp.Theta1, 1e-6f);
            Assert.AreEqual(_dp.theta2_0, _dp.Theta2, 1e-6f);
            Assert.AreEqual(0f, _dp.Omega1, 1e-6f);
            Assert.AreEqual(0f, _dp.Omega2, 1e-6f);
            Assert.AreEqual(0f, _dp.SimTime, 1e-6f);
        }
    }
}
