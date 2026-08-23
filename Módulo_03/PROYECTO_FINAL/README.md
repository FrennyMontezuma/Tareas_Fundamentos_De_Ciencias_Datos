# README — Proyecto Final: Manejo de Datos (EDA)

**Archivo documentado:** `proyecto_final.py`
**Estudiante:** Frenny Montezuma Castillo
**Módulo:** Manejo de Datos – EDA
**Grupo:** Grupo 4

Este README explica **cómo está construido internamente** el programa `proyecto_final.py`: sus dependencias, su arquitectura, cada función que lo compone, el flujo de datos entre ellas y el manejo de errores implementado.

---

## 1. Propósito del programa

Aplicación de consola con **menú interactivo** que permite cargar el archivo `ventas_tienda_tecnologia_ampliado.csv`, explorarlo, limpiarlo, analizarlo, generar gráficos y registrar nuevos datos manualmente, cubriendo todas las herramientas de EDA vistas en el curso.

## 2. Requisitos y dependencias

| Librería | Uso dentro del programa |
|---|---|
| `os` | Limpiar pantalla, verificar existencia de archivos, crear carpetas |
| `sys` | Salida controlada del programa (`sys.exit`) |
| `datetime` | Validar y construir fechas ingresadas manualmente |
| `numpy` | Manejo de valores `NaN` durante la limpieza |
| `pandas` | Carga, limpieza, agrupación y análisis del CSV (motor principal) |
| `matplotlib` (opcional) | Generación de gráficos. Si no está instalada, el programa **no se detiene**: la opción 10 del menú lo informa y continúa funcionando |

Instalación:
```bash
pip install pandas numpy matplotlib
```

`matplotlib` se configura con el backend `"Agg"` porque el programa corre en consola (sin interfaz gráfica); los gráficos se **guardan como archivos `.png`** en lugar de mostrarse en pantalla.

---

## 3. Arquitectura general del código

El archivo se organiza en **6 bloques**, en este orden:

1. **Estado global** — clase `EstadoApp` y variable `ESTADO`.
2. **Utilidades de pantalla / entrada de datos** — funciones `leer_*`, `pausar`, `imprimir_titulo`.
3. **Funciones del menú principal** — una función por cada opción (1 a 11).
4. **Función de limpieza de datos** — `limpiar_datos()`, usada internamente por varias opciones.
5. **Submenú de ingreso de datos** — opción 12 y sus funciones auxiliares.
6. **Menú principal** — `mostrar_menu_principal()` y `main()`, el punto de entrada.

```
main()
 └─ mostrar_menu_principal()      (dibuja el menú)
 └─ leer_opcion_menu()            (valida la opción elegida)
 └─ diccionario "acciones"        (despacha la opción a su función)
      ├─ cargar_archivo_csv()
      ├─ mostrar_informacion_dataset()
      ├─ mostrar_primeras_ultimas_filas()
      ├─ analizar_tipos_datos()
      ├─ analizar_valores_nulos()
      ├─ analizar_duplicados()
      ├─ mostrar_estadisticas_descriptivas()  → limpiar_datos()
      ├─ filtrar_consultar_datos()            → limpiar_datos()
      ├─ agrupaciones_y_operaciones()         → limpiar_datos()
      ├─ generar_graficos()                   → limpiar_datos()
      ├─ analisis_adicional()                 → limpiar_datos()
      └─ submenu_ingreso_datos()
           ├─ ingresar_nuevo_registro()
           ├─ mostrar_registros_ingresados()
           ├─ guardar_nuevos_datos()
           └─ mostrar_readme()
```

---

## 4. Estado global — clase `EstadoApp`

El programa **no usa variables globales sueltas**; todo el estado vive dentro de una sola instancia (`ESTADO`) de la clase `EstadoApp`. Esto evita depender de `global` dentro de cada función y centraliza los datos que persisten entre opciones del menú.

