"""Module pour l'intégration de l'IA via LiteLLM."""

import os
from typing import List, Dict, Optional
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

# Charger les variables d'environnement
load_dotenv()

# Import LiteLLM
try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    st.warning("⚠️ LiteLLM n'est pas disponible. Fonctionnalités IA limitées.")


class CrimeAnalysisBot:
    """Chatbot pour l'analyse de données de criminalité."""
    
    def __init__(self, 
                 default_model: str = "gpt-5-nano",
                 fallback_model: str = "claude-3-haiku-20240307"):
        """
        Initialise le chatbot.
        
        Args:
            default_model: Modèle principal à utiliser
            fallback_model: Modèle de secours
        """
        self.default_model = os.getenv("DEFAULT_MODEL", default_model)
        self.fallback_model = os.getenv("FALLBACK_MODEL", fallback_model)
        self.conversation_history = []
        
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles disponibles."""
        models = []
        
        # Vérifier les clés API disponibles
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_api_key_here":
            models.extend(["gpt-5-nano", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
        
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key != "your_anthropic_key_here":
            models.extend([
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229", 
                "claude-3-haiku-20240307"
            ])
        
        if not models:
            models = [self.default_model]
        
        return models
    
    def generate_response(self, 
                         prompt: str, 
                         model: Optional[str] = None,
                         context: Optional[str] = None) -> str:
        """
        Génère une réponse avec l'IA.
        
        Args:
            prompt: Question de l'utilisateur
            model: Modèle à utiliser (None = défaut)
            context: Contexte additionnel
            
        Returns:
            Réponse générée
        """
        if not LITELLM_AVAILABLE:
            return self._generate_fallback_response(prompt)
        
        model_to_use = model or self.default_model
        
        # Construire le message système
        system_message = """Tu es un assistant expert en analyse de données de criminalité en France.
        Tu aides les utilisateurs à comprendre les statistiques, identifier les tendances et 
        tirer des conclusions pertinentes. Réponds de manière concise et factuelle."""
        
        if context:
            system_message += f"\n\nContexte des données:\n{context}"
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = completion(
                model=model_to_use,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Sauvegarder dans l'historique
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": answer
            })
            
            return answer
            
        except Exception as e:
            st.error(f"Erreur lors de la génération: {e}")
            # Essayer avec le modèle de secours
            if model_to_use != self.fallback_model:
                try:
                    return self.generate_response(prompt, self.fallback_model, context)
                except:
                    return self._generate_fallback_response(prompt)
            return self._generate_fallback_response(prompt)
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Génère une réponse de secours sans IA."""
        responses = {
            "tendance": "Les données montrent des variations selon les périodes et les territoires. Pour une analyse détaillée, consultez les graphiques ci-dessus.",
            "comparaison": "La comparaison entre départements révèle des disparités importantes liées à la densité de population et aux contextes locaux.",
            "augmentation": "Plusieurs facteurs peuvent expliquer les variations: démographie, politiques de sécurité, contexte socio-économique.",
            "diminution": "Une baisse peut résulter d'actions préventives, de changements démographiques ou de modifications dans les méthodes d'enregistrement."
        }
        
        prompt_lower = prompt.lower()
        for key, response in responses.items():
            if key in prompt_lower:
                return response
        
        return "Je peux vous aider à analyser les données de criminalité. Posez-moi des questions sur les tendances, les comparaisons entre départements, ou les types de crimes."
    
    def analyze_trends(self, df: pd.DataFrame, department: Optional[str] = None) -> str:
        """
        Analyse les tendances dans les données.
        
        Args:
            df: DataFrame avec les données
            department: Département à analyser
            
        Returns:
            Analyse textuelle
        """
        # Préparer le contexte
        if department:
            df_filtered = df[df['code_dept'] == department]
            context = f"Données pour le département {department}"
        else:
            df_filtered = df
            context = "Données nationales"
        
        # Calculer quelques statistiques
        if 'annee' in df_filtered.columns and 'faits' in df_filtered.columns:
            evolution = df_filtered.groupby('annee')['faits'].sum()
            if len(evolution) > 1:
                variation = ((evolution.iloc[-1] - evolution.iloc[0]) / evolution.iloc[0] * 100)
                context += f"\nÉvolution totale: {variation:.1f}%"
        
        prompt = f"""Analyse les tendances de criminalité basées sur ces informations:
        {context}
        
        Fournis une analyse concise en 3-4 phrases couvrant:
        1. La tendance générale (hausse/baisse)
        2. Les points notables
        3. Une conclusion ou recommandation"""
        
        return self.generate_response(prompt, context=context)
    
    def generate_report(self, 
                       department: str,
                       stats: Dict,
                       model: Optional[str] = None) -> str:
        """
        Génère un rapport automatique.
        
        Args:
            department: Nom du département
            stats: Dictionnaire de statistiques
            model: Modèle à utiliser
            
        Returns:
            Rapport textuel
        """
        context = f"""Statistiques pour {department}:
        - Total des faits: {stats.get('total', 0):,.0f}
        - Évolution: {stats.get('evolution', 0):.1f}%
        - Type principal: {stats.get('top_crime', 'N/A')}
        - Période: {stats.get('year_start', 'N/A')} - {stats.get('year_end', 'N/A')}
        """
        
        prompt = f"""Génère un rapport d'analyse concis (5-6 phrases) sur la criminalité dans {department}.
        
        Inclus:
        1. Un résumé des chiffres clés
        2. L'analyse de l'évolution
        3. Les types de crimes dominants
        4. Une recommandation pour les décideurs
        
        Utilise un ton professionnel et factuel."""
        
        return self.generate_response(prompt, model, context)
    
    def compare_departments(self,
                          dept1_name: str,
                          dept1_stats: Dict,
                          dept2_name: str,
                          dept2_stats: Dict,
                          model: Optional[str] = None) -> str:
        """
        Compare deux départements.
        
        Args:
            dept1_name: Nom du premier département
            dept1_stats: Stats du premier département
            dept2_name: Nom du second département
            dept2_stats: Stats du second département
            model: Modèle à utiliser
            
        Returns:
            Analyse comparative
        """
        context = f"""Comparaison {dept1_name} vs {dept2_name}:
        
        {dept1_name}:
        - Total: {dept1_stats.get('total', 0):,.0f}
        - Évolution: {dept1_stats.get('evolution', 0):.1f}%
        
        {dept2_name}:
        - Total: {dept2_stats.get('total', 0):,.0f}
        - Évolution: {dept2_stats.get('evolution', 0):.1f}%
        """
        
        prompt = f"""Compare la situation de criminalité entre {dept1_name} et {dept2_name}.
        
        Fournis une analyse en 4-5 phrases couvrant:
        1. Quelle zone a le plus de criminalité
        2. Les différences d'évolution
        3. Une explication possible des différences
        4. Des recommandations différenciées"""
        
        return self.generate_response(prompt, model, context)
    
    def answer_question(self,
                       question: str,
                       data_context: str,
                       model: Optional[str] = None) -> str:
        """
        Répond à une question sur les données.
        
        Args:
            question: Question de l'utilisateur
            data_context: Contexte des données
            model: Modèle à utiliser
            
        Returns:
            Réponse
        """
        return self.generate_response(question, model, data_context)
    
    def clear_history(self):
        """Efface l'historique de conversation."""
        self.conversation_history = []


def get_data_summary(df: pd.DataFrame) -> str:
    """
    Crée un résumé textuel des données pour le contexte IA.
    
    Args:
        df: DataFrame à résumer
        
    Returns:
        Résumé textuel
    """
    summary = []
    
    if 'annee' in df.columns:
        years = df['annee'].unique()
        summary.append(f"Période: {years.min():.0f} - {years.max():.0f}")
    
    if 'code_dept' in df.columns:
        n_depts = df['code_dept'].nunique()
        summary.append(f"Départements: {n_depts}")
    
    if 'faits' in df.columns:
        total = df['faits'].sum()
        summary.append(f"Total des faits: {total:,.0f}")
    elif any(col.isdigit() for col in df.columns):
        month_cols = [col for col in df.columns if col.isdigit()]
        total = df[month_cols].sum().sum()
        summary.append(f"Total des faits: {total:,.0f}")
    
    if 'classe' in df.columns:
        n_types = df['classe'].nunique()
        summary.append(f"Types de crimes: {n_types}")
    
    return " | ".join(summary)
