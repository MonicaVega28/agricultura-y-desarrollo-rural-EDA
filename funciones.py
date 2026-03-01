import pandas as pd
import matplotlib.pyplot as plt
import ConexionBD as BD

def leer_archivo(nombre_archivo):
    df = pd.read_csv(nombre_archivo)
    return df
    
def unir_data(df_csv, df_bd):
    df_datos_completos = pd.concat([df_csv, df_bd], ignore_index=True)
    return df_datos_completos

def grafico_lineas(df, columna_x, columna_y, titulo="Gráfico de líneas"):
    plt.figure()
    plt.plot(df[columna_x], df[columna_y])
    plt.title(titulo)
    plt.xlabel(columna_x)
    plt.ylabel(columna_y)
    plt.grid(True)
    plt.show()

def grafico_dispersion(df, x, y, titulo="Gráfico de dispersión"):
    plt.figure()
    plt.scatter(df[x], df[y])
    plt.title(titulo)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.grid(True)
    plt.show()
    

def leer_TablaBD(nombre_tabla):
    df = BD.get_Tabla(nombre_tabla)
    return df
 
 
def conversion_Datos(df, columna, tipo_dato):
    df[columna] = df[columna].astype(tipo_dato)
    return df


def grafico_mancuerna(df, tiempo, sembrado, cosechado, titulo="Análisis de Brecha de Áreas"):

    plt.figure(figsize=(12, 7))
    
    # 1. Dibujar la línea gris que une los dos puntos (la brecha)
    plt.hlines(y=df[tiempo], xmin=df[cosechado], xmax=df[sembrado], color='grey', alpha=0.5)
    
    # 2. Dibujar los puntos de inicio y fin
    plt.scatter(df[sembrado], df[tiempo], color='navy', label='Sembrado', s=100, zorder=3)
    plt.scatter(df[cosechado], df[tiempo], color='red', label='Cosechado', s=100, zorder=3)
    
    # 3. Estética del gráfico
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel("Hectáreas")
    plt.ylabel("Periodo (Semestre/Mes)")
    plt.legend()
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout() # Ajusta márgenes para que no se corten las etiquetas
    plt.show()
    
    
def grafico_pareto_rubros(df, columna_categoria, columna_valor, titulo="Análisis de Pareto de Producción"):
    # 1. Preparar los datos: Agrupar, Sumar y Ordenar
    df_pareto = df.groupby(columna_categoria)[columna_valor].sum().sort_values(ascending=False).reset_index()
    
    # 2. Calcular porcentajes y acumulado
    df_pareto['porcentaje'] = (df_pareto[columna_valor] / df_pareto[columna_valor].sum()) * 100
    df_pareto['acumulado'] = df_pareto['porcentaje'].cumsum()

    # 3. Crear la visualización
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Barras para producción individual
    ax1.bar(df_pareto[columna_categoria], df_pareto[columna_valor], color="steelblue", alpha=0.8)
    ax1.set_ylabel("Producción (Toneladas)")
    plt.xticks(rotation=90)

    # Eje secundario para el porcentaje acumulado
    ax2 = ax1.twinx()
    ax2.plot(df_pareto[columna_categoria], df_pareto['acumulado'], color="red", marker="D", ms=5, label="% Acumulado")
    ax2.axhline(80, color="orange", linestyle="--", label="Límite 80%") # Línea guía del 80%
    ax2.set_ylabel("Porcentaje Acumulado (%)")
    ax2.set_ylim(0, 110)

    plt.title(titulo, fontsize=15, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.4)
    
    # Identificar cuántos rubros representan el 80%
    cantidad_80 = df_pareto[df_pareto['acumulado'] <= 85].shape[0] # Usamos 85 para ver los que bordean el límite
    print(f" Resultado del Análisis: Aproximadamente {cantidad_80} rubros generan el 80% de la producción total.")
    
    plt.tight_layout()
    plt.show()