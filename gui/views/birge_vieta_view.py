"""Vista de entrada de datos para Birge-Vieta (hora crítica del CPU con Horner + Newton-Raphson)."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any, List

from methods.birge_vieta import birge_vieta, format_polynomial


class BirgeVietaView(ttk.Frame):
    def __init__(self, parent, on_solve_callback: Callable[[Dict[str, Any]], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.on_solve_callback = on_solve_callback
        self._setup_ui()

    def _setup_ui(self):
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # coeficientes
        lbl_coef = ttk.Label(
            container,
            text="Coeficientes de la función de carga C(t) [uso de CPU % en función de la hora t]:",
            font=("Segoe UI", 9, "bold")
        )
        lbl_coef.pack(anchor=tk.W, pady=(0, 2))

        self.entry_coeffs = ttk.Entry(container, font=("Consolas", 10))
        self.entry_coeffs.pack(fill=tk.X, pady=(0, 4))
        self.entry_coeffs.insert(0, "-2.5, 60, -270")
        self.entry_coeffs.bind("<KeyRelease>", self._update_poly_preview)

        # vista previa
        self.lbl_preview = ttk.Label(
            container,
            text="Carga: C(t) = -2.5t^2 + 60t - 270  |  Umbral Crítico = 85.0 %",
            font=("Consolas", 9, "bold"),
            foreground="#1e40af"
        )
        self.lbl_preview.pack(anchor=tk.W, pady=(0, 8))

        # parámetros
        grid_frame = ttk.Frame(container)
        grid_frame.pack(fill=tk.X, pady=(0, 8))

        # umbral
        ttk.Label(grid_frame, text="Umbral Crítico de CPU (%):", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=4)
        self.entry_threshold = ttk.Entry(grid_frame, width=10, font=("Consolas", 9))
        self.entry_threshold.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=4)
        self.entry_threshold.insert(0, "85.0")
        self.entry_threshold.bind("<KeyRelease>", self._update_poly_preview)

        # t0
        ttk.Label(grid_frame, text="Hora inicial estimada (t₀ en hrs):", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky=tk.W, padx=(0, 8), pady=4)
        self.entry_x0 = ttk.Entry(grid_frame, width=10, font=("Consolas", 9))
        self.entry_x0.grid(row=0, column=3, sticky=tk.W, padx=(0, 20), pady=4)
        self.entry_x0.insert(0, "9.0")

        # tolerancia
        ttk.Label(grid_frame, text="Tolerancia de error permitida (ε):", font=("Segoe UI", 9, "bold")).grid(row=0, column=4, sticky=tk.W, padx=(0, 8), pady=4)
        self.entry_tol = ttk.Entry(grid_frame, width=10, font=("Consolas", 9))
        self.entry_tol.grid(row=0, column=5, sticky=tk.W, pady=4)
        self.entry_tol.insert(0, "0.0001")

        # máx. iteraciones
        ttk.Label(grid_frame, text="Máximo de iteraciones:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=4)
        self.entry_max_iter = ttk.Entry(grid_frame, width=10, font=("Consolas", 9))
        self.entry_max_iter.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=4)
        self.entry_max_iter.insert(0, "50")

        # botones de ejemplos y limpiar
        btn_box = ttk.Frame(container)
        btn_box.pack(fill=tk.X, pady=(6, 2))

        btn_example1 = ttk.Button(btn_box, text="💡 Cargar Caso 1 (Pico Escolar 10:35 AM)", command=self.load_example_1)
        btn_example1.pack(side=tk.LEFT, padx=(0, 8))

        btn_example2 = ttk.Button(btn_box, text="💡 Cargar Caso 2 (Carga Cúbica Tarde)", command=self.load_example_2)
        btn_example2.pack(side=tk.LEFT, padx=(0, 8))

        btn_clear = ttk.Button(btn_box, text="🗑 Limpiar Campos", command=self.clear_fields)
        btn_clear.pack(side=tk.LEFT)

    def _update_poly_preview(self, event=None):
        text = self.entry_coeffs.get().strip()
        thresh = self.entry_threshold.get().strip()
        try:
            parts = [float(p) for p in text.replace(",", " ").split() if p]
            if parts:
                poly_str = format_polynomial(parts)
                self.lbl_preview.config(
                    text=f"Carga: C(t) = {poly_str}  [% CPU]  |  Umbral Crítico = {thresh}%",
                    foreground="#1e40af"
                )
            else:
                self.lbl_preview.config(text="C(t) = ...", foreground="#64748b")
        except Exception:
            self.lbl_preview.config(text="Formato de coeficientes inválido", foreground="#dc2626")

    def load_example_1(self):
        # ejemplo 1: C(t) = -2.5 t^2 + 60 t - 270, t0 = 9.0
        self.entry_coeffs.delete(0, tk.END)
        self.entry_coeffs.insert(0, "-2.5, 60, -270")
        self.entry_threshold.delete(0, tk.END)
        self.entry_threshold.insert(0, "85.0")
        self.entry_x0.delete(0, tk.END)
        self.entry_x0.insert(0, "9.0")
        self.entry_tol.delete(0, tk.END)
        self.entry_tol.insert(0, "0.0001")
        self.entry_max_iter.delete(0, tk.END)
        self.entry_max_iter.insert(0, "50")
        self._update_poly_preview()

    def load_example_2(self):
        # ejemplo 2: cúbica, t0 = 12.0
        self.entry_coeffs.delete(0, tk.END)
        self.entry_coeffs.insert(0, "-0.2, 4.5, -15, -40")
        self.entry_threshold.delete(0, tk.END)
        self.entry_threshold.insert(0, "85.0")
        self.entry_x0.delete(0, tk.END)
        self.entry_x0.insert(0, "12.0")
        self.entry_tol.delete(0, tk.END)
        self.entry_tol.insert(0, "0.0001")
        self.entry_max_iter.delete(0, tk.END)
        self.entry_max_iter.insert(0, "50")
        self._update_poly_preview()

    def clear_fields(self):
        self.entry_coeffs.delete(0, tk.END)
        self.entry_threshold.delete(0, tk.END)
        self.entry_x0.delete(0, tk.END)
        self.entry_tol.delete(0, tk.END)
        self.entry_max_iter.delete(0, tk.END)
        self.lbl_preview.config(text="C(t) = ...", foreground="#64748b")

    def solve(self):
        """Valida las entradas y corre Birge-Vieta."""
        raw_coeffs = self.entry_coeffs.get().strip()
        if not raw_coeffs:
            messagebox.showerror("Error de Validación", "Por favor ingresa los coeficientes de la función de carga C(t).")
            return

        try:
            coeffs = [float(p) for p in raw_coeffs.replace(",", " ").split() if p]
        except ValueError:
            messagebox.showerror("Error de Formato", "Los coeficientes deben ser números reales (ej: -2.5, 60, -270).")
            return

        if len(coeffs) < 2:
            messagebox.showerror("Error de Grado", "La función de carga debe tener al menos grado 1.")
            return

        try:
            threshold = float(self.entry_threshold.get().strip())
        except ValueError:
            messagebox.showerror("Error de Formato", "El umbral de CPU debe ser un número (ej: 85.0).")
            return

        try:
            x0 = float(self.entry_x0.get().strip())
        except ValueError:
            messagebox.showerror("Error de Formato", "La hora inicial estimada t₀ debe ser un número real (ej: 9.0 hrs).")
            return

        try:
            tol = float(self.entry_tol.get().strip())
            if tol <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error de Formato", "La tolerancia debe ser un número positivo (ej: 0.0001).")
            return

        try:
            max_iter = int(self.entry_max_iter.get().strip())
            if max_iter <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error de Formato", "El número máximo de iteraciones debe ser un entero positivo.")
            return

        res = birge_vieta(
            coeffs=coeffs,
            x0=x0,
            threshold=threshold,
            tol=tol,
            max_iter=max_iter,
            error_type="relativo"
        )

        if not res.get("success", False) and len(res.get("iterations", [])) == 0:
            messagebox.showwarning("Atención en el Cálculo", res.get("message", "No fue posible iniciar el cálculo."))
            return

        self.on_solve_callback(res)
