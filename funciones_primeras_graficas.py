import pandas as pd
import matplotlib.pyplot as plt
import ConexionBD as BD
import unicodedata
import plotly.express as px
import plotly.graph_objects as go

def leer_archivo(nombre_archivo):
    df = pd.read_csv(nombre_archivo)
    return df
    
def unir_data(df_csv, df_bd):
    df_datos_completos = pd.concat([df_csv, df_bd], ignore_index=True)
    return df_datos_completos



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

    labels = list(pd.unique(agg["Subregion"].tolist() + agg["Rubro"].tolist()))
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