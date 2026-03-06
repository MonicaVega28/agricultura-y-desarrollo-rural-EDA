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


def preparar_datos_area_volumen(df):
    df_total = (
        df.groupby("Rubro")
          .agg({
              "Área Producción": "sum",
              "Volumen Producción": "sum"
          })
          .reset_index()
    )
    
    df_total["Rendimiento"] = df_total["Volumen Producción"] / df_total["Área Producción"]
    
    df_total["Produccion_norm"] = df_total["Volumen Producción"] / df_total["Volumen Producción"].max()
    df_total["Area_norm"] = df_total["Área Producción"] / df_total["Área Producción"].max()    
    return df_total



def grafica_top(df, columna_valor, titulo, subtitulo="", top_n=10):

    df_top = df.sort_values(
        by=columna_valor,
        ascending=False
    ).head(top_n)

    fig = px.bar(
        df_top,
        x=columna_valor,
        y="Rubro",
        orientation="h",
        text_auto=True
    )

    fig.update_traces(
        marker_color="#2E86C1",
        hovertemplate='<b>Rubro:</b> %{y}<br>' +
                      '<b>Valor:</b> %{x:,.0f}<extra></extra>'
    )

    fig.update_layout(

        title=f'<b>{titulo}</b><br><sup>{subtitulo}</sup>',

        xaxis_title=columna_valor,
        yaxis_title="Rubro",

        template='plotly_white',

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        margin=dict(l=20, r=20, t=100, b=20),

        yaxis=dict(
            categoryorder='total ascending',
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            gridwidth=1
        ),

        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            gridwidth=1
        )
    )

    return fig


def top_municipios(df, top=15):

    prod = (
        df.groupby("Municipio")["Volumen Producción"]
        .sum()
        .sort_values(ascending=False)
        .head(top)
        .reset_index()
    )

    fig = px.bar(
        prod,
        x="Volumen Producción",
        y="Municipio",
        orientation="h",
        color="Volumen Producción",
        color_continuous_scale=["#85C1E9", "#2E86C1"],
    )

    fig.update_traces(
        hovertemplate='<b>Municipio:</b> %{y}<br>' +
                      '<b>Producción:</b> %{x:,.0f}<extra></extra>'
    )

    fig.update_layout(

        title=f'<b>Top {top} municipios con mayor producción agrícola</b>'
              '<br><sup>Volumen total acumulado en el periodo analizado</sup>',

        xaxis_title="Volumen de Producción",
        yaxis_title="Municipio",

        template='plotly_white',

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        margin=dict(l=20, r=20, t=100, b=20),

        yaxis=dict(
            categoryorder="total ascending",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            gridwidth=1
        ),

        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            gridwidth=1
        )
    )

    return fig

def peso_produccion_sub_municipio(df):

    prod = (
        df.groupby(["Subregion", "Municipio"])["Volumen Producción"]
        .sum()
        .reset_index()
    )

    fig = px.treemap(
        prod,
        path=["Subregion", "Municipio"],
        values="Volumen Producción",
        color="Volumen Producción",
        color_continuous_scale=["#85C1E9", "#2E86C1"]
    )

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>' +
                      'Producción: %{value:,.0f}<extra></extra>'
    )

    fig.update_layout(

        title='<b>Distribución de la Producción Agrícola</b>'
              '<br><sup>Participación de municipios dentro de cada subregión</sup>',

        template='plotly_white',

        height=700,   # 👈 gráfico más alto
        width=1000,   # 👈 opcional, más ancho

        margin=dict(
            l=20,
            r=20,
            t=100,
            b=20
        )
    )

    return fig

def heatmap_especializacion(df):

    tabla = (
        df.groupby(["Subregion","Rubro"])["Volumen Producción"]
        .sum()
        .reset_index()
        .pivot(index="Subregion", columns="Rubro", values="Volumen Producción")
        .fillna(0)
    )

    fig = go.Figure(data=go.Heatmap(
        z=tabla.values,
        x=tabla.columns,
        y=tabla.index,
        colorscale="YlGnBu"
    ))

    fig.update_layout(
        title="Especialización agrícola por subregión",
        xaxis_title="Rubro",
        yaxis_title="Subregión"
    )
    return fig

