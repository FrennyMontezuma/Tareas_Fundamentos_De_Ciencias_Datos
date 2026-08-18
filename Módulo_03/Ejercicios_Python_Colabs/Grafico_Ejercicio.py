import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Datos y cálculo de límites
lista_clientes = [f"C{i}" for i in range(1, 16)]
monto_compras = [45, 52, 38, 60, 48, 55, 42, 50, 58, 47, 5, 53, 310, 44, 49]
datos = pd.DataFrame({"Cliente": lista_clientes, "Monto": monto_compras})

q1_val = np.quantile(datos["Monto"], 0.25, method="linear")
q3_val = np.quantile(datos["Monto"], 0.75, method="linear")
iqr_val = q3_val - q1_val

lim_inf = q1_val - 1.5 * iqr_val
lim_sup = q3_val + 1.5 * iqr_val

# 2. Asignar color rojo a las barras que superan o bajan del límite
colores = [
    "#C0392B" if (m < lim_inf or m > lim_sup) else "#2980B9"
    for m in datos["Monto"]
]

# 3. Crear gráfico de barras
plt.figure(figsize=(9, 5))
plt.bar(
    datos["Cliente"],
    datos["Monto"],
    color=colores,
    edgecolor="black",
    alpha=0.85,
)

# Líneas límite
plt.axhline(
    lim_sup, color="red", linestyle="--", label=f"Lím. Superior ({lim_sup})"
)
plt.axhline(
    lim_inf, color="red", linestyle="--", label=f"Lím. Inferior ({lim_inf})"
)

plt.title("Monto de Compras por Cliente", fontsize=12, fontweight="bold")
plt.xlabel("Cliente")
plt.ylabel("Monto ($)")
plt.legend()
plt.tight_layout()
plt.show()