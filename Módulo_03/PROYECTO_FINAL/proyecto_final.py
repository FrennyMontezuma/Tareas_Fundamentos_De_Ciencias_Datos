import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd

try:
    import matplotlib
    """se guardan los graficos en disco y tambien se muestran en pantalla"""
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False

"""
ESTADO GLOBAL DEL PROGRAMA
"""
class EstadoApp:
    """Guarda el estado del programa durante la ejecucion."""

    def __init__(self):
        """DataFrame original tal como se carga"""
        self.df = None
        """DataFrame despues de la limpieza"""
        self.df_limpio = None
        self.ruta_archivo = None
        """registros ingresados manualmente"""
        self.registros_nuevos = []
        self.carpeta_graficos = "graficos_salida"

    def datos_cargados(self):
        return self.df is not None

    def datos_listos_para_analisis(self):
        return self.df_limpio is not None


ESTADO = EstadoApp()
COLUMNAS_ESPERADAS = [
    "id_venta", "fecha", "producto", "categoria", "cantidad",
    "precio_unitario", "vendedor", "region", "metodo_pago", "cliente_frecuente",
]


"""
UTILIDADES DE PANTALLA / ENTRADA DE DATOS
"""
def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def pausar():
    input("\nPresione ENTER para continuar...")


def imprimir_titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def leer_opcion_menu(mensaje, opciones_validas):
    """Solicita una opcion de menu y valida que sea una de las opciones validas.
    Maneja entradas con formato incorrecto (no numericas) sin detener el programa."""
    while True:
        try:
            entrada = input(mensaje).strip()
            if entrada in opciones_validas:
                return entrada
            print(f"Opcion invalida. Elija una de las siguientes: {', '.join(opciones_validas)}")
        except (KeyboardInterrupt, EOFError):
            print("\nEntrada interrumpida.")
            return None


def leer_entero(mensaje, minimo=None, maximo=None, permitir_vacio=False):
    """Solicita un numero entero al usuario, validando el formato."""
    while True:
        valor = input(mensaje).strip()
        if permitir_vacio and valor == "":
            return None
        try:
            numero = int(valor)
            if minimo is not None and numero < minimo:
                print(f"El valor debe ser mayor o igual a {minimo}.")
                continue
            if maximo is not None and numero > maximo:
                print(f"El valor debe ser menor o igual a {maximo}.")
                continue
            return numero
        except ValueError:
            print("Formato incorrecto: debe ingresar un numero entero. Intente de nuevo.")


def leer_decimal(mensaje, minimo=None, permitir_vacio=False):
    """Solicita un numero decimal al usuario, validando el formato."""
    while True:
        valor = input(mensaje).strip()
        if permitir_vacio and valor == "":
            return None
        try:
            numero = float(valor)
            if minimo is not None and numero < minimo:
                print(f"El valor debe ser mayor o igual a {minimo}.")
                continue
            return numero
        except ValueError:
            print("Formato incorrecto: debe ingresar un numero (use punto decimal). Intente de nuevo.")


def leer_texto(mensaje, permitir_vacio=False):
    while True:
        valor = input(mensaje).strip()
        if valor or permitir_vacio:
            return valor
        print("Este campo no puede quedar vacio.")


def leer_fecha(mensaje):
    """Solicita una fecha en formato AAAA-MM-DD y valida que sea correcta."""
    while True:
        valor = input(mensaje).strip()
        try:
            return datetime.strptime(valor, "%Y-%m-%d").date()
        except ValueError:
            print("Formato de fecha incorrecto. Use AAAA-MM-DD, por ejemplo 2025-08-23.")


"""
1. CARGA DE ARCHIVO CSV
"""
def cargar_archivo_csv():
    imprimir_titulo("1. CARGAR ARCHIVO CSV")
    ruta = input(
        "Ingrese la ruta del archivo CSV "
        "(ENTER para usar 'ventas_tienda_tecnologia_ampliado.csv'): "
    ).strip()
    if ruta == "":
        ruta = "ventas_tienda_tecnologia_ampliado.csv"

    if not os.path.exists(ruta):
        print(f"\nERROR: el archivo '{ruta}' no existe o la ruta es incorrecta.")
        print("Verifique el nombre del archivo e intentelo nuevamente.")
        pausar()
        return

    try:
        df = pd.read_csv(ruta)
    except Exception as error:
        """Manejo de archivos que no se pueden cargar correctamente"""
        print(f"\nERROR: no fue posible leer el archivo. Detalle: {error}")
        pausar()
        return

    faltantes = [c for c in COLUMNAS_ESPERADAS if c not in df.columns]
    if faltantes:
        print(f"\nADVERTENCIA: el archivo no contiene las columnas esperadas: {faltantes}")
        print("El programa continuara, pero algunos analisis podrian no estar disponibles.")

    ESTADO.df = df
    ESTADO.df_limpio = None
    ESTADO.ruta_archivo = ruta
    print(f"\nArchivo cargado correctamente: {ruta}")
    print(f"Filas: {df.shape[0]}  |  Columnas: {df.shape[1]}")
    pausar()