| Atributo | Contenido |
|---|---|
| `self.df` | `DataFrame` con los datos **tal como se cargaron** del CSV (sin limpiar) |
| `self.df_limpio` | `DataFrame` **después de aplicar `limpiar_datos()`**. Se reinicia a `None` cada vez que se carga un archivo nuevo o se incorporan registros nuevos, para forzar una limpieza actualizada |
| `self.ruta_archivo` | Ruta del último archivo CSV cargado (se muestra en el encabezado del menú) |
| `self.registros_nuevos` | Lista de diccionarios con los registros ingresados manualmente en el submenú (opción 12) |
| `self.carpeta_graficos` | Nombre de la carpeta donde se guardan los `.png` generados (`"graficos_salida"`) |

Métodos:
- `datos_cargados()` → `True` si ya existe `self.df` (se usó para bloquear opciones que necesitan un CSV cargado).
- `datos_listos_para_analisis()` → `True` si ya existe `self.df_limpio` (no se usa de forma obligatoria, pero está disponible para extender el programa).

`COLUMNAS_ESPERADAS` es una lista a nivel de módulo con los 10 nombres de columna que debería tener el CSV; se usa en `cargar_archivo_csv()` para advertir si el archivo cargado no coincide con la estructura esperada.

---

## 5. Utilidades de pantalla y de entrada de datos

Estas funciones se reutilizan en **todo** el programa para no repetir lógica de validación.

### `limpiar_pantalla()`
Limpia la consola (`cls` en Windows, `clear` en Linux/Mac) antes de redibujar el menú principal.

### `pausar()`
Detiene la ejecución con `input("Presione ENTER...")` para que el usuario pueda leer el resultado antes de que la pantalla se limpie de nuevo.

### `imprimir_titulo(texto)`
Imprime un encabezado uniforme (línea de `=`, texto, línea de `=`) para cada sección del programa.

### `leer_opcion_menu(mensaje, opciones_validas)`
Pide al usuario una opción de menú (texto) y **repite la pregunta** hasta que el valor esté dentro del conjunto `opciones_validas`.
- Maneja `KeyboardInterrupt` y `EOFError` (por ejemplo, si la entrada estándar se cierra) devolviendo `None` en vez de lanzar una excepción — así el programa nunca se cae por una interrupción de teclado.

### `leer_entero(mensaje, minimo=None, maximo=None, permitir_vacio=False)`
Solicita un número entero:
- Reintenta si el texto no se puede convertir con `int()` (`ValueError`).
- Reintenta si el número está fuera del rango `[minimo, maximo]`.
- Si `permitir_vacio=True` y el usuario solo presiona ENTER, devuelve `None` (usado, por ejemplo, para campos opcionales).

### `leer_decimal(mensaje, minimo=None, permitir_vacio=False)`
Igual que `leer_entero`, pero para `float()` — se usa para `precio_unitario` y montos de filtro.

### `leer_texto(mensaje, permitir_vacio=False)`
Pide texto libre y no acepta cadenas vacías salvo que `permitir_vacio=True`.

### `leer_fecha(mensaje)`
Pide una fecha en formato `AAAA-MM-DD` y la valida con `datetime.strptime`. Si el formato es incorrecto, vuelve a pedirla en lugar de aceptar cualquier texto.

> Todas estas funciones de lectura son la base del **manejo de errores de formato** exigido por el proyecto: ninguna entrada incorrecta detiene el programa, siempre se vuelve a solicitar el dato.

---

## 6. Funciones del menú principal (opciones 1 a 11)

### Opción 1 — `cargar_archivo_csv()`
- Solicita la ruta del archivo (por defecto `ventas_tienda_tecnologia_ampliado.csv` si se presiona ENTER).
- Verifica con `os.path.exists()` que el archivo exista; si no, muestra un error y **no rompe el programa**.
- Intenta `pd.read_csv()` dentro de un `try/except` — si el archivo está corrupto o mal formado, se captura la excepción y se informa al usuario.
- Compara las columnas del archivo contra `COLUMNAS_ESPERADAS` y advierte (sin bloquear) si faltan columnas.
- Al cargar correctamente, actualiza `ESTADO.df`, reinicia `ESTADO.df_limpio` a `None` (para forzar una limpieza fresca) y guarda `ESTADO.ruta_archivo`.

