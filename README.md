# Calculadora de Métodos Numéricos

Aplicación de escritorio moderna y educativa desarrollada en **Python** con interfaz gráfica (**Tkinter** + **NumPy**) diseñada para resolver problemáticas numéricas mediante tres métodos fundamentales de análisis numérico, con terminología clara para estudiantes y matemáticos:

1. **Método de Birge-Vieta**:
   - Aplica secuencialmente dos métodos matemáticos fundamentales:
     - **1° Método de Horner (Doble división sintética):** Evalúa el polinomio $P(x_k) = b_0$ y su primera derivada $P'(x_k) = c_1$.
     - **2° Método de Newton-Raphson:** Actualiza la aproximación de la raíz mediante la fórmula:
       $$x_{k+1} = x_k - \frac{P(x_k)}{P'(x_k)} = x_k - \frac{b_0}{c_1}$$
     - **Comprobación directa:** Sustituye la raíz calculada $x^*$ en el polinomio original $P(x)$ demostrando que $P(x^*) \approx 0$.
2. **Método de Gauss-Seidel**:
   - Resolución iterativa de sistemas de ecuaciones lineales $A\mathbf{x} = \mathbf{b}$, con verificación rigurosa de dominancia diagonal, opción de reordenamiento de ecuaciones y comprobación sustituyendo la solución en cada una de las ecuaciones originales.
3. **Método del Polinomio de Interpolación de Newton**:
   - Construcción del polinomio interpolante único mediante tabla de diferencias divididas, formulación en factores de Newton, simplificación algebraica a forma canónica ($P(x) = a_n x^n + \dots + a_0$), estimación en un punto $x^*$ y comprobación sustituyendo todos los puntos conocidos dados.

---

## 🚀 Ejecución sin Terminal ni Archivos `.bat`

Para garantizar una experiencia limpia y profesional (ideal para repositorios de GitHub), la aplicación **no requiere ejecutarse desde la terminal ni hacer doble clic en archivos `.bat`**:

### Opción 1: Ejecutable Autónomo para Windows (.exe con PyInstaller)
El proyecto incluye el ejecutable compilado con **PyInstaller** en modo de ventana (`--noconsole` / `--windowed`):
- Ubicación: `dist/CalculadoraMetodosNumericos.exe`
- **Solo haz doble clic** sobre `CalculadoraMetodosNumericos.exe` para abrir directamente la calculadora sin que se abra ninguna consola o terminal.

> **¿Deseas recompilar el ejecutable?**
> Puedes generar una nueva compilación en cualquier momento ejecutando:
> ```bash
> python build_exe.py
> ```

### Opción 2: Ejecución Directa en Python sin Consola (`.pyw`)
En sistemas Windows con Python instalado, haz **doble clic en `Calculadora.pyw`**:
- La extensión `.pyw` está asociada automáticamente con `pythonw.exe`, ejecutando la interfaz gráfica de forma nativa sin abrir ninguna ventana de terminal.

---

## 🎨 Diseño y Flujo de la Interfaz Gráfica

La interfaz está organizada bajo una arquitectura vertical intuitiva y centrada en el proceso de resolución matemática:

```text
┌────────────────────────────────────────────────────────────────────────┐
│               CALCULADORA DE MÉTODOS NUMÉRICOS                         │
└────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  📥 1. APARTADO PARA INGRESAR LOS DATOS                                │
│  - Campos con lenguaje claro para estudiantes                          │
│  - Ejemplos precargados listos para probar con un clic                 │
│  - Margen de error permitido (ε) y máximo de iteraciones               │
└────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  ⚙ 2. OPCIONES PARA ELEGIR CÓMO RESOLVERLO                             │
│  ( ) Opción 1: Método de Birge-Vieta (1° Horner  ➔  2° Newton-Raphson) │
│  ( ) Opción 2: Método de Gauss-Seidel (Sistemas lineales Ax = b)       │
│  ( ) Opción 3: Polinomio de Interpolación de Newton                    │
│                                                                        │
│  [ ▶ RESOLVER PROBLEMA CON EL MÉTODO SELECCIONADO ]                    │
└────────────────────────────────────────────────────────────────────────┘
                                 │
                    (Aparece una vez resuelto)
                                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│  🎯 3. RESOLUCIÓN DEL PROBLEMA                                         │
│  - Solución encontrada (raíz, valores de incógnitas o polinomio)       │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 🔍 COMPROBACIÓN: SUSTITUCIÓN EN LA ECUACIÓN PRINCIPAL            │  │
│  │ Sustituye los valores obtenidos en la función/ecuación original  │  │
│  │ para verificar que se cumple la igualdad matemáticamente.        │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  [ 📋 Mostrar Procedimiento que se Llevó a Cabo ▼ ] (Botón interactivo)│
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ AL ACTIVAR "MOSTRAR PROCEDIMIENTO":                              │  │
│  │ • Fundamento metodológico aplicado paso a paso                   │  │
│  │ • Tabla matemática con encabezados formales (xₖ, Horner, Newton) │  │
│  │ • Desglose Amplio con su propia barra de desplazamiento vertical │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🧮 Tabla y Desglose Matemático

### Encabezados Matemáticos en Birge-Vieta:
La tabla iterativa de Birge-Vieta utiliza encabezados claros y rigurosos:
- **`Iteración (k)`**: Número del paso actual.
- **`Aproximación xₖ`**: Valor actual en la iteración $k-1$.
- **`P(xₖ) [Horner: b₀]`**: Residuo de la 1ª división sintética de Horner evaluando $P(x_k)$.
- **`P'(xₖ) [Horner: c₁]`**: Residuo de la 2ª división sintética de Horner evaluando la derivada $P'(x_k)$.
- **`Siguiente xₖ₊₁ (Newton)`**: Nueva aproximación generada con $x_k - \frac{b_0}{c_1}$.
- **`Error Relativo (%)`**: Margen de error porcentual respecto al nuevo valor.

### Comprobación por Sustitución Directa:
- **En Birge-Vieta:** Se sustituye $x^*$ en cada término de $P(x)$, sumando los valores hasta comprobar $P(x^*) \approx 0$.
- **En Gauss-Seidel:** Se sustituyen los valores calculados de $x_1, x_2, \dots, x_n$ en el miembro izquierdo de cada ecuación para comparar contra el término independiente $b_i$.
- **En Newton:** Se sustituyen las abscisas de todos los puntos conocidos dados en el polinomio resultante para confirmar que $P(x_i) = y_i$.

---

## 📁 Estructura del Repositorio

```text
Proyecto-Calculadora De Métodos/
│
├── dist/                                  # Carpeta de distribución compilada
│   └── CalculadoraMetodosNumericos.exe    # Ejecutable autónomo para Windows (PyInstaller)
│
├── main.py                                # Punto de entrada estándar
├── Calculadora.pyw                        # Lanzador sin consola para Windows
├── build_exe.py                           # Script para compilar el ejecutable
├── requirements.txt                       # Dependencias mínimas (numpy, pyinstaller)
├── README.md                              # Documentación del proyecto
├── .gitignore                             # Filtro de archivos para GitHub
│
├── methods/                               # Módulos matemáticos y algoritmos
│   ├── birge_vieta.py                     # Método de Birge-Vieta (Horner + Newton-Raphson)
│   ├── gauss_seidel.py                    # Método de Gauss-Seidel y dominancia
│   └── newton_interpolation.py            # Polinomio de Newton y diferencias divididas
│
├── gui/                                   # Interfaz gráfica de usuario
│   ├── app.py                             # Ventana principal, layout vertical y comprobación
│   ├── components/                        # Componentes UI reutilizables
│   │   └── table_view.py                  # Tabla de iteraciones con ttk.Treeview
│   └── views/                             # Formularios de ingreso de datos para estudiantes
│       ├── birge_vieta_view.py            # Formulario de Birge-Vieta
│       ├── gauss_seidel_view.py           # Formulario de Gauss-Seidel
│       └── newton_view.py                 # Formulario de Interpolación de Newton
│
└── tests/                                 # Pruebas automatizadas
    ├── test_all_methods.py                # Tests matemáticos de los tres métodos
    └── test_gui.py                        # Tests de ciclo de vida e interfaz de usuario
```

---

## 🧪 Pruebas Automatizadas
Para verificar el correcto funcionamiento de toda la suite de métodos numéricos y la interfaz gráfica:
```bash
python -m unittest discover tests
```
Resultado:
```text
......
----------------------------------------------------------------------
Ran 6 tests in ~2.1s
OK
```
