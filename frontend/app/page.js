"use client";

import React, { useState, useEffect, useRef } from "react";

// Web Audio Synthesizer for tactile key sounds
class SoundSynthesizer {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx && typeof window !== "undefined") {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume();
    }
  }

  play(type = "num") {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.connect(gain);
      gain.connect(this.ctx.destination);

      const now = this.ctx.currentTime;

      if (type === "num") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(540, now);
        osc.frequency.exponentialRampToValueAtTime(320, now + 0.04);
        gain.gain.setValueAtTime(0.04, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.04);
        osc.start(now);
        osc.stop(now + 0.04);
      } else if (type === "op") {
        osc.type = "triangle";
        osc.frequency.setValueAtTime(750, now);
        osc.frequency.exponentialRampToValueAtTime(400, now + 0.06);
        gain.gain.setValueAtTime(0.06, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.06);
        osc.start(now);
        osc.stop(now + 0.06);
      } else if (type === "sci") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(580, now + 0.08);
        gain.gain.setValueAtTime(0.05, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.08);
        osc.start(now);
        osc.stop(now + 0.08);
      } else if (type === "equal") {
        osc.type = "triangle";
        osc.frequency.setValueAtTime(600, now);
        osc.frequency.exponentialRampToValueAtTime(950, now + 0.12);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.12);
        osc.start(now);
        osc.stop(now + 0.12);
      } else if (type === "clear") {
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(350, now);
        osc.frequency.exponentialRampToValueAtTime(150, now + 0.08);
        gain.gain.setValueAtTime(0.04, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.08);
        osc.start(now);
        osc.stop(now + 0.08);
      }
    } catch (e) {
      // Audio fallback silent
    }
  }
}

const synth = new SoundSynthesizer();

