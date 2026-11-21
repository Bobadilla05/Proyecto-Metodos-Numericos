"""Tabla de resultados (ttk.Treeview) con scroll, para las iteraciones."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any


class ResultTableView(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(self, selectmode="browse", show="headings")
        self.v_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        # colores de las filas
        self.tree.tag_configure("evenrow", background="#f8fafc")
        self.tree.tag_configure("oddrow", background="#ffffff")
        self.tree.tag_configure("highlight", background="#ecfdf5", foreground="#065f46")

        self.current_columns = []

    def set_columns(self, columns: List[Dict[str, Any]]):
        """
        Define las columnas.
        columns es una lista de dicts con 'id', 'text', 'width' y opcional 'anchor'.
        """
        self.clear()
        col_ids = [c["id"] for c in columns]
        self.current_columns = columns
        self.tree["columns"] = col_ids

        for col in columns:
            self.tree.heading(col["id"], text=col["text"], anchor=col.get("anchor", tk.CENTER))
            self.tree.column(
                col["id"],
                width=col.get("width", 110),
                minwidth=col.get("minwidth", 70),
                anchor=col.get("anchor", tk.CENTER)
            )

    def populate(self, rows: List[List[Any]], highlight_last: bool = False):
        """Llena la tabla con las filas."""
        self.clear_rows()
        for i, row in enumerate(rows):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            if highlight_last and i == len(rows) - 1:
                tag = "highlight"

            formatted_vals = []
            for val in row:
                if isinstance(val, float):
                    if abs(val) < 1e-4 and abs(val) > 1e-15:
                        formatted_vals.append(f"{val:.5e}")
                    else:
                        formatted_vals.append(f"{val:.6f}")
                elif val is None:
                    formatted_vals.append("-")
                else:
                    formatted_vals.append(str(val))

            self.tree.insert("", tk.END, values=formatted_vals, tags=(tag,))

    def clear_rows(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear(self):
        self.clear_rows()
        self.tree["columns"] = []
        self.current_columns = []