def requiere_datos_cargados():
    if not ESTADO.datos_cargados():
        print("\nATENCION: primero debe cargar un archivo CSV (opcion 1 del menu principal).")
        pausar()
        return False
    return True


"""
2. INFORMACION GENERAL DEL CONJUNTO DE DATOS
"""
def mostrar_informacion_dataset():
    imprimir_titulo("2. INFORMACION DEL CONJUNTO DE DATOS")
    if not requiere_datos_cargados():
        return
    df = ESTADO.df
    print(f"Numero de filas   : {df.shape[0]}")
    print(f"Numero de columnas: {df.shape[1]}")
    print("\nNombres de columnas:")
    for col in df.columns:
        print(f"  - {col}")
    print("\nResumen (info):")
    df.info()
    pausar()


"""
3. PRIMERAS Y ULTIMAS FILAS
"""
def mostrar_primeras_ultimas_filas():
    imprimir_titulo("3. PRIMERAS Y ULTIMAS FILAS")
    if not requiere_datos_cargados():
        return
    n = leer_entero("Cuantas filas desea ver al inicio y al final (ej. 5): ", minimo=1, maximo=len(ESTADO.df))
    print(f"\n--- Primeras {n} filas ---")
    print(ESTADO.df.head(n).to_string())
    print(f"\n--- Ultimas {n} filas ---")
    print(ESTADO.df.tail(n).to_string())
    pausar()


"""
4. TIPOS DE DATOS
"""
def analizar_tipos_datos():
    imprimir_titulo("4. TIPOS DE DATOS POR COLUMNA")
    if not requiere_datos_cargados():
        return
    print(ESTADO.df.dtypes)
    pausar()


"""
5. VALORES NULOS
"""
def analizar_valores_nulos():
    imprimir_titulo("5. VALORES NULOS / FALTANTES")
    if not requiere_datos_cargados():
        return
    df = ESTADO.df
    nulos = df.isnull().sum()
    porcentaje = (nulos / len(df) * 100).round(2)
    resumen = pd.DataFrame({"nulos": nulos, "porcentaje_%": porcentaje})
    resumen = resumen[resumen["nulos"] > 0]
    if resumen.empty:
        print("No se encontraron valores nulos en el conjunto de datos.")
    else:
        print(resumen.to_string())
    pausar()


"""
6. DATOS DUPLICADOS
"""
def analizar_duplicados():
    imprimir_titulo("6. DATOS DUPLICADOS")
    if not requiere_datos_cargados():
        return
    df = ESTADO.df
    filas_duplicadas = df.duplicated().sum()
    print(f"Filas totalmente duplicadas: {filas_duplicadas}")
    if "id_venta" in df.columns:
        ids_duplicados = df["id_venta"].duplicated().sum()
        print(f"Valores repetidos en id_venta: {ids_duplicados}")
    pausar()


