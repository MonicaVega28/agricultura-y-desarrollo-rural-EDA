import pandas as pd
import matplotlib.pyplot as plt
import ConexionBD as BD
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------
# SECCIÓN 1: CARGA Y TRANSFORMACIÓN DE DATOS
# ---------------------------------------------------------
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


# =============================================================================
# GRÁFICO DE MANCUERNA 
# =============================================================================

def grafico_mancuerna_plotly(df, tiempo, sembrado, cosechado, titulo="Análisis de Brecha de Áreas"):
    # 1. Asegurar que los datos estén ordenados por tiempo para que el gráfico sea lógico
    df_sorted = df.sort_values(tiempo)

    fig = go.Figure()

    # 2. Agregar las líneas que unen los puntos (las "mancuernas")
    # Plotly no tiene un 'hlines' directo para esto, así que usamos un bucle eficiente
    for i, row in df_sorted.iterrows():
        fig.add_trace(go.Scatter(
            x=[row[cosechado], row[sembrado]],
            y=[row[tiempo], row[tiempo]],
            mode="lines",
            line=dict(color="grey", width=2),
            showlegend=False,
            hoverinfo='skip'
        ))

    # 3. Agregar los puntos de Área Cosechada
    fig.add_trace(go.Scatter(
        x=df_sorted[cosechado],
        y=df_sorted[tiempo],
        mode="markers",
        name="Cosechado (Producción)",
        marker=dict(color="red", size=12),
        hovertemplate="Cosechado: %{x} ha<extra></extra>"
    ))

    # 4. Agregar los puntos de Área Sembrada
    fig.add_trace(go.Scatter(
        x=df_sorted[sembrado],
        y=df_sorted[tiempo],
        mode="markers",
        name="Sembrado (Total)",
        marker=dict(color="navy", size=12),
        hovertemplate="Sembrado: %{x} ha<extra></extra>"
    ))

    # 5. Configuración estética
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        title_x=0.5,
        xaxis_title="Hectáreas",
        yaxis_title="Periodo",
        height=700,
        template="plotly_white",
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.show()
    

# =============================================================================
# GRÁFICO DE PARETO PARA RUBROS (PLOTLY)
# =============================================================================

def grafico_pareto_top50(df, columna_categoria, columna_valor, titulo="Análisis de Pareto: Top 50 Rubros"):
    # 1. Preparar datos completos para el cálculo correcto del 100%
    df_pareto = df.groupby(columna_categoria)[columna_valor].sum().sort_values(ascending=False).reset_index()
    total_produccion = df_pareto[columna_valor].sum()
    
    # 2. Calcular porcentajes sobre el TOTAL
    df_pareto['porcentaje'] = (df_pareto[columna_valor] / total_produccion) * 100
    df_pareto['acumulado'] = df_pareto['porcentaje'].cumsum()

    # 3. Filtrar solo los primeros 50 para la visualización
    df_top = df_pareto.head(50)

    # 4. Crear figura interactiva
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras de Producción (Top 50)
    fig.add_trace(
        go.Bar(x=df_top[columna_categoria], y=df_top[columna_valor], 
               name="Producción (Ton)", marker_color='steelblue'),
        secondary_y=False,
    )

    # Línea de Porcentaje Acumulado (Top 50)
    fig.add_trace(
        go.Scatter(x=df_top[columna_categoria], y=df_top['acumulado'], 
                   name="% Acumulado", line=dict(color="red", width=3)),
        secondary_y=True,
    )

    # Línea guía del 80%
    fig.add_hline(y=80, line_dash="dash", line_color="orange", secondary_y=True,
                  annotation_text="Límite Pareto (80%)", annotation_position="bottom right")

    # 5. Estética y Legibilidad
    fig.update_layout(
        title_text=f"<b>{titulo}</b>",
        title_x=0.5,
        xaxis_tickangle=-45,
        height=600,
        margin=dict(b=100),
        hovermode="x unified",
        template="plotly_white"
    )

    fig.update_yaxes(title_text="Producción (Toneladas)", secondary_y=False)
    fig.update_yaxes(title_text="Porcentaje Acumulado (%)", secondary_y=True, range=[0, 105])

    fig.show()
    
    # Insight para el reporte
    cantidad_80 = df_pareto[df_pareto['acumulado'] <= 81].shape[0]
    print(f"Análisis Profesional: Solo {cantidad_80} rubros representan el 80% de la producción total en Antioquia.")