### `requiere_datos_cargados()`
Función de apoyo usada al inicio de **todas** las demás opciones del menú (2 a 11). Si `ESTADO.df` es `None`, muestra un mensaje pidiendo cargar primero el CSV y devuelve `False`; cada función del menú revisa este valor antes de continuar. Así se cumple el requerimiento de "manejar el intento de analizar datos antes de cargar un archivo".

### Opción 2 — `mostrar_informacion_dataset()`
Muestra número de filas, número de columnas, listado de nombres de columna y el resumen `df.info()` (tipos de datos y conteo de no nulos por columna).

### Opción 3 — `mostrar_primeras_ultimas_filas()`
Pide un número `n` (validado con `leer_entero`, entre 1 y el total de filas) y muestra `head(n)` y `tail(n)` del DataFrame original.

### Opción 4 — `analizar_tipos_datos()`
Imprime `ESTADO.df.dtypes` (tipo de cada columna: entero, decimal o texto).

### Opción 5 — `analizar_valores_nulos()`
Calcula, por columna, la cantidad de nulos (`isnull().sum()`) y el porcentaje respecto al total de filas. Solo muestra las columnas que sí tienen nulos; si no hay ninguna, lo indica explícitamente.

### Opción 6 — `analizar_duplicados()`
Muestra:
- Cantidad de filas **totalmente** duplicadas (`df.duplicated().sum()`).
- Cantidad de valores repetidos en la columna `id_venta` (duplicados de identificador, aunque el resto de la fila sea distinto).

### `limpiar_datos()` — función central de limpieza
No aparece como opción de menú directa: se ejecuta **automáticamente** la primera vez que el usuario entra a una opción que necesita datos limpios (7, 8, 9, 10 u 11), y queda guardada en `ESTADO.df_limpio` para no repetir el proceso en cada llamada. Pasos que ejecuta, en orden:

1. **Elimina duplicados exactos** con `drop_duplicates()`.
2. **Normaliza texto** (`categoria`, `producto`, `region`, `vendedor`, `metodo_pago`): quita espacios en blanco y aplica formato *Title Case*, resolviendo variaciones como `"accesorios"`, `" Accesorios"`, `"ACCESORIOS"` → `"Accesorios"`.
3. **Normaliza `cliente_frecuente`** a únicamente dos valores (`"Sí"` / `"No"`), sin importar si el dato original era `"si"`, `"SI"`, `"no"`, `"NO"`, etc.
4. **Normaliza fechas**: intenta interpretar cada valor primero como `AAAA-MM-DD` y, si falla, como `DD/MM/AAAA`; si ninguno funciona, deja `NaT` (fecha nula) en vez de detener el programa.
5. **Corrige cantidades negativas** llevándolas a su valor absoluto (se documentan como errores de digitación) y cuenta cuántas se corrigieron.
6. **Imputa `precio_unitario` nulo** usando la mediana del mismo producto (`groupby("producto")`); si algún producto no tuviera ningún precio disponible, usa la mediana general como respaldo.
7. **Reemplaza `region` nula** por el texto `"No especificada"` en lugar de eliminar la fila, para no perder información de venta.
8. **Crea la columna calculada `venta_total`** = `cantidad × precio_unitario`, base de casi todos los análisis posteriores.

Devuelve una tupla `(duplicados_eliminados, cantidades_negativas)` y deja el resultado guardado en `ESTADO.df_limpio`.

### Opción 7 — `mostrar_estadisticas_descriptivas()`
Si `ESTADO.df_limpio` aún no existe, llama a `limpiar_datos()`. Luego imprime `describe()` (conteo, media, desviación estándar, mínimo, cuartiles, máximo) de las columnas `cantidad`, `precio_unitario` y `venta_total`.

### Opción 8 — `filtrar_consultar_datos()`
Submenú con tres tipos de filtro sobre los datos limpios:
1. Por **categoría** (comparación insensible a mayúsculas).
2. Por **región** (comparación insensible a mayúsculas).
3. Por **monto de venta mayor a un valor** ingresado por el usuario (`venta_total > monto`).