"""
LIMPIEZA DE DATOS (funcion de apoyo, usada por varias opciones del menu)
"""
def limpiar_datos():
    """Aplica el proceso de limpieza descrito en el informe y guarda el
    resultado en ESTADO.df_limpio. Se puede volver a ejecutar en cualquier
    momento sobre los datos originales cargados."""
    df = ESTADO.df.copy()

    antes = len(df)
    df = df.drop_duplicates()
    duplicados_eliminados = antes - len(df)

    for col in ["categoria", "producto", "region", "vendedor", "metodo_pago"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    if "cliente_frecuente" in df.columns:
        def normalizar_si_no(valor):
            v = str(valor).strip().lower()
            if v in ("si", "sí"):
                return "Sí"
            if v == "no":
                return "No"
            return np.nan
        df["cliente_frecuente"] = df["cliente_frecuente"].apply(normalizar_si_no)

    if "fecha" in df.columns:
        def parsear_fecha(valor):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return pd.to_datetime(valor, format=fmt)
                except (ValueError, TypeError):
                    continue
            return pd.NaT
        df["fecha"] = df["fecha"].apply(parsear_fecha)

    cantidades_negativas = 0
    if "cantidad" in df.columns:
        cantidades_negativas = int((df["cantidad"] < 0).sum())
        df["cantidad"] = df["cantidad"].abs()

    if "precio_unitario" in df.columns and "producto" in df.columns:
        df["precio_unitario"] = df.groupby("producto")["precio_unitario"].transform(
            lambda s: s.fillna(s.median())
        )
        df["precio_unitario"] = df["precio_unitario"].fillna(df["precio_unitario"].median())

    if "region" in df.columns:
        df["region"] = df["region"].replace("nan", np.nan)
        df["region"] = df["region"].fillna("No especificada")

    if "cantidad" in df.columns and "precio_unitario" in df.columns:
        df["venta_total"] = df["cantidad"] * df["precio_unitario"]

    ESTADO.df_limpio = df
    return duplicados_eliminados, cantidades_negativas


"""
7. ESTADISTICAS DESCRIPTIVAS
"""
def mostrar_estadisticas_descriptivas():
    imprimir_titulo("7. ESTADISTICAS DESCRIPTIVAS")
    if not requiere_datos_cargados():
        return
    if ESTADO.df_limpio is None:
        print("Aplicando limpieza de datos antes de calcular estadisticas...")
        limpiar_datos()
    df = ESTADO.df_limpio
    numericas = [c for c in ["cantidad", "precio_unitario", "venta_total"] if c in df.columns]
    print(df[numericas].describe().round(2).to_string())
    pausar()


"""
8. FILTRAR O CONSULTAR DATOS
"""
def filtrar_consultar_datos():
    imprimir_titulo("8. FILTRAR / CONSULTAR DATOS")
    if not requiere_datos_cargados():
        return
    if ESTADO.df_limpio is None:
        print("Aplicando limpieza de datos antes de filtrar...")
        limpiar_datos()
    df = ESTADO.df_limpio

    print("Opciones de filtro disponibles:")
    print("  1. Filtrar por categoria")
    print("  2. Filtrar por region")
    print("  3. Filtrar ventas mayores a un monto")
    print("  0. Cancelar")
    opcion = leer_opcion_menu("Seleccione una opcion: ", {"0", "1", "2", "3"})

    if opcion == "0" or opcion is None:
        return
    elif opcion == "1":
        print("Categorias disponibles:", ", ".join(sorted(df["categoria"].unique())))
        valor = leer_texto("Ingrese la categoria a filtrar: ")
        resultado = df[df["categoria"].str.lower() == valor.lower()]
    elif opcion == "2":
        print("Regiones disponibles:", ", ".join(sorted(df["region"].unique())))
        valor = leer_texto("Ingrese la region a filtrar: ")
        resultado = df[df["region"].str.lower() == valor.lower()]
    elif opcion == "3":
        monto = leer_decimal("Ingrese el monto minimo de venta_total: ", minimo=0)
        resultado = df[df["venta_total"] > monto]

    print(f"\nSe encontraron {len(resultado)} registros que cumplen el filtro.")
    if len(resultado) > 0:
        print(resultado.head(15).to_string())
        if len(resultado) > 15:
            print(f"... ({len(resultado) - 15} filas adicionales no mostradas)")
    pausar()


"""
9. AGRUPACIONES Y OPERACIONES
"""
def agrupaciones_y_operaciones():
    imprimir_titulo("9. AGRUPACIONES Y OPERACIONES")
    if not requiere_datos_cargados():
        return
    if ESTADO.df_limpio is None:
        print("Aplicando limpieza de datos antes de agrupar...")
        limpiar_datos()
    df = ESTADO.df_limpio

    print("Opciones de agrupacion disponibles:")
    print("  1. Monto total vendido por categoria")
    print("  2. Monto total vendido por region")
    print("  3. Monto total vendido por vendedor (top 10)")
    print("  4. Numero de transacciones por metodo de pago")
    print("  5. Venta promedio segun cliente frecuente (Si/No)")
    print("  0. Cancelar")
    opcion = leer_opcion_menu("Seleccione una opcion: ", {"0", "1", "2", "3", "4", "5"})

    if opcion == "0" or opcion is None:
        return
    elif opcion == "1":
        resultado = df.groupby("categoria")["venta_total"].agg(["sum", "mean", "count"]).sort_values("sum", ascending=False)
    elif opcion == "2":
        resultado = df.groupby("region")["venta_total"].sum().sort_values(ascending=False)
    elif opcion == "3":
        resultado = df.groupby("vendedor")["venta_total"].sum().sort_values(ascending=False).head(10)
    elif opcion == "4":
        resultado = df.groupby("metodo_pago")["venta_total"].agg(["sum", "count"])
    elif opcion == "5":
        resultado = df.groupby("cliente_frecuente")["venta_total"].agg(["sum", "mean", "count"])

    print()
    print(resultado.round(2).to_string())
    pausar()


"""
10. REPRESENTACIONES GRAFICAS
"""
def generar_graficos():
    imprimir_titulo("10. REPRESENTACIONES GRAFICAS")
    if not requiere_datos_cargados():
        return
    if not MATPLOTLIB_OK:
        print("La libreria matplotlib no esta instalada. Instalela con: pip install matplotlib")
        pausar()
        return
    if ESTADO.df_limpio is None:
        print("Aplicando limpieza de datos antes de graficar...")
        limpiar_datos()
    df = ESTADO.df_limpio

    os.makedirs(ESTADO.carpeta_graficos, exist_ok=True)

    print("Opciones de graficos disponibles:")
    print("  1. Barras: monto total vendido por categoria")
    print("  2. Circular (pie): distribucion de ventas por region")
    print("  3. Caja (boxplot): precio unitario por categoria")
    print("  4. Linea: evolucion mensual del monto vendido")
    print("  5. Generar todos los graficos anteriores")
    print("  0. Cancelar")
    opcion = leer_opcion_menu("Seleccione una opcion: ", {"0", "1", "2", "3", "4", "5"})

    if opcion == "0" or opcion is None:
        return

    def money_fmt(x, pos):
        return f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K"

    def grafico_barras_categoria():
        datos = df.groupby("categoria")["venta_total"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8, 5))
        datos.plot(kind="bar", ax=ax, color="#4C72B0")
        ax.set_title("Monto total vendido por categoria")
        ax.set_ylabel("Venta total (CRC)")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        ruta = os.path.join(ESTADO.carpeta_graficos, "ventas_por_categoria.png")
        plt.savefig(ruta)
        plt.show()
        plt.close()
        print(f"Grafico guardado en: {ruta}")

    def grafico_pie_region():
        datos = df.groupby("region")["venta_total"].sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(7, 7))
        datos.plot(kind="pie", ax=ax, autopct="%1.1f%%", ylabel="")
        ax.set_title("Distribucion del monto vendido por region")
        plt.tight_layout()
        ruta = os.path.join(ESTADO.carpeta_graficos, "ventas_por_region.png")
        plt.savefig(ruta)
        plt.show()
        plt.close()
        print(f"Grafico guardado en: {ruta}")

    def grafico_boxplot_precio():
        fig, ax = plt.subplots(figsize=(8, 5))
        df.boxplot(column="precio_unitario", by="categoria", ax=ax, rot=30)
        ax.set_title("Distribucion del precio unitario por categoria")
        ax.set_ylabel("Precio unitario (CRC)")
        plt.suptitle("")
        plt.tight_layout()
        ruta = os.path.join(ESTADO.carpeta_graficos, "boxplot_precio_categoria.png")
        plt.savefig(ruta)
        plt.show()
        plt.close()
        print(f"Grafico guardado en: {ruta}")

    def grafico_linea_mensual():
        temp = df.copy()
        temp["mes"] = temp["fecha"].dt.to_period("M").astype(str)
        datos = temp.groupby("mes")["venta_total"].sum()
        fig, ax = plt.subplots(figsize=(9, 5))
        datos.plot(kind="line", marker="o", ax=ax, color="#DD8452")
        ax.set_title("Evolucion del monto vendido por mes")
        ax.set_ylabel("Venta total (CRC)")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(money_fmt))
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        ruta = os.path.join(ESTADO.carpeta_graficos, "ventas_por_mes.png")
        plt.savefig(ruta)
        plt.show()
        plt.close()
        print(f"Grafico guardado en: {ruta}")

    acciones = {
        "1": grafico_barras_categoria,
        "2": grafico_pie_region,
        "3": grafico_boxplot_precio,
        "4": grafico_linea_mensual,
    }

    try:
        if opcion == "5":
            for accion in acciones.values():
                accion()
        else:
            acciones[opcion]()
    except Exception as error:
        print(f"No fue posible generar el grafico. Detalle: {error}")

    pausar()


