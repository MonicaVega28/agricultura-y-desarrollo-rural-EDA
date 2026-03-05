import pandas as pd
import matplotlib.pyplot as plt
import ConexionBD as BD
import unicodedata
import plotly.graph_objects as go
import plotly.express as px

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