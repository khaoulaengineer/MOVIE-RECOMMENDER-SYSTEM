import streamlit as st
import pandas as pd
import pickle

st.set_page_config(page_title="🎬 Movie Recommender", page_icon="🎬", layout="wide")

st.markdown('''
<style>
.main {padding: 2rem;}
h1 {color: #E50914; text-align: center; font-size: 3rem;}
.movie-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 5px solid #E50914;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.stButton>button {
    background-color: #E50914;
    color: white;
    font-size: 1.1rem;
    padding: 0.75rem 2rem;
    border-radius: 5px;
    width: 100%;
}
.stButton>button:hover {background-color: #b20710;}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    with open('movie_similarity.pkl', 'rb') as f:
        similarity_matrix = pickle.load(f)
    movies = pd.read_csv('movies_list.csv')
    return similarity_matrix, movies

try:
    similarity_matrix, movies = load_data()
    st.success(f"✅ {len(movies)} films chargés avec succès !")
except Exception as e:
    st.error(f"❌ Erreur de chargement : {str(e)}")
    st.stop()

def get_recommendations(movie_title, n_recommendations=10):
    # Debug : afficher ce qu'on cherche
    st.write(f"🔍 Recherche de : '{movie_title}'")
    
    # Recherche exacte
    exact_match = movies[movies['title'] == movie_title]
    
    if exact_match.empty:
        st.warning(f"⚠️ Film '{movie_title}' non trouvé exactement")
        # Essayer une recherche partielle
        partial_match = movies[movies['title'].str.contains(movie_title, case=False, na=False)]
        if not partial_match.empty:
            st.info(f"Films similaires trouvés : {partial_match['title'].tolist()[:5]}")
        return None
    
    movie_id = exact_match.iloc[0]['movie_id']
    movie_name = exact_match.iloc[0]['title']
    
    st.write(f"✅ Film trouvé : {movie_name} (ID: {movie_id})")
    
    # Vérifie si dans la matrice
    if movie_id not in similarity_matrix.columns:
        st.error(f"❌ Film ID {movie_id} pas dans la matrice de similarité")
        st.write(f"IDs disponibles : {list(similarity_matrix.columns)[:10]}...")
        return None
    
    st.write(f"✅ Film dans la matrice de similarité")
    
    # Calcul des recommandations
    similar_scores = similarity_matrix[movie_id].sort_values(ascending=False)
    similar_scores = similar_scores[similar_scores.index != movie_id]
    top_similar = similar_scores.head(n_recommendations)
    
    st.write(f"✅ {len(top_similar)} recommandations trouvées")
    
    recommendations = pd.DataFrame({
        'movie_id': top_similar.index,
        'similarity_score': top_similar.values
    })
    
    recommendations = pd.merge(recommendations, movies[['movie_id', 'title']], on='movie_id')
    return recommendations, movie_name

st.markdown("<h1>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Découvre des films similaires à tes préférés !</p>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("### 📊 Statistiques")
    st.metric("Films disponibles", f"{len(movies):,}")
    st.metric("Algorithme", "Collaborative Filtering")
    st.markdown("---")
    st.info("1. Sélectionne un film\n2. Clique sur 'Recommander'\n3. Découvre des films similaires !")
    
    # Debug info
    with st.expander("🔧 Debug Info"):
        st.write(f"Colonnes movies : {movies.columns.tolist()}")
        st.write(f"Premiers films : {movies['title'].head().tolist()}")
        st.write(f"Matrice shape : {similarity_matrix.shape}")

with col1:
    st.markdown("### 🔍 Recherche de film")
    movie_list = [""] + sorted(movies['title'].tolist())
    selected_movie = st.selectbox("Tape ou sélectionne un film :", options=movie_list, index=0)
    n_recs = st.slider("Nombre de recommandations :", min_value=5, max_value=20, value=10)
    recommend_button = st.button("🎯 Obtenir des recommandations")

if recommend_button:
    if selected_movie == "":
        st.warning("⚠️ Veuillez sélectionner un film d'abord !")
    else:
        st.markdown("---")
        st.markdown("### 🔍 Processus de recherche")
        
        result = get_recommendations(selected_movie, n_recs)
        
        if result is None:
            st.error(f"❌ Impossible de générer des recommandations pour '{selected_movie}'")
        else:
            recommendations, actual_movie_name = result
            
            st.markdown("---")
            st.markdown(f"<h2 style='text-align: center; color: #E50914;'>🎬 Si vous aimez '{actual_movie_name}'...</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #666;'>Vous aimerez aussi ces {len(recommendations)} films :</p>", unsafe_allow_html=True)
            st.markdown("")
            
            for idx, row in recommendations.iterrows():
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.markdown(f'''
                        <div class="movie-card">
                            <div style="font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;">
                                {idx + 1}. {row['title']}
                            </div>
                            <div style="color: #666;">
                                💯 Score de similarité : {row['similarity_score']:.1%}
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                with col_b:
                    st.write("")
                    st.write("")
                    st.progress(float(row['similarity_score']))
            
            st.success(f"✅ {len(recommendations)} films recommandés avec succès !")
            avg_similarity = recommendations['similarity_score'].mean()
            st.info(f"📊 Score de similarité moyen : {avg_similarity:.1%}")

with st.sidebar:
    st.markdown("### 👨‍💻 À propos")
    st.markdown("""
    **Créé par :** [Ton Nom]
    
    **Technologies :**
    - Python 🐍
    - Scikit-learn
    - Streamlit
    - Pandas
    
    **Dataset :** MovieLens 100K
    
    **Algorithme :** Collaborative Filtering
    """)

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #999; padding: 20px;'>
        <p>🎬 Movie Recommender System | Créé avec ❤️ et Python</p>
        <p>Projet d'Ingénierie des Données - 2025</p>
    </div>
""", unsafe_allow_html=True)