"""
11. ANALISIS ADICIONAL (relacion entre variables)
"""
def analisis_adicional():
    imprimir_titulo("11. ANALISIS ADICIONAL - RELACION ENTRE VARIABLES")
    if not requiere_datos_cargados():
        return
    if ESTADO.df_limpio is None:
        print("Aplicando limpieza de datos antes de analizar...")
        limpiar_datos()
    df = ESTADO.df_limpio

    numericas = [c for c in ["cantidad", "precio_unitario", "venta_total"] if c in df.columns]
    print("Matriz de correlacion entre variables numericas:")
    print(df[numericas].corr().round(3).to_string())

    print("\nTop 10 productos por unidades vendidas:")
    print(df.groupby("producto")["cantidad"].sum().sort_values(ascending=False).head(10).to_string())
    pausar()


"""
12. SUBMENU - INGRESO DE NUEVOS DATOS
"""
def submenu_ingreso_datos():
    while True:
        imprimir_titulo("12. SUBMENU - INGRESO DE DATOS")
        print("1. Ingresar un nuevo registro")
        print("2. Mostrar registros ingresados")
        print("3. Guardar los nuevos datos")
        print("4. Regresar al menu principal")
        print("5. Readme (informacion de la estructura del proyecto)")

        opcion = leer_opcion_menu("Seleccione una opcion: ", {"1", "2", "3", "4", "5"})
        if opcion is None or opcion == "4":
            break
        elif opcion == "1":
            ingresar_nuevo_registro()
        elif opcion == "2":
            mostrar_registros_ingresados()
        elif opcion == "3":
            guardar_nuevos_datos()
        elif opcion == "5":
            mostrar_readme()


