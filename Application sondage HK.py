# coding: utf-8
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="🧮 Analyse & Échantillonnage", layout="wide")

st.title("📊 Analyse de données & Tirage d'échantillon")

# === MENU LATÉRAL ===
st.sidebar.header("🧭 Navigation")
show_data = st.sidebar.checkbox("Aperçu des données")
show_description = st.sidebar.checkbox("Analyse descriptive")
show_distribution = st.sidebar.checkbox("Visualisation des répartitions")
show_uniques = st.sidebar.checkbox("Combinaisons uniques")
show_sampling = st.sidebar.checkbox("Calcul d'échantillon (Cochran)")
show_draw = st.sidebar.checkbox("Tirage d'échantillon")
show_poll = st.sidebar.checkbox("Mini-sondage")

# === CHARGEMENT DES DONNÉES ===
fichier = st.sidebar.file_uploader("📁 Charger un fichier CSV ou Excel", type=["csv", "xlsx"])
if fichier:
    df = pd.read_csv(fichier) if fichier.name.endswith(".csv") else pd.read_excel(fichier)

    if show_data:
        st.subheader("📄 Aperçu des données")
        st.dataframe(df.head())

    if show_description:
        st.subheader("📈 Statistiques descriptives")
        st.write(df.describe(include='all'))




    if show_distribution:
        st.subheader("📊 Répartition des individus par modalités")

        var_cat = df.select_dtypes(include=['object', 'category']).columns.tolist()
        selected_vars = st.multiselect("Choisis les variables à analyser", var_cat)

        if selected_vars:
            for var in selected_vars:
                st.markdown(f"### 🔹 Répartition pour : `{var}`")

                # Répartition des modalités
                repartition = df[var].value_counts().reset_index()
                repartition.columns = [var, 'Effectif']

                # Affichage du graphique
                fig, ax = plt.subplots()
                sns.barplot(data=repartition, y=var, x='Effectif', palette="Blues_d", ax=ax)
                ax.set_title(f"Distribution de {var}")
                st.pyplot(fig)

                # Affichage du tableau
                st.dataframe(repartition)

                # Téléchargement du tableau
                csv = repartition.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Télécharger la répartition de `{var}` (CSV)",
                    data=csv,
                    file_name=f"repartition_{var}.csv",
                    mime='text/csv'
                )



    if show_uniques:
        st.subheader("🔍 Combinaisons uniques")
        colonnes_selection = st.multiselect("Sélectionne les colonnes", df.columns.tolist())
        if colonnes_selection:
            uniques_df = df[colonnes_selection].drop_duplicates()
            st.success(f"✅ {len(uniques_df)} combinaisons uniques trouvées.")
            st.dataframe(uniques_df)
            csv = uniques_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger (CSV)", data=csv, file_name="valeurs_uniques.csv", mime='text/csv')

    if show_sampling:
        st.subheader("📐 Calcul de taille d’échantillon (Formule de Cochran)")
        z = st.number_input("Score Z (ex : 1.96)", value=1.96)
        p = st.number_input("Proportion estimée p", min_value=0.0, max_value=1.0, value=0.5)
        e = st.number_input("Marge d’erreur e", min_value=0.001, max_value=1.0, value=0.05)
        N = st.number_input("Taille de la population (0 si infinie)", min_value=0, value=0)
        if st.button("📊 Calculer"):
            n0 = (z**2 * p * (1-p)) / (e**2)
            if N > 0:
                n = n0 / (1 + ((n0 - 1) / N))
                st.success(f"📋 Taille corrigée (population finie) : {int(n)}")
            else:
                st.success(f"📋 Taille estimée (population infinie) : {int(n0)}")

    if show_draw:
        st.subheader("🎲 Tirage d’un échantillon")
        type_tirage = st.selectbox("Type de tirage", ["Aléatoire simple", "Stratifié proportionnel"])
        if type_tirage == "Aléatoire simple":
            taille = st.number_input("Taille de l’échantillon", 1, len(df), min(100, len(df)))
            if st.button("🎯 Tirer un échantillon"):
                echantillon = df.sample(n=taille, random_state=42)
                st.success(f"✅ {taille} lignes tirées aléatoirement.")
                st.dataframe(echantillon)
                st.download_button("📥 Télécharger (CSV)", echantillon.to_csv(index=False), "echantillon.csv")
        elif type_tirage == "Stratifié proportionnel":
            colonnes_cat = df.select_dtypes(include='object').columns.tolist()
            if colonnes_cat:
                var_strat = st.selectbox("Variable de stratification", colonnes_cat)
                taille_strat = st.number_input("Taille totale de l’échantillon", 1, len(df), min(100, len(df)))
                if st.button("📊 Tirer l’échantillon stratifié"):
                    echantillon = df.groupby(var_strat, group_keys=False)\
                                    .apply(lambda x: x.sample(frac=taille_strat/len(df), random_state=42))
                    st.success(f"✅ {len(echantillon)} lignes tirées proportionnellement à '{var_strat}'.")
                    st.dataframe(echantillon)
                    st.download_button("📥 Télécharger (CSV)", echantillon.to_csv(index=False), "echantillon_stratifie.csv")
            else:
                st.warning("Aucune variable catégorielle disponible.")

    if show_poll:
        st.subheader("🗳️ Mini-sondage")
        nom = st.text_input("Ton nom")
        satisfaction = st.radio("Es-tu satisfait de l'application ?", ["Oui", "Non", "Peut-être"])
        if st.button("✅ Envoyer"):
            st.success(f"Merci **{nom}** pour ta réponse : _{satisfaction}_ 🎉")

else:
    st.info("⏳ Charge un fichier pour commencer.")

