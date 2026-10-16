"""
Automated Test Suite for Scientific Calculator Backend Engine
Tests health, calculation, symbolic calculus, equation solving,
matrix operations, statistics, and graph sampling.
"""

import unittest
from fastapi.testclient import TestClient
from backend.server import app

client = TestClient(app)

class TestCalculatorEngine(unittest.TestCase):
    def test_health_check(self):
        """Test API health endpoint."""
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("precision_dps"), 50)

    def test_basic_calculation(self):
        """Test arithmetic and symbolic evaluation."""
        payload = {"expression": "25 * 4 + 10^2"}
        response = client.post("/api/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(float(data.get("float_value")), 200.0)

    def test_high_precision_pi(self):
        """Test high-precision evaluation of constants."""
        payload = {"expression": "pi", "precision": 30}
        response = client.post("/api/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertTrue(str(data.get("numeric")).startswith("3.141592653589793"))

    def test_calculus_derivative(self):
        """Test symbolic differentiation d/dx(x^3 - 4*x^2 + 6*x)."""
        payload = {
            "expression": "x^3 - 4*x^2 + 6*x",
            "variable": "x",
            "operation": "diff",
            "order": 1
        }
        response = client.post("/api/calculus", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("3*x**2 - 8*x + 6", data.get("result_symbolic"))

    def test_calculus_integral(self):
        """Test indefinite integral of cos(x)."""
        payload = {
            "expression": "cos(x)",
            "variable": "x",
            "operation": "integrate"
        }
        response = client.post("/api/calculus", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("result_symbolic"), "sin(x)")

    def test_equation_solve(self):
        """Test solving quadratic equation x^2 - 9 = 0."""
        payload = {
            "equation": "x^2 - 9",
            "variable": "x"
        }
        response = client.post("/api/solve", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        solutions = [float(s) for s in data.get("solutions", [])]
        self.assertIn(3.0, solutions)
        self.assertIn(-3.0, solutions)

    def test_matrix_determinant(self):
        """Test matrix determinant."""
        payload = {
            "matrix_a": [[1.0, 2.0], [3.0, 4.0]],
            "operation": "det"
        }
        response = client.post("/api/matrix", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertAlmostEqual(float(data.get("determinant")), -2.0)

    def test_descriptive_statistics(self):
        """Test statistics engine."""
        payload = {
            "data": [10.0, 20.0, 30.0, 40.0, 50.0]
        }
        response = client.post("/api/statistics", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("success"))
        summary = data.get("summary", {})
        self.assertEqual(summary.get("mean"), 30.0)
        self.assertEqual(summary.get("median"), 30.0)
        self.assertEqual(summary.get("min"), 10.0)
        self.assertEqual(summary.get("max"), 50.0)

if __name__ == "__main__":
    unittest.main()