Muestra hasta 15 filas del resultado y, si hay más, indica cuántas filas adicionales no se están mostrando.

### Opción 9 — `agrupaciones_y_operaciones()`
Submenú con cinco agrupaciones distintas usando `groupby()`:
1. Monto total vendido por categoría (`sum`, `mean`, `count`).
2. Monto total vendido por región.
3. Top 10 vendedores por monto vendido.
4. Número de transacciones por método de pago.
5. Monto de venta promedio según si el cliente es frecuente o no.

### Opción 10 — `generar_graficos()`
Si `matplotlib` no está instalado (`MATPLOTLIB_OK == False`), informa al usuario y no intenta graficar. Si está disponible, crea la carpeta `graficos_salida/` (si no existe) y ofrece:
1. Gráfico de **barras**: monto total por categoría.
2. Gráfico **circular (pie)**: distribución del monto por región.
3. **Diagrama de caja (boxplot)**: precio unitario por categoría.
4. Gráfico de **línea**: evolución mensual del monto vendido.
5. Generar los cuatro anteriores de una sola vez.

Cada gráfico se guarda como `.png` dentro de `graficos_salida/` y se informa la ruta exacta del archivo. Toda la generación está envuelta en un `try/except` general para que un error al graficar (por ejemplo, datos insuficientes) no detenga el programa.

### Opción 11 — `analisis_adicional()`
Calcula la **matriz de correlación** (`corr()`) entre `cantidad`, `precio_unitario` y `venta_total`, y muestra el **top 10 de productos por unidades vendidas** (`groupby("producto")["cantidad"].sum()`).

---

## 7. Submenú — Ingreso de datos (opción 12)

Implementado con `submenu_ingreso_datos()`, un bucle independiente del menú principal que solo termina cuando el usuario elige "Regresar al menú principal" o se interrumpe la entrada.

### `ingresar_nuevo_registro()`
Pide, campo por campo, la información de una nueva venta, reutilizando las funciones de lectura validada (`leer_entero`, `leer_fecha`, `leer_texto`, `leer_decimal`, `leer_opcion_menu`). El registro se arma como un diccionario con **las mismas 10 columnas** del CSV original y se agrega a `ESTADO.registros_nuevos`. Si el usuario cancela con `Ctrl+C` o cierra la entrada, la función captura la excepción y aborta el ingreso sin afectar los registros ya guardados.

### `mostrar_registros_ingresados()`
Convierte `ESTADO.registros_nuevos` en un `DataFrame` temporal y lo imprime; si la lista está vacía, lo indica explícitamente en vez de mostrar una tabla vacía.

### `guardar_nuevos_datos()`
- Pide el nombre del archivo de salida (por defecto `nuevos_registros.csv`).
- Guarda los registros con `to_csv()` dentro de un `try/except` (maneja, por ejemplo, permisos de escritura inválidos).
- Pregunta si se desean **incorporar** esos registros al `DataFrame` principal (`ESTADO.df`) mediante `pd.concat()`. Si el usuario acepta, además reinicia `ESTADO.df_limpio = None` para que la próxima vez que se pida un análisis, la limpieza se vuelva a ejecutar **incluyendo los datos nuevos**.

### `mostrar_readme()`
Imprime en pantalla un resumen del flujo de trabajo recomendado y la estructura de columnas esperada (una versión corta, pensada para consulta rápida dentro del programa; este archivo `README.md` es la versión extendida).

---

## 8. Menú principal y punto de entrada

### `mostrar_menu_principal()`
Limpia la pantalla y dibuja el encabezado con el nombre del archivo cargado y su estado (`Cargado` / `No cargado`), seguido de las 13 opciones numeradas.

### `main()`
- Define el diccionario `acciones`, que **mapea cada número de opción a su función** correspondiente (patrón *dispatch table*, evita una cadena larga de `if/elif`).
- Bucle principal: dibuja el menú, pide una opción válida con `leer_opcion_menu()`, y:
  - Si la entrada se interrumpe (`None`) o el usuario elige `13`, termina el programa con un mensaje de despedida.
  - En cualquier otro caso, ejecuta la función asociada dentro de un `try/except Exception` adicional, de modo que **cualquier error no previsto** en una opción del menú se reporte en pantalla sin cerrar el programa completo.

