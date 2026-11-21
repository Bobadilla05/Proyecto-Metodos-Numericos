"""
Punto de entrada de la calculadora de métodos numéricos.

Métodos: Birge-Vieta, Bisección, Gauss-Seidel e interpolación de Newton.
Se ejecuta con: python main.py
"""

import sys
import os

# para que encuentre gui y methods
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from gui.app import NumericalMethodsApp


def main():
    try:
        app = NumericalMethodsApp()
        app.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
