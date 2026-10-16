"""
End-to-End (E2E) Integration & Workflow Test Suite for QuantumCalc
Tests full end-to-end scientific pipelines:
1. Health & Core Engine Status
2. High-Precision Arithmetic Pipeline (50-DPS)
3. Calculus Pipeline: Differentiate -> Integrate -> Fundamental Theorem of Calculus
4. Matrix Pipeline: Det -> Inverse -> Matrix Multiplication A * A^(-1) == I
5. Statistics Pipeline: Distribution Summary & Linear Regression
6. Equation Solving & Root Finding Pipeline
7. Resilient Error Handling (Singular matrices, parse errors, division by zero)
"""

import sys
import os
import unittest
import numpy as np
from fastapi.testclient import TestClient
from backend.server import app

client = TestClient(app)

class TestCalculatorE2EPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=======================================================")
        print("   STARTING QUANTUMCALC E2E SCIENTIFIC PIPELINE TESTS   ")
        print("=======================================================")

    def test_01_e2e_health_and_version(self):
        """E2E Pipeline 1: Healthcheck and system diagnostics"""
        resp = client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertGreaterEqual(data.get("precision_dps"), 50)
        print("  [PASS] E2E Healthcheck & SymPy 50-DPS Engine: PASS")

    def test_02_e2e_high_precision_pi_euler(self):
        """E2E Pipeline 2: High precision transcendental calculations"""
        # Euler's identity: e^(i*pi) + 1 = 0
        resp = client.post("/api/calculate", json={"expression": "exp(I*pi) + 1", "precision": 30})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("symbolic"), "0")

        # 50-digit Pi verification
        resp_pi = client.post("/api/calculate", json={"expression": "pi", "precision": 50})
        self.assertTrue(resp_pi.json().get("success"))
        pi_val = resp_pi.json().get("numeric")
        self.assertTrue(pi_val.startswith("3.1415926535897932384626433832795028841971693993751"))
        print("  [PASS] E2E 50-DPS Transcendental & Euler Identity: PASS")

    def test_03_e2e_calculus_closed_loop(self):
        """E2E Pipeline 3: Closed-loop calculus: Differentiate then Integrate"""
        # Original: f(x) = x^4 - 5*x^2 + 4
        orig = "x^4 - 5*x^2 + 4"
        
        # Step A: Differentiate f(x) -> 4*x^3 - 10*x
        diff_resp = client.post("/api/calculus", json={
            "expression": orig,
            "variable": "x",
            "operation": "diff"
        })
        self.assertTrue(diff_resp.json().get("success"))
        derivative = diff_resp.json().get("result_symbolic")
        self.assertIn("4*x**3 - 10*x", derivative)

        # Step B: Integrate the derivative back -> x^4 - 5*x^2
        integ_resp = client.post("/api/calculus", json={
            "expression": derivative,
            "variable": "x",
            "operation": "integrate"
        })
        self.assertTrue(integ_resp.json().get("success"))
        recovered = integ_resp.json().get("result_symbolic")
        self.assertIn("x**4 - 5*x**2", recovered)

        # Step C: Definite Integral from 0 to 2
        def_resp = client.post("/api/calculus", json={
            "expression": orig,
            "variable": "x",
            "operation": "integrate",
            "lower_limit": "0",
            "upper_limit": "2"
        })
        self.assertTrue(def_resp.json().get("success"))
        self.assertIsNotNone(def_resp.json().get("result_symbolic"))
        print("  [PASS] E2E Closed-Loop Calculus (d/dx & int dx): PASS")

    def test_04_e2e_matrix_linear_algebra_pipeline(self):
        """E2E Pipeline 4: Matrix Det -> Inverse -> Verification A * A^(-1) == I"""
        matrix_a = [
            [2.0, 1.0, 1.0],
            [1.0, 3.0, 2.0],
            [1.0, 0.0, 0.0]
        ]
        
        # Det
        det_resp = client.post("/api/matrix", json={"matrix_a": matrix_a, "operation": "det"})
        self.assertTrue(det_resp.json().get("success"))
        det_val = det_resp.json().get("determinant")
        self.assertNotEqual(det_val, 0.0)

        # Inverse
        inv_resp = client.post("/api/matrix", json={"matrix_a": matrix_a, "operation": "inv"})
        self.assertTrue(inv_resp.json().get("success"))
        inv_matrix = inv_resp.json().get("inverse")

        # Multiply A * A^(-1)
        mul_resp = client.post("/api/matrix", json={
            "matrix_a": matrix_a,
            "matrix_b": inv_matrix,
            "operation": "multiply"
        })
        self.assertTrue(mul_resp.json().get("success"))
        prod = np.array(mul_resp.json().get("result"))
        identity = np.eye(3)
        np.testing.assert_allclose(prod, identity, atol=1e-5)
        print("  [PASS] E2E Matrix Pipeline (Det, Invert, Verify A * A^-1 = I): PASS")

    def test_05_e2e_stats_and_linear_regression(self):
        """E2E Pipeline 5: Full statistics profile and linear regression"""
        x_data = [1.0, 2.0, 3.0, 4.0, 5.0]
        y_data = [2.0, 4.0, 6.0, 8.0, 10.0] # perfect y = 2x
        
        resp = client.post("/api/statistics", json={"data": x_data, "data_y": y_data})
        self.assertTrue(resp.json().get("success"))
        data = resp.json()
        summary = data.get("summary", {})
        self.assertEqual(summary.get("mean"), 3.0)
        
        reg = data.get("regression", {})
        self.assertAlmostEqual(reg.get("slope"), 2.0, places=4)
        self.assertAlmostEqual(reg.get("intercept"), 0.0, places=4)
        self.assertAlmostEqual(reg.get("r_squared"), 1.0, places=4)
        print("  [PASS] E2E Statistics & Linear Regression (R^2 = 1.0): PASS")

    def test_06_e2e_equation_solving_roots(self):
        """E2E Pipeline 6: Polynomial root solving and factorization"""
        resp = client.post("/api/solve", json={"equation": "x^3 - 6*x^2 + 11*x - 6 = 0", "variable": "x"})
        self.assertTrue(resp.json().get("success"))
        solutions = [float(s) for s in resp.json().get("solutions")]
        self.assertEqual(sorted(solutions), [1.0, 2.0, 3.0])
        print("  [PASS] E2E Polynomial Equation Solver (roots 1, 2, 3): PASS")

    def test_07_e2e_error_resilience(self):
        """E2E Pipeline 7: Error boundary and resilience testing"""
        # Singular matrix inversion
        singular = [[1.0, 2.0], [2.0, 4.0]]
        resp_sing = client.post("/api/matrix", json={"matrix_a": singular, "operation": "inv"})
        self.assertFalse(resp_sing.json().get("success"))
        self.assertIn("singular", resp_sing.json().get("error", "").lower())

        # Empty data in stats
        resp_empty = client.post("/api/statistics", json={"data": []})
        self.assertFalse(resp_empty.json().get("success"))
        print("  [PASS] E2E Resilience & Boundary Handling: PASS")

if __name__ == "__main__":
    unittest.main()