def especializacion_subregion(df):

    prod = (
        df.groupby(["Subregion","Rubro"])["Volumen Producción"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        prod,
        x="Subregion",
        y="Volumen Producción",
        color="Rubro",
        title="Distribución de la producción agrícola por subregión y rubro"
    )
    return fig

def top_rubro_subregion(df, top_rubros=3):

    agg = (
        df.groupby(["Subregion", "Rubro"])["Volumen Producción"]
        .sum()
        .reset_index()
    )

    top = (
        agg.groupby("Rubro")["Volumen Producción"]
        .sum()
        .sort_values(ascending=False)
        .head(top_rubros)
        .index
    )

    agg = agg[agg["Rubro"].isin(top)]

    labels = list(set(agg["Subregion"].tolist() + agg["Rubro"].tolist()))
    label_to_idx = {label: i for i, label in enumerate(labels)}

    source = agg["Subregion"].map(label_to_idx)
    target = agg["Rubro"].map(label_to_idx)
    value = agg["Volumen Producción"]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=18,
            line=dict(color="black", width=0.5),
            label=labels,
            color="#85C1E9"
        ),

        link=dict(
            source=source,
            target=target,
            value=value,
            color="rgba(46,134,193,0.35)"
        )
    )])

    fig.update_layout(

        title='<b>Flujo de Producción Agrícola</b>'
              '<br><sup>Relación entre subregiones y rubros principales</sup>',

        template='plotly_white',

        height=650,

        margin=dict(
            l=20,
            r=20,
            t=100,
            b=20
        ),

        font_size=12
    )

    return fig


def variacion_produccion(df):

    prod = (
        df.groupby("Año")["Volumen Producción"]
        .sum()
        .reset_index()
        .sort_values("Año")
    )

    prod["Cambio"] = prod["Volumen Producción"].diff().fillna(0)

    measure = ["absolute"] + ["relative"] * (len(prod) - 1)

    fig = go.Figure(go.Waterfall(
        x=prod["Año"],
        y=prod["Cambio"],
        measure=measure,

        increasing={"marker":{"color":"#2E86C1"}},
        decreasing={"marker":{"color":"#EF553B"}},

        hovertemplate='<b>Año:</b> %{x}<br>' +
                      '<b>Cambio:</b> %{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(

        title='<b>Variación Anual de la Producción Agrícola</b>'
              '<br><sup>Cambios interanuales en el volumen total producido</sup>',

        xaxis_title="Año",
        yaxis_title="Cambio en Producción",

        template='plotly_white',

        margin=dict(
            l=20,
            r=20,
            t=100,
            b=20
        ),

        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            gridwidth=1
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            gridwidth=1
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="black",
        opacity=0.3
    )

    return fig

def grafica_comparacion_normalizada(df, top_n=10):

    df_top = df.sort_values(
        by="Produccion_norm",
        ascending=False
    ).head(top_n)

    fig = px.bar(
        df_top,
        x="Rubro",
        y=["Produccion_norm", "Area_norm"],
        barmode="group",
        color_discrete_sequence=["#2E86C1", "#85C1E9"]
    )

    fig.update_traces(
        hovertemplate='<b>Rubro:</b> %{x}<br>' +
                      '<b>Valor normalizado:</b> %{y:.2f}<extra></extra>'
    )

    fig.update_layout(

        title='<b>Comparación Normalizada entre Producción y Área</b>'
              '<br><sup>Escala relativa (0-1) para comparar magnitudes distintas</sup>',

        xaxis_title="Rubro",
        yaxis_title="Valor normalizado",

        template='plotly_white',

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        margin=dict(l=20, r=20, t=100, b=20),

        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            gridwidth=1
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            gridwidth=1
        )
    )

    return fig


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


