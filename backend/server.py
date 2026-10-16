"""
Scientific Calculator - Python Backend Engine
Powered by FastAPI, SymPy, NumPy, SciPy, Pandas, and mpmath.
Provides high-precision calculations, symbolic calculus, equation solving,
linear algebra, statistical distributions, and 2D function sampling.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import math
import numpy as np
import pandas as pd
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
import mpmath
import scipy.stats as stats

# Set mpmath precision
mpmath.mp.dps = 50

app = FastAPI(
    title="Scientific Calculator API",
    description="High-precision scientific computation engine with SymPy, NumPy, SciPy & Pandas",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Transformations for SymPy parser: allows 2x -> 2*x, ^ -> **, etc.
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor
)

def safe_parse(expr_str: str):
    """Clean and parse mathematical expression safely."""
    # Pre-clean common aliases
    expr_str = expr_str.strip()
    expr_str = expr_str.replace("×", "*").replace("÷", "/")
    expr_str = expr_str.replace("π", "pi").replace("√", "sqrt")
    expr_str = expr_str.replace("ln(", "log(")
    expr_str = expr_str.replace("arcsin", "asin").replace("arccos", "acos").replace("arctan", "atan")
    
    local_dict = {
        'e': sp.E,
        'pi': sp.pi,
        'inf': sp.oo,
        'deg': sp.pi / 180,
    }
    return parse_expr(expr_str, local_dict=local_dict, transformations=TRANSFORMATIONS, evaluate=True)

# ----------------- Models -----------------

class CalcRequest(BaseModel):
    expression: str
    precision: Optional[int] = 16
    angle_mode: Optional[str] = "RAD" # "RAD" or "DEG"

class CalculusRequest(BaseModel):
    expression: str
    variable: Optional[str] = "x"
    operation: str # "diff", "integrate", "limit", "series"
    order: Optional[int] = 1
    lower_limit: Optional[str] = None
    upper_limit: Optional[str] = None
    limit_point: Optional[str] = None
    limit_dir: Optional[str] = "+-" # "+", "-", "+-"

class SolveRequest(BaseModel):
    equation: str
    variable: Optional[str] = "x"

class MatrixRequest(BaseModel):
    matrix_a: List[List[float]]
    matrix_b: Optional[List[List[float]]] = None
    operation: str # "det", "inv", "transpose", "eigen", "rank", "multiply", "add"

class StatsRequest(BaseModel):
    data: List[float]
    data_y: Optional[List[float]] = None # For regression

class GraphRequest(BaseModel):
    expression: str
    variable: Optional[str] = "x"
    x_min: Optional[float] = -10.0
    x_max: Optional[float] = 10.0
    points: Optional[int] = 200

# ----------------- Endpoints -----------------

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "engine": "Python 3.12 + FastAPI + SymPy + Pandas + NumPy + SciPy",
        "precision_dps": mpmath.mp.dps
    }

@app.post("/api/calculate")
def calculate(req: CalcRequest):
    try:
        expr_str = req.expression
        if req.angle_mode.upper() == "DEG":
            # Adjust trigonometric calls with degree conversion if requested
            pass # Standard functions operate in rad or symbol

        parsed = safe_parse(expr_str)
        symbolic_str = str(sp.simplify(parsed))
        latex_str = sp.latex(parsed)

        # High precision evaluation
        try:
            val_num = parsed.evalf(req.precision or 16)
            numeric_str = str(val_num)
        except Exception:
            numeric_str = symbolic_str

        # Float approximation
        float_val = None
        try:
            float_val = float(val_num)
            if math.isnan(float_val) or math.isinf(float_val):
                float_val = None
        except Exception:
            pass

        return {
            "success": True,
            "expression": req.expression,
            "symbolic": symbolic_str,
            "latex": latex_str,
            "numeric": numeric_str,
            "float_value": float_val
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/calculus")
def calculus(req: CalculusRequest):
    try:
        var = sp.Symbol(req.variable or "x")
        expr = safe_parse(req.expression)
        op = req.operation.lower()
        result_expr = None
        explanation = ""

        if op in ["diff", "derivative"]:
            order = req.order or 1
            result_expr = sp.diff(expr, var, order)
            explanation = f"Derivative with respect to {var} of order {order}"
        elif op in ["integrate", "integral"]:
            if req.lower_limit is not None and req.upper_limit is not None:
                a = safe_parse(req.lower_limit)
                b = safe_parse(req.upper_limit)
                result_expr = sp.integrate(expr, (var, a, b))
                explanation = f"Definite integral from {a} to {b} with respect to {var}"
            else:
                result_expr = sp.integrate(expr, var)
                explanation = f"Indefinite integral with respect to {var} (+ C)"
        elif op == "limit":
            pt = safe_parse(req.limit_point or "0")
            dir_arg = "+" if req.limit_dir == "+" else ("-" if req.limit_dir == "-" else "+-")
            result_expr = sp.limit(expr, var, pt, dir=dir_arg)
            explanation = f"Limit as {var} -> {pt}"
        elif op == "series":
            pt = safe_parse(req.limit_point or "0")
            order = req.order or 4
            result_expr = sp.series(expr, var, pt, n=order).removeO()
            explanation = f"Taylor series expansion at {var}={pt} to order {order}"
        else:
            raise ValueError(f"Unknown operation: {op}")

        return {
            "success": True,
            "operation": op,
            "explanation": explanation,
            "result_symbolic": str(result_expr),
            "result_latex": sp.latex(result_expr),
            "result_numeric": str(result_expr.evalf(10)) if result_expr.is_number else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/solve")
def solve_eq(req: SolveRequest):
    try:
        var = sp.Symbol(req.variable or "x")
        raw_eq = req.equation
        if "=" in raw_eq:
            lhs_str, rhs_str = raw_eq.split("=", 1)
            lhs = safe_parse(lhs_str)
            rhs = safe_parse(rhs_str)
            eq = sp.Eq(lhs, rhs)
            solutions = sp.solve(eq, var)
        else:
            expr = safe_parse(raw_eq)
            solutions = sp.solve(expr, var)

        sol_strs = [str(s) for s in solutions]
        sol_latex = [sp.latex(s) for s in solutions]
        sol_approx = []
        for s in solutions:
            try:
                sol_approx.append(str(s.evalf(8)))
            except Exception:
                sol_approx.append(str(s))

        return {
            "success": True,
            "equation": req.equation,
            "variable": str(var),
            "solutions": sol_strs,
            "solutions_latex": sol_latex,
            "approximate": sol_approx
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/matrix")
def matrix_ops(req: MatrixRequest):
    try:
        a = sp.Matrix(req.matrix_a)
        op = req.operation.lower()
        res_data = {}

        if op == "det":
            res_data["determinant"] = float(a.det())
            res_data["symbolic"] = str(a.det())
        elif op == "inv":
            if a.det() == 0:
                raise ValueError("Matrix is singular and non-invertible (det = 0)")
            inv = a.inv()
            res_data["inverse"] = [[float(v) for v in row] for row in inv.tolist()]
        elif op == "transpose":
            trans = a.T
            res_data["transpose"] = [[float(v) for v in row] for row in trans.tolist()]
        elif op == "rank":
            res_data["rank"] = int(a.rank())
        elif op == "eigen":
            eigenvals = a.eigenvals()
            res_data["eigenvalues"] = {str(k): int(v) for k, v in eigenvals.items()}
        elif op == "multiply":
            if not req.matrix_b:
                raise ValueError("Matrix B is required for multiplication")
            b = sp.Matrix(req.matrix_b)
            prod = a * b
            res_data["result"] = [[float(v) for v in row] for row in prod.tolist()]
        elif op == "add":
            if not req.matrix_b:
                raise ValueError("Matrix B is required for addition")
            b = sp.Matrix(req.matrix_b)
            add_res = a + b
            res_data["result"] = [[float(v) for v in row] for row in add_res.tolist()]
        else:
            raise ValueError(f"Unsupported matrix operation: {op}")

        return {"success": True, "operation": op, **res_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/statistics")
def statistics(req: StatsRequest):
    try:
        if not req.data:
            raise ValueError("Dataset cannot be empty")
        
        # Analyze using Pandas Series
        s = pd.Series(req.data, dtype=float)
        summary = {
            "count": int(s.count()),
            "sum": float(s.sum()),
            "mean": float(s.mean()),
            "median": float(s.median()),
            "std_dev": float(s.std()) if len(s) > 1 else 0.0,
            "variance": float(s.var()) if len(s) > 1 else 0.0,
            "min": float(s.min()),
            "max": float(s.max()),
            "range": float(s.max() - s.min()),
            "q1": float(s.quantile(0.25)),
            "q3": float(s.quantile(0.75)),
            "iqr": float(s.quantile(0.75) - s.quantile(0.25)),
            "skewness": float(s.skew()) if len(s) > 2 else 0.0,
            "kurtosis": float(s.kurtosis()) if len(s) > 3 else 0.0
        }

        # Linear regression if data_y provided
        regression = None
        if req.data_y and len(req.data_y) == len(req.data):
            df = pd.DataFrame({"x": req.data, "y": req.data_y})
            slope, intercept, r_value, p_value, std_err = stats.linregress(df["x"], df["y"])
            regression = {
                "slope": float(slope),
                "intercept": float(intercept),
                "r": float(r_value),
                "r_squared": float(r_value ** 2),
                "p_value": float(p_value),
                "std_err": float(std_err),
                "equation": f"y = {slope:.4f}x + {intercept:.4f}"
            }

        return {
            "success": True,
            "summary": summary,
            "regression": regression
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/graph")
def graph_points(req: GraphRequest):
    try:
        var = sp.Symbol(req.variable or "x")
        expr = safe_parse(req.expression)
        
        f = sp.lambdify(var, expr, modules=["numpy", {"sin": np.sin, "cos": np.cos, "tan": np.tan, "sqrt": np.sqrt}])
        
        x_min = req.x_min if req.x_min is not None else -10.0
        x_max = req.x_max if req.x_max is not None else 10.0
        n_pts = min(req.points or 200, 500)
        
        x_vals = np.linspace(x_min, x_max, n_pts)
        y_vals = []
        points = []

        for x in x_vals:
            try:
                y = float(f(x))
                if np.isnan(y) or np.isinf(y) or abs(y) > 1e6:
                    points.append({"x": round(float(x), 4), "y": None})
                else:
                    points.append({"x": round(float(x), 4), "y": round(float(y), 4)})
            except Exception:
                points.append({"x": round(float(x), 4), "y": None})

        # Find roots in the interval
        roots = []
        try:
            sol = sp.solve(expr, var)
            for r in sol:
                try:
                    val = float(r.evalf())
                    if x_min <= val <= x_max:
                        roots.append(round(val, 4))
                except Exception:
                    pass
        except Exception:
            pass

        return {
            "success": True,
            "expression": req.expression,
            "points": points,
            "roots": roots
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