export default function ScientificCalculatorApp() {
  // Theme & Sound
  const [theme, setTheme] = useState("cyber");
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [activeTab, setActiveTab] = useState("calculator"); // 'calculator', 'calculus', 'grapher', 'matrix', 'statistics', 'converter'

  // Calculator Core State
  const [expression, setExpression] = useState("");
  const [displayResult, setDisplayResult] = useState("0");
  const [symbolicResult, setSymbolicResult] = useState("");
  const [history, setHistory] = useState([]);
  const [angleMode, setAngleMode] = useState("RAD"); // 'RAD' or 'DEG'
  const [isSecondMode, setIsSecondMode] = useState(false);
  const [memory, setMemory] = useState(0);
  const [isEvaluating, setIsEvaluating] = useState(false);

  // Backend Status
  const [backendOnline, setBackendOnline] = useState(false);

  // Calculus Studio State
  const [calcExpr, setCalcExpr] = useState("sin(x)*x^2");
  const [calcVar, setCalcVar] = useState("x");
  const [calcOp, setCalcOp] = useState("diff"); // 'diff', 'integrate', 'limit', 'series'
  const [calcOrder, setCalcOrder] = useState(1);
  const [calcLower, setCalcLower] = useState("0");
  const [calcUpper, setCalcUpper] = useState("pi");
  const [calcLimitPt, setCalcLimitPt] = useState("0");
  const [calcResult, setCalcResult] = useState(null);
  const [calcLoading, setCalcLoading] = useState(false);

  // Equation Solver State
  const [solveEq, setSolveEq] = useState("x^2 - 5*x + 6 = 0");
  const [solveResult, setSolveResult] = useState(null);
  const [solveLoading, setSolveLoading] = useState(false);

  // Grapher State
  const [graphFunc, setGraphFunc] = useState("sin(x)");
  const [graphRange, setGraphRange] = useState({ min: -10, max: 10 });
  const [graphRoots, setGraphRoots] = useState([]);
  const canvasRef = useRef(null);

  // Matrix State
  const [matrixSize, setMatrixSize] = useState(3);
  const [matrixA, setMatrixA] = useState([
    [1, 2, 3],
    [0, 1, 4],
    [5, 6, 0]
  ]);
  const [matrixB, setMatrixB] = useState([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
  ]);
  const [matrixOp, setMatrixOp] = useState("det");
  const [matrixResult, setMatrixResult] = useState(null);

  // Statistics State
  const [statInputX, setStatInputX] = useState("12, 19, 23, 29, 34, 45, 52, 58, 63, 71");
  const [statInputY, setStatInputY] = useState("15, 22, 28, 32, 40, 49, 56, 61, 68, 77");
  const [statResult, setStatResult] = useState(null);
  const [statLoading, setStatLoading] = useState(false);

  // Converter State
  const [convCategory, setConvCategory] = useState("length");
  const [convFromVal, setConvFromVal] = useState("1");
  const [convFromUnit, setConvFromUnit] = useState("meter");
  const [convToUnit, setConvToUnit] = useState("foot");
  const [convResult, setConvResult] = useState("3.28084");

  // Sync theme
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // Sync sound
  useEffect(() => {
    synth.enabled = soundEnabled;
  }, [soundEnabled]);

  // Check Backend Health
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/health", { method: "GET" });
        if (res.ok) {
          const data = await res.json();
          setBackendOnline(true);
        } else {
          setBackendOnline(false);
        }
      } catch (err) {
        setBackendOnline(false);
      }
    };
    checkBackend();
    const interval = setInterval(checkBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Don't intercept when user is typing in form inputs
      if (["INPUT", "TEXTAREA"].includes(e.target.tagName)) return;

      const key = e.key;
      if (!isNaN(key)) {
        handleInput(key, "num");
      } else if (["+", "-", "*", "/", "%", "^", "(", ")"].includes(key)) {
        const opMap = { "*": "×", "/": "÷" };
        handleInput(opMap[key] || key, "op");
      } else if (key === "Enter" || key === "=") {
        e.preventDefault();
        evaluateCalculator();
      } else if (key === "Backspace") {
        handleBackspace();
      } else if (key === "Escape") {
        handleClear();
      } else if (key === ".") {
        handleInput(".", "num");
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [expression, angleMode]);

  // Play audio
  const playSfx = (type) => {
    synth.play(type);
  };

  // Calculator Keypad Input
  const handleInput = (val, type = "num") => {
    playSfx(type);
    setExpression((prev) => {
      if (prev === "0" && val !== ".") return val;
      return prev + val;
    });
  };

  const handleClear = () => {
    playSfx("clear");
    setExpression("");
    setDisplayResult("0");
    setSymbolicResult("");
  };

  const handleBackspace = () => {
    playSfx("num");
    setExpression((prev) => (prev.length > 0 ? prev.slice(0, -1) : ""));
  };

  // Memory Handlers
  const handleMemory = (op) => {
    playSfx("sci");
    const currentNum = parseFloat(displayResult) || 0;
    if (op === "MC") setMemory(0);
    else if (op === "MR") {
      setExpression((prev) => prev + memory.toString());
    } else if (op === "M+") setMemory((prev) => prev + currentNum);
    else if (op === "M-") setMemory((prev) => prev - currentNum);
    else if (op === "MS") setMemory(currentNum);
  };

  // Frontend Math Evaluator (with fallback & degree/radian support)
  const evaluateInClient = (exprStr) => {
    try {
      let sanitized = exprStr
        .replace(/×/g, "*")
        .replace(/÷/g, "/")
        .replace(/π/g, "Math.PI")
        .replace(/e/g, "Math.E")
        .replace(/\^/g, "**");

      // Replace functions with Math counterparts
      const isDeg = angleMode === "DEG";
      const toRad = isDeg ? `*(Math.PI/180)` : "";

      // Trigonometry
      sanitized = sanitized.replace(/sin\(([^)]+)\)/g, `Math.sin(($1)${toRad})`);
      sanitized = sanitized.replace(/cos\(([^)]+)\)/g, `Math.cos(($1)${toRad})`);
      sanitized = sanitized.replace(/tan\(([^)]+)\)/g, `Math.tan(($1)${toRad})`);

      sanitized = sanitized.replace(/asin\(([^)]+)\)/g, isDeg ? `(Math.asin($1)*(180/Math.PI))` : `Math.asin($1)`);
      sanitized = sanitized.replace(/acos\(([^)]+)\)/g, isDeg ? `(Math.acos($1)*(180/Math.PI))` : `Math.acos($1)`);
      sanitized = sanitized.replace(/atan\(([^)]+)\)/g, isDeg ? `(Math.atan($1)*(180/Math.PI))` : `Math.atan($1)`);

      sanitized = sanitized.replace(/log\(/g, "Math.log10(");
      sanitized = sanitized.replace(/ln\(/g, "Math.log(");
      sanitized = sanitized.replace(/sqrt\(/g, "Math.sqrt(");
      sanitized = sanitized.replace(/cbrt\(/g, "Math.cbrt(");
      sanitized = sanitized.replace(/abs\(/g, "Math.abs(");

      // Factorial parsing: e.g. 5!
      sanitized = sanitized.replace(/(\d+)!/g, (match, n) => {
        let num = parseInt(n, 10);
        let r = 1;
        for (let i = 2; i <= num; i++) r *= i;
        return r;
      });

      // Safely evaluate
      const fn = new Function(`"use strict"; return (${sanitized});`);
      const val = fn();
      if (typeof val === "number" && !isNaN(val)) {
        return Number.isInteger(val) ? val.toString() : parseFloat(val.toFixed(10)).toString();
      }
      return val?.toString() || "Error";
    } catch (err) {
      return "Error";
    }
  };

  // Evaluate Calculator (Calls Python Backend for SymPy High Precision, falls back to Client JS)
  const evaluateCalculator = async () => {
    if (!expression.trim()) return;
    playSfx("equal");
    setIsEvaluating(true);

    const clientRes = evaluateInClient(expression);
    setDisplayResult(clientRes);

    if (backendOnline) {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/calculate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            expression: expression,
            angle_mode: angleMode,
            precision: 20
          })
        });
        const data = await res.json();
        if (data.success) {
          setDisplayResult(data.numeric);
          setSymbolicResult(data.symbolic !== data.numeric ? data.symbolic : "");
          addHistory(expression, data.numeric, data.symbolic);
        } else {
          addHistory(expression, clientRes, "");
        }
      } catch (e) {
        addHistory(expression, clientRes, "");
      }
    } else {
      addHistory(expression, clientRes, "");
    }

    setIsEvaluating(false);
  };

  const addHistory = (expr, res, sym) => {
    const item = {
      id: Date.now(),
      expr,
      result: res,
      symbolic: sym,
      timestamp: new Date().toLocaleTimeString()
    };
    setHistory((prev) => [item, ...prev.slice(0, 49)]);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const exportHistoryCSV = () => {
    const csvContent = "data:text/csv;charset=utf-8,"
      + "Timestamp,Expression,Numeric Result,Symbolic Result\n"
      + history.map(h => `"${h.timestamp}","${h.expr}","${h.result}","${h.symbolic || ''}"`).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `quantumcalc_history_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Calculus Studio Solver
  const handleCalculusSubmit = async () => {
    if (!calcExpr.trim()) return;
    setCalcLoading(true);
    setCalcResult(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/calculus", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          expression: calcExpr,
          variable: calcVar,
          operation: calcOp,
          order: parseInt(calcOrder) || 1,
          lower_limit: calcLower || null,
          upper_limit: calcUpper || null,
          limit_point: calcLimitPt || null
        })
      });
      const data = await res.json();
      setCalcResult(data);
    } catch (e) {
      setCalcResult({ success: false, error: "Backend server offline or request failed." });
    }
    setCalcLoading(false);
  };

  // Equation Solver
  const handleSolveSubmit = async () => {
    if (!solveEq.trim()) return;
    setSolveLoading(true);
    setSolveResult(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          equation: solveEq,
          variable: "x"
        })
      });
      const data = await res.json();
      setSolveResult(data);
    } catch (e) {
      setSolveResult({ success: false, error: "Backend server offline or request failed." });
    }
    setSolveLoading(false);
  };

  // Statistics Lab
  const handleStatsSubmit = async () => {
    const rawX = statInputX.split(/[\s,]+/).filter(Boolean).map(Number);
    const rawY = statInputY.split(/[\s,]+/).filter(Boolean).map(Number);

    if (rawX.some(isNaN)) {
      alert("Please ensure all X inputs are valid numbers.");
      return;
    }

    setStatLoading(true);
    setStatResult(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/statistics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: rawX,
          data_y: rawY.length === rawX.length ? rawY : null
        })
      });
      const data = await res.json();
      setStatResult(data);
    } catch (e) {
      setStatResult({ success: false, error: "Backend server offline or request failed." });
    }
    setStatLoading(false);
  };

  // Canvas Function Grapher
  const drawGraph = (points = [], roots = []) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = (canvas.width = canvas.offsetWidth * window.devicePixelRatio);
    const height = (canvas.height = canvas.offsetHeight * window.devicePixelRatio);

    ctx.clearRect(0, 0, width, height);

    const xMin = graphRange.min;
    const xMax = graphRange.max;
    let yMin = -10;
    let yMax = 10;

    // Filter valid Ys to set scale
    const validYs = points.filter(p => p.y !== null).map(p => p.y);
    if (validYs.length > 0) {
      const curYMin = Math.min(...validYs);
      const curYMax = Math.max(...validYs);
      if (curYMax - curYMin > 0.1 && Math.abs(curYMax) < 500) {
        yMin = Math.max(curYMin - 1, -50);
        yMax = Math.min(curYMax + 1, 50);
      }
    }

    const mapX = (x) => ((x - xMin) / (xMax - xMin)) * width;
    const mapY = (y) => height - ((y - yMin) / (yMax - yMin)) * height;

    // Grid lines
    ctx.strokeStyle = "rgba(148, 163, 184, 0.1)";
    ctx.lineWidth = 1 * window.devicePixelRatio;

    for (let x = Math.ceil(xMin); x <= Math.floor(xMax); x += 2) {
      const cx = mapX(x);
      ctx.beginPath();
      ctx.moveTo(cx, 0);
      ctx.lineTo(cx, height);
      ctx.stroke();
    }

    for (let y = Math.ceil(yMin); y <= Math.floor(yMax); y += 2) {
      const cy = mapY(y);
      ctx.beginPath();
      ctx.moveTo(0, cy);
      ctx.lineTo(width, cy);
      ctx.stroke();
    }

    // Axes
    ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
    ctx.lineWidth = 1.5 * window.devicePixelRatio;

    // X Axis
    if (yMin <= 0 && yMax >= 0) {
      const yZero = mapY(0);
      ctx.beginPath();
      ctx.moveTo(0, yZero);
      ctx.lineTo(width, yZero);
      ctx.stroke();
    }

    // Y Axis
    if (xMin <= 0 && xMax >= 0) {
      const xZero = mapX(0);
      ctx.beginPath();
      ctx.moveTo(xZero, 0);
      ctx.lineTo(xZero, height);
      ctx.stroke();
    }

    // Plot curve
    if (points.length > 1) {
      ctx.strokeStyle = "#06b6d4";
      ctx.shadowColor = "rgba(6, 182, 212, 0.8)";
      ctx.shadowBlur = 12 * window.devicePixelRatio;
      ctx.lineWidth = 2.5 * window.devicePixelRatio;

      ctx.beginPath();
      let isDrawing = false;

      for (let i = 0; i < points.length; i++) {
        const pt = points[i];
        if (pt.y === null || isNaN(pt.y)) {
          isDrawing = false;
          continue;
        }
        const px = mapX(pt.x);
        const py = mapY(pt.y);

        if (!isDrawing) {
          ctx.moveTo(px, py);
          isDrawing = true;
        } else {
          ctx.lineTo(px, py);
        }
      }
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    // Mark Roots
    roots.forEach((r) => {
      if (r >= xMin && r <= xMax) {
        const rx = mapX(r);
        const ry = mapY(0);
        ctx.fillStyle = "#f43f5e";
        ctx.beginPath();
        ctx.arc(rx, ry, 5 * window.devicePixelRatio, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#fff";
        ctx.font = `${10 * window.devicePixelRatio}px JetBrains Mono`;
        ctx.fillText(`(${r}, 0)`, rx + 8, ry - 8);
      }
    });
  };

  const handleGraphSubmit = async () => {
    if (!graphFunc.trim()) return;

    if (backendOnline) {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/graph", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            expression: graphFunc,
            variable: "x",
            x_min: graphRange.min,
            x_max: graphRange.max,
            points: 250
          })
        });
        const data = await res.json();
        if (data.success) {
          setGraphRoots(data.roots || []);
          drawGraph(data.points, data.roots || []);
          return;
        }
      } catch (e) {
        // Fallback to client graphing
      }
    }

    // Client fallback graphing
    const clientPoints = [];
    const step = (graphRange.max - graphRange.min) / 200;
    for (let x = graphRange.min; x <= graphRange.max; x += step) {
      try {
        let fnStr = graphFunc
          .replace(/sin/g, "Math.sin")
          .replace(/cos/g, "Math.cos")
          .replace(/tan/g, "Math.tan")
          .replace(/sqrt/g, "Math.sqrt")
          .replace(/log/g, "Math.log10")
          .replace(/ln/g, "Math.log")
          .replace(/\^/g, "**")
          .replace(/pi/g, "Math.PI")
          .replace(/e/g, "Math.E");
        
        // replace variable x
        const evalFn = new Function("x", `"use strict"; return (${fnStr});`);
        const y = evalFn(x);
        if (typeof y === "number" && !isNaN(y) && isFinite(y)) {
          clientPoints.push({ x, y });
        } else {
          clientPoints.push({ x, y: null });
        }
      } catch (err) {
        clientPoints.push({ x, y: null });
      }
    }
    drawGraph(clientPoints, []);
  };

  useEffect(() => {
    if (activeTab === "grapher") {
      handleGraphSubmit();
    }
  }, [activeTab, graphRange]);

  // Matrix Operations
  const handleMatrixSubmit = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/matrix", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          matrix_a: matrixA,
          matrix_b: ["multiply", "add"].includes(matrixOp) ? matrixB : null,
          operation: matrixOp
        })
      });
      const data = await res.json();
      setMatrixResult(data);
    } catch (e) {
      setMatrixResult({ success: false, error: "Matrix computation failed or backend offline." });
    }
  };

  // Unit Converter
  const convertUnits = () => {
    const val = parseFloat(convFromVal);
    if (isNaN(val)) return;

    const conversions = {
      length: {
        meter: 1,
        kilometer: 1000,
        centimeter: 0.01,
        millimeter: 0.001,
        mile: 1609.344,
        yard: 0.9144,
        foot: 0.3048,
        inch: 0.0254
      },
      mass: {
        kilogram: 1,
        gram: 0.001,
        milligram: 0.000001,
        pound: 0.453592,
        ounce: 0.0283495
      },
      speed: {
        "meter/sec": 1,
        "km/h": 0.277778,
        "mph": 0.44704,
        "knot": 0.514444
      },
      energy: {
        joule: 1,
        kilojoule: 1000,
        calorie: 4.184,
        kilocalorie: 4184,
        watthour: 3600,
        electronvolt: 1.602176634e-19
      }
    };

    if (convCategory === "temperature") {
      let c = val;
      if (convFromUnit === "fahrenheit") c = (val - 32) * (5 / 9);
      if (convFromUnit === "kelvin") c = val - 273.15;

      let out = c;
      if (convToUnit === "fahrenheit") out = c * (9 / 5) + 32;
      if (convToUnit === "kelvin") out = c + 273.15;
      setConvResult(out.toFixed(6));
      return;
    }

    const cat = conversions[convCategory];
    if (cat && cat[convFromUnit] && cat[convToUnit]) {
      const base = val * cat[convFromUnit];
      const out = base / cat[convToUnit];
      setConvResult(out.toFixed(6));
    }
  };

  useEffect(() => {
    convertUnits();
  }, [convCategory, convFromVal, convFromUnit, convToUnit]);

  return (
    <>
      {/* Top Application Bar */}
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon">∑</div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span className="brand-title">QUANTUMCALC</span>
              <span className="brand-badge">PRO SCIENTIFIC</span>
            </div>
          </div>
        </div>

        <div className="header-controls">
          {/* API Backend indicator */}
          <div className="api-status-badge">
            <span
              className="status-dot"
              style={{
                background: backendOnline ? "#10b981" : "#f43f5e",
                boxShadow: backendOnline ? "0 0 8px #10b981" : "0 0 8px #f43f5e"
              }}
            />
            <span>{backendOnline ? "Python Core Online" : "Client JS Mode"}</span>
          </div>

          {/* Sound Toggle */}
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className={`sound-toggle-btn ${soundEnabled ? "active" : ""}`}
            title="Toggle Sound Effects"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              {soundEnabled ? (
                <>
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
                </>
              ) : (
                <>
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                  <line x1="23" y1="9" x2="17" y2="15" />
                  <line x1="17" y1="9" x2="23" y2="15" />
                </>
              )}
            </svg>
            <span>{soundEnabled ? "SFX On" : "Muted"}</span>
          </button>

          {/* Theme Selector */}
          <div className="theme-pill-group" title="Select Theme">
            <div
              className={`theme-dot ${theme === "cyber" ? "active" : ""}`}
              style={{ background: "#06b6d4" }}
              onClick={() => setTheme("cyber")}
              title="Cyber Neon"
            />
            <div
              className={`theme-dot ${theme === "emerald" ? "active" : ""}`}
              style={{ background: "#10b981" }}
              onClick={() => setTheme("emerald")}
              title="Emerald Matrix"
            />
            <div
              className={`theme-dot ${theme === "sunset" ? "active" : ""}`}
              style={{ background: "#f43f5e" }}
              onClick={() => setTheme("sunset")}
              title="Sunset Horizon"
            />
            <div
              className={`theme-dot ${theme === "obsidian" ? "active" : ""}`}
              style={{ background: "#6366f1" }}
              onClick={() => setTheme("obsidian")}
              title="Obsidian Space"
            />
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="calculator-app-container">
        {/* Navigation Tabs */}
        <nav className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === "calculator" ? "active" : ""}`}
            onClick={() => setActiveTab("calculator")}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="4" y="2" width="16" height="20" rx="2" />
              <line x1="8" y1="6" x2="16" y2="6" />
              <line x1="16" y1="14" x2="16" y2="18" />
              <path d="M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M8 18h.01M12 18h.01" />
            </svg>
            Scientific Pad
          </button>

          <button
            className={`nav-tab-btn ${activeTab === "calculus" ? "active" : ""}`}
            onClick={() => setActiveTab("calculus")}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z" />
              <path d="M6 6h10M6 10h10M6 14h6" />
            </svg>
            Calculus & Solver
          </button>

          <button
            className={`nav-tab-btn ${activeTab === "grapher" ? "active" : ""}`}
            onClick={() => setActiveTab("grapher")}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
            2D Grapher
          </button>

          <button
            className={`nav-tab-btn ${activeTab === "matrix" ? "active" : ""}`}
            onClick={() => setActiveTab("matrix")}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <line x1="9" y1="3" x2="9" y2="21" />
              <line x1="15" y1="3" x2="15" y2="21" />
            </svg>
            Matrix Studio
          </button>

          <button
            className={`nav-tab-btn ${activeTab === "statistics" ? "active" : ""}`}
            onClick={() => setActiveTab("statistics")}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 3v18h18" />
              <path d="m19 9-5 5-4-4-3 3" />
            </svg>
            Pandas Stats Lab
          </button>

          <button
            className={`nav-tab-btn ${activeTab === "converter" ? "active" : ""}`}
            onClick={() => setActiveTab("converter")}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="17 1 21 5 17 9" />
              <path d="M3 11V9a4 4 0 0 1 4-4h14" />
              <polyline points="7 23 3 19 7 15" />
              <path d="M21 13v2a4 4 0 0 1-4 4H3" />
            </svg>
            Unit Converter & Constants
          </button>
        </nav>

        {/* TAB 1: SCIENTIFIC PAD */}
        {activeTab === "calculator" && (
          <div className="app-grid">
            {/* Calculator Chassis */}
            <div className="calc-chassis">
              {/* Display Screen */}
              <div className="calc-screen">
                <div className="screen-top-bar">
                  <div className="mode-pills">
                    <button
                      className={`mode-badge ${angleMode === "RAD" ? "active" : ""}`}
                      onClick={() => setAngleMode("RAD")}
                    >
                      RAD
                    </button>
                    <button
                      className={`mode-badge ${angleMode === "DEG" ? "active" : ""}`}
                      onClick={() => setAngleMode("DEG")}
                    >
                      DEG
                    </button>
                    {isSecondMode && <span className="mode-badge active">2nd</span>}
                    {memory !== 0 && <span className="mode-badge active">M</span>}
                  </div>
                  <div className="screen-indicators">
                    {backendOnline && <span className="active-ind">SymPy 50-DPS</span>}
                  </div>
                </div>

                {/* History Expression Tape */}
                <div className="screen-history-preview">
                  {expression || "0"}
                </div>

                {/* Primary Result Display */}
                <div className="screen-main-input">
                  <span>{displayResult}</span>
                  <span className="cursor-blink" />
                </div>

                {/* Symbolic Display */}
                {symbolicResult && (
                  <div className="screen-secondary-symbolic">
                    Exact: {symbolicResult}
                  </div>
                )}
              </div>

              {/* Memory Row */}
              <div className="calc-quick-row">
                <button className="quick-btn" onClick={() => handleMemory("MC")}>MC</button>
                <button className={`quick-btn ${memory !== 0 ? "active" : ""}`} onClick={() => handleMemory("MR")}>MR</button>
                <button className="quick-btn" onClick={() => handleMemory("M+")}>M+</button>
                <button className="quick-btn" onClick={() => handleMemory("M-")}>M-</button>
                <button className="quick-btn" onClick={() => handleMemory("MS")}>MS</button>
                <button
                  className={`quick-btn ${isSecondMode ? "active" : ""}`}
                  onClick={() => setIsSecondMode(!isSecondMode)}
                >
                  2nd
                </button>
              </div>

              {/* Scientific Keypad Grid */}
              <div className="calc-keypad">
                {/* Row 1 */}
                <button
                  className="key-btn key-sci"
                  onClick={() => handleInput(isSecondMode ? "asin(" : "sin(", "sci")}
                >
                  {isSecondMode ? "sin⁻¹" : "sin"}
                </button>
                <button
                  className="key-btn key-sci"
                  onClick={() => handleInput(isSecondMode ? "acos(" : "cos(", "sci")}
                >
                  {isSecondMode ? "cos⁻¹" : "cos"}
                </button>
                <button
                  className="key-btn key-sci"
                  onClick={() => handleInput(isSecondMode ? "atan(" : "tan(", "sci")}
                >
                  {isSecondMode ? "tan⁻¹" : "tan"}
                </button>
                <button
                  className="key-btn key-sci"
                  onClick={() => handleInput(isSecondMode ? "e^(" : "ln(", "sci")}
                >
                  {isSecondMode ? "eˣ" : "ln"}
                </button>
                <button
                  className="key-btn key-sci"
                  onClick={() => handleInput(isSecondMode ? "10^(" : "log(", "sci")}
                >
                  {isSecondMode ? "10ˣ" : "log"}
                </button>
                <button className="key-btn key-danger" onClick={handleClear}>AC</button>

                {/* Row 2 */}
                <button
                  className="key-btn key-sci"
                  onClick={() => handleInput(isSecondMode ? "^(1/2)" : "^2", "sci")}
                >
                  {isSecondMode ? "√x" : "x²"}
                </button>
                <button
                  className="key-btn key-sci"
                  onClick={() => handleInput(isSecondMode ? "^(1/3)" : "^3", "sci")}
                >
                  {isSecondMode ? "∛x" : "x³"}
                </button>
                <button className="key-btn key-sci" onClick={() => handleInput("^", "sci")}>xʸ</button>
                <button className="key-btn key-sci" onClick={() => handleInput("pi", "sci")}>π</button>
                <button className="key-btn key-sci" onClick={() => handleInput("e", "sci")}>e</button>
                <button className="key-btn key-danger" onClick={handleBackspace}>⌫</button>

                {/* Row 3 */}
                <button className="key-btn key-sci" onClick={() => handleInput("!", "sci")}>n!</button>
                <button className="key-btn key-sci" onClick={() => handleInput("(", "sci")}>(</button>
                <button className="key-btn key-sci" onClick={() => handleInput(")", "sci")}>)</button>
                <button className="key-btn key-sci" onClick={() => handleInput("%", "sci")}>%</button>
                <button className="key-btn key-sci" onClick={() => handleInput("1/(", "sci")}>1/x</button>
                <button className="key-btn key-op" onClick={() => handleInput("÷", "op")}>÷</button>

                {/* Row 4 */}
                <button className="key-btn key-sci" onClick={() => handleInput("abs(", "sci")}>|x|</button>
                <button className="key-btn key-num" onClick={() => handleInput("7", "num")}>7</button>
                <button className="key-btn key-num" onClick={() => handleInput("8", "num")}>8</button>
                <button className="key-btn key-num" onClick={() => handleInput("9", "num")}>9</button>
                <button className="key-btn key-sci" onClick={() => handleInput("sqrt(", "sci")}>√</button>
                <button className="key-btn key-op" onClick={() => handleInput("×", "op")}>×</button>

                {/* Row 5 */}
                <button
                  className="key-btn key-sci"
                  onClick={() => {
                    setCalcExpr(expression);
                    setActiveTab("calculus");
                  }}
                  title="Send to Calculus Studio"
                >
                  ∫ dx
                </button>
                <button className="key-btn key-num" onClick={() => handleInput("4", "num")}>4</button>
                <button className="key-btn key-num" onClick={() => handleInput("5", "num")}>5</button>
                <button className="key-btn key-num" onClick={() => handleInput("6", "num")}>6</button>
                <button className="key-btn key-sci" onClick={() => handleInput("*(10^", "sci")}>EXP</button>
                <button className="key-btn key-op" onClick={() => handleInput("-", "op")}>−</button>

                {/* Row 6 */}
                <button
                  className="key-btn key-sci"
                  onClick={() => {
                    setGraphFunc(expression || "sin(x)");
                    setActiveTab("grapher");
                  }}
                  title="Send to 2D Grapher"
                >
                  Plot
                </button>
                <button className="key-btn key-num" onClick={() => handleInput("1", "num")}>1</button>
                <button className="key-btn key-num" onClick={() => handleInput("2", "num")}>2</button>
                <button className="key-btn key-num" onClick={() => handleInput("3", "num")}>3</button>
                <button className="key-btn key-num" onClick={() => handleInput(".", "num")}>.</button>
                <button className="key-btn key-op" onClick={() => handleInput("+", "op")}>+</button>

                {/* Row 7 */}
                <button className="key-btn key-sci" onClick={() => handleInput("deg", "sci")}>deg</button>
                <button className="key-btn key-num" onClick={() => handleInput("0", "num")}>0</button>
                <button className="key-btn key-num" onClick={() => handleInput("00", "num")}>00</button>
                <button className="key-btn key-num" onClick={() => handleInput("(-", "num")}>±</button>
                <button className="key-btn key-equal" onClick={evaluateCalculator}>
                  {isEvaluating ? "..." : "="}
                </button>
              </div>
            </div>

            {/* Side Card: History & Tape */}
            <div className="side-panel">
              <div className="card-box">
                <div className="card-title-bar">
                  <div className="card-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" />
                      <polyline points="12 6 12 12 16 14" />
                    </svg>
                    Calculation Tape
                  </div>
                  <div style={{ display: "flex", gap: "0.4rem" }}>
                    {history.length > 0 && (
                      <>
                        <button className="card-action-btn" onClick={exportHistoryCSV} title="Export CSV">
                          CSV
                        </button>
                        <button className="card-action-btn" onClick={() => setHistory([])} title="Clear Tape">
                          Clear
                        </button>
                      </>
                    )}
                  </div>
                </div>

                <div className="history-list">
                  {history.length === 0 ? (
                    <div className="history-empty">
                      No calculations recorded yet. Use the keypad or keyboard to calculate!
                    </div>
                  ) : (
                    history.map((h) => (
                      <div
                        key={h.id}
                        className="history-item"
                        onClick={() => {
                          setExpression(h.result);
                          setDisplayResult(h.result);
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--text-dim)" }}>
                          <span>{h.timestamp}</span>
                          <span
                            onClick={(e) => {
                              e.stopPropagation();
                              copyToClipboard(h.result);
                            }}
                            style={{ cursor: "pointer", color: "var(--accent-cyan)" }}
                          >
                            Copy
                          </span>
                        </div>
                        <div className="hist-expr">{h.expr}</div>
                        <div className="hist-res">{h.result}</div>
                        {h.symbolic && (
                          <div style={{ fontSize: "0.75rem", color: "var(--accent-violet)", textAlign: "right" }}>
                            Exact: {h.symbolic}
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Quick Science Snippets Card */}
              <div className="card-box">
                <div className="card-title-bar">
                  <div className="card-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                    </svg>
                    Quick Formula Presets
                  </div>
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                  {[
                    { label: "Euler's Identity", expr: "e^(pi * 0) + 1" },
                    { label: "Gaussian", expr: "1/sqrt(2*pi)*e^(-0.5)" },
                    { label: "Golden Ratio φ", expr: "(1+sqrt(5))/2" },
                    { label: "Hypotenuse (3,4)", expr: "sqrt(3^2 + 4^2)" },
                    { label: "Permutation P(10,3)", expr: "10!/(10-3)!" },
                  ].map((preset, idx) => (
                    <button
                      key={idx}
                      className="quick-btn"
                      style={{ fontSize: "0.75rem", padding: "0.4rem 0.6rem" }}
                      onClick={() => {
                        setExpression(preset.expr);
                        playSfx("sci");
                      }}
                    >
                      {preset.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: CALCULUS & EQUATION SOLVER */}
        {activeTab === "calculus" && (
          <div className="studio-container">
            <h2 style={{ fontSize: "1.4rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ color: "var(--accent-cyan)" }}>∫ dx</span>
              Symbolic Calculus Studio & Equation Solver (SymPy)
            </h2>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
              {/* Calculus Panel */}
              <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--accent-violet)" }}>
                  Calculus Operations
                </h3>

                <div className="form-group">
                  <label className="form-label">Mathematical Expression f(x):</label>
                  <input
                    type="text"
                    className="text-input"
                    value={calcExpr}
                    onChange={(e) => setCalcExpr(e.target.value)}
                    placeholder="e.g. sin(x)*x^2, exp(-x^2), x/(x+1)"
                  />
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                  <div className="form-group">
                    <label className="form-label">Variable:</label>
                    <input
                      type="text"
                      className="text-input"
                      value={calcVar}
                      onChange={(e) => setCalcVar(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Operation:</label>
                    <select
                      className="text-input"
                      value={calcOp}
                      onChange={(e) => setCalcOp(e.target.value)}
                      style={{ cursor: "pointer" }}
                    >
                      <option value="diff">Derivative (d/dx)</option>
                      <option value="integrate">Integral (Indefinite/Definite)</option>
                      <option value="limit">Limit (x → a)</option>
                      <option value="series">Taylor Series Expansion</option>
                    </select>
                  </div>
                </div>

                {calcOp === "diff" && (
                  <div className="form-group">
                    <label className="form-label">Derivative Order:</label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      className="text-input"
                      value={calcOrder}
                      onChange={(e) => setCalcOrder(e.target.value)}
                    />
                  </div>
                )}

                {calcOp === "integrate" && (
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                    <div className="form-group">
                      <label className="form-label">Lower Limit (Optional):</label>
                      <input
                        type="text"
                        className="text-input"
                        value={calcLower}
                        onChange={(e) => setCalcLower(e.target.value)}
                        placeholder="e.g. 0"
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label">Upper Limit (Optional):</label>
                      <input
                        type="text"
                        className="text-input"
                        value={calcUpper}
                        onChange={(e) => setCalcUpper(e.target.value)}
                        placeholder="e.g. pi"
                      />
                    </div>
                  </div>
                )}

                {calcOp === "limit" && (
                  <div className="form-group">
                    <label className="form-label">Limit Point (x → a):</label>
                    <input
                      type="text"
                      className="text-input"
                      value={calcLimitPt}
                      onChange={(e) => setCalcLimitPt(e.target.value)}
                    />
                  </div>
                )}

                <button
                  className="action-btn-primary"
                  onClick={handleCalculusSubmit}
                  disabled={calcLoading}
                >
                  {calcLoading ? "Computing with SymPy..." : "Compute Calculus"}
                </button>

                {calcResult && (
                  <div className="result-card">
                    <div className="result-header">
                      {calcResult.success ? calcResult.explanation : "Error"}
                    </div>
                    {calcResult.success ? (
                      <>
                        <div className="result-body">{calcResult.result_symbolic}</div>
                        {calcResult.result_numeric && (
                          <div style={{ fontSize: "0.95rem", color: "var(--accent-cyan)" }}>
                            Approximate: {calcResult.result_numeric}
                          </div>
                        )}
                        <div style={{ fontSize: "0.8rem", color: "var(--text-dim)" }}>
                          LaTeX: {calcResult.result_latex}
                        </div>
                      </>
                    ) : (
                      <div style={{ color: "var(--accent-rose)" }}>{calcResult.error}</div>
                    )}
                  </div>
                )}
              </div>

              {/* Equation Solver Panel */}
              <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--accent-cyan)" }}>
                  Algebraic Equation Solver
                </h3>

                <div className="form-group">
                  <label className="form-label">Equation (in terms of x):</label>
                  <input
                    type="text"
                    className="text-input"
                    value={solveEq}
                    onChange={(e) => setSolveEq(e.target.value)}
                    placeholder="e.g. x^2 - 5*x + 6 = 0, exp(x) = 10, sin(x) = 0.5"
                  />
                </div>

                <div style={{ display: "flex", gap: "0.5rem" }}>
                  {[
                    "x^2 - 4 = 0",
                    "3*x + 7 = 22",
                    "2*x^2 - 8*x + 6 = 0",
                    "x^3 - 3*x + 1 = 0"
                  ].map((eqSample, i) => (
                    <button
                      key={i}
                      className="quick-btn"
                      onClick={() => setSolveEq(eqSample)}
                    >
                      {eqSample}
                    </button>
                  ))}
                </div>

                <button
                  className="action-btn-primary"
                  onClick={handleSolveSubmit}
                  disabled={solveLoading}
                >
                  {solveLoading ? "Solving Equation..." : "Solve Equation for x"}
                </button>

                {solveResult && (
                  <div className="result-card">
                    <div className="result-header">Solutions for {solveResult.variable}</div>
                    {solveResult.success ? (
                      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                        {solveResult.solutions.length === 0 ? (
                          <div style={{ color: "var(--text-muted)" }}>No solutions found in domain.</div>
                        ) : (
                          solveResult.solutions.map((sol, index) => (
                            <div
                              key={index}
                              style={{
                                background: "rgba(0,0,0,0.3)",
                                padding: "0.6rem 1rem",
                                borderRadius: "8px",
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center"
                              }}
                            >
                              <span style={{ color: "var(--accent-cyan)", fontWeight: 600 }}>
                                x_{index + 1} = {sol}
                              </span>
                              <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                                ≈ {solveResult.approximate[index]}
                              </span>
                            </div>
                          ))
                        )}
                      </div>
                    ) : (
                      <div style={{ color: "var(--accent-rose)" }}>{solveResult.error}</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: 2D FUNCTION GRAPHER */}
        {activeTab === "grapher" && (
          <div className="studio-container">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h2 style={{ fontSize: "1.4rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span style={{ color: "var(--accent-cyan)" }}>📈</span>
                Interactive 2D Function Grapher
              </h2>

              <div style={{ display: "flex", gap: "0.5rem" }}>
                {[
                  "sin(x)",
                  "cos(x)",
                  "x^2 - 4",
                  "sin(x)/x",
                  "1/(1+x^2)",
                  "x^3 - 3*x"
                ].map((sample, idx) => (
                  <button
                    key={idx}
                    className="quick-btn"
                    onClick={() => {
                      setGraphFunc(sample);
                    }}
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "3fr 1fr", gap: "1rem" }}>
              <div className="form-group">
                <label className="form-label">Function f(x):</label>
                <input
                  type="text"
                  className="text-input"
                  value={graphFunc}
                  onChange={(e) => setGraphFunc(e.target.value)}
                  placeholder="e.g. sin(x), x^2 - 4, exp(-x^2)*cos(5*x)"
                />
              </div>

              <div style={{ display: "flex", gap: "0.5rem", alignItems: "flex-end" }}>
                <button
                  className="action-btn-primary"
                  onClick={handleGraphSubmit}
                  style={{ width: "100%" }}
                >
                  Plot Graph
                </button>
              </div>
            </div>

            {/* Interactive Canvas Grapher */}
            <div className="graph-container">
              <canvas ref={canvasRef} className="graph-canvas" />
              <div className="graph-controls">
                <div style={{ display: "flex", gap: "1rem", alignItems: "center", fontSize: "0.85rem", color: "var(--text-muted)" }}>
                  <span>Range: [{graphRange.min}, {graphRange.max}]</span>
                  {graphRoots.length > 0 && (
                    <span style={{ color: "var(--accent-rose)" }}>
                      Roots (f(x)=0): {graphRoots.join(", ")}
                    </span>
                  )}
                </div>

                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button
                    className="card-action-btn"
                    onClick={() => setGraphRange((r) => ({ min: r.min * 1.5, max: r.max * 1.5 }))}
                  >
                    Zoom −
                  </button>
                  <button
                    className="card-action-btn"
                    onClick={() => setGraphRange((r) => ({ min: r.min * 0.7, max: r.max * 0.7 }))}
                  >
                    Zoom +
                  </button>
                  <button
                    className="card-action-btn"
                    onClick={() => setGraphRange({ min: -10, max: 10 })}
                  >
                    Reset View
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: MATRIX STUDIO */}
        {activeTab === "matrix" && (
          <div className="studio-container">
            <h2 style={{ fontSize: "1.4rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ color: "var(--accent-violet)" }}>⊞</span>
              Matrix & Linear Algebra Studio
            </h2>

            <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
              <span className="form-label">Matrix Dimension:</span>
              {[2, 3, 4].map((dim) => (
                <button
                  key={dim}
                  className={`quick-btn ${matrixSize === dim ? "active" : ""}`}
                  style={{ flex: "none", padding: "0.4rem 1rem" }}
                  onClick={() => {
                    setMatrixSize(dim);
                    setMatrixA(Array(dim).fill(0).map(() => Array(dim).fill(0)));
                    setMatrixB(Array(dim).fill(0).map(() => Array(dim).fill(0)));
                  }}
                >
                  {dim} × {dim}
                </button>
              ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
              {/* Matrix A */}
              <div>
                <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--accent-cyan)", marginBottom: "0.5rem" }}>
                  Matrix A
                </h3>
                <div
                  className="matrix-grid"
                  style={{ gridTemplateColumns: `repeat(${matrixSize}, 70px)` }}
                >
                  {matrixA.map((row, r) =>
                    row.map((val, c) => (
                      <input
                        key={`a-${r}-${c}`}
                        type="number"
                        className="matrix-cell"
                        value={val}
                        onChange={(e) => {
                          const updated = matrixA.map((rw) => [...rw]);
                          updated[r][c] = parseFloat(e.target.value) || 0;
                          setMatrixA(updated);
                        }}
                      />
                    ))
                  )}
                </div>
              </div>

              {/* Matrix B */}
              {["multiply", "add"].includes(matrixOp) && (
                <div>
                  <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "var(--accent-violet)", marginBottom: "0.5rem" }}>
                    Matrix B
                  </h3>
                  <div
                    className="matrix-grid"
                    style={{ gridTemplateColumns: `repeat(${matrixSize}, 70px)` }}
                  >
                    {matrixB.map((row, r) =>
                      row.map((val, c) => (
                        <input
                          key={`b-${r}-${c}`}
                          type="number"
                          className="matrix-cell"
                          value={val}
                          onChange={(e) => {
                            const updated = matrixB.map((rw) => [...rw]);
                            updated[r][c] = parseFloat(e.target.value) || 0;
                            setMatrixB(updated);
                          }}
                        />
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Matrix Operations */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", margin: "1rem 0" }}>
              {[
                { op: "det", label: "Determinant det(A)" },
                { op: "inv", label: "Inverse A⁻¹" },
                { op: "transpose", label: "Transpose Aᵀ" },
                { op: "rank", label: "Rank(A)" },
                { op: "eigen", label: "Eigenvalues" },
                { op: "multiply", label: "Multiply A × B" },
                { op: "add", label: "Add A + B" }
              ].map((item) => (
                <button
                  key={item.op}
                  className={`quick-btn ${matrixOp === item.op ? "active" : ""}`}
                  style={{ padding: "0.6rem 1rem", fontSize: "0.85rem" }}
                  onClick={() => {
                    setMatrixOp(item.op);
                  }}
                >
                  {item.label}
                </button>
              ))}
            </div>

            <button className="action-btn-primary" onClick={handleMatrixSubmit}>
              Calculate Matrix Operation
            </button>

            {matrixResult && (
              <div className="result-card">
                <div className="result-header">Result: {matrixResult.operation}</div>
                {matrixResult.success ? (
                  <div>
                    {matrixResult.determinant !== undefined && (
                      <div className="result-body">det(A) = {matrixResult.determinant}</div>
                    )}
                    {matrixResult.rank !== undefined && (
                      <div className="result-body">Rank = {matrixResult.rank}</div>
                    )}
                    {matrixResult.eigenvalues && (
                      <div>
                        {Object.entries(matrixResult.eigenvalues).map(([ev, mul], i) => (
                          <div key={i} style={{ fontSize: "1.1rem", color: "var(--accent-cyan)" }}>
                            λ_{i + 1} = {ev} (multiplicity: {mul})
                          </div>
                        ))}
                      </div>
                    )}
                    {(matrixResult.inverse || matrixResult.transpose || matrixResult.result) && (
                      <div style={{ display: "inline-block", background: "rgba(0,0,0,0.4)", padding: "1rem", borderRadius: "10px" }}>
                        {(matrixResult.inverse || matrixResult.transpose || matrixResult.result).map((row, ri) => (
                          <div key={ri} style={{ display: "flex", gap: "1rem", fontFamily: "var(--font-mono)", fontSize: "1.1rem" }}>
                            [ {row.map((v, ci) => <span key={ci} style={{ minWidth: "40px", textAlign: "right" }}>{Number(v).toFixed(3)}</span>)} ]
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <div style={{ color: "var(--accent-rose)" }}>{matrixResult.error}</div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 5: PANDAS STATISTICS LAB */}
        {activeTab === "statistics" && (
          <div className="studio-container">
            <h2 style={{ fontSize: "1.4rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ color: "var(--accent-emerald)" }}>📊</span>
              Pandas & SciPy Statistical Analysis Lab
            </h2>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
              <div className="form-group">
                <label className="form-label">Dataset X (Comma or Space Separated):</label>
                <textarea
                  className="text-input"
                  rows="3"
                  value={statInputX}
                  onChange={(e) => setStatInputX(e.target.value)}
                  placeholder="e.g. 10, 15, 19, 24, 30, 36, 42, 50"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Dataset Y (Optional for Linear Regression):</label>
                <textarea
                  className="text-input"
                  rows="3"
                  value={statInputY}
                  onChange={(e) => setStatInputY(e.target.value)}
                  placeholder="e.g. 12, 17, 21, 27, 32, 39, 45, 54"
                />
              </div>
            </div>

            <button
              className="action-btn-primary"
              onClick={handleStatsSubmit}
              disabled={statLoading}
            >
              {statLoading ? "Analyzing with Pandas & SciPy..." : "Run Statistical Analysis"}
            </button>

            {statResult && statResult.success && (
              <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
                {/* Summary Grid */}
                <div className="stat-cards-grid">
                  <div className="stat-item">
                    <span className="stat-label">Sample Count (N)</span>
                    <span className="stat-value">{statResult.summary.count}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Mean (μ)</span>
                    <span className="stat-value">{statResult.summary.mean.toFixed(4)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Median (Q2)</span>
                    <span className="stat-value">{statResult.summary.median.toFixed(4)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Std Deviation (σ)</span>
                    <span className="stat-value">{statResult.summary.std_dev.toFixed(4)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Variance (σ²)</span>
                    <span className="stat-value">{statResult.summary.variance.toFixed(4)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Min / Max</span>
                    <span className="stat-value">{statResult.summary.min} / {statResult.summary.max}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Range</span>
                    <span className="stat-value">{statResult.summary.range.toFixed(4)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">IQR (Q3 - Q1)</span>
                    <span className="stat-value">{statResult.summary.iqr.toFixed(4)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Skewness</span>
                    <span className="stat-value">{statResult.summary.skewness.toFixed(4)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Kurtosis</span>
                    <span className="stat-value">{statResult.summary.kurtosis.toFixed(4)}</span>
                  </div>
                </div>

                {/* Regression Summary */}
                {statResult.regression && (
                  <div className="result-card">
                    <div className="result-header">Linear Regression Model (SciPy)</div>
                    <div className="result-body" style={{ color: "var(--accent-emerald)" }}>
                      {statResult.regression.equation}
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginTop: "0.5rem" }}>
                      <div>Correlation (r): <b>{statResult.regression.r.toFixed(4)}</b></div>
                      <div>R-Squared (R²): <b>{statResult.regression.r_squared.toFixed(4)}</b></div>
                      <div>p-value: <b>{statResult.regression.p_value.toExponential(3)}</b></div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 6: UNIT CONVERTER & CONSTANTS */}
        {activeTab === "converter" && (
          <div className="studio-container">
            <h2 style={{ fontSize: "1.4rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ color: "var(--accent-amber)" }}>⚖️</span>
              Unit Converter & Physical Constants
            </h2>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>
              {/* Unit Converter Panel */}
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--accent-amber)" }}>
                  Unit Conversion
                </h3>

                <div className="form-group">
                  <label className="form-label">Category:</label>
                  <select
                    className="text-input"
                    value={convCategory}
                    onChange={(e) => {
                      const cat = e.target.value;
                      setConvCategory(cat);
                      if (cat === "length") {
                        setConvFromUnit("meter");
                        setConvToUnit("foot");
                      } else if (cat === "mass") {
                        setConvFromUnit("kilogram");
                        setConvToUnit("pound");
                      } else if (cat === "temperature") {
                        setConvFromUnit("celsius");
                        setConvToUnit("fahrenheit");
                      } else if (cat === "speed") {
                        setConvFromUnit("meter/sec");
                        setConvToUnit("mph");
                      } else if (cat === "energy") {
                        setConvFromUnit("joule");
                        setConvToUnit("calorie");
                      }
                    }}
                  >
                    <option value="length">Length</option>
                    <option value="mass">Mass & Weight</option>
                    <option value="temperature">Temperature</option>
                    <option value="speed">Speed</option>
                    <option value="energy">Energy & Work</option>
                  </select>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                  <div className="form-group">
                    <label className="form-label">Value:</label>
                    <input
                      type="number"
                      className="text-input"
                      value={convFromVal}
                      onChange={(e) => setConvFromVal(e.target.value)}
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">From Unit:</label>
                    <select
                      className="text-input"
                      value={convFromUnit}
                      onChange={(e) => setConvFromUnit(e.target.value)}
                    >
                      {convCategory === "length" && (
                        <>
                          <option value="meter">Meter (m)</option>
                          <option value="kilometer">Kilometer (km)</option>
                          <option value="centimeter">Centimeter (cm)</option>
                          <option value="millimeter">Millimeter (mm)</option>
                          <option value="mile">Mile (mi)</option>
                          <option value="yard">Yard (yd)</option>
                          <option value="foot">Foot (ft)</option>
                          <option value="inch">Inch (in)</option>
                        </>
                      )}
                      {convCategory === "mass" && (
                        <>
                          <option value="kilogram">Kilogram (kg)</option>
                          <option value="gram">Gram (g)</option>
                          <option value="milligram">Milligram (mg)</option>
                          <option value="pound">Pound (lb)</option>
                          <option value="ounce">Ounce (oz)</option>
                        </>
                      )}
                      {convCategory === "temperature" && (
                        <>
                          <option value="celsius">Celsius (°C)</option>
                          <option value="fahrenheit">Fahrenheit (°F)</option>
                          <option value="kelvin">Kelvin (K)</option>
                        </>
                      )}
                      {convCategory === "speed" && (
                        <>
                          <option value="meter/sec">m/s</option>
                          <option value="km/h">km/h</option>
                          <option value="mph">mph</option>
                          <option value="knot">Knot</option>
                        </>
                      )}
                      {convCategory === "energy" && (
                        <>
                          <option value="joule">Joule (J)</option>
                          <option value="kilojoule">Kilojoule (kJ)</option>
                          <option value="calorie">Calorie (cal)</option>
                          <option value="kilocalorie">Kilocalorie (kcal)</option>
                          <option value="watthour">Watt-hour (Wh)</option>
                          <option value="electronvolt">Electronvolt (eV)</option>
                        </>
                      )}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">To Unit:</label>
                  <select
                    className="text-input"
                    value={convToUnit}
                    onChange={(e) => setConvToUnit(e.target.value)}
                  >
                    {convCategory === "length" && (
                      <>
                        <option value="meter">Meter (m)</option>
                        <option value="kilometer">Kilometer (km)</option>
                        <option value="centimeter">Centimeter (cm)</option>
                        <option value="millimeter">Millimeter (mm)</option>
                        <option value="mile">Mile (mi)</option>
                        <option value="yard">Yard (yd)</option>
                        <option value="foot">Foot (ft)</option>
                        <option value="inch">Inch (in)</option>
                      </>
                    )}
                    {convCategory === "mass" && (
                      <>
                        <option value="kilogram">Kilogram (kg)</option>
                        <option value="gram">Gram (g)</option>
                        <option value="milligram">Milligram (mg)</option>
                        <option value="pound">Pound (lb)</option>
                        <option value="ounce">Ounce (oz)</option>
                      </>
                    )}
                    {convCategory === "temperature" && (
                      <>
                        <option value="celsius">Celsius (°C)</option>
                        <option value="fahrenheit">Fahrenheit (°F)</option>
                        <option value="kelvin">Kelvin (K)</option>
                      </>
                    )}
                    {convCategory === "speed" && (
                      <>
                        <option value="meter/sec">m/s</option>
                        <option value="km/h">km/h</option>
                        <option value="mph">mph</option>
                        <option value="knot">Knot</option>
                      </>
                    )}
                    {convCategory === "energy" && (
                      <>
                        <option value="joule">Joule (J)</option>
                        <option value="kilojoule">Kilojoule (kJ)</option>
                        <option value="calorie">Calorie (cal)</option>
                        <option value="kilocalorie">Kilocalorie (kcal)</option>
                        <option value="watthour">Watt-hour (Wh)</option>
                        <option value="electronvolt">Electronvolt (eV)</option>
                      </>
                    )}
                  </select>
                </div>

                <div className="result-card">
                  <div className="result-header">Converted Value</div>
                  <div className="result-body">{convResult} {convToUnit}</div>
                </div>
              </div>

              {/* Physical Constants Panel */}
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 600, color: "var(--accent-cyan)" }}>
                  Universal Physical Constants
                </h3>

                <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                  {[
                    { name: "Speed of Light (c)", val: "299792458", unit: "m/s" },
                    { name: "Planck's Constant (h)", val: "6.62607015e-34", unit: "J·s" },
                    { name: "Gravitational Constant (G)", val: "6.67430e-11", unit: "m³/(kg·s²)" },
                    { name: "Avogadro's Number (N_A)", val: "6.02214076e23", unit: "mol⁻¹" },
                    { name: "Boltzmann Constant (k_B)", val: "1.380649e-23", unit: "J/K" },
                    { name: "Elementary Charge (e)", val: "1.602176634e-19", unit: "C" },
                    { name: "Standard Gravity (g)", val: "9.80665", unit: "m/s²" },
                  ].map((item, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: "rgba(255, 255, 255, 0.03)",
                        border: "1px solid var(--bg-panel-border)",
                        padding: "0.75rem 1rem",
                        borderRadius: "12px",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center"
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>{item.name}</div>
                        <div style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>{item.unit}</div>
                      </div>
                      <button
                        className="quick-btn"
                        style={{ flex: "none", padding: "0.3rem 0.75rem" }}
                        onClick={() => {
                          setExpression((prev) => prev + item.val);
                          setActiveTab("calculator");
                        }}
                      >
                        Insert {item.val}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div>
          QUANTUMCALC Studio — Engineered with <b>Next.js 16</b>, <b>React 19</b>, and <b>Python 3.12</b> (FastAPI, SymPy, Pandas, NumPy, SciPy, mpmath).
        </div>
      </footer>
    </>
  );
}
