"""Fichier d'initialisation du package utils."""

from .data import DataLoader, load_population_data, calculate_crime_rate
from .charts import (
    create_choropleth_map,
    create_temporal_evolution_chart,
    create_crime_types_pie_chart,
    create_bar_chart,
    create_comparison_chart,
    create_heatmap,
    create_statistics_cards
)
from .chatbot import CrimeAnalysisBot, get_data_summary

__all__ = [
    'DataLoader',
    'load_population_data',
    'calculate_crime_rate',
    'create_choropleth_map',
    'create_temporal_evolution_chart',
    'create_crime_types_pie_chart',
    'create_bar_chart',
    'create_comparison_chart',
    'create_heatmap',
    'create_statistics_cards',
    'CrimeAnalysisBot',
    'get_data_summary'
]
