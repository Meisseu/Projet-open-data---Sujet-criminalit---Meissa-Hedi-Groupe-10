"""
SafeCity Dashboard - Tableau de bord sécurité urbaine
Application Streamlit pour l'analyse de la criminalité en France
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Import des modules utilitaires
from utils import (
    DataLoader,
    load_population_data,
    calculate_crime_rate,
    create_choropleth_map,
    create_temporal_evolution_chart,
    create_crime_types_pie_chart,
    create_bar_chart,
    create_comparison_chart,
    create_heatmap,
    create_statistics_cards,
    CrimeAnalysisBot,
    get_data_summary
)

# Configuration de la page
st.set_page_config(
    page_title="SafeCity Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_data_loader():
    """Initialise le chargeur de données."""
    return DataLoader()


@st.cache_resource
def init_chatbot():
    """Initialise le chatbot IA."""
    return CrimeAnalysisBot()


def main():
    """Fonction principale de l'application."""
    
    # En-tête
    st.markdown('<h1 class="main-header">🏛️ SafeCity Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Tableau de bord interactif pour l'analyse de la criminalité en France")
    
    # Initialisation
    data_loader = init_data_loader()
    chatbot = init_chatbot()
    
    # Sidebar - Filtres et configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Choix du modèle IA
        st.subheader("🤖 Modèle IA")
        available_models = chatbot.get_available_models()
        selected_model = st.selectbox(
            "Sélectionner un modèle",
            available_models,
            help="Choisissez le modèle d'IA pour l'analyse"
        )
        
        st.divider()
        
        # Filtres de données
        st.subheader("🔍 Filtres")
        
        # Charger les données
        with st.spinner("Chargement des données..."):
            df = data_loader.load_crime_data(sample_size=50000)  # Limiter pour la performance
        
        # Filtre année
        if 'annee' in df.columns:
            years = sorted(df['annee'].unique())
            if len(years) > 0:
                selected_years = st.slider(
                    "Période",
                    min_value=int(years[0]),
                    max_value=int(years[-1]),
                    value=(int(years[0]), int(years[-1]))
                )
                df = df[(df['annee'] >= selected_years[0]) & (df['annee'] <= selected_years[1])]
        
        # Filtre département
        if 'departement' in df.columns:
            departments = ['Tous'] + sorted(df['departement'].unique().tolist())
            selected_dept = st.selectbox("Département", departments)
            
            if selected_dept != 'Tous':
                df_filtered = df[df['departement'] == selected_dept]
            else:
                df_filtered = df
        else:
            df_filtered = df
            selected_dept = 'Tous'
        
        # Filtre type de crime
        if 'classe' in df.columns:
            crime_types = ['Tous'] + sorted(df['classe'].unique().tolist())
            selected_crime = st.selectbox("Type de crime", crime_types)
            
            if selected_crime != 'Tous':
                df_filtered = df_filtered[df_filtered['classe'] == selected_crime]
        
        st.divider()
        
        # Informations
        st.subheader("📊 Données")
        st.info(f"""
        **Enregistrements:** {len(df_filtered):,}  
        **Période:** {selected_years[0] if 'annee' in df.columns else 'N/A'} - {selected_years[1] if 'annee' in df.columns else 'N/A'}  
        **Départements:** {df_filtered['code_dept'].nunique() if 'code_dept' in df_filtered.columns else 0}
        """)
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📍 Vue d'ensemble",
        "📈 Analyse temporelle", 
        "🗺️ Cartographie",
        "⚖️ Comparaison",
        "💬 Assistant IA"
    ])
    
    # TAB 1: Vue d'ensemble
    with tab1:
        st.header("Vue d'ensemble des statistiques")
        
        # Calcul des statistiques clés
        if 'faits' not in df_filtered.columns:
            month_cols = [col for col in df_filtered.columns if col.isdigit() or 'mois' in col.lower()]
            if month_cols:
                df_filtered['faits'] = df_filtered[month_cols].sum(axis=1)
            else:
                df_filtered['faits'] = 1
        
        total_crimes = df_filtered['faits'].sum()
        
        # Calculer l'évolution
        if 'annee' in df_filtered.columns and len(df_filtered['annee'].unique()) > 1:
            evolution_df = data_loader.get_temporal_evolution(df_filtered)
            if len(evolution_df) > 1:
                evolution_pct = evolution_df['evolution_pct'].iloc[-1]
            else:
                evolution_pct = 0
        else:
            evolution_pct = 0
        
        # Crime le plus fréquent
        crime_dist = data_loader.get_crime_types_distribution(df_filtered)
        if len(crime_dist) > 0:
            top_crime = crime_dist.iloc[0]['type_crime']
            top_crime_pct = crime_dist.iloc[0]['pourcentage']
        else:
            top_crime = "N/A"
            top_crime_pct = 0
        
        # Afficher les cartes de statistiques
        st.markdown(
            create_statistics_cards(total_crimes, evolution_pct, top_crime, top_crime_pct),
            unsafe_allow_html=True
        )
        
        # Graphiques en colonnes
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 10 Départements")
            top_depts = data_loader.get_top_departments(df_filtered, n=10)
            if len(top_depts) > 0:
                fig = create_bar_chart(
                    top_depts,
                    x_column='departement',
                    y_column='total_faits',
                    title="Départements avec le plus de faits",
                    orientation='h'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pas de données disponibles")
        
        with col2:
            st.subheader("Distribution par type de crime")
            if len(crime_dist) > 0:
                fig = create_crime_types_pie_chart(crime_dist)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pas de données disponibles")
        
        # Tableau des données
        st.subheader("📋 Données détaillées")
        dept_stats = data_loader.get_department_stats(df_filtered)
        st.dataframe(
            dept_stats.head(20),
            use_container_width=True,
            hide_index=True
        )
    
    # TAB 2: Analyse temporelle
    with tab2:
        st.header("Analyse de l'évolution temporelle")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Évolution annuelle")
            evolution_df = data_loader.get_temporal_evolution(df_filtered)
            
            if len(evolution_df) > 0:
                fig = create_temporal_evolution_chart(evolution_df)
                st.plotly_chart(fig, use_container_width=True)
                
                # Afficher les données
                st.dataframe(evolution_df, use_container_width=True, hide_index=True)
            else:
                st.info("Pas de données temporelles disponibles")
        
        with col2:
            st.subheader("Statistiques")
            if len(evolution_df) > 1:
                total_variation = ((evolution_df['total_faits'].iloc[-1] - evolution_df['total_faits'].iloc[0]) 
                                  / evolution_df['total_faits'].iloc[0] * 100)
                
                st.metric(
                    "Variation totale",
                    f"{total_variation:+.1f}%",
                    delta=f"{evolution_df['total_faits'].iloc[-1] - evolution_df['total_faits'].iloc[0]:,.0f} faits"
                )
                
                st.metric(
                    "Année maximale",
                    f"{evolution_df.loc[evolution_df['total_faits'].idxmax(), 'annee']:.0f}",
                    delta=f"{evolution_df['total_faits'].max():,.0f} faits"
                )
                
                st.metric(
                    "Année minimale",
                    f"{evolution_df.loc[evolution_df['total_faits'].idxmin(), 'annee']:.0f}",
                    delta=f"{evolution_df['total_faits'].min():,.0f} faits"
                )
        
        # Heatmap par type et année
        if 'classe' in df_filtered.columns and 'annee' in df_filtered.columns:
            st.subheader("Carte de chaleur: Types de crimes par année")
            
            # Limiter aux 10 types les plus fréquents
            top_classes = df_filtered.groupby('classe')['faits'].sum().nlargest(10).index
            df_heatmap = df_filtered[df_filtered['classe'].isin(top_classes)]
            
            if len(df_heatmap) > 0:
                fig = create_heatmap(
                    df_heatmap,
                    x_column='annee',
                    y_column='classe',
                    value_column='faits',
                    title="Évolution des types de crimes"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # TAB 3: Cartographie
    with tab3:
        st.header("Cartographie de la criminalité")
        
        st.subheader("Carte choroplèthe par département")
        
        # Préparer les données pour la carte
        dept_stats = data_loader.get_department_stats(df_filtered)
        
        if len(dept_stats) > 0:
            # Options de visualisation
            col1, col2 = st.columns([3, 1])
            
            with col2:
                metric_choice = st.radio(
                    "Métrique à afficher",
                    ["Nombre absolu", "Taux pour 1000 hab."]
                )
            
            # Calculer le taux si nécessaire
            if metric_choice == "Taux pour 1000 hab.":
                population = load_population_data()
                dept_stats['population'] = dept_stats['code_dept'].map(population)
                dept_stats['taux'] = dept_stats.apply(
                    lambda row: calculate_crime_rate(row['total_faits'], row['population']) 
                    if pd.notna(row['population']) else 0,
                    axis=1
                )
                value_col = 'taux'
                title = "Taux de criminalité pour 1000 habitants par département"
            else:
                value_col = 'total_faits'
                title = "Nombre de faits par département"
            
            with col1:
                fig = create_choropleth_map(
                    dept_stats,
                    value_column=value_col,
                    title=title
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Tableau des données géographiques
            st.subheader("📊 Données par département")
            display_cols = ['code_dept', 'departement', 'total_faits']
            if 'taux' in dept_stats.columns:
                display_cols.append('taux')
            
            st.dataframe(
                dept_stats[display_cols].head(20),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Pas de données géographiques disponibles")
    
    # TAB 4: Comparaison
    with tab4:
        st.header("Comparaison entre départements")
        
        # Sélection des départements à comparer
        if 'departement' in df.columns:
            available_depts = sorted(df['departement'].unique().tolist())
            
            col1, col2 = st.columns(2)
            
            with col1:
                depts_to_compare = st.multiselect(
                    "Sélectionner les départements à comparer (max 5)",
                    available_depts,
                    max_selections=5
                )
            
            with col2:
                comparison_metric = st.selectbox(
                    "Métrique de comparaison",
                    ["Total des faits", "Évolution annuelle", "Types de crimes"]
                )
            
            if len(depts_to_compare) >= 2:
                # Filtrer les données
                df_comparison = df[df['departement'].isin(depts_to_compare)]
                
                if comparison_metric == "Total des faits":
                    st.subheader("Comparaison du nombre total de faits")
                    
                    dept_stats = data_loader.get_department_stats(df_comparison)
                    dept_codes = df[df['departement'].isin(depts_to_compare)]['code_dept'].unique()
                    
                    fig = create_comparison_chart(
                        dept_stats,
                        departments=dept_codes,
                        metric='total_faits',
                        title="Comparaison du nombre total de faits"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif comparison_metric == "Évolution annuelle":
                    st.subheader("Comparaison de l'évolution temporelle")
                    
                    import plotly.graph_objects as go
                    fig = go.Figure()
                    
                    for dept in depts_to_compare:
                        df_dept = df_comparison[df_comparison['departement'] == dept]
                        evolution = data_loader.get_temporal_evolution(df_dept)
                        
                        fig.add_trace(go.Scatter(
                            x=evolution['annee'],
                            y=evolution['total_faits'],
                            mode='lines+markers',
                            name=dept
                        ))
                    
                    fig.update_layout(
                        title="Évolution temporelle par département",
                        xaxis_title="Année",
                        yaxis_title="Nombre de faits",
                        height=500,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                else:  # Types de crimes
                    st.subheader("Comparaison par types de crimes")
                    
                    cols = st.columns(len(depts_to_compare))
                    
                    for idx, dept in enumerate(depts_to_compare):
                        with cols[idx]:
                            df_dept = df_comparison[df_comparison['departement'] == dept]
                            crime_dist = data_loader.get_crime_types_distribution(df_dept)
                            
                            st.markdown(f"**{dept}**")
                            if len(crime_dist) > 0:
                                fig = create_crime_types_pie_chart(
                                    crime_dist.head(5),
                                    title=f"Top 5 - {dept}"
                                )
                                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("👆 Sélectionnez au moins 2 départements pour la comparaison")
        else:
            st.warning("Les données de département ne sont pas disponibles")
    
    # TAB 5: Assistant IA
    with tab5:
        st.header("💬 Assistant IA d'analyse")
        
        st.markdown("""
        Posez des questions sur les données de criminalité. L'assistant IA peut vous aider à:
        - 📊 Analyser les tendances
        - 🔍 Comparer les territoires
        - 📝 Générer des rapports
        - 💡 Interpréter les statistiques
        """)
        
        # Zone de chat
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Chat")
            
            # Contexte des données
            data_context = get_data_summary(df_filtered)
            
            # Zone de saisie
            user_question = st.text_area(
                "Votre question:",
                placeholder="Ex: Quelle est la tendance de la criminalité à Paris ?",
                height=100
            )
            
            col_a, col_b = st.columns([1, 4])
            with col_a:
                ask_button = st.button("🤖 Poser la question", type="primary")
            with col_b:
                clear_button = st.button("🗑️ Effacer l'historique")
            
            if clear_button:
                chatbot.clear_history()
                st.success("Historique effacé")
                st.rerun()
            
            # Afficher la réponse
            if ask_button and user_question:
                with st.spinner("Analyse en cours..."):
                    response = chatbot.answer_question(
                        user_question,
                        data_context,
                        model=selected_model
                    )
                
                st.markdown("### 🤖 Réponse:")
                st.info(response)
        
        with col2:
            st.subheader("Actions rapides")
            
            # Générer une analyse de tendance
            if st.button("📈 Analyser les tendances", use_container_width=True):
                with st.spinner("Génération de l'analyse..."):
                    dept_code = None
                    if selected_dept != 'Tous' and 'code_dept' in df_filtered.columns:
                        dept_code = df_filtered[df_filtered['departement'] == selected_dept]['code_dept'].iloc[0]
                    
                    analysis = chatbot.analyze_trends(df_filtered, dept_code)
                    st.markdown("### 📊 Analyse des tendances:")
                    st.success(analysis)
            
            # Générer un rapport
            if st.button("📝 Générer un rapport", use_container_width=True):
                if selected_dept != 'Tous':
                    with st.spinner("Génération du rapport..."):
                        # Calculer les stats
                        df_dept = df[df['departement'] == selected_dept]
                        
                        if 'faits' not in df_dept.columns:
                            month_cols = [col for col in df_dept.columns if col.isdigit()]
                            if month_cols:
                                df_dept['faits'] = df_dept[month_cols].sum(axis=1)
                        
                        total = df_dept['faits'].sum()
                        
                        evolution_df = data_loader.get_temporal_evolution(df_dept)
                        evolution = evolution_df['evolution_pct'].iloc[-1] if len(evolution_df) > 1 else 0
                        
                        crime_dist = data_loader.get_crime_types_distribution(df_dept)
                        top_crime = crime_dist.iloc[0]['type_crime'] if len(crime_dist) > 0 else "N/A"
                        
                        stats = {
                            'total': total,
                            'evolution': evolution,
                            'top_crime': top_crime,
                            'year_start': selected_years[0] if 'annee' in df.columns else 'N/A',
                            'year_end': selected_years[1] if 'annee' in df.columns else 'N/A'
                        }
                        
                        report = chatbot.generate_report(
                            selected_dept,
                            stats,
                            model=selected_model
                        )
                        
                        st.markdown("### 📄 Rapport:")
                        st.success(report)
                else:
                    st.warning("Sélectionnez un département spécifique")
            
            st.divider()
            
            # Suggestions de questions
            st.markdown("**💡 Suggestions:**")
            suggestions = [
                "Quelle est la tendance générale ?",
                "Quel département est le plus sûr ?",
                "Quels sont les crimes les plus fréquents ?",
                "Comment expliquer l'évolution ?",
                "Quelles recommandations pour réduire la criminalité ?"
            ]
            
            for suggestion in suggestions:
                if st.button(suggestion, key=f"sug_{suggestion}", use_container_width=True):
                    with st.spinner("Analyse en cours..."):
                        response = chatbot.answer_question(
                            suggestion,
                            data_context,
                            model=selected_model
                        )
                    st.markdown("### 🤖 Réponse:")
                    st.info(response)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><strong>SafeCity Dashboard</strong> - Projet Open Data & IA</p>
        <p>Sources: data.gouv.fr | Ministère de l'Intérieur | INSEE</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
