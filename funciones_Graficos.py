import plotly.express as px
import plotly.graph_objects as go
import ConexionBD as BD
import pandas as pd


def leer_TablaBD(nombre_tabla):
    df = BD.get_Tabla(nombre_tabla)
    return df
 
def leer_archivo(nombre_archivo):
    df = pd.read_csv(nombre_archivo)
    return df

def unir_data(df_csv, df_bd):
    df_datos_completos = pd.concat([df_csv, df_bd], ignore_index=True)
    return df_datos_completos
 
def conversion_Datos(df, columna, tipo_dato):
    df[columna] = df[columna].astype(tipo_dato)
    return df


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