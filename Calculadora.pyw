"""Lanzador para abrir la calculadora con doble clic en Windows (pythonw, sin consola)."""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from gui.app import NumericalMethodsApp


def main():
    try:
        app = NumericalMethodsApp()
        app.mainloop()
    except Exception as e:
        import tkinter.messagebox as mb
        mb.showerror("Error de Ejecución", f"Ocurrió un error al iniciar la aplicación:\n{e}")


if __name__ == "__main__":
    main()
