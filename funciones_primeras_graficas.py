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



def grafica_top(df, columna_valor, titulo, top_n=10):
    
    df_top = df.sort_values(
        by=columna_valor,
        ascending=False
    ).head(top_n)
    
    fig = px.bar(
        df_top,
        x=columna_valor,
        y="Rubro",
        orientation="h",
        title=titulo,
        text_auto=True
    )
    
    fig.update_layout(
        template="simple_white",   # 👈 CLAVE
        
        title=dict(
            x=0.5,
            xanchor='center',
            font=dict(
                size=22,
                family="Arial",
                color="#2f3e5c"
            )
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
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
    
    fig.update_traces(marker_color="#2E86C1")
    
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
        title="Comparación Normalizada Producción vs Área (Escala 0-1)",
        color_discrete_sequence=["#2E86C1", "#85C1E9"]
    )

    fig.update_layout(
        template="simple_white",

        title=dict(
            x=0.5,
            xanchor='center',
            font=dict(
                size=22,
                family="Arial",
                color="#2f3e5c"
            )
        ),

        plot_bgcolor="white",
        paper_bgcolor="white",

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
        color_continuous_scale="Agsunset",
        title=f"Top {top} municipios con mayor volumen de producción agrícola"
    )

    fig.update_layout(
        yaxis=dict(categoryorder="total ascending")
    )

    return fig

def treemap_produccion_municipio(df):

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
        color_continuous_scale="Viridis",
        title="Distribución del volumen de producción agrícola por subregión y municipio"
    )

    fig.update_layout(
        margin=dict(t=50, l=25, r=25, b=25)
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

def sankey_subregion_rubro(df, top_rubros=3):

    # limpiar nulos de producción
    data = df.dropna(subset=["Volumen Producción"])

    # agregación por subregión y rubro
    agg = (
        data.groupby(["Subregion", "Rubro"])["Volumen Producción"]
        .sum()
        .reset_index()
    )

    # opcional: limitar a los rubros con mayor producción total
    top = (
        agg.groupby("Rubro")["Volumen Producción"]
        .sum()
        .sort_values(ascending=False)
        .head(top_rubros)
        .index
    )
    agg = agg[agg["Rubro"].isin(top)]

    # crear lista de nodos
    labels = list(pd.unique(agg["Subregion"].tolist() + agg["Rubro"].tolist()))
    label_to_idx = {label: i for i, label in enumerate(labels)}

    # crear links
    source = agg["Subregion"].map(label_to_idx)
    target = agg["Rubro"].map(label_to_idx)
    value = agg["Volumen Producción"]

    # construir sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=18,
            line=dict(color="black", width=0.5),
            label=labels
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])

    fig.update_layout(
        title="Flujo de producción agrícola: Subregión → Rubro",
        font_size=12
    )

    return fig


def waterfall_produccion(df):

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
        increasing={"marker":{"color":"green"}},
        decreasing={"marker":{"color":"red"}}
    ))

    fig.update_layout(
        title="Cambios anuales en el volumen de producción agrícola",
        xaxis_title="Año",
        yaxis_title="Cambio en producción"
    )

    return fig