### Bloque `if __name__ == "__main__":`
Punto de entrada real del script. Envuelve `main()` en un `try/except KeyboardInterrupt` para que, si el usuario presiona `Ctrl+C` en cualquier momento, el programa se cierre con un mensaje amigable en lugar de mostrar un *traceback*.

---

## 9. Manejo de errores — resumen

| Situación | Dónde se maneja | Resultado |
|---|---|---|
| Archivo CSV inexistente o ruta incorrecta | `cargar_archivo_csv()` | Mensaje de error, no se carga nada, el programa continúa |
| Archivo CSV corrupto / no legible | `cargar_archivo_csv()` (`try/except` sobre `pd.read_csv`) | Mensaje de error con el detalle de la excepción |
| Columnas faltantes respecto a lo esperado | `cargar_archivo_csv()` | Advertencia, pero el archivo se carga igual |
| Opción de menú inexistente | `leer_opcion_menu()` | Se vuelve a pedir la opción, sin cerrar el programa |
| Texto en vez de número | `leer_entero()` / `leer_decimal()` | Se vuelve a pedir el valor |
| Número fuera de rango | `leer_entero()` | Se vuelve a pedir el valor |
| Fecha con formato incorrecto (ingreso manual) | `leer_fecha()` | Se vuelve a pedir la fecha |
| Fechas mixtas dentro del CSV (`AAAA-MM-DD` y `DD/MM/AAAA`) | `limpiar_datos()` | Se interpretan ambos formatos; si ninguno aplica, queda como fecha nula (`NaT`) |
| Intentar analizar/filtrar/graficar sin haber cargado un CSV | `requiere_datos_cargados()` | Mensaje de advertencia, se regresa al menú principal |
| Cantidades negativas en el CSV | `limpiar_datos()` | Se corrigen a valor absoluto y se cuenta cuántas se corrigieron |
| Precio unitario o región nulos | `limpiar_datos()` | Se imputan (mediana por producto) o se reemplazan (`"No especificada"`) |
| `matplotlib` no instalado | `generar_graficos()` | Aviso claro, la opción no rompe el programa |
| Error al generar un gráfico específico | `generar_graficos()` (`try/except`) | Se informa el error puntual, el menú sigue disponible |
| Error al guardar el archivo de nuevos registros | `guardar_nuevos_datos()` | Se informa el error, los registros en memoria no se pierden |
| `Ctrl+C` / cierre de la entrada estándar en cualquier punto | `leer_opcion_menu()` y bloque final `try/except KeyboardInterrupt` | Cierre controlado del programa, sin *traceback* |
| Error no previsto dentro de cualquier opción del menú | `main()` (`try/except Exception` alrededor de cada acción) | Se informa el error y se regresa al menú principal, sin cerrar el programa |

---

## 10. Archivos generados por el programa en tiempo de ejecución

| Archivo / carpeta | Generado por | Contenido |
|---|---|---|
| `graficos_salida/ventas_por_categoria.png` | Opción 10 → sub-opción 1 o 5 | Barras: monto total por categoría |
| `graficos_salida/ventas_por_region.png` | Opción 10 → sub-opción 2 o 5 | Circular: distribución por región |
| `graficos_salida/boxplot_precio_categoria.png` | Opción 10 → sub-opción 3 o 5 | Caja: precio unitario por categoría |
| `graficos_salida/ventas_por_mes.png` | Opción 10 → sub-opción 4 o 5 | Línea: evolución mensual del monto vendido |
| `nuevos_registros.csv` (o el nombre que indique el usuario) | Opción 12 → "Guardar los nuevos datos" | Registros ingresados manualmente en el submenú |

---

## 11. Cómo ejecutar el programa

```bash
python proyecto_final.py
```

Se recomienda ubicar `proyecto_final.py` y `ventas_tienda_tecnologia_ampliado.csv` en la misma carpeta para poder usar la ruta por defecto al presionar ENTER en la opción 1.
