using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using MechanicsDSL.Classical;

namespace MechanicsDSL.Tests
{
    /// <summary>
    /// Runtime tests for MechanicsDSL Unity components.
    /// Validates physics correctness of MechanicsDSL-generated equations of motion.
    /// Run via Unity Test Runner: Window > General > Test Runner > PlayMode
    /// </summary>
    public class TestPendulumEOM
    {
        private GameObject _go;
        private PendulumComponent _pendulum;

        [SetUp]
        public void SetUp()
        {
            _go       = new GameObject("TestPendulum");
            _pendulum = _go.AddComponent<PendulumComponent>();
            _pendulum.mass    = 1.0f;
            _pendulum.length  = 0.25f;
            _pendulum.gravity = 9.81f;
            _pendulum.theta0  = 0.3f;
            _pendulum.omega0  = 0.0f;
            _pendulum.dt      = 0.001f;
        }

        [TearDown]
        public void TearDown() => Object.DestroyImmediate(_go);

        [Test]
        public void InitialEnergyIsPositive()
        {
            Assert.Greater(_pendulum.Energy, 0f,
                "Energy should be positive for non-zero initial angle");
        }

        [UnityTest]
        public IEnumerator EnergyConservedOverTenSeconds()
        {
            float E0 = _pendulum.Energy;
            yield return new WaitForSeconds(10f);
            float drift = Mathf.Abs((_pendulum.Energy - E0) / E0);
            Assert.Less(drift, 1e-3f,
                $"Energy drift {drift:E3} exceeded tolerance after 10 s");
        }

        [UnityTest]
        public IEnumerator ResetRestoresInitialConditions()
        {
            yield return new WaitForSeconds(2f);
            _pendulum.ResetToInitialConditions();
            yield return null;
            Assert.AreEqual(_pendulum.theta0, _pendulum.Theta, 1e-6f);
            Assert.AreEqual(0f, _pendulum.Omega, 1e-6f);
            Assert.AreEqual(0f, _pendulum.SimTime, 1e-6f);
        }

        [Test]
        public void EquilibriumRemainStationary()
        {
            _pendulum.theta0 = 0f;
            _pendulum.omega0 = 0f;
            _pendulum.ResetToInitialConditions();
            // After one fixed update the state should not move
            Assert.AreEqual(0f, _pendulum.Theta, 1e-12f);
            Assert.AreEqual(0f, _pendulum.Omega, 1e-12f);
        }

        [Test]
        public void BobTransformUpdated()
        {
            var bob = new GameObject("Bob").transform;
            _pendulum.bobTransform = bob;
            // Simulate one step manually
            _pendulum.theta0 = 0.5f;
            _pendulum.ResetToInitialConditions();
            // Bob should be displaced from pivot
            float expected_x = _pendulum.length * Mathf.Sin(0.5f);
            Assert.AreNotEqual(0f, bob.localPosition.x, 1e-5f);
        }
    }
}