def ingresar_nuevo_registro():
    imprimir_titulo("INGRESAR NUEVO REGISTRO")
    print("Complete la informacion del nuevo registro de venta.")
    print("(Debe respetar el mismo formato utilizado en el archivo CSV)\n")

    try:
        id_venta = leer_entero("id_venta (numero entero): ", minimo=0)
        fecha = leer_fecha("fecha (AAAA-MM-DD): ")
        producto = leer_texto("producto: ")
        categoria = leer_texto("categoria: ")
        cantidad = leer_entero("cantidad (entero positivo): ", minimo=1)
        precio_unitario = leer_decimal("precio_unitario (CRC): ", minimo=0)
        vendedor = leer_texto("vendedor: ")
        region = leer_texto("region: ")
        metodo_pago = leer_texto("metodo_pago: ")
        cliente_frecuente = leer_opcion_menu(
            "cliente_frecuente (Si/No) -> escriba 'Si' o 'No': ", {"Si", "No", "si", "no"}
        )
    except (KeyboardInterrupt, EOFError):
        print("\nIngreso cancelado.")
        return

    registro = {
        "id_venta": id_venta,
        "fecha": fecha.strftime("%Y-%m-%d"),
        "producto": producto,
        "categoria": categoria,
        "cantidad": cantidad,
        "precio_unitario": precio_unitario,
        "vendedor": vendedor,
        "region": region,
        "metodo_pago": metodo_pago,
        "cliente_frecuente": "Sí" if cliente_frecuente.lower() == "si" else "No",
    }
    ESTADO.registros_nuevos.append(registro)
    print("\nRegistro ingresado correctamente.")
    pausar()


def mostrar_registros_ingresados():
    imprimir_titulo("REGISTROS INGRESADOS MANUALMENTE")
    if not ESTADO.registros_nuevos:
        print("Aun no se ha ingresado ningun registro nuevo.")
    else:
        df_nuevos = pd.DataFrame(ESTADO.registros_nuevos)
        print(df_nuevos.to_string())
    pausar()


