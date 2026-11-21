"""
Genera el .exe con PyInstaller.
Uso: python build_exe.py
"""

import os
import subprocess
import sys


def build():
    print("Iniciando compilación con PyInstaller...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_file = os.path.join(base_dir, "main.py")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=CalculadoraMetodosNumericos",
        "--onefile",
        "--windowed",
        "--noconsole",
        "--clean",
        main_file
    ]

    print(f"Ejecutando comando: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=base_dir)

    if result.returncode == 0:
        exe_path = os.path.join(base_dir, "dist", "CalculadoraMetodosNumericos.exe")
        print("\n" + "=" * 65)
        print("✔ COMPILACIÓN EXITOSA")
        print(f"Ejecutable generado en:\n  {exe_path}")
        print("=" * 65)
    else:
        print("\n❌ Ocurrió un error durante la compilación.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()
