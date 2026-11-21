"""Vista de entrada de datos para Gauss-Seidel (balance de carga de servidores, Ax = b)."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any, List

from methods.gauss_seidel import gauss_seidel
import numpy as np


class GaussSeidelView(ttk.Frame):
    def __init__(self, parent, on_solve_callback: Callable[[Dict[str, Any]], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.on_solve_callback = on_solve_callback
        self.matrix_entries = []
        self.vector_entries = []
        self.x0_entries = []
        self.current_dim = 3
        self._setup_ui()

    def _setup_ui(self):
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # selector del tamaño n
        top_bar = ttk.Frame(container)
        top_bar.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(top_bar, text="Número de servidores / ecuaciones (n):", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        self.spin_dim = ttk.Spinbox(top_bar, from_=2, to=6, width=4, font=("Consolas", 9), command=self._on_dim_changed)
        self.spin_dim.set(3)
        self.spin_dim.pack(side=tk.LEFT, padx=(0, 20))
        self.spin_dim.bind("<Return>", lambda e: self._on_dim_changed())

        # checkbox de pivoteo
        self.var_autopivot = tk.BooleanVar(value=True)
        chk_pivot = ttk.Checkbutton(
            top_bar,
            text="Reordenar ecuaciones para optimizar la diagonal principal",
            variable=self.var_autopivot
        )
        chk_pivot.pack(side=tk.LEFT)

        # parámetros
        grid_params = ttk.Frame(container)
        grid_params.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(grid_params, text="Tolerancia de error (ε):", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        self.entry_tol = ttk.Entry(grid_params, width=12, font=("Consolas", 9))
        self.entry_tol.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=2)
        self.entry_tol.insert(0, "0.0001")

        ttk.Label(grid_params, text="Máximo de iteraciones:", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky=tk.W, padx=(0, 8), pady=2)
        self.entry_max_iter = ttk.Entry(grid_params, width=8, font=("Consolas", 9))
        self.entry_max_iter.grid(row=0, column=3, sticky=tk.W, padx=(0, 20), pady=2)
        self.entry_max_iter.insert(0, "50")

        ttk.Label(grid_params, text="Factor de aceleración (ω = 1.0 estándar):", font=("Segoe UI", 9, "bold")).grid(row=0, column=4, sticky=tk.W, padx=(0, 8), pady=2)
        self.entry_omega = ttk.Entry(grid_params, width=8, font=("Consolas", 9))
        self.entry_omega.grid(row=0, column=5, sticky=tk.W, pady=2)
        self.entry_omega.insert(0, "1.0")

        # cuadrícula de la matriz
        self.grid_container = ttk.Frame(container)
        self.grid_container.pack(fill=tk.BOTH, expand=True, pady=4)

        # botones de ejemplos
        btn_box = ttk.Frame(container)
        btn_box.pack(fill=tk.X, pady=(6, 2))

        btn_ex1 = ttk.Button(btn_box, text="💡 Caso 1 (Balance Cluster Escolar 3 Servidores)", command=self.load_example_1)
        btn_ex1.pack(side=tk.LEFT, padx=(0, 8))

        btn_ex2 = ttk.Button(btn_box, text="💡 Caso 2 (Cluster 4 Servidores)", command=self.load_example_2)
        btn_ex2.pack(side=tk.LEFT, padx=(0, 8))

        btn_clear = ttk.Button(btn_box, text="🗑 Limpiar Matriz", command=self.clear_matrix)
        btn_clear.pack(side=tk.LEFT)

        # matriz inicial
        self._rebuild_matrix_grid(3)
        self.load_example_1()

    def _on_dim_changed(self):
        try:
            val = int(self.spin_dim.get())
            if 2 <= val <= 6 and val != self.current_dim:
                self.current_dim = val
                self._rebuild_matrix_grid(val)
        except Exception:
            pass

    def _rebuild_matrix_grid(self, n: int):
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        self.matrix_entries = []
        self.vector_entries = []
        self.x0_entries = []

        ttk.Label(self.grid_container, text="Servidor / Ecuación", font=("Segoe UI", 9, "bold"), foreground="#64748b").grid(row=0, column=0, padx=6, pady=2)
        for j in range(n):
            ttk.Label(
                self.grid_container,
                text=f"Servidor {j+1} (x_{j+1})",
                font=("Segoe UI", 9, "bold"),
                foreground="#1e3a8a"
            ).grid(row=0, column=j + 1, padx=4, pady=2)

        ttk.Label(self.grid_container, text="=", font=("Segoe UI", 10, "bold"), foreground="#64748b").grid(row=0, column=n + 1, padx=4)
        ttk.Label(self.grid_container, text="Demanda Total % (b)", font=("Segoe UI", 9, "bold"), foreground="#166534").grid(row=0, column=n + 2, padx=4, pady=2)
        ttk.Label(self.grid_container, text="x₀ Inicial", font=("Segoe UI", 8, "bold"), foreground="#64748b").grid(row=0, column=n + 3, padx=4, pady=2)

        for i in range(n):
            ttk.Label(
                self.grid_container,
                text=f"Nodo {i+1}:",
                font=("Segoe UI", 9, "bold"),
                foreground="#334155"
            ).grid(row=i + 1, column=0, padx=6, pady=3)

            row_entries = []
            for j in range(n):
                e = ttk.Entry(self.grid_container, width=8, font=("Consolas", 9), justify=tk.RIGHT)
                e.grid(row=i + 1, column=j + 1, padx=3, pady=3)
                e.insert(0, "1.0" if i == j else "0.0")
                row_entries.append(e)
            self.matrix_entries.append(row_entries)

            ttk.Label(self.grid_container, text="=", font=("Segoe UI", 10, "bold"), foreground="#64748b").grid(row=i + 1, column=n + 1, padx=2)

            eb = ttk.Entry(self.grid_container, width=8, font=("Consolas", 9), justify=tk.RIGHT)
            eb.grid(row=i + 1, column=n + 2, padx=3, pady=3)
            eb.insert(0, "0.0")
            self.vector_entries.append(eb)

            ex0 = ttk.Entry(self.grid_container, width=7, font=("Consolas", 8), justify=tk.RIGHT)
            ex0.grid(row=i + 1, column=n + 3, padx=3, pady=3)
            ex0.insert(0, "0.0")
            self.x0_entries.append(ex0)

    def load_example_1(self):
        # ejemplo de 3 servidores (web, bd, archivos):
        # 10x1 - x2 + 2x3 = 60
        # -x1 + 11x2 - x3 = 85
        # 2x1 - x2 + 10x3 = 45
        if self.current_dim != 3:
            self.current_dim = 3
            self.spin_dim.set(3)
            self._rebuild_matrix_grid(3)

        A_data = [
            [10.0, -1.0, 2.0],
            [-1.0, 11.0, -1.0],
            [2.0, -1.0, 10.0]
        ]
        b_data = [60.0, 85.0, 45.0]

        for i in range(3):
            for j in range(3):
                self.matrix_entries[i][j].delete(0, tk.END)
                self.matrix_entries[i][j].insert(0, str(A_data[i][j]))
            self.vector_entries[i].delete(0, tk.END)
            self.vector_entries[i].insert(0, str(b_data[i]))
            self.x0_entries[i].delete(0, tk.END)
            self.x0_entries[i].insert(0, "0.0")

        self.entry_tol.delete(0, tk.END)
        self.entry_tol.insert(0, "0.0001")
        self.entry_max_iter.delete(0, tk.END)
        self.entry_max_iter.insert(0, "50")
        self.entry_omega.delete(0, tk.END)
        self.entry_omega.insert(0, "1.0")

    def load_example_2(self):
        # ejemplo de 4 servidores:
        self.current_dim = 4
        self.spin_dim.set(4)
        self._rebuild_matrix_grid(4)

        A_data = [
            [10.0, -2.0, -1.0, -1.0],
            [-2.0, 10.0, -1.0, -1.0],
            [-1.0, -1.0, 10.0, -2.0],
            [-1.0, -1.0, -2.0, 10.0]
        ]
        b_data = [40.0, 65.0, 80.0, 30.0]

        for i in range(4):
            for j in range(4):
                self.matrix_entries[i][j].delete(0, tk.END)
                self.matrix_entries[i][j].insert(0, str(A_data[i][j]))
            self.vector_entries[i].delete(0, tk.END)
            self.vector_entries[i].insert(0, str(b_data[i]))
            self.x0_entries[i].delete(0, tk.END)
            self.x0_entries[i].insert(0, "0.0")

    def clear_matrix(self):
        n = self.current_dim
        for i in range(n):
            for j in range(n):
                self.matrix_entries[i][j].delete(0, tk.END)
                self.matrix_entries[i][j].insert(0, "0.0")
            self.vector_entries[i].delete(0, tk.END)
            self.vector_entries[i].insert(0, "0.0")
            self.x0_entries[i].delete(0, tk.END)
            self.x0_entries[i].insert(0, "0.0")

    def solve(self):
        """Lee A y b y corre Gauss-Seidel."""
        n = self.current_dim
        A = []
        b = []
        x0 = []

        try:
            for i in range(n):
                row = []
                for j in range(n):
                    val = float(self.matrix_entries[i][j].get().strip())
                    row.append(val)
                A.append(row)
                b.append(float(self.vector_entries[i].get().strip()))
                x0_str = self.x0_entries[i].get().strip()
                x0.append(float(x0_str) if x0_str else 0.0)
        except ValueError:
            messagebox.showerror("Error de Formato", "Todos los valores de las ecuaciones deben ser números reales válidos.")
            return

        try:
            tol = float(self.entry_tol.get().strip())
            if tol <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error de Formato", "La tolerancia de error debe ser un número positivo (ej: 0.0001).")
            return

        try:
            max_iter = int(self.entry_max_iter.get().strip())
            if max_iter <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error de Formato", "El número máximo de iteraciones debe ser un entero positivo.")
            return

        try:
            omega = float(self.entry_omega.get().strip())
        except ValueError:
            messagebox.showerror("Error de Formato", "El factor de aceleración ω debe ser un número real (ej: 1.0).")
            return

        auto_pivot = self.var_autopivot.get()

        res = gauss_seidel(
            A_matrix=A,
            b_vector=b,
            x0=x0,
            tol=tol,
            max_iter=max_iter,
            omega=omega,
            error_type="relativo",
            auto_pivot=auto_pivot
        )

        if not res.get("success", False) and len(res.get("iterations", [])) <= 1:
            messagebox.showwarning("Atención en el Cálculo", res.get("message", "No fue posible resolver el sistema."))
            return

        self.on_solve_callback(res)
