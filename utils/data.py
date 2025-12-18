"""Module utilitaire pour la gestion et le traitement des données."""

import pandas as pd
import requests
from pathlib import Path
import json
from typing import Optional, Dict, List
import streamlit as st


class DataLoader:
    """Classe pour charger et traiter les données de criminalité."""
    
    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    @st.cache_data
    def load_crime_data(_self, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Charge les données de criminalité depuis l'API data.gouv.fr
        
        Args:
            sample_size: Nombre de lignes à charger (None = toutes)
            
        Returns:
            DataFrame avec les données de criminalité
        """
        # URL de l'API data.gouv.fr pour les crimes et délits
        url = "https://www.data.gouv.fr/fr/datasets/r/fa9dd0ab-a8ab-45ba-a7cf-a59a8264811b"
        
        cache_file = _self.data_dir / "crime_data.csv"
        
        # Charger depuis le cache si disponible
        if cache_file.exists():
            df = pd.read_csv(cache_file, nrows=sample_size)
        else:
            try:
                # Télécharger les données
                df = pd.read_csv(url, nrows=sample_size, sep=";", encoding="utf-8")
                # Sauvegarder en cache
                df.to_csv(cache_file, index=False)
            except Exception as e:
                st.warning(f"Impossible de télécharger les données: {e}. Utilisation de données de démonstration.")
                df = _self._create_demo_data()
        
        # Nettoyage et préparation
        df = _self._clean_crime_data(df)
        return df
    
    def _clean_crime_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie et prépare les données de criminalité."""
        # Renommer les colonnes pour standardisation
        column_mapping = {
            'Code département': 'code_dept',
            'Département': 'departement',
            'Code service': 'code_service',
            'Service': 'service',
            'Unité de compte': 'unite',
            'Classe': 'classe',
            'classe': 'classe',
            'Index': 'index',
            'Millésime': 'annee',
            'annee': 'annee'
        }
        
        # Renommer les colonnes qui existent
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        # Convertir l'année en numérique
        if 'annee' in df.columns:
            df['annee'] = pd.to_numeric(df['annee'], errors='coerce')
        
        # Supprimer les lignes avec des valeurs manquantes critiques
        critical_cols = [col for col in ['code_dept', 'annee', 'classe'] if col in df.columns]
        if critical_cols:
            df = df.dropna(subset=critical_cols)
        
        return df
    
    def _create_demo_data(self) -> pd.DataFrame:
        """Crée des données de démonstration pour les tests."""
        import numpy as np
        
        departements = {
            '75': 'Paris', '13': 'Bouches-du-Rhône', '69': 'Rhône',
            '59': 'Nord', '92': 'Hauts-de-Seine', '93': 'Seine-Saint-Denis',
            '94': 'Val-de-Marne', '91': 'Essonne', '78': 'Yvelines'
        }
        
        classes = [
            'Vols sans violence contre des personnes',
            'Coups et blessures volontaires',
            'Cambriolages',
            'Destructions et dégradations',
            'Vols de véhicules'
        ]
        
        data = []
        for annee in range(2019, 2024):
            for code_dept, dept_name in departements.items():
                for classe in classes:
                    faits = np.random.randint(100, 5000)
                    data.append({
                        'code_dept': code_dept,
                        'departement': dept_name,
                        'annee': annee,
                        'classe': classe,
                        'faits': faits
                    })
        
        return pd.DataFrame(data)
    
    @st.cache_data
    def get_department_stats(_self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule les statistiques par département.
        
        Args:
            df: DataFrame des crimes
            
        Returns:
            DataFrame avec statistiques agrégées
        """
        if 'faits' not in df.columns:
            # Si pas de colonne faits, essayer de trouver les colonnes de mois
            month_cols = [col for col in df.columns if col.isdigit() or 'mois' in col.lower()]
            if month_cols:
                df['faits'] = df[month_cols].sum(axis=1)
            else:
                df['faits'] = 1
        
        stats = df.groupby(['code_dept', 'departement']).agg({
            'faits': 'sum',
            'annee': 'count'
        }).reset_index()
        
        stats.columns = ['code_dept', 'departement', 'total_faits', 'nb_enregistrements']
        
        return stats.sort_values('total_faits', ascending=False)
    
    @st.cache_data
    def get_temporal_evolution(_self, df: pd.DataFrame, 
                                dept_code: Optional[str] = None) -> pd.DataFrame:
        """
        Calcule l'évolution temporelle des crimes.
        
        Args:
            df: DataFrame des crimes
            dept_code: Code département à filtrer (None = tous)
            
        Returns:
            DataFrame avec évolution annuelle
        """
        if dept_code:
            df = df[df['code_dept'] == dept_code]
        
        if 'faits' not in df.columns:
            month_cols = [col for col in df.columns if col.isdigit() or 'mois' in col.lower()]
            if month_cols:
                df['faits'] = df[month_cols].sum(axis=1)
            else:
                df['faits'] = 1
        
        evolution = df.groupby('annee')['faits'].sum().reset_index()
        evolution.columns = ['annee', 'total_faits']
        
        # Calculer l'évolution en pourcentage
        evolution['evolution_pct'] = evolution['total_faits'].pct_change() * 100
        
        return evolution
    
    @st.cache_data
    def get_crime_types_distribution(_self, df: pd.DataFrame, 
                                      dept_code: Optional[str] = None,
                                      year: Optional[int] = None) -> pd.DataFrame:
        """
        Calcule la distribution par type de crime.
        
        Args:
            df: DataFrame des crimes
            dept_code: Code département à filtrer
            year: Année à filtrer
            
        Returns:
            DataFrame avec distribution par type
        """
        filtered_df = df.copy()
        
        if dept_code:
            filtered_df = filtered_df[filtered_df['code_dept'] == dept_code]
        
        if year:
            filtered_df = filtered_df[filtered_df['annee'] == year]
        
        if 'faits' not in filtered_df.columns:
            month_cols = [col for col in filtered_df.columns if col.isdigit() or 'mois' in col.lower()]
            if month_cols:
                filtered_df['faits'] = filtered_df[month_cols].sum(axis=1)
            else:
                filtered_df['faits'] = 1
        
        distribution = filtered_df.groupby('classe')['faits'].sum().reset_index()
        distribution.columns = ['type_crime', 'total']
        distribution = distribution.sort_values('total', ascending=False)
        
        # Calculer le pourcentage
        distribution['pourcentage'] = (distribution['total'] / distribution['total'].sum() * 100).round(2)
        
        return distribution
    
    @st.cache_data
    def get_top_departments(_self, df: pd.DataFrame, 
                            n: int = 10, 
                            year: Optional[int] = None) -> pd.DataFrame:
        """
        Retourne les n départements avec le plus de crimes.
        
        Args:
            df: DataFrame des crimes
            n: Nombre de départements à retourner
            year: Année à filtrer
            
        Returns:
            DataFrame avec top départements
        """
        filtered_df = df.copy()
        
        if year:
            filtered_df = filtered_df[filtered_df['annee'] == year]
        
        if 'faits' not in filtered_df.columns:
            month_cols = [col for col in filtered_df.columns if col.isdigit() or 'mois' in col.lower()]
            if month_cols:
                filtered_df['faits'] = filtered_df[month_cols].sum(axis=1)
            else:
                filtered_df['faits'] = 1
        
        top = filtered_df.groupby(['code_dept', 'departement'])['faits'].sum().reset_index()
        top = top.sort_values('faits', ascending=False).head(n)
        top.columns = ['code_dept', 'departement', 'total_faits']
        
        return top


def load_population_data() -> Dict[str, int]:
    """
    Charge les données de population par département.
    
    Returns:
        Dictionnaire {code_dept: population}
    """
    # Données de population approximatives (2023)
    population = {
        '75': 2165000, '13': 2040000, '69': 1850000, '59': 2608000,
        '92': 1609000, '93': 1623000, '94': 1395000, '91': 1296000,
        '78': 1431000, '31': 1380000, '06': 1083000, '44': 1429000,
        '33': 1623000, '67': 1142000, '62': 1471000, '76': 1254000,
        '77': 1421000, '95': 1241000, '35': 1079000, '34': 1175000
    }
    
    return population


def calculate_crime_rate(total_crimes: int, population: int) -> float:
    """
    Calcule le taux de criminalité pour 1000 habitants.
    
    Args:
        total_crimes: Nombre total de crimes
        population: Population du territoire
        
    Returns:
        Taux pour 1000 habitants
    """
    if population == 0:
        return 0
    return (total_crimes / population) * 1000
