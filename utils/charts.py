"""Module pour la création de visualisations interactives."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium
from typing import Optional, List
import streamlit as st


def create_choropleth_map(df: pd.DataFrame, 
                          value_column: str = 'total_faits',
                          title: str = "Carte de la criminalité par département") -> go.Figure:
    """
    Crée une carte choroplèthe de France.
    
    Args:
        df: DataFrame avec colonnes 'code_dept' et value_column
        value_column: Nom de la colonne pour les valeurs
        title: Titre de la carte
        
    Returns:
        Figure Plotly
    """
    # Préparer les données pour la carte
    df_map = df.copy()
    
    # Assurer que le code département est en format string à 2 chiffres
    if 'code_dept' in df_map.columns:
        df_map['code_dept'] = df_map['code_dept'].astype(str).str.zfill(2)
    
    fig = px.choropleth(
        df_map,
        locations='code_dept',
        geojson='https://france-geojson.gregoiredavid.fr/repo/departements.geojson',
        featureidkey='properties.code',
        color=value_column,
        hover_name='departement' if 'departement' in df_map.columns else None,
        hover_data={value_column: ':,.0f', 'code_dept': True},
        color_continuous_scale='Reds',
        title=title,
        labels={value_column: 'Nombre de faits'}
    )
    
    fig.update_geos(
        fitbounds='locations',
        visible=False
    )
    
    fig.update_layout(
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    
    return fig


def create_temporal_evolution_chart(df: pd.DataFrame,
                                    x_column: str = 'annee',
                                    y_column: str = 'total_faits',
                                    title: str = "Évolution temporelle de la criminalité") -> go.Figure:
    """
    Crée un graphique d'évolution temporelle.
    
    Args:
        df: DataFrame avec données temporelles
        x_column: Colonne pour l'axe X (temps)
        y_column: Colonne pour l'axe Y (valeurs)
        title: Titre du graphique
        
    Returns:
        Figure Plotly
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[x_column],
        y=df[y_column],
        mode='lines+markers',
        name='Total des faits',
        line=dict(color='#d62728', width=3),
        marker=dict(size=8)
    ))
    
    # Ajouter une ligne de tendance
    if len(df) > 1:
        z = np.polyfit(range(len(df)), df[y_column], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=df[x_column],
            y=p(range(len(df))),
            mode='lines',
            name='Tendance',
            line=dict(color='#1f77b4', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Année',
        yaxis_title='Nombre de faits',
        hovermode='x unified',
        height=400
    )
    
    return fig


def create_crime_types_pie_chart(df: pd.DataFrame,
                                 labels_column: str = 'type_crime',
                                 values_column: str = 'total',
                                 title: str = "Distribution par type de crime") -> go.Figure:
    """
    Crée un graphique en camembert pour les types de crimes.
    
    Args:
        df: DataFrame avec les données
        labels_column: Colonne pour les labels
        values_column: Colonne pour les valeurs
        title: Titre du graphique
        
    Returns:
        Figure Plotly
    """
    # Prendre seulement les 10 premiers types
    df_top = df.head(10)
    
    fig = px.pie(
        df_top,
        values=values_column,
        names=labels_column,
        title=title,
        hole=0.3  # Donut chart
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Nombre: %{value:,.0f}<br>Pourcentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig


def create_bar_chart(df: pd.DataFrame,
                     x_column: str,
                     y_column: str,
                     title: str = "Comparaison",
                     color_column: Optional[str] = None,
                     orientation: str = 'v') -> go.Figure:
    """
    Crée un graphique en barres.
    
    Args:
        df: DataFrame avec les données
        x_column: Colonne pour l'axe X
        y_column: Colonne pour l'axe Y
        title: Titre du graphique
        color_column: Colonne pour la couleur
        orientation: 'v' pour vertical, 'h' pour horizontal
        
    Returns:
        Figure Plotly
    """
    fig = px.bar(
        df,
        x=x_column if orientation == 'v' else y_column,
        y=y_column if orientation == 'v' else x_column,
        color=color_column,
        title=title,
        orientation=orientation,
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        height=400,
        xaxis_title=x_column if orientation == 'v' else y_column,
        yaxis_title=y_column if orientation == 'v' else x_column,
        showlegend=True if color_column else False
    )
    
    return fig


def create_comparison_chart(df: pd.DataFrame,
                            departments: List[str],
                            metric: str = 'total_faits',
                            title: str = "Comparaison entre départements") -> go.Figure:
    """
    Crée un graphique de comparaison entre départements.
    
    Args:
        df: DataFrame avec les données
        departments: Liste des codes départements à comparer
        metric: Métrique à comparer
        title: Titre du graphique
        
    Returns:
        Figure Plotly
    """
    df_filtered = df[df['code_dept'].isin(departments)]
    
    fig = px.bar(
        df_filtered,
        x='departement',
        y=metric,
        color='code_dept',
        title=title,
        labels={metric: 'Nombre de faits', 'departement': 'Département'},
        text=metric
    )
    
    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(
        height=450,
        showlegend=False,
        xaxis_tickangle=-45
    )
    
    return fig


def create_heatmap(df: pd.DataFrame,
                   x_column: str,
                   y_column: str,
                   value_column: str,
                   title: str = "Carte de chaleur") -> go.Figure:
    """
    Crée une heatmap.
    
    Args:
        df: DataFrame avec les données
        x_column: Colonne pour l'axe X
        y_column: Colonne pour l'axe Y
        value_column: Colonne pour les valeurs
        title: Titre du graphique
        
    Returns:
        Figure Plotly
    """
    # Pivoter les données pour la heatmap
    pivot_df = df.pivot_table(
        values=value_column,
        index=y_column,
        columns=x_column,
        aggfunc='sum'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale='Reds',
        hoverongaps=False,
        hovertemplate='Année: %{x}<br>Type: %{y}<br>Nombre: %{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_column,
        yaxis_title=y_column,
        height=500
    )
    
    return fig


def create_folium_map(df: pd.DataFrame,
                      lat_column: str = 'latitude',
                      lon_column: str = 'longitude',
                      popup_columns: Optional[List[str]] = None) -> folium.Map:
    """
    Crée une carte interactive Folium.
    
    Args:
        df: DataFrame avec les données géographiques
        lat_column: Nom de la colonne latitude
        lon_column: Nom de la colonne longitude
        popup_columns: Colonnes à afficher dans le popup
        
    Returns:
        Carte Folium
    """
    # Centre de la France
    center_lat = 46.603354
    center_lon = 1.888334
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Ajouter des marqueurs si les données géographiques sont disponibles
    if lat_column in df.columns and lon_column in df.columns:
        for idx, row in df.iterrows():
            if pd.notna(row[lat_column]) and pd.notna(row[lon_column]):
                popup_text = ""
                if popup_columns:
                    for col in popup_columns:
                        if col in row:
                            popup_text += f"<b>{col}:</b> {row[col]}<br>"
                
                folium.CircleMarker(
                    location=[row[lat_column], row[lon_column]],
                    radius=5,
                    popup=folium.Popup(popup_text, max_width=200),
                    color='red',
                    fill=True,
                    fillColor='red'
                ).add_to(m)
    
    return m


def create_statistics_cards(total_crimes: int,
                           evolution_pct: float,
                           top_crime_type: str,
                           top_crime_pct: float) -> str:
    """
    Crée des cartes de statistiques en HTML.
    
    Args:
        total_crimes: Nombre total de crimes
        evolution_pct: Évolution en pourcentage
        top_crime_type: Type de crime le plus fréquent
        top_crime_pct: Pourcentage du crime le plus fréquent
        
    Returns:
        HTML string
    """
    evolution_color = "green" if evolution_pct < 0 else "red"
    evolution_icon = "↓" if evolution_pct < 0 else "↑"
    
    html = f"""
    <div style="display: flex; gap: 20px; margin: 20px 0;">
        <div style="flex: 1; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; color: white;">
            <h3 style="margin: 0; font-size: 16px; opacity: 0.9;">Total des faits</h3>
            <p style="margin: 10px 0 0 0; font-size: 32px; font-weight: bold;">
                {total_crimes:,.0f}
            </p>
        </div>
        <div style="flex: 1; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 20px; border-radius: 10px; color: white;">
            <h3 style="margin: 0; font-size: 16px; opacity: 0.9;">Évolution annuelle</h3>
            <p style="margin: 10px 0 0 0; font-size: 32px; font-weight: bold;">
                {evolution_icon} {abs(evolution_pct):.1f}%
            </p>
        </div>
        <div style="flex: 1; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 20px; border-radius: 10px; color: white;">
            <h3 style="margin: 0; font-size: 16px; opacity: 0.9;">Crime principal</h3>
            <p style="margin: 10px 0 0 0; font-size: 18px; font-weight: bold;">
                {top_crime_type[:30]}
            </p>
            <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold;">
                {top_crime_pct:.1f}%
            </p>
        </div>
    </div>
    """
    return html


# Import numpy pour les calculs
import numpy as np
