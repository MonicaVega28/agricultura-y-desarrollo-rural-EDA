import pandas as pd
import matplotlib.pyplot as plt
import unicodedata
import ConexionBD as BD
import plotly.express as px
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


def estandarizar_nombres(df, columna_municipio):
    print(f"Estandarizando textos en la columna: '{columna_municipio}'...")
    df_limpio = df.copy()
    df_limpio[columna_municipio] = df_limpio[columna_municipio].str.upper()
    
    
    def quitar_tildes(texto):
        if pd.isna(texto): 
            return texto
        
        texto_normalizado = unicodedata.normalize('NFKD', str(texto))
        return texto_normalizado.encode('ASCII', 'ignore').decode('utf-8')
    
    df_limpio[columna_municipio] = df_limpio[columna_municipio].apply(quitar_tildes)
    
    df_limpio[columna_municipio] = df_limpio[columna_municipio].str.strip()
    
    df_limpio[columna_municipio] = df_limpio[columna_municipio].replace(r'\s+', ' ', regex=True)
    
    print("¡Estandarización completada!")
    return df_limpio


def reemplazar_nombre_municipios(df, columna, diccionario):
    df_copia = df.copy()
    df_copia[columna] = df_copia[columna].replace(diccionario)
    return df_copia

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


def grafico_eficiencia_cultivos(df, titulo="Eficiencia de Cultivos"):
    
    df = df.copy()
    df["Área Total"]         = pd.to_numeric(df["Área Total"],         errors="coerce")
    df["Volumen Producción"] = pd.to_numeric(df["Volumen Producción"], errors="coerce")

    df_agrupado = df.groupby("Rubro").agg(
        Area_Total=("Área Total", "mean"),
        Volumen_Produccion=("Volumen Producción", "mean")
    ).reset_index()

    mediana_x = df_agrupado["Area_Total"].median()
    mediana_y = df_agrupado["Volumen_Produccion"].median()

    fig = px.scatter(
        df_agrupado,
        x="Area_Total",
        y="Volumen_Produccion",
        text="Rubro",
        title=titulo,
        labels={
            "Area_Total": "Área Total Promedio (ha)",
            "Volumen_Produccion": "Volumen de Producción Promedio (ton)"
        },
        template="plotly_white"
    )

    fig.update_traces(textposition="top center", marker=dict(size=10, color="steelblue", opacity=0.8))
    fig.add_vline(x=mediana_x, line_dash="dash", line_color="red",   annotation_text="Mediana Área",       annotation_position="top")
    fig.add_hline(y=mediana_y, line_dash="dash", line_color="green", annotation_text="Mediana Producción", annotation_position="right")

    fig.add_annotation(x=df_agrupado["Area_Total"].max() * 0.9, y=df_agrupado["Volumen_Produccion"].max() * 0.95, text="Mucha tierra,<br>alta producción",          showarrow=False, font=dict(color="green"))
    fig.add_annotation(x=df_agrupado["Area_Total"].max() * 0.9, y=df_agrupado["Volumen_Produccion"].min() * 1.5,  text="Mucha tierra,<br>poca producción",           showarrow=False, font=dict(color="red"))
    fig.add_annotation(x=df_agrupado["Area_Total"].min(),        y=df_agrupado["Volumen_Produccion"].max() * 0.95, text="Eficientes<br>(poco espacio,<br>alta producción)", showarrow=False, font=dict(color="blue"))

    fig.update_layout(title_font_size=20)
    
    return fig


def grafico_top10_tierra(df, titulo="Top 10 Cultivos que Más Tierra Ocupan"):
    
    df = df.copy()
    df["Área Total"] = pd.to_numeric(df["Área Total"], errors="coerce")

    # Agrupar y sacar top 10
    df_top10 = df.groupby("Rubro").agg(
        Area_Total=("Área Total", "mean")
    ).reset_index().sort_values("Area_Total", ascending=True).tail(10)  # ascending=True para que el mayor quede arriba

    fig = px.bar(
        df_top10,
        x="Area_Total",
        y="Rubro",
        orientation="h",  # ← barras horizontales
        title=titulo,
        labels={
            "Area_Total": "Área Total Promedio (ha)",
            "Rubro": "Cultivo"
        },
        text="Area_Total",  # ← muestra el valor en cada barra
        color="Area_Total",
        color_continuous_scale="Blues",
        template="plotly_white"
    )

    fig.update_traces(
        texttemplate="%{text:,.0f} ha",  # formato con separador de miles
        textposition="outside"
    )

    fig.update_layout(
        title_font_size=20,
        coloraxis_showscale=False,  # oculta la barra de color
        xaxis_title="Área Total Promedio (ha)",
        yaxis_title="Cultivo",
        margin=dict(l=20, r=100, t=60, b=40)
    )

    return fig


def grafico_agrupado_años(df, metrica="Volumen Producción", tipo=None, rubro=None, subregion=None, titulo="Evolución por Año"):
    """
    Gráfico de línea agrupado por Año.

    Parámetros:
        df        : DataFrame con los datos
        metrica   : "Volumen Producción" o "Área Total"
        tipo      : Filtrar por valor de columna Tipo      (opcional)
        rubro     : Filtrar por valor de columna Rubro     (opcional)
        subregion : Filtrar por valor de columna Subregion (opcional)
        titulo    : Título del gráfico
    """
    df = df.copy()
    df[metrica] = pd.to_numeric(df[metrica], errors="coerce")

    # ── Aplicar filtros opcionales ──
    if tipo:
        df = df[df["Tipo"] == tipo]
    if rubro:
        df = df[df["Rubro"] == rubro]
    if subregion:
        df = df[df["Subregion"] == subregion]

    # ── Agrupar por Año y Subregion para ver líneas por cada subregión ──
    df_agrupado = df.groupby(["Año", "Subregion"]).agg(
        Valor=(metrica, "sum")
    ).reset_index()

    fig = px.line(
        df_agrupado,
        x="Año",
        y="Valor",
        color="Subregion",   # ← una línea por subregión
        markers=True,
        title=titulo,
        labels={
            "Año": "Año",
            "Valor": metrica,
            "Subregion": "Subregión"
        },
        template="plotly_white"
    )

    fig.update_layout(
        title_font_size=20,
        xaxis_title="Año",
        yaxis_title=metrica,
        legend_title="Subregión",
        hovermode="x unified"  # ← al hacer hover muestra todas las subregiones del año
    )

    return fig