def guardar_nuevos_datos():
    imprimir_titulo("GUARDAR NUEVOS DATOS")
    if not ESTADO.registros_nuevos:
        print("No hay registros nuevos para guardar.")
        pausar()
        return

    nombre_archivo = input(
        "Nombre del archivo de salida (ENTER para 'nuevos_registros.csv'): "
    ).strip()
    if nombre_archivo == "":
        nombre_archivo = "nuevos_registros.csv"

    try:
        df_nuevos = pd.DataFrame(ESTADO.registros_nuevos)
        df_nuevos.to_csv(nombre_archivo, index=False)
        print(f"\nSe guardaron {len(df_nuevos)} registros en '{nombre_archivo}'.")

        if ESTADO.df is not None:
            respuesta = leer_opcion_menu(
                "Desea incorporar estos registros al conjunto de datos cargado en memoria? (S/N): ",
                {"S", "N", "s", "n"},
            )
            if respuesta and respuesta.lower() == "s":
                ESTADO.df = pd.concat([ESTADO.df, df_nuevos], ignore_index=True)
                """se debera volver a limpiar"""
                ESTADO.df_limpio = None
                print("Registros incorporados al conjunto de datos en memoria.")
    except Exception as error:
        print(f"ERROR al guardar el archivo: {error}")
    pausar()


def mostrar_readme():
    imprimir_titulo("README - ESTRUCTURA DEL PROYECTO")
    texto = """
Este programa forma parte del Proyecto Final del modulo de Manejo de Datos - EDA.

Estructura de columnas esperada en el archivo CSV:
  id_venta, fecha, producto, categoria, cantidad, precio_unitario,
  vendedor, region, metodo_pago, cliente_frecuente

Flujo de trabajo sugerido:
  1) Cargar archivo CSV (opcion 1)
  2) Explorar la informacion, tipos de datos, nulos y duplicados (opciones 2 a 6)
  3) Consultar estadisticas descriptivas (opcion 7) -> aplica limpieza automaticamente
  4) Filtrar, agrupar y graficar (opciones 8, 9 y 10)
  5) Ingresar nuevos registros desde el submenu (opcion 12) si se requiere
  6) Salir del programa (opcion 13)

Los nuevos registros ingresados manualmente pueden guardarse en un archivo CSV
independiente y, opcionalmente, incorporarse al conjunto de datos en memoria.
"""
    print(texto)
    pausar()


"""
MENU PRINCIPAL
"""
def mostrar_menu_principal():
    limpiar_pantalla()
    print("=" * 70)
    print("   PROYECTO FINAL - MANEJO DE DATOS (EDA)")
    print("   Ventas de una tienda de tecnologia")
    print("=" * 70)
    estado_texto = "Cargado" if ESTADO.datos_cargados() else "No cargado"
    print(f"   Archivo actual: {ESTADO.ruta_archivo or '-'}   [{estado_texto}]")
    print("-" * 70)
    print(" 1. Cargar archivo CSV")
    print(" 2. Mostrar informacion del conjunto de datos")
    print(" 3. Mostrar primeras y ultimas filas")
    print(" 4. Analizar tipos de datos")
    print(" 5. Analizar valores nulos")
    print(" 6. Analizar datos duplicados")
    print(" 7. Obtener estadisticas descriptivas")
    print(" 8. Filtrar o consultar datos")
    print(" 9. Realizar agrupaciones y operaciones")
    print("10. Generar representaciones graficas")
    print("11. Realizar analisis adicional (relacion entre variables)")
    print("12. Ingresar nuevos datos (submenu)")
    print("13. Salir")
    print("=" * 70)


def main():
    opciones_validas = {str(n) for n in range(1, 14)}
    acciones = {
        "1": cargar_archivo_csv,
        "2": mostrar_informacion_dataset,
        "3": mostrar_primeras_ultimas_filas,
        "4": analizar_tipos_datos,
        "5": analizar_valores_nulos,
        "6": analizar_duplicados,
        "7": mostrar_estadisticas_descriptivas,
        "8": filtrar_consultar_datos,
        "9": agrupaciones_y_operaciones,
        "10": generar_graficos,
        "11": analisis_adicional,
        "12": submenu_ingreso_datos,
    }

    while True:
        mostrar_menu_principal()
        opcion = leer_opcion_menu("Seleccione una opcion (1-13): ", opciones_validas)

        if opcion is None:
            print("\nSaliendo del programa...")
            break
        if opcion == "13":
            print("\nGracias por utilizar el programa. Hasta pronto!")
            break

        accion = acciones.get(opcion)
        if accion:
            try:
                accion()
            except Exception as error:
                """Manejo general de errores para que el programa nunca se caiga"""
                print(f"\nOcurrio un error inesperado: {error}")
                pausar()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario. Hasta pronto!")
        sys.exit(0)