def grafico_tendencia_lineas(df, columna_tiempo, columna_valor, titulo="Tendencia del Área Sembrada"):
    """
    Genera un gráfico de líneas interactivo con la paleta de colores azul unificada.
    """
    # 1. Agrupar por tiempo para asegurar que sumamos todo lo del mismo año
    df_linea = df.groupby(columna_tiempo)[columna_valor].sum().reset_index()
    df_linea = df_linea.sort_values(columna_tiempo)

    # 2. Crear el gráfico
    fig = go.Figure()

    # --- CAMBIO DE COLOR AQUÍ ---
    # Cambiamos 'forestgreen' por '#3182bd' para mantener la identidad visual
    fig.add_trace(go.Scatter(
        x=df_linea[columna_tiempo],
        y=df_linea[columna_valor],
        mode='lines+markers',
        line=dict(color='#3182bd', width=3), # Azul unificado
        marker=dict(size=10, color='#3182bd'), # Marcadores a juego
        name=columna_valor,
        hovertemplate="Año: %{x}<br>Total: %{y} ha<extra></extra>"
    ))

    # 3. Estética profesional
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        title_x=0.5,
        xaxis_title="Año / Periodo",
        yaxis_title="Hectáreas",
        template="plotly_white",
        hovermode="x unified"
    )

    fig.show()


def grafico_diferencia_areas(df, columna_tiempo, col_sembrada, col_cosechada, titulo="Análisis de Hectáreas No Cosechadas"):
    """
    Calcula y grafica la diferencia neta (pérdida) entre el área 
    sembrada y la cosecha total por periodo, usando la paleta de colores unificada.
    """
    # 1. Agrupar y calcular la diferencia
    df_gap = df.groupby(columna_tiempo)[[col_sembrada, col_cosechada]].sum().reset_index()
    df_gap['Diferencia'] = df_gap[col_sembrada] - df_gap[col_cosechada]
    df_gap = df_gap.sort_values(columna_tiempo)

    # 2. Crear el gráfico de barras interactivo
    fig = go.Figure()

    # --- CAMBIO DE COLOR AQUÍ ---
    # Se reemplaza 'indianred' por el azul hexadecimal '#3182bd' extraído de la referencia.
    fig.add_trace(go.Bar(
        x=df_gap[columna_tiempo],
        y=df_gap['Diferencia'],
        marker_color='#3182bd', # Color unificado 
        name='Hectáreas Perdidas',
        hovertemplate="Año: %{x}<br>Pérdida: %{y} ha<extra></extra>"
    ))

    # 3. Estética de reporte
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        title_x=0.5,
        xaxis_title="Año / Periodo",
        yaxis_title="Hectáreas de Diferencia (Pérdida)",
        template="plotly_white", # Mantiene fondo limpio
        hovermode="x unified"
    )

    fig.show()

