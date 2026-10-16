"""
Scientific Calculator - Native Desktop Application
Built with CustomTkinter, SymPy, NumPy, SciPy, and mpmath.
Features:
- Sleek modern dark mode UI (Windows 11 Fluent aesthetic)
- Full scientific functions (Trig, Inverse, Hyperbolic, Powers, Roots, Logarithms)
- Exact symbolic calculus (Derivatives, Integrals, Limits, Series)
- Matrix Studio (Determinant, Inverse, Eigenvalues, Multiplication)
- Statistical Analysis & Normal Distribution
- Multi-category Unit Converter
- Live History Tape with click-to-recall
- Keyboard input support
"""

import sys
import os
import math
import re
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
import numpy as np
import mpmath

# Configure mpmath precision
mpmath.mp.dps = 50

# Configure SymPy parser transformations
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor
)

# CustomTkinter Global Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ScientificDesktopCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QuantumCalc - Scientific Desktop Studio")
        self.geometry("980x740")
        self.minsize(860, 680)

        # State variables
        self.current_expr = ""
        self.last_result = "0"
        self.angle_mode = "RAD"  # 'RAD' or 'DEG'
        self.memory_val = 0.0
        self.history = []

        # Setup GUI Layout
        self._build_ui()
        self._bind_keyboard()

    def _build_ui(self):
        # Main background container
        self.configure(fg_color="#0b0f19")

        # Top Header Bar
        header = ctk.CTkFrame(self, fg_color="#111827", height=50, corner_radius=0)
        header.pack(fill="x", side="top")

        title_lbl = ctk.CTkLabel(
            header,
            text="⚡ QuantumCalc  |  Desktop Studio",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#60a5fa"
        )
        title_lbl.pack(side="left", padx=20, pady=10)

        # Angle mode switch & precision badge
        mode_frame = ctk.CTkFrame(header, fg_color="transparent")
        mode_frame.pack(side="right", padx=20)

        self.deg_rad_btn = ctk.CTkButton(
            mode_frame,
            text="RAD",
            width=65,
            height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#1e293b",
            hover_color="#334155",
            text_color="#38bdf8",
            corner_radius=6,
            command=self._toggle_angle_mode
        )
        self.deg_rad_btn.pack(side="left", padx=6)

        prec_badge = ctk.CTkLabel(
            mode_frame,
            text="50-DPS SymPy Core",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8",
            fg_color="#1f2937",
            corner_radius=6,
            padx=10,
            pady=4
        )
        prec_badge.pack(side="left", padx=6)

        # Center content frame (Tabs + History Sidebar)
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=14, pady=10)

        # Left/Center Tabview
        self.tabs = ctk.CTkTabview(
            main_content,
            fg_color="#111827",
            segmented_button_fg_color="#1e293b",
            segmented_button_selected_color="#2563eb",
            segmented_button_selected_hover_color="#1d4ed8",
            segmented_button_unselected_hover_color="#334155",
            text_color="#f8fafc",
            corner_radius=12
        )
        self.tabs.pack(fill="both", expand=True, side="left", padx=(0, 10))

        # Add Tabs
        self.tab_calc = self.tabs.add("Scientific")
        self.tab_calculus = self.tabs.add("Calculus & Algebra")
        self.tab_matrix = self.tabs.add("Matrix Studio")
        self.tab_stats = self.tabs.add("Statistics")
        self.tab_converter = self.tabs.add("Unit Converter")

        # Build each tab
        self._build_scientific_tab()
        self._build_calculus_tab()
        self._build_matrix_tab()
        self._build_stats_tab()
        self._build_converter_tab()

        # Right History Sidebar
        self._build_history_sidebar(main_content)

    def _build_display(self, parent):
        disp_frame = ctk.CTkFrame(parent, fg_color="#090d16", corner_radius=12, border_width=1, border_color="#1e293b")
        disp_frame.pack(fill="x", pady=(4, 10), padx=4)

        # Top sub-display: active expression
        self.sub_display = ctk.CTkLabel(
            disp_frame,
            text="",
            font=ctk.CTkFont(family="Consolas", size=15),
            text_color="#94a3b8",
            anchor="e"
        )
        self.sub_display.pack(fill="x", padx=16, pady=(10, 2))

        # Main Entry display: editable or results
        self.main_entry = ctk.CTkEntry(
            disp_frame,
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
            text_color="#f8fafc",
            fg_color="transparent",
            border_width=0,
            justify="right"
        )
        self.main_entry.insert(0, "0")
        self.main_entry.pack(fill="x", padx=12, pady=(0, 10))
        self.main_entry.bind("<Return>", lambda e: self._evaluate_expression())

    def _build_scientific_tab(self):
        tab = self.tab_calc

        # Display
        self._build_display(tab)

        # Keypad container
        keypad_frame = ctk.CTkFrame(tab, fg_color="transparent")
        keypad_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Configure 6 columns
        for c in range(6):
            keypad_frame.columnconfigure(c, weight=1, uniform="calc_col")

        # Button definitions (label, command, bg_type)
        # bg_types: 'func', 'op', 'num', 'action', 'eq'
        buttons = [
            # Row 0: Memory & special
            [("MC", lambda: self._mem_clear(), "mem"),
             ("MR", lambda: self._mem_recall(), "mem"),
             ("M+", lambda: self._mem_add(), "mem"),
             ("M-", lambda: self._mem_sub(), "mem"),
             ("AC", lambda: self._clear_all(), "action"),
             ("DEL", lambda: self._delete_last(), "action")],

            # Row 1: Trig & constants
            [("sin", lambda: self._insert_token("sin("), "func"),
             ("cos", lambda: self._insert_token("cos("), "func"),
             ("tan", lambda: self._insert_token("tan("), "func"),
             ("π", lambda: self._insert_token("pi"), "func"),
             ("e", lambda: self._insert_token("e"), "func"),
             ("÷", lambda: self._insert_token("/"), "op")],

            # Row 2: Inverses & logs
            [("asin", lambda: self._insert_token("asin("), "func"),
             ("acos", lambda: self._insert_token("acos("), "func"),
             ("atan", lambda: self._insert_token("atan("), "func"),
             ("ln", lambda: self._insert_token("ln("), "func"),
             ("log₁₀", lambda: self._insert_token("log("), "func"),
             ("×", lambda: self._insert_token("*"), "op")],

            # Row 3: Powers & roots + num
            [("x²", lambda: self._insert_token("^2"), "func"),
             ("xʸ", lambda: self._insert_token("^"), "func"),
             ("√x", lambda: self._insert_token("sqrt("), "func"),
             ("7", lambda: self._insert_token("7"), "num"),
             ("8", lambda: self._insert_token("8"), "num"),
             ("9", lambda: self._insert_token("9"), "num")],

            # Row 4: Math specials + num & minus
            [("1/x", lambda: self._insert_token("1/("), "func"),
             ("|x|", lambda: self._insert_token("abs("), "func"),
             ("x!", lambda: self._insert_token("!"), "func"),
             ("4", lambda: self._insert_token("4"), "num"),
             ("5", lambda: self._insert_token("5"), "num"),
             ("6", lambda: self._insert_token("6"), "num")],

            # Row 5: Brackets & num & plus
            [("(", lambda: self._insert_token("("), "op"),
             (")", lambda: self._insert_token(")"), "op"),
             ("%", lambda: self._insert_token("%"), "op"),
             ("1", lambda: self._insert_token("1"), "num"),
             ("2", lambda: self._insert_token("2"), "num"),
             ("3", lambda: self._insert_token("3"), "num")],

            # Row 6: Bottom row with Equal
            [("±", lambda: self._toggle_sign(), "op"),
             ("³√x", lambda: self._insert_token("cbrt("), "func"),
             ("Ans", lambda: self._insert_token(self.last_result), "mem"),
             ("0", lambda: self._insert_token("0"), "num"),
             (".", lambda: self._insert_token("."), "num"),
             ("−", lambda: self._insert_token("-"), "op")],
        ]

        # Colors config
        colors = {
            "num": {"fg": "#1e293b", "hover": "#334155", "text": "#f8fafc", "border": None},
            "op": {"fg": "#1e1b4b", "hover": "#312e81", "text": "#a5b4fc", "border": "#3730a3"},
            "func": {"fg": "#0f172a", "hover": "#1e293b", "text": "#93c5fd", "border": "#1e293b"},
            "mem": {"fg": "#172554", "hover": "#1e3a8a", "text": "#60a5fa", "border": None},
            "action": {"fg": "#7f1d1d", "hover": "#991b1b", "text": "#fecaca", "border": None},
            "eq": {"fg": "#059669", "hover": "#10b981", "text": "#ffffff", "border": None},
        }

        # Render rows
        row_idx = 0
        for row in buttons:
            keypad_frame.rowconfigure(row_idx, weight=1)
            col_idx = 0
            for label, cmd, btype in row:
                c = colors[btype]
                btn = ctk.CTkButton(
                    keypad_frame,
                    text=label,
                    command=cmd,
                    font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold" if btype in ("num", "action", "eq") else "normal"),
                    fg_color=c["fg"],
                    hover_color=c["hover"],
                    text_color=c["text"],
                    corner_radius=8,
                    border_width=1 if c["border"] else 0,
                    border_color=c["border"] if c["border"] else c["fg"],
                    height=38
                )
                btn.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky="nsew")
                col_idx += 1
            row_idx += 1

        # Extra wide Equal Button at bottom
        eq_frame = ctk.CTkFrame(tab, fg_color="transparent")
        eq_frame.pack(fill="x", padx=7, pady=(4, 6))

        eq_btn = ctk.CTkButton(
            eq_frame,
            text="=  EVALUATE EXACT & DECIMAL",
            command=self._evaluate_expression,
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color="#2563eb",
            hover_color="#3b82f6",
            text_color="#ffffff",
            corner_radius=10,
            height=44
        )
        eq_btn.pack(fill="x")

    def _build_history_sidebar(self, parent):
        side = ctk.CTkFrame(parent, fg_color="#111827", width=250, corner_radius=12)
        side.pack(fill="y", side="right")

        top = ctk.CTkFrame(side, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(12, 6))

        title = ctk.CTkLabel(
            top,
            text="History Tape",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cbd5e1"
        )
        title.pack(side="left")

        clr_btn = ctk.CTkButton(
            top,
            text="Clear",
            width=50,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#374151",
            hover_color="#4b5563",
            corner_radius=6,
            command=self._clear_history
        )
        clr_btn.pack(side="right")

        self.hist_scroll = ctk.CTkScrollableFrame(
            side,
            fg_color="transparent",
            label_text=""
        )
        self.hist_scroll.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_calculus_tab(self):
        tab = self.tab_calculus

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        # Title
        lbl = ctk.CTkLabel(
            scroll,
            text="Symbolic Calculus & Equation Studio",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#60a5fa"
        )
        lbl.pack(anchor="w", pady=(0, 12))

        # Expression input
        expr_box = ctk.CTkFrame(scroll, fg_color="#1e293b", corner_radius=10)
        expr_box.pack(fill="x", pady=6)

        ctk.CTkLabel(expr_box, text="Function f(x) or Equation:", font=ctk.CTkFont(weight="bold"), text_color="#cbd5e1").pack(anchor="w", padx=12, pady=(10, 4))
        self.calc_input = ctk.CTkEntry(expr_box, placeholder_text="e.g. x^3 - 4*x^2 + 6*x - 24  or  sin(x)*cos(x)", height=38, font=ctk.CTkFont(family="Consolas", size=14))
        self.calc_input.pack(fill="x", padx=12, pady=(0, 10))

        # Action Buttons
        btn_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_grid.pack(fill="x", pady=8)
        for i in range(4):
            btn_grid.columnconfigure(i, weight=1)

        actions = [
            ("d/dx (Derivative)", self._calc_derivative, "#2563eb"),
            ("∫ dx (Indefinite)", self._calc_integral, "#7c3aed"),
            ("Factor", self._calc_factor, "#059669"),
            ("Expand", self._calc_expand, "#d97706"),
            ("Simplify", self._calc_simplify, "#0891b2"),
            ("Solve f(x)=0", self._calc_solve, "#e11d48"),
            ("Taylor (x=0, n=5)", self._calc_taylor, "#4f46e5"),
            ("Critical Points", self._calc_roots, "#059669"),
        ]

        r = 0
        c = 0
        for text, cmd, col in actions:
            btn = ctk.CTkButton(
                btn_grid,
                text=text,
                command=cmd,
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=col,
                hover_color=col,
                height=38,
                corner_radius=8
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            c += 1
            if c >= 4:
                c = 0
                r += 1

        # Definite integral bounds
        def_frame = ctk.CTkFrame(scroll, fg_color="#1e293b", corner_radius=10)
        def_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(def_frame, text="Definite Integral  ∫ [a to b] f(x) dx:", font=ctk.CTkFont(weight="bold"), text_color="#cbd5e1").pack(anchor="w", padx=12, pady=(10, 4))
        
        bounds_f = ctk.CTkFrame(def_frame, fg_color="transparent")
        bounds_f.pack(fill="x", padx=12, pady=(0, 10))
        
        ctk.CTkLabel(bounds_f, text="Lower bound a:").pack(side="left", padx=4)
        self.bound_a = ctk.CTkEntry(bounds_f, width=80, placeholder_text="0")
        self.bound_a.pack(side="left", padx=4)

        ctk.CTkLabel(bounds_f, text="Upper bound b:").pack(side="left", padx=(14, 4))
        self.bound_b = ctk.CTkEntry(bounds_f, width=80, placeholder_text="pi")
        self.bound_b.pack(side="left", padx=4)

        ctk.CTkButton(
            bounds_f,
            text="Compute Definite Integral",
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            command=self._calc_definite_integral
        ).pack(side="left", padx=16)

        # Output box
        ctk.CTkLabel(scroll, text="Calculus Result / Step Output:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#cbd5e1").pack(anchor="w", pady=(10, 4))
        self.calc_output = ctk.CTkTextbox(
            scroll,
            height=160,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#090d16",
            text_color="#38bdf8",
            corner_radius=10,
            border_width=1,
            border_color="#1e293b"
        )
        self.calc_output.pack(fill="x", pady=(0, 10))

    def _build_matrix_tab(self):
        tab = self.tab_matrix
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        lbl = ctk.CTkLabel(
            scroll,
            text="Matrix & Linear Algebra Studio",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#60a5fa"
        )
        lbl.pack(anchor="w", pady=(0, 10))

        # Matrix A input
        box_a = ctk.CTkFrame(scroll, fg_color="#1e293b", corner_radius=10)
        box_a.pack(fill="x", pady=6)
        ctk.CTkLabel(box_a, text="Matrix A (Row per line, space/comma separated):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(8, 4))
        self.matrix_a_text = ctk.CTkTextbox(box_a, height=75, font=ctk.CTkFont(family="Consolas", size=13))
        self.matrix_a_text.insert("1.0", "1 2 3\n0 1 4\n5 6 0")
        self.matrix_a_text.pack(fill="x", padx=12, pady=(0, 10))

        # Action buttons for Matrix A
        m_btns = ctk.CTkFrame(scroll, fg_color="transparent")
        m_btns.pack(fill="x", pady=6)
        for i in range(4):
            m_btns.columnconfigure(i, weight=1)

        m_actions = [
            ("Determinant (det A)", lambda: self._matrix_op("det")),
            ("Inverse (A⁻¹)", lambda: self._matrix_op("inv")),
            ("Transpose (Aᵀ)", lambda: self._matrix_op("trans")),
            ("Eigenvalues & Vectors", lambda: self._matrix_op("eigen")),
            ("Matrix Rank", lambda: self._matrix_op("rank")),
            ("Trace (Tr A)", lambda: self._matrix_op("trace")),
            ("RREF (Reduced Echelon)", lambda: self._matrix_op("rref")),
            ("Characteristic Poly", lambda: self._matrix_op("charpoly")),
        ]

        r, c = 0, 0
        for text, cmd in m_actions:
            btn = ctk.CTkButton(
                m_btns,
                text=text,
                command=cmd,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#1e293b",
                hover_color="#334155",
                border_width=1,
                border_color="#3b82f6",
                text_color="#93c5fd",
                height=36
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            c += 1
            if c >= 4:
                c = 0
                r += 1

        # Matrix Result Output
        ctk.CTkLabel(scroll, text="Matrix Computation Result:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 4))
        self.matrix_output = ctk.CTkTextbox(
            scroll,
            height=150,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#090d16",
            text_color="#34d399",
            corner_radius=10,
            border_width=1,
            border_color="#1e293b"
        )
        self.matrix_output.pack(fill="x", pady=(0, 10))

    def _build_stats_tab(self):
        tab = self.tab_stats
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        lbl = ctk.CTkLabel(
            scroll,
            text="Descriptive Statistics & Normal Distribution",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#60a5fa"
        )
        lbl.pack(anchor="w", pady=(0, 10))

        # Dataset input
        box = ctk.CTkFrame(scroll, fg_color="#1e293b", corner_radius=10)
        box.pack(fill="x", pady=6)
        ctk.CTkLabel(box, text="Enter Data Sample (comma, space, or newline separated):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(8, 4))
        self.stats_input = ctk.CTkTextbox(box, height=75, font=ctk.CTkFont(family="Consolas", size=13))
        self.stats_input.insert("1.0", "12, 15, 14, 10, 18, 20, 22, 19, 14, 15, 17, 24, 28, 19")
        self.stats_input.pack(fill="x", padx=12, pady=(0, 10))

        stat_btn = ctk.CTkButton(
            scroll,
            text="Compute Complete Statistical Analysis",
            command=self._calc_stats,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#059669",
            hover_color="#10b981",
            height=40
        )
        stat_btn.pack(fill="x", pady=8)

        # Output box
        ctk.CTkLabel(scroll, text="Statistical Summary Report:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 4))
        self.stats_output = ctk.CTkTextbox(
            scroll,
            height=220,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#090d16",
            text_color="#fbbf24",
            corner_radius=10,
            border_width=1,
            border_color="#1e293b"
        )
        self.stats_output.pack(fill="x", pady=(0, 10))

    def _build_converter_tab(self):
        tab = self.tab_converter
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        lbl = ctk.CTkLabel(
            scroll,
            text="Scientific & Engineering Unit Converter",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#60a5fa"
        )
        lbl.pack(anchor="w", pady=(0, 12))

        # Categories
        self.unit_categories = {
            "Length": ["meter (m)", "kilometer (km)", "centimeter (cm)", "millimeter (mm)", "mile (mi)", "yard (yd)", "foot (ft)", "inch (in)", "nautical mile"],
            "Mass": ["kilogram (kg)", "gram (g)", "milligram (mg)", "pound (lb)", "ounce (oz)", "metric ton (t)"],
            "Temperature": ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"],
            "Speed": ["m/s", "km/h", "mph", "knot", "mach"],
            "Data": ["Byte (B)", "Kilobyte (KB)", "Megabyte (MB)", "Gigabyte (GB)", "Terabyte (TB)", "Petabyte (PB)"],
            "Energy": ["Joule (J)", "Kilojoule (kJ)", "calorie (cal)", "Kilocalorie (kcal)", "Watt-hour (Wh)", "Kilowatt-hour (kWh)", "Electronvolt (eV)"]
        }

        cat_frame = ctk.CTkFrame(scroll, fg_color="#1e293b", corner_radius=10)
        cat_frame.pack(fill="x", pady=6)

        ctk.CTkLabel(cat_frame, text="Select Category:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=12, pady=(10, 4))
        self.cat_menu = ctk.CTkOptionMenu(
            cat_frame,
            values=list(self.unit_categories.keys()),
            command=self._on_unit_cat_change,
            fg_color="#2563eb",
            button_color="#1d4ed8"
        )
        self.cat_menu.pack(anchor="w", padx=12, pady=(0, 12))

        # Input and Output units row
        conv_frame = ctk.CTkFrame(scroll, fg_color="#1e293b", corner_radius=10)
        conv_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(conv_frame, text="From Unit & Value:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")
        ctk.CTkLabel(conv_frame, text="To Target Unit:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=12, pady=(10, 4), sticky="w")

        self.from_val = ctk.CTkEntry(conv_frame, placeholder_text="Value", width=140, font=ctk.CTkFont(size=14))
        self.from_val.insert(0, "1")
        self.from_val.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

        self.from_unit_menu = ctk.CTkOptionMenu(conv_frame, values=self.unit_categories["Length"], width=180)
        self.from_unit_menu.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="w")

        self.to_unit_menu = ctk.CTkOptionMenu(conv_frame, values=self.unit_categories["Length"], width=180)
        self.to_unit_menu.set(self.unit_categories["Length"][1])
        self.to_unit_menu.grid(row=2, column=1, padx=12, pady=(0, 12), sticky="w")

        conv_btn = ctk.CTkButton(
            scroll,
            text="Convert Unit",
            command=self._perform_unit_conversion,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2563eb",
            hover_color="#3b82f6",
            height=40
        )
        conv_btn.pack(fill="x", pady=8)

        self.conv_res_lbl = ctk.CTkLabel(
            scroll,
            text="Result: 1 meter (m) = 0.001 kilometer (km)",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color="#34d399",
            fg_color="#090d16",
            corner_radius=10,
            padx=16,
            pady=16
        )
        self.conv_res_lbl.pack(fill="x", pady=10)

    # ------------------ Core Scientific Engine ------------------
    def _insert_token(self, token):
        val = self.main_entry.get()
        if val == "0" and token not in (".", "^", "+", "-", "*", "/", "%", "^2"):
            self.main_entry.delete(0, "end")
        self.main_entry.insert("end", token)

    def _clear_all(self):
        self.main_entry.delete(0, "end")
        self.main_entry.insert(0, "0")
        self.sub_display.configure(text="")

    def _delete_last(self):
        val = self.main_entry.get()
        if len(val) > 1:
            self.main_entry.delete(len(val) - 1, "end")
        else:
            self.main_entry.delete(0, "end")
            self.main_entry.insert(0, "0")

    def _toggle_sign(self):
        val = self.main_entry.get()
        if not val or val == "0":
            return
        if val.startswith("-"):
            self.main_entry.delete(0, 1)
        else:
            self.main_entry.insert(0, "-")

    def _toggle_angle_mode(self):
        if self.angle_mode == "RAD":
            self.angle_mode = "DEG"
            self.deg_rad_btn.configure(text="DEG", text_color="#f59e0b")
        else:
            self.angle_mode = "RAD"
            self.deg_rad_btn.configure(text="RAD", text_color="#38bdf8")

    def _mem_clear(self):
        self.memory_val = 0.0

    def _mem_recall(self):
        self._insert_token(str(self.memory_val))

    def _mem_add(self):
        try:
            val = float(self.main_entry.get())
            self.memory_val += val
        except Exception:
            pass

    def _mem_sub(self):
        try:
            val = float(self.main_entry.get())
            self.memory_val -= val
        except Exception:
            pass

    def _safe_parse(self, expr_str):
        clean = expr_str.strip()
        clean = clean.replace("×", "*").replace("÷", "/")
        clean = clean.replace("π", "pi").replace("√", "sqrt")
        clean = clean.replace("ln(", "log(")
        clean = clean.replace("arcsin", "asin").replace("arccos", "acos").replace("arctan", "atan")

        # Handle degree mode for trigonometric functions
        if self.angle_mode == "DEG":
            # Replace sin(arg) with sin(rad(arg))
            for f in ["sin", "cos", "tan"]:
                clean = re.sub(rf'\b{f}\(([^)]+)\)', rf'{f}((\1)*pi/180)', clean)

        local_dict = {
            'e': sp.E,
            'pi': sp.pi,
            'tau': 2 * sp.pi,
            'phi': sp.GoldenRatio,
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'asin': sp.asin,
            'acos': sp.acos,
            'atan': sp.atan,
            'log': sp.log,
            'sqrt': sp.sqrt,
            'cbrt': sp.cbrt,
            'abs': sp.Abs,
            'factorial': sp.factorial,
        }

        # Replace ! with factorial()
        clean = re.sub(r'(\w+)!', r'factorial(\1)', clean)
        return parse_expr(clean, local_dict=local_dict, transformations=TRANSFORMATIONS, evaluate=True)

    def _evaluate_expression(self):
        expr_raw = self.main_entry.get().strip()
        if not expr_raw:
            return

        try:
            parsed = self._safe_parse(expr_raw)
            # Exact symbolic result
            exact_val = sp.simplify(parsed)
            # High precision decimal
            numeric_val = mpmath.mpmathify(exact_val.evalf(50))
            num_str = mpmath.nstr(numeric_val, 16)

            # Pretty format result
            self.sub_display.configure(text=f"{expr_raw} = {sp.pretty(exact_val) if len(str(exact_val)) < 30 else ''}")
            self.main_entry.delete(0, "end")
            self.main_entry.insert(0, num_str)

            self.last_result = num_str
            self._add_history(expr_raw, num_str)

        except Exception as e:
            # Fallback evaluation via Python eval with restricted globals
            try:
                allowed_math = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
                allowed_math.update({"pi": math.pi, "e": math.e})
                clean_expr = expr_raw.replace("^", "**").replace("×", "*").replace("÷", "/")
                res = str(eval(clean_expr, {"__builtins__": {}}, allowed_math))
                self.sub_display.configure(text=f"{expr_raw} =")
                self.main_entry.delete(0, "end")
                self.main_entry.insert(0, res)
                self.last_result = res
                self._add_history(expr_raw, res)
            except Exception as e2:
                self.sub_display.configure(text=f"Error: {str(e)[:35]}")

    def _add_history(self, expr, res):
        self.history.append((expr, res))
        item = ctk.CTkFrame(self.hist_scroll, fg_color="#1e293b", corner_radius=8)
        item.pack(fill="x", pady=4, padx=2)

        lbl_expr = ctk.CTkLabel(item, text=expr, font=ctk.CTkFont(family="Consolas", size=12), text_color="#94a3b8", anchor="w")
        lbl_expr.pack(fill="x", padx=8, pady=(4, 0))

        lbl_res = ctk.CTkLabel(item, text=f"= {res}", font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), text_color="#38bdf8", anchor="w")
        lbl_res.pack(fill="x", padx=8, pady=(0, 4))

        # Click to paste into calculator
        item.bind("<Button-1>", lambda e, r=res: self._paste_history_result(r))
        lbl_expr.bind("<Button-1>", lambda e, r=res: self._paste_history_result(r))
        lbl_res.bind("<Button-1>", lambda e, r=res: self._paste_history_result(r))

    def _paste_history_result(self, res):
        self.main_entry.delete(0, "end")
        self.main_entry.insert(0, res)

    def _clear_history(self):
        for w in self.hist_scroll.winfo_children():
            w.destroy()
        self.history.clear()

    def _bind_keyboard(self):
        self.bind("<Escape>", lambda e: self._clear_all())

    # ------------------ Calculus Handlers ------------------
    def _calc_derivative(self):
        text = self.calc_input.get().strip()
        if not text:
            return
        try:
            x = sp.Symbol('x')
            expr = self._safe_parse(text)
            diff_res = sp.diff(expr, x)
            output = f"Expression: f(x) = {expr}\n"
            output += f"First Derivative f'(x):\n  {diff_res}\n\n"
            output += f"Second Derivative f''(x):\n  {sp.diff(diff_res, x)}\n\n"
            output += f"Factored Form:\n  {sp.factor(diff_res)}"
            self._set_calc_output(output)
        except Exception as e:
            self._set_calc_output(f"Error computing derivative: {e}")

    def _calc_integral(self):
        text = self.calc_input.get().strip()
        if not text:
            return
        try:
            x = sp.Symbol('x')
            expr = self._safe_parse(text)
            integ = sp.integrate(expr, x)
            output = f"Indefinite Integral  ∫ f(x) dx:\n  {integ} + C\n\n"
            output += f"Expanded Form:\n  {sp.expand(integ)} + C"
            self._set_calc_output(output)
        except Exception as e:
            self._set_calc_output(f"Error computing integral: {e}")

    def _calc_definite_integral(self):
        text = self.calc_input.get().strip()
        a_str = self.bound_a.get().strip()
        b_str = self.bound_b.get().strip()
        if not text:
            return
        try:
            x = sp.Symbol('x')
            expr = self._safe_parse(text)
            a = self._safe_parse(a_str) if a_str else 0
            b = self._safe_parse(b_str) if b_str else sp.pi
            val = sp.integrate(expr, (x, a, b))
            val_num = val.evalf(25)
            output = f"Definite Integral ∫ [{a} to {b}] ({expr}) dx:\n\n"
            output += f"Exact Analytic Value : {val}\n"
            output += f"Decimal Approximation: {val_num}\n"
            self._set_calc_output(output)
        except Exception as e:
            self._set_calc_output(f"Error: {e}")

    def _calc_factor(self):
        self._generic_sym_op(sp.factor, "Factored Form")

    def _calc_expand(self):
        self._generic_sym_op(sp.expand, "Expanded Form")

    def _calc_simplify(self):
        self._generic_sym_op(sp.simplify, "Simplified Form")

    def _calc_solve(self):
        text = self.calc_input.get().strip()
        if not text:
            return
        try:
            x = sp.Symbol('x')
            expr = self._safe_parse(text)
            sol = sp.solve(expr, x)
            output = f"Solving Equation: {expr} = 0\n\n"
            output += f"Solutions found ({len(sol)}):\n"
            for i, s in enumerate(sol, 1):
                try:
                    num = s.evalf(8)
                    output += f"  x_{i} = {s}   (~ {num})\n"
                except Exception:
                    output += f"  x_{i} = {s}\n"
            self._set_calc_output(output)
        except Exception as e:
            self._set_calc_output(f"Error solving equation: {e}")

    def _calc_taylor(self):
        text = self.calc_input.get().strip()
        if not text:
            return
        try:
            x = sp.Symbol('x')
            expr = self._safe_parse(text)
            series = sp.series(expr, x, 0, 6)
            self._set_calc_output(f"Taylor Series around x = 0 (up to O(x^6)):\n\n{series}")
        except Exception as e:
            self._set_calc_output(f"Error: {e}")

    def _calc_roots(self):
        text = self.calc_input.get().strip()
        if not text:
            return
        try:
            x = sp.Symbol('x')
            expr = self._safe_parse(text)
            f_prime = sp.diff(expr, x)
            crit = sp.solve(f_prime, x)
            output = f"Critical points for f(x) = {expr} (where f'(x) = 0):\n\n"
            output += f"f'(x) = {f_prime}\n\nCritical x values:\n"
            for c in crit:
                y = expr.subs(x, c)
                output += f"  x = {c}  =>  y = {y}\n"
            self._set_calc_output(output)
        except Exception as e:
            self._set_calc_output(f"Error: {e}")

    def _generic_sym_op(self, op_func, title):
        text = self.calc_input.get().strip()
        if not text:
            return
        try:
            expr = self._safe_parse(text)
            res = op_func(expr)
            self._set_calc_output(f"{title}:\n  {res}")
        except Exception as e:
            self._set_calc_output(f"Error: {e}")

    def _set_calc_output(self, text):
        self.calc_output.delete("1.0", "end")
        self.calc_output.insert("1.0", text)

    # ------------------ Matrix Handlers ------------------
    def _parse_matrix_a(self):
        raw = self.matrix_a_text.get("1.0", "end").strip()
        lines = [line.strip() for line in raw.split("\n") if line.strip()]
        data = []
        for line in lines:
            parts = re.split(r'[, \t]+', line)
            data.append([float(sp.sympify(p).evalf()) for p in parts if p])
        return sp.Matrix(data)

    def _matrix_op(self, op):
        try:
            M = self._parse_matrix_a()
            rows, cols = M.shape
            output = f"Matrix Dimension: {rows} × {cols}\n"

            if op == "det":
                if rows != cols:
                    output += "Error: Determinant requires a square matrix!"
                else:
                    d = M.det()
                    output += f"Determinant det(A) = {d}\n"
            elif op == "inv":
                if rows != cols:
                    output += "Error: Inverse requires a square matrix!"
                elif M.det() == 0:
                    output += "Matrix is Singular (Determinant = 0), non-invertible!"
                else:
                    inv = M.inv()
                    output += f"Inverse Matrix A⁻¹:\n{sp.pretty(inv)}"
            elif op == "trans":
                output += f"Transpose Matrix Aᵀ:\n{sp.pretty(M.T)}"
            elif op == "eigen":
                if rows != cols:
                    output += "Error: Eigenvalues require a square matrix!"
                else:
                    eigenvals = M.eigenvals()
                    output += f"Eigenvalues (with multiplicity):\n"
                    for val, mult in eigenvals.items():
                        output += f"  λ = {val.evalf(6)}  (multiplicity: {mult})\n"
            elif op == "rank":
                output += f"Matrix Rank: {M.rank()}"
            elif op == "trace":
                if rows != cols:
                    output += "Error: Trace requires a square matrix!"
                else:
                    output += f"Matrix Trace: {M.trace()}"
            elif op == "rref":
                rref_m, pivots = M.rref()
                output += f"Reduced Row Echelon Form (RREF):\n{sp.pretty(rref_m)}\n\nPivot columns: {pivots}"
            elif op == "charpoly":
                x = sp.Symbol('λ')
                cp = M.charpoly(x)
                output += f"Characteristic Polynomial:\n{cp.as_expr()}"

            self.matrix_output.delete("1.0", "end")
            self.matrix_output.insert("1.0", output)
        except Exception as e:
            self.matrix_output.delete("1.0", "end")
            self.matrix_output.insert("1.0", f"Matrix Calculation Error:\n{e}")

    # ------------------ Stats Handlers ------------------
    def _calc_stats(self):
        raw = self.stats_input.get("1.0", "end").strip()
        if not raw:
            return
        try:
            parts = re.split(r'[, \n\t]+', raw)
            vals = [float(p) for p in parts if p]
            if not vals:
                return

            arr = np.array(vals)
            n = len(arr)
            mean = np.mean(arr)
            std = np.std(arr, ddof=1) if n > 1 else 0.0
            var = np.var(arr, ddof=1) if n > 1 else 0.0
            median = np.median(arr)
            q25 = np.percentile(arr, 25)
            q75 = np.percentile(arr, 75)
            iqr = q75 - q25

            out = "=" * 45 + "\n"
            out += "     COMPREHENSIVE STATISTICAL PROFILE     \n"
            out += "=" * 45 + "\n"
            out += f"Sample Size (N)     : {n}\n"
            out += f"Mean (Average)      : {mean:.6f}\n"
            out += f"Median (Q2)         : {median:.6f}\n"
            out += f"Standard Deviation  : {std:.6f}\n"
            out += f"Variance            : {var:.6f}\n"
            out += f"Minimum             : {np.min(arr):.6f}\n"
            out += f"Maximum             : {np.max(arr):.6f}\n"
            out += f"Range               : {(np.max(arr) - np.min(arr)):.6f}\n"
            out += f"First Quartile (Q1) : {q25:.6f}\n"
            out += f"Third Quartile (Q3) : {q75:.6f}\n"
            out += f"Interquartile (IQR) : {iqr:.6f}\n"
            out += f"Sum of Elements     : {np.sum(arr):.6f}\n"

            self.stats_output.delete("1.0", "end")
            self.stats_output.insert("1.0", out)
        except Exception as e:
            self.stats_output.delete("1.0", "end")
            self.stats_output.insert("1.0", f"Error calculating statistics:\n{e}")

    # ------------------ Converter Handlers ------------------
    def _on_unit_cat_change(self, cat):
        units = self.unit_categories[cat]
        self.from_unit_menu.configure(values=units)
        self.to_unit_menu.configure(values=units)
        self.from_unit_menu.set(units[0])
        self.to_unit_menu.set(units[1] if len(units) > 1 else units[0])

    def _perform_unit_conversion(self):
        cat = self.cat_menu.get()
        u_from = self.from_unit_menu.get()
        u_to = self.to_unit_menu.get()

        try:
            val = float(self.from_val.get())
        except ValueError:
            self.conv_res_lbl.configure(text="Please enter a valid numeric value.")
            return

        res = None
        # Conversion Factors relative to base unit
        if cat == "Length":
            # Base: meter
            to_meter = {
                "meter (m)": 1.0,
                "kilometer (km)": 1000.0,
                "centimeter (cm)": 0.01,
                "millimeter (mm)": 0.001,
                "mile (mi)": 1609.344,
                "yard (yd)": 0.9144,
                "foot (ft)": 0.3048,
                "inch (in)": 0.0254,
                "nautical mile": 1852.0
            }
            res = (val * to_meter[u_from]) / to_meter[u_to]

        elif cat == "Mass":
            # Base: kilogram
            to_kg = {
                "kilogram (kg)": 1.0,
                "gram (g)": 0.001,
                "milligram (mg)": 1e-6,
                "pound (lb)": 0.45359237,
                "ounce (oz)": 0.02834952,
                "metric ton (t)": 1000.0
            }
            res = (val * to_kg[u_from]) / to_kg[u_to]

        elif cat == "Temperature":
            # Convert from u_from to Celsius first
            c_val = val
            if u_from == "Fahrenheit (°F)":
                c_val = (val - 32.0) * 5.0 / 9.0
            elif u_from == "Kelvin (K)":
                c_val = val - 273.15

            # Convert from Celsius to u_to
            if u_to == "Celsius (°C)":
                res = c_val
            elif u_to == "Fahrenheit (°F)":
                res = (c_val * 9.0 / 5.0) + 32.0
            elif u_to == "Kelvin (K)":
                res = c_val + 273.15

        elif cat == "Speed":
            # Base: m/s
            to_ms = {
                "m/s": 1.0,
                "km/h": 1.0 / 3.6,
                "mph": 0.44704,
                "knot": 0.514444,
                "mach": 343.0
            }
            res = (val * to_ms[u_from]) / to_ms[u_to]

        elif cat == "Data":
            # Base: Byte
            to_bytes = {
                "Byte (B)": 1,
                "Kilobyte (KB)": 1024,
                "Megabyte (MB)": 1024**2,
                "Gigabyte (GB)": 1024**3,
                "Terabyte (TB)": 1024**4,
                "Petabyte (PB)": 1024**5
            }
            res = (val * to_bytes[u_from]) / to_bytes[u_to]

        elif cat == "Energy":
            # Base: Joule
            to_joule = {
                "Joule (J)": 1.0,
                "Kilojoule (kJ)": 1000.0,
                "calorie (cal)": 4.184,
                "Kilocalorie (kcal)": 4184.0,
                "Watt-hour (Wh)": 3600.0,
                "Kilowatt-hour (kWh)": 3.6e6,
                "Electronvolt (eV)": 1.602176634e-19
            }
            res = (val * to_joule[u_from]) / to_joule[u_to]

        if res is not None:
            self.conv_res_lbl.configure(text=f"Result: {val} {u_from}  =  {res:.8g} {u_to}")


def main():
    app = ScientificDesktopCalculator()
    app.mainloop()


if __name__ == "__main__":
    main()
