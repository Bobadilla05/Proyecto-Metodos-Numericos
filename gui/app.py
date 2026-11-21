"""
Ventana principal de la calculadora.
Tema: carga de CPU de un servidor escolar a lo largo del día y la hora en que
pasa el umbral (85%). Métodos: Birge-Vieta, Bisección y Gauss-Seidel.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any

from gui.components.table_view import ResultTableView
from gui.views.birge_vieta_view import BirgeVietaView
from gui.views.bisection_view import BisectionView
from gui.views.gauss_seidel_view import GaussSeidelView


class NumericalMethodsApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # dpi alto en windows
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self.title("Estimación de Carga de Servidor — Plataforma Escolar | Métodos Numéricos")
        self.geometry("1140x900")
        self.minsize(980, 720)

        # estilos
        self._setup_styles()

        # método seleccionado
        self.selected_method = tk.StringVar(value="birge_vieta")
        self.last_result = None
        self.procedure_visible = False

        # armo la interfaz
        self._setup_layout()

    def _setup_styles(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # colores
        bg_main = "#f8fafc"
        card_bg = "#ffffff"
        primary = "#1d4ed8"
        text_dark = "#0f172a"

        self.configure(bg=bg_main)

        self.style.configure(".", background=bg_main, foreground=text_dark, font=("Segoe UI", 9))
        self.style.configure("TFrame", background=bg_main)
        self.style.configure("Card.TFrame", background=card_bg, relief="flat")
        self.style.configure("TLabelframe", background=card_bg, relief="solid", borderwidth=1)
        self.style.configure(
            "TLabelframe.Label",
            background=card_bg,
            foreground="#1e3a8a",
            font=("Segoe UI", 10, "bold")
        )

        # botón principal
        self.style.configure(
            "Primary.TButton",
            background=primary,
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 9)
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", "#1e40af"), ("pressed", "#172554")],
            foreground=[("active", "#ffffff")]
        )

        # botón del procedimiento
        self.style.configure(
            "Procedure.TButton",
            font=("Segoe UI", 9, "bold"),
            padding=(14, 6)
        )

        # botones secundarios
        self.style.configure(
            "TButton",
            font=("Segoe UI", 9),
            padding=(8, 4)
        )

        # tabla
        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#e2e8f0",
            foreground="#1e293b",
            padding=(6, 4)
        )
        self.style.configure("Treeview", rowheight=24, font=("Consolas", 9))

    def _setup_layout(self):
        # encabezado
        header_frame = tk.Frame(self, bg="#1e293b", height=82)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(
            header_frame,
            text="ESTIMACIÓN Y MONITOREO DE CARGA DE UN SERVIDOR",
            font=("Segoe UI", 13, "bold"),
            fg="#f8fafc",
            bg="#1e293b"
        )
        title_lbl.pack(anchor=tk.W, padx=25, pady=(8, 2))

        sub_lbl = tk.Label(
            header_frame,
            text="Plataforma Escolar: Análisis de uso de CPU y cálculo de la hora crítica de saturación (Umbral: 85%).",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        )
        sub_lbl.pack(anchor=tk.W, padx=25)

        sub_ctx = tk.Label(
            header_frame,
            text="Determina el polinomio de carga C(t) y calcula a qué hora del día el servidor alcanza el umbral de degradación.",
            font=("Segoe UI", 8, "italic"),
            fg="#94a3b8",
            bg="#1e293b"
        )
        sub_ctx.pack(anchor=tk.W, padx=25)

        # barra de estado
        self.status_bar = tk.Frame(self, bg="#e2e8f0", height=24)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        self.lbl_footer = tk.Label(
            self.status_bar,
            text="Listo | Ingresa los datos de carga del servidor y selecciona un método de resolución.",
            font=("Segoe UI", 8),
            fg="#475569",
            bg="#e2e8f0"
        )
        self.lbl_footer.pack(side=tk.LEFT, padx=15)

        # contenedor con scroll
        main_container = tk.Frame(self, bg="#f8fafc")
        main_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(main_container, bg="#f8fafc", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_content = tk.Frame(self.canvas, bg="#f8fafc")

        self.scroll_window = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")

        self.scroll_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.scroll_window, width=e.width)
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind_all(
            "<MouseWheel>",
            self._on_mousewheel
        )

        # datos de entrada
        self.input_card = ttk.LabelFrame(
            self.scroll_content,
            text="  1. Apartado para Ingresar los Datos del Servidor  ",
            padding=12
        )
        self.input_card.pack(fill=tk.X, padx=20, pady=(15, 10))

        # aquí cambia la vista según el método
        self.views_container = ttk.Frame(self.input_card)
        self.views_container.pack(fill=tk.BOTH, expand=True)

        self.views = {
            "birge_vieta": BirgeVietaView(self.views_container, on_solve_callback=self.handle_results),
            "bisection": BisectionView(self.views_container, on_solve_callback=self.handle_results),
            "gauss_seidel": GaussSeidelView(self.views_container, on_solve_callback=self.handle_results)
        }

        self.current_view = self.views["birge_vieta"]
        self.current_view.pack(fill=tk.BOTH, expand=True)

        # elegir método
        self.methods_card = ttk.LabelFrame(
            self.scroll_content,
            text="  2. Opciones para Elegir Cómo Resolverlo  ",
            padding=12
        )
        self.methods_card.pack(fill=tk.X, padx=20, pady=(0, 15))

        lbl_options_title = ttk.Label(
            self.methods_card,
            text="Selecciona el método numérico para analizar la carga del servidor escolar:",
            font=("Segoe UI", 9, "bold"),
            foreground="#334155"
        )
        lbl_options_title.pack(anchor=tk.W, pady=(0, 8))

        # opciones de método
        options_box = tk.Frame(self.methods_card, bg="#ffffff")
        options_box.pack(fill=tk.X, pady=(0, 12))

        methods_info = [
            (
                "birge_vieta",
                "Opción 1: Método de Birge-Vieta (Horner + Newton-Raphson)",
                "Calcula la hora crítica exacta resolviendo C(t) - 85% = 0 con alta velocidad, aplicando 1° Método de Horner (evaluación de carga) y 2° Método de Newton-Raphson."
            ),
            (
                "bisection",
                "Opción 2: Método de Bisección",
                "Determina la hora crítica en un intervalo horario [a, b] (ej. 8:00 a 12:00 hrs) dividiendo sucesivamente el intervalo donde la carga pasa de nivel normal a saturación."
            ),
            (
                "gauss_seidel",
                "Opción 3: Método de Gauss-Seidel",
                "Resuelve el sistema de ecuaciones lineales para modelar la carga o el balance de tráfico entre los servidores del cluster escolar (Ax = b)."
            )
        ]

        self.radio_widgets = []
        for val, title, desc in methods_info:
            opt_frame = tk.Frame(
                options_box,
                bg="#f8fafc",
                bd=1,
                relief="solid",
                padx=10,
                pady=8
            )
            opt_frame.pack(fill=tk.X, pady=3)

            rb = tk.Radiobutton(
                opt_frame,
                text=f" {title}",
                value=val,
                variable=self.selected_method,
                command=self._on_method_selected,
                font=("Segoe UI", 10, "bold"),
                bg="#f8fafc",
                activebackground="#f8fafc",
                fg="#1e3a8a",
                cursor="hand2"
            )
            rb.pack(anchor=tk.W)
            self.radio_widgets.append((rb, opt_frame))

            lbl_desc = tk.Label(
                opt_frame,
                text=f"      {desc}",
                font=("Segoe UI", 8, "italic"),
                fg="#475569",
                bg="#f8fafc",
                justify=tk.LEFT
            )
            lbl_desc.pack(anchor=tk.W)

        # botón resolver
        solve_bar = ttk.Frame(self.methods_card)
        solve_bar.pack(fill=tk.X, pady=(6, 2))

        self.btn_solve_master = ttk.Button(
            solve_bar,
            text="▶  RESOLVER Y ESTIMAR CARGA DEL SERVIDOR CON EL MÉTODO SELECCIONADO",
            style="Primary.TButton",
            command=self._execute_solve
        )
        self.btn_solve_master.pack(fill=tk.X)

        # resultados
        self.result_section = ttk.LabelFrame(
            self.scroll_content,
            text="  3. Resolución del Problema (Estimación de Carga)  ",
            padding=14
        )
        # oculto hasta que se resuelva

        # mensaje de estado
        self.lbl_result_status = tk.Label(
            self.result_section,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#059669",
            anchor=tk.W
        )
        self.lbl_result_status.pack(fill=tk.X, pady=(0, 6))

        # cuadro de la solución
        self.solution_box = tk.Frame(
            self.result_section,
            bg="#f0fdf4",
            bd=1,
            relief="solid",
            padx=14,
            pady=10
        )
        self.solution_box.pack(fill=tk.X, pady=(0, 10))

        self.lbl_solution_title = tk.Label(
            self.solution_box,
            text="RESULTADO DEL ANÁLISIS DE CARGA DEL SERVIDOR:",
            font=("Segoe UI", 9, "bold"),
            bg="#f0fdf4",
            fg="#166534"
        )
        self.lbl_solution_title.pack(anchor=tk.W)

        self.lbl_solution_highlight = tk.Label(
            self.solution_box,
            text="",
            font=("Consolas", 11, "bold"),
            bg="#f0fdf4",
            fg="#15803d",
            justify=tk.LEFT,
            wraplength=1000
        )
        self.lbl_solution_highlight.pack(anchor=tk.W, pady=(4, 0))

        # cuadro de la comprobación
        self.verification_box = tk.Frame(
            self.result_section,
            bg="#f0f9ff",
            bd=1,
            relief="solid",
            padx=14,
            pady=10
        )
        self.verification_box.pack(fill=tk.X, pady=(0, 12))

        self.lbl_verification_title = tk.Label(
            self.verification_box,
            text="🔍 COMPROBACIÓN: SUSTITUCIÓN DE LA HORA EN LA FUNCIÓN DE CARGA C(t)",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f9ff",
            fg="#0369a1"
        )
        self.lbl_verification_title.pack(anchor=tk.W)

        self.lbl_verification_content = tk.Label(
            self.verification_box,
            text="",
            font=("Consolas", 9),
            bg="#f0f9ff",
            fg="#0c4a6e",
            justify=tk.LEFT,
            wraplength=1000
        )
        self.lbl_verification_content.pack(anchor=tk.W, pady=(4, 2))

        self.lbl_verification_verdict = tk.Label(
            self.verification_box,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f9ff",
            fg="#0284c7",
            justify=tk.LEFT
        )
        self.lbl_verification_verdict.pack(anchor=tk.W, pady=(2, 0))

        # barra del procedimiento
        proc_option_bar = tk.Frame(self.result_section, bg="#ffffff")
        proc_option_bar.pack(fill=tk.X, pady=(4, 8))

        self.lbl_proc_prompt = tk.Label(
            proc_option_bar,
            text="¿Deseas consultar el procedimiento matemático detallado que se llevó a cabo?",
            font=("Segoe UI", 9, "bold"),
            fg="#334155",
            bg="#ffffff"
        )
        self.lbl_proc_prompt.pack(side=tk.LEFT, padx=(0, 12))

        self.btn_toggle_procedure = ttk.Button(
            proc_option_bar,
            text="📋 Mostrar Procedimiento que se Llevó a Cabo  ▼",
            style="Procedure.TButton",
            command=self.toggle_procedure_view
        )
        self.btn_toggle_procedure.pack(side=tk.LEFT)

        # procedimiento desplegable
        self.procedure_container = tk.Frame(self.result_section, bg="#ffffff")

        # explicación del método
        self.lbl_proc_summary = tk.Label(
            self.procedure_container,
            text="",
            font=("Consolas", 9),
            bg="#f8fafc",
            fg="#1e293b",
            justify=tk.LEFT,
            relief="solid",
            bd=1,
            padx=12,
            pady=8
        )
        self.lbl_proc_summary.pack(fill=tk.X, pady=(0, 10))

        # tabla de iteraciones
        lbl_tbl_title = tk.Label(
            self.procedure_container,
            text="Tabla Paso a Paso de las Iteraciones:",
            font=("Segoe UI", 10, "bold"),
            fg="#1e3a8a",
            bg="#ffffff"
        )
        lbl_tbl_title.pack(anchor=tk.W, pady=(4, 4))

        self.table_frame = tk.Frame(self.procedure_container, height=230)
        self.table_frame.pack(fill=tk.X, pady=(0, 12))
        self.table_frame.pack_propagate(False)

        self.result_table = ResultTableView(self.table_frame)
        self.result_table.pack(fill=tk.BOTH, expand=True)

        # desglose con scroll
        lbl_detail_title = tk.Label(
            self.procedure_container,
            text="Desglose Matemático Detallado Paso a Paso:",
            font=("Segoe UI", 10, "bold"),
            fg="#1e3a8a",
            bg="#ffffff"
        )
        lbl_detail_title.pack(anchor=tk.W, pady=(4, 4))

        proc_text_frame = tk.Frame(self.procedure_container, bg="#ffffff", bd=1, relief="solid")
        proc_text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        self.txt_proc_scroll = ttk.Scrollbar(proc_text_frame, orient=tk.VERTICAL)
        self.txt_procedure_detail = tk.Text(
            proc_text_frame,
            height=16,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#f8fafc",
            relief="flat",
            padx=14,
            pady=12,
            yscrollcommand=self.txt_proc_scroll.set
        )
        self.txt_proc_scroll.config(command=self.txt_procedure_detail.yview)

        self.txt_procedure_detail.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.txt_proc_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_mousewheel(self, event):
        widget_under_mouse = self.winfo_containing(event.x_root, event.y_root)
        if widget_under_mouse != self.txt_procedure_detail:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_method_selected(self):
        method_key = self.selected_method.get()

        if self.current_view:
            self.current_view.pack_forget()

        self.current_view = self.views[method_key]
        self.current_view.pack(fill=tk.BOTH, expand=True)

        names = {
            "birge_vieta": "Método de Birge-Vieta activo (Horner + Newton-Raphson para hora crítica)",
            "bisection": "Método de Bisección activo (Búsqueda de hora crítica en intervalo [a, b])",
            "gauss_seidel": "Método de Gauss-Seidel activo (Sistemas y balance de servidores del cluster)"
        }
        self.lbl_footer.config(text=f"Modo Activo: {names.get(method_key, '')}")

        self._hide_result_section()

    def _execute_solve(self):
        if self.current_view:
            self.current_view.solve()

    def _hide_result_section(self):
        self.result_section.pack_forget()
        self.procedure_container.pack_forget()
        self.procedure_visible = False
        self.btn_toggle_procedure.config(text="📋 Mostrar Procedimiento que se Llevó a Cabo  ▼")

    def handle_results(self, result: Dict[str, Any]):
        """Muestra resultados, comprobación y procedimiento."""
        self.last_result = result
        method_name = result.get("method_name", "")

        self.result_section.pack(fill=tk.X, padx=20, pady=(0, 20))

        if result.get("success", False):
            self.lbl_result_status.config(
                text=f"✔ {result.get('message', 'Análisis completado exitosamente.')}",
                fg="#059669"
            )
            self.solution_box.config(bg="#f0fdf4")
            self.lbl_solution_title.config(bg="#f0fdf4", fg="#166534")
            self.lbl_solution_highlight.config(bg="#f0fdf4", fg="#15803d")
        else:
            self.lbl_result_status.config(
                text=f"⚠ {result.get('message', 'Atención en el cálculo.')}",
                fg="#dc2626"
            )
            self.solution_box.config(bg="#fef2f2")
            self.lbl_solution_title.config(bg="#fef2f2", fg="#991b1b")
            self.lbl_solution_highlight.config(bg="#fef2f2", fg="#b91c1c")

        if "Birge-Vieta" in method_name:
            self._display_birge_vieta_solution(result)
        elif "Bisección" in method_name:
            self._display_bisection_solution(result)
        elif "Gauss-Seidel" in method_name:
            self._display_gauss_seidel_solution(result)

        self.scroll_content.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0.55)

    def _display_birge_vieta_solution(self, result: Dict[str, Any]):
        root = result.get("root")
        clock_time = result.get("clock_time", f"{root:.4f} hrs")
        final_cpu = result.get("final_cpu", 85.0)
        iters_count = len(result.get("iterations", []))
        poly_str = result.get("poly_str", "")
        thresh = result.get("threshold", 85.0)

        # resumen de la solución
        text_hl = (
            f"• HORA CRÍTICA DETECTADA:        t ≈ {clock_time}\n"
            f"• Porcentaje de Uso de CPU:      C({root:.4f}) = {final_cpu:.2f}%  (Umbral Crítico: {thresh:.1f}%)\n"
            f"• Pasos requeridos para converger: {iters_count} iteraciones\n"
            f"• Modelo de Carga del Servidor:  C(t) = {poly_str}"
        )
        self.lbl_solution_highlight.config(text=text_hl)

        # comprobación
        v = result.get("verification", {})
        verif_text = (
            f"{v.get('polynomial_formula', '')}\n"
            f"Sustituyendo t = {root:.4f} hrs:\n"
            f"  {v.get('substitution_step', '')}\n"
            f"  {v.get('evaluation_step', '')}"
        )
        self.lbl_verification_content.config(text=verif_text)
        self.lbl_verification_verdict.config(text=v.get("message", ""))

        # resumen del procedimiento
        summary_text = (
            "========================================================================================\n"
            "PROCEDIMIENTO DEL MÉTODO DE BIRGE-VIETA (Estimación de Carga de Servidor Escolar)\n"
            "Calcula la hora crítica t* resolviendo P(t) = C(t) - 85% = 0 mediante dos pasos:\n"
            "  1. MÉTODO DE HORNER (Doble división sintética):\n"
            "     • 1ª división sintética: Evalúa el exceso de carga P(tₖ), obteniendo b₀ = P(tₖ).\n"
            "     • 2ª división sintética: Evalúa la tasa de incremento de carga P'(tₖ), obteniendo c₁ = P'(tₖ).\n"
            "  2. MÉTODO DE NEWTON-RAPHSON (Actualización horaria):\n"
            "     • Aplica la fórmula: tₖ₊₁ = tₖ - [ P(tₖ) / P'(tₖ) ] = tₖ - [ b₀ / c₁ ]\n"
            "     • Calcula el error relativo porcentual hasta satisfacer la tolerancia permitida.\n"
            "========================================================================================"
        )
        self.lbl_proc_summary.config(text=summary_text)

        # columnas de la tabla
        columns = [
            {"id": "iter", "text": "Iteración (k)", "width": 95},
            {"id": "x_k", "text": "Aproximación tₖ (hrs)", "width": 140},
            {"id": "p_x", "text": "Exceso P(tₖ) [b₀]", "width": 145},
            {"id": "p_prime", "text": "Tasa P'(tₖ) [c₁]", "width": 145},
            {"id": "x_next", "text": "Siguiente tₖ₊₁ (hrs)", "width": 155},
            {"id": "error", "text": "Error Relativo (%)", "width": 135}
        ]
        self.result_table.set_columns(columns)

        # filas
        rows = []
        detail_lines = []
        for it in result.get("iterations", []):
            err_val = it["error_rel"]
            rows.append([
                it["iter"],
                it["x_k"],
                it["p_x"],
                it["p_prime_x"],
                it["x_next"],
                err_val
            ])

            h = it["horner_details"]
            nw = it["newton_details"]
            detail_lines.append(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"ITERACIÓN {it['iter']}  (Hora actual evaluada: t_{it['iter']-1} = {it['x_k']:.4f} hrs)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"1. PASO: MÉTODO DE HORNER (Doble división sintética)\n"
                f"   • Coeficientes de P(t) = C(t) - {thresh}%: {h['a_coeffs']}\n"
                f"   • 1ª división sintética:  b = {h['b_coeffs']}\n"
                f"     --> Residuo b₀: Exceso sobre el umbral P(t_{it['iter']-1}) = {h['b0']:.4f} % CPU\n"
                f"   • 2ª división sintética:  c = {h['c_coeffs']}\n"
                f"     --> Residuo c₁: Tasa de cambio de carga P'(t_{it['iter']-1}) = {h['c1']:.4f} %/hr\n\n"
                f"2. PASO: MÉTODO DE NEWTON-RAPHSON (Actualización de hora)\n"
                f"   • Fórmula:       t_{it['iter']} = t_{it['iter']-1} - [ b₀ / c₁ ]\n"
                f"   • Sustitución:   {nw['substitution']}\n"
                f"   • Nueva hora:    t_{it['iter']} = {nw['result']:.4f} hrs\n"
                f"   • Error porcentual en este paso: {err_val:.6f} %\n\n"
            )

        self.result_table.populate(rows, highlight_last=True)

        self.txt_procedure_detail.config(state=tk.NORMAL)
        self.txt_procedure_detail.delete("1.0", tk.END)
        self.txt_procedure_detail.insert("1.0", "".join(detail_lines))
        self.txt_procedure_detail.config(state=tk.DISABLED)

    def _display_bisection_solution(self, result: Dict[str, Any]):
        root = result.get("root")
        clock_time = result.get("clock_time", f"{root:.4f} hrs")
        final_cpu = result.get("final_cpu", 85.0)
        iters_count = len(result.get("iterations", []))
        thresh = result.get("threshold", 85.0)
        a_init = result.get("a_init", 8.0)
        b_init = result.get("b_init", 12.0)

        # resumen de la solución
        text_hl = (
            f"• HORA CRÍTICA ESTIMADA:        t ≈ {clock_time}\n"
            f"• Uso de CPU en esa hora:       C({root:.4f}) = {final_cpu:.2f}%  (Umbral Crítico: {thresh:.1f}%)\n"
            f"• Intervalo Horario Analizado:  [{a_init:.1f} hrs, {b_init:.1f} hrs]\n"
            f"• Iteraciones de Bisección:     {iters_count} divisiones de intervalo"
        )
        self.lbl_solution_highlight.config(text=text_hl)

        # comprobación
        v = result.get("verification", {})
        verif_text = (
            f"Sustituyendo t = {root:.4f} hrs en el modelo de carga C(t):\n"
            f"  {v.get('substitution_step', '')}\n"
            f"  {v.get('evaluation_step', '')}"
        )
        self.lbl_verification_content.config(text=verif_text)
        self.lbl_verification_verdict.config(text=v.get("message", ""))

        # resumen del procedimiento
        summary_text = (
            "========================================================================================\n"
            "PROCEDIMIENTO DEL MÉTODO DE BISECCIÓN (Estimación de Carga de Servidor Escolar)\n"
            "  1. Se verifica el Teorema de Bolzano en el intervalo horario inicial [a, b]:\n"
            "     P(a) = C(a) - 85% < 0  y  P(b) = C(b) - 85% > 0  (cambio de signo comprobado).\n"
            "  2. En cada iteración k se calcula el punto medio: mₖ = (aₖ + bₖ) / 2.\n"
            "  3. Se evalúa el signo del producto P(aₖ)·P(mₖ):\n"
            "     • Si P(aₖ)·P(mₖ) < 0: La hora crítica está en la primera mitad [aₖ, mₖ] -> bₖ₊₁ = mₖ.\n"
            "     • Si P(aₖ)·P(mₖ) > 0: La hora crítica está en la segunda mitad [mₖ, bₖ] -> aₖ₊₁ = mₖ.\n"
            "  4. El intervalo se reduce a la mitad en cada paso hasta satisfacer la tolerancia.\n"
            "========================================================================================"
        )
        self.lbl_proc_summary.config(text=summary_text)

        # columnas de la tabla
        columns = [
            {"id": "iter", "text": "Iteración (k)", "width": 95},
            {"id": "a", "text": "Hora Inicial aₖ", "width": 120},
            {"id": "b", "text": "Hora Final bₖ", "width": 120},
            {"id": "m", "text": "Punto Medio mₖ", "width": 130},
            {"id": "fa", "text": "P(aₖ) [%]", "width": 115},
            {"id": "fm", "text": "P(mₖ) [%]", "width": 115},
            {"id": "sign", "text": "Signo P(a)·P(m)", "width": 150},
            {"id": "error", "text": "Error Relativo (%)", "width": 135}
        ]
        self.result_table.set_columns(columns)

        # filas
        rows = []
        detail_lines = []
        for it in result.get("iterations", []):
            rows.append([
                it["iter"],
                it["a"],
                it["b"],
                it["m"],
                it["f_a"],
                it["f_m"],
                it["sign_str"].split("(")[0].strip(),
                it["error_rel"]
            ])

            detail_lines.append(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"ITERACIÓN {it['iter']}: Intervalo [{it['a']:.4f} hrs, {it['b']:.4f} hrs]\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  • Punto Medio Horario:  m_{it['iter']} = ({it['a']:.4f} + {it['b']:.4f}) / 2 = {it['m']:.4f} hrs\n"
                f"  • Carga de CPU estimada: C(m_{it['iter']}) = {it['cpu_usage']:.2f} %\n"
                f"  • Exceso sobre 85%:      P(m_{it['iter']}) = {it['f_m']:+.4f} %\n"
                f"  • Condición de Bolzano:  P(a)={it['f_a']:+.4f}% | P(m)={it['f_m']:+.4f}%  -->  {it['sign_str']}\n"
                f"  • Decisión:              {it['decision']}\n"
                f"  • Error estimado:        {it['error_rel']:.6f} %\n\n"
            )

        self.result_table.populate(rows, highlight_last=True)

        self.txt_procedure_detail.config(state=tk.NORMAL)
        self.txt_procedure_detail.delete("1.0", tk.END)
        self.txt_procedure_detail.insert("1.0", "".join(detail_lines))
        self.txt_procedure_detail.config(state=tk.DISABLED)

    def _display_gauss_seidel_solution(self, result: Dict[str, Any]):
        sol = result.get("solution", [])
        iters_count = len(result.get("iterations", [])) - 1
        sol_lines = [f"• Servidor {i+1} (x_{i+1}): {val:.2f}% de carga CPU" for i, val in enumerate(sol)]
        sol_formatted = "\n".join(sol_lines)
        is_dom = "Sí (Convergencia matemática garantizada)" if result.get("is_dominant") else "No estrictamente dominante (pero convergió)"

        # resumen de la solución
        text_hl = (
            f"Distribución de Carga del Cluster de Servidores Escolares:\n"
            f"{sol_formatted}\n"
            f"• Total de iteraciones realizadas: {iters_count}\n"
            f"• Dominancia diagonal del sistema:  {is_dom}"
        )
        self.lbl_solution_highlight.config(text=text_hl)

        # comprobación en cada ecuación
        v = result.get("verification", {})
        eq_lines = [eq.get("display_str", "") for eq in v.get("equations", [])]
        self.lbl_verification_content.config(text="\n".join(eq_lines))
        self.lbl_verification_verdict.config(text=v.get("message", ""))

        # resumen del procedimiento
        summary_text = (
            "========================================================================================\n"
            "PROCEDIMIENTO DEL MÉTODO DE GAUSS-SEIDEL (Balance de Servidores Escolares)\n"
            "  1. Verificación de dominancia diagonal (|a_ii| > sum_{j!=i} |a_ij|) en el cluster.\n"
            "  2. Despeje de la carga de cada servidor x_i en su ecuación correspondiente.\n"
            "  3. En cada iteración se sustituyen inmediatamente los valores actualizados de los servidores\n"
            "     anteriores, acelerando la convergencia del balance de carga.\n"
            "========================================================================================"
        )
        self.lbl_proc_summary.config(text=summary_text)

        # columnas de la tabla
        n = result.get("dim", len(sol))
        columns = [{"id": "iter", "text": "Iteración (k)", "width": 95}]
        for i in range(n):
            columns.append({"id": f"x{i+1}", "text": f"Servidor {i+1} (%)", "width": 130})
        columns.append({"id": "error", "text": "Error Máximo (%)", "width": 135})

        self.result_table.set_columns(columns)

        # filas
        rows = []
        detail_lines = []
        for it in result.get("iterations", []):
            row = [it["iter"]] + it["x"] + [it["error"] if it["iter"] > 0 else "-"]
            rows.append(row)

            if it["iter"] > 0:
                detail_lines.append(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"ITERACIÓN {it['iter']}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Cálculo de la carga de cada servidor sustituyendo valores actualizados:\n"
                )
                for s in it.get("steps_per_var", []):
                    detail_lines.append(f"  • {s['equation']}\n")
                detail_lines.append(f"  Diferencia máxima porcentual en esta iteración: {it['error']:.6f} %\n\n")

        self.result_table.populate(rows, highlight_last=True)

        self.txt_procedure_detail.config(state=tk.NORMAL)
        self.txt_procedure_detail.delete("1.0", tk.END)
        self.txt_procedure_detail.insert("1.0", "".join(detail_lines) if detail_lines else "Sin iteraciones adicionales.")
        self.txt_procedure_detail.config(state=tk.DISABLED)

    def toggle_procedure_view(self):
        """Muestra u oculta el procedimiento detallado."""
        if not self.procedure_visible:
            self.procedure_container.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
            self.btn_toggle_procedure.config(text="📋 Ocultar Procedimiento que se Llevó a Cabo  ▲")
            self.procedure_visible = True
        else:
            self.procedure_container.pack_forget()
            self.btn_toggle_procedure.config(text="📋 Mostrar Procedimiento que se Llevó a Cabo  ▼")
            self.procedure_visible = False

        self.scroll_content.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