def grafico_burbujas_emergentes_plotly(df, rubro, tiempo, valor, anio_i, anio_f):
    # 1. Preparar datos de ambos años
    df_f = df[df[tiempo].isin([anio_i, anio_f])]
    df_p = df_f.groupby([rubro, tiempo])[valor].sum().unstack(fill_value=0).reset_index()
    df_p.columns = [rubro, 'Inicio', 'Fin']
    
    # 2. Clasificación técnica (Asegúrese que los nombres coincidan con el mapa de abajo)
    def clasificar(row):
        if row['Inicio'] == 0: return 'Nuevo (No existía)'
        if row['Fin'] > (row['Inicio'] * 5): return 'Crecimiento Explosivo'
        return 'Tradicional'
    
    df_p['Categoría'] = df_p.apply(clasificar, axis=1)
    
    # 3. Mapeo de colores EXPLÍCITO (Usando el azul #3182bd de su referencia)
    colores_unificados = {
        'Crecimiento Explosivo': '#3182bd',  # El azul de image_7.png
        'Nuevo (No existía)': '#9ecae1',     # Un azul más suave para armonizar
        'Tradicional': '#d9d9d9'             # Gris neutro para no distraer
    }
    
    # 4. Crear el gráfico
    fig = px.scatter(df_p, x="Inicio", y="Fin",
                     size="Fin", 
                     color="Categoría", # Esto le dice a Plotly qué columna mirar
                     color_discrete_map=colores_unificados, # Esto le dice qué color usar
                     hover_name=rubro, 
                     size_max=60,
                     title=f"<b>Evolución de Rubros: {anio_i} vs {anio_f}</b>",
                     labels={"Inicio": f"Hectáreas en {anio_i}", "Fin": f"Hectáreas en {anio_f}"})

    fig.update_layout(
        template="plotly_white", 
        height=600,
        title_x=0.5,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.show()



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

def graficar_comparativa_volatilidad(df):
    df_clean = df.copy()
    df_clean['Año'] = pd.to_numeric(df_clean['Año'])
    df_clean['Volumen Producción'] = pd.to_numeric(df_clean['Volumen Producción'], errors='coerce')
    
  
    df_agrupado = df_clean.groupby(['Año', 'Tipo'])['Volumen Producción'].sum().reset_index()

    
    df_agrupado = df_agrupado.sort_values(['Tipo', 'Año'])
    df_agrupado['variacion_anual'] = df_agrupado.groupby('Tipo')['Volumen Producción'].pct_change() * 100

    
    fig = go.Figure()

   
    colores = {'Transitorios': '#EF553B', 'Permanentes': '#636EFA'}

    for tipo in ['Transitorios', 'Permanentes']:
        df_tipo = df_agrupado[df_agrupado['Tipo'] == tipo]
        
        fig.add_trace(go.Scatter(
            x=df_tipo['Año'],
            y=df_tipo['variacion_anual'],
            mode='lines+markers',
            name=tipo,
            line=dict(width=3, color=colores.get(tipo)),
            marker=dict(size=8),
            hovertemplate='<b>Año:</b> %{x}<br>' +
                          '<b>Variación:</b> %{y:.2f}%<extra></extra>'
        ))

 
    fig.update_layout(
        title='<b>Análisis de Volatilidad: Cultivos Transitorios vs. Permanentes</b><br><sup>Variación porcentual anual de la producción en Antioquia</sup>',
        xaxis_title='Año',
        yaxis_title='Variación de Producción (%)',
        hovermode='x unified',
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=100, b=20)
    )

    
    fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.3)

    return fig


def graficar_tasa_perdida_rubro(df):
   
    df_clean = df.copy()
    df_clean.columns = (
        df_clean.columns
        .str.strip()
        .str.lower()
        .str.replace('ñ', 'n')
        .str.replace('á', 'a')
        .str.replace('é', 'e')
        .str.replace('í', 'i')
        .str.replace('ó', 'o')
        .str.replace('ú', 'u')
    )

    col_rubro = 'rubro'
    col_area_total = 'area total'
    col_area_prod = 'area produccion'

    df_clean[col_area_total] = pd.to_numeric(df_clean[col_area_total], errors='coerce')
    df_clean[col_area_prod] = pd.to_numeric(df_clean[col_area_prod], errors='coerce')

    df_agrupado = df_clean.groupby(col_rubro)[[col_area_total, col_area_prod]].sum().reset_index()

    df_agrupado['area_perdida'] = df_agrupado[col_area_total] - df_agrupado[col_area_prod]
    
    df_agrupado = df_agrupado[df_agrupado[col_area_total] > 0]
 
    df_agrupado['tasa_perdida_pct'] = (df_agrupado['area_perdida'] / df_agrupado[col_area_total]) * 100

    df_significativo = df_agrupado[df_agrupado[col_area_total] > 500]

    df_top = df_significativo.sort_values('tasa_perdida_pct', ascending=False).head(15)

    fig = px.bar(
        df_top,
        x='tasa_perdida_pct',
        y=col_rubro,
        orientation='h',
        title='<b>Top 15 Cultivos con Mayor Tasa de Pérdida de Tierra</b><br><sup>% de hectáreas sembradas que NO lograron cosecharse</sup>',
        labels={
            'tasa_perdida_pct': 'Tasa de Pérdida (%)', 
            col_rubro: 'Cultivo (Rubro)'
        },
        color='tasa_perdida_pct',
        color_continuous_scale='Reds', 
        text_auto='.2f' 
    )

    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'}, 
        template='plotly_white',
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=80, b=20)
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Tasa de pérdida: %{x:.2f}%<extra></extra>"
    )
    return fig