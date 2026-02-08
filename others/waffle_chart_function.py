import matplotlib.pyplot as plt
import pandas as pd

def create_waffle_share_chart_final(
    df: pd.DataFrame, # DataFrame contenant 'lab' et 'percent'
    share_color: str = "#f72585", 
    complement_color: str = "#7a0325",
    background_color: str = "#222725",
    title_text: str = "SHARE OF CEREALS USED AS ANIMAL FEEDS",
    credit_text: str = "Data OWID (year 2021) | Plot Benjamin Nowak",
    save_path: str = None
):
    """
    Génère un graphique Waffle empilé stylisé pour la visualisation des parts de données.
    
    Args:
        df (pd.DataFrame): DataFrame contenant au moins les colonnes 'lab' et 'percent'.
        share_color (str): Couleur pour la part représentée (ex: rose).
        complement_color (str): Couleur pour la part complémentaire (ex: rouge foncé).
        background_color (str): Couleur de fond de la figure.
        title_text (str): Texte du titre.
        credit_text (str): Texte de crédit.
        save_path (str, optional): Chemin pour sauvegarder la figure.
    """
    
    # --- 1. SIMULATION DES DÉPENDANCES ET PROPRIÉTÉS DE POLICE ---
    # La logique de chargement des polices est simulée.
    class MockFont:
        def __init__(self, name, weight=None): pass
    class MockWaffle:
        @staticmethod
        def make_waffle(ax, rows, columns, values, colors, **kwargs):
            # Créer un vrai graphique waffle avec des carrés
            total_squares = rows * columns  # 100 carrés au total
            share_squares = int(values[0])  # Nombre de carrés pour la valeur principale
            complement_squares = total_squares - share_squares
            
            # Créer la grille de carrés
            square_data = []
            
            # Ajouter les carrés pour la part principale (rose)
            for i in range(share_squares):
                row = i // columns
                col = i % columns
                square_data.append((row, col, colors[0]))
            
            # Ajouter les carrés pour la part complémentaire (rouge foncé)
            for i in range(share_squares, total_squares):
                row = i // columns
                col = i % columns
                square_data.append((row, col, colors[1]))
            
            # Dessiner chaque carré
            for row, col, color in square_data:
                # Position du carré (inversé pour que ça commence en haut à gauche)
                x = col
                y = rows - row - 1
                
                # Créer un rectangle pour chaque carré avec bordures fines
                rect = plt.Rectangle((x, y), 0.98, 0.98, facecolor=color, edgecolor=background_color, linewidth=0.3)
                ax.add_patch(rect)
            
            # Configurer les limites et supprimer les axes
            ax.set_xlim(-5, columns - 0.5)
            ax.set_ylim(-0.5, rows - 0.5)
            ax.set_aspect('equal')
            ax.axis('off')
    def mock_fig_text(x, y, s, color, fontsize, font=None, highlight_text_props=None, ha="left", **kwargs):
        # Traitement du texte avec mise en évidence
        if "ANIMAL FEEDS" in s:
            # Diviser le titre pour mettre en évidence "ANIMAL FEEDS"
            parts = s.split("ANIMAL FEEDS")
            fig = plt.gcf()
            fig.text(x, y, parts[0], color=color, fontsize=fontsize, ha=ha, weight='bold', **kwargs)
            # Calculer la position pour "ANIMAL FEEDS" en rose
            text_width = len(parts[0]) * 0.012  # Estimation approximative
            fig.text(x + text_width, y, "ANIMAL FEEDS", color=share_color, fontsize=fontsize, ha=ha, weight='bold', **kwargs)
            if len(parts) > 1 and parts[1]:
                fig.text(x + text_width + len("ANIMAL FEEDS") * 0.012, y, parts[1], color=color, fontsize=fontsize, ha=ha, weight='bold', **kwargs)
        else:
            # Traitement normal pour les crédits
            if "Data" in s and "Plot" in s:
                # Mise en évidence pour Data et Plot
                plt.gcf().text(x, y, s, color=color, fontsize=fontsize, ha=ha, weight='normal', **kwargs)
            else:
                plt.gcf().text(x, y, s, color=color, fontsize=fontsize, ha=ha, **kwargs)

    Waffle = MockWaffle
    fig_text = mock_fig_text
    
    # Polices de substitution pour Matplotlib (résout le TypeError)
    FONT_PROPS_TITLE = {'family': 'sans-serif', 'weight': 'bold', 'fontsize': 22}
    FONT_PROPS_BOLD = {'family': 'sans-serif', 'weight': 'bold', 'fontsize': 13}
    FONT_PROPS_LIGHT = {'family': 'sans-serif', 'weight': 'light', 'fontsize': 13}

    # Objets de police Mock (utilisés dans les arguments de fig_text)
    font_title = MockFont("Staatliches")
    font_credit = MockFont("Raleway", weight="light")
    bold_font_credit = MockFont("Raleway", weight="bold")


    # --- 2. INITIALISATION DE LA FIGURE ET DES AXES ---
    number_of_bars = len(df)
    if number_of_bars == 0:
        print("Le DataFrame est vide.")
        return

    fig, axs = plt.subplots(
        nrows=number_of_bars, 
        ncols=1, 
        figsize=(16, number_of_bars * 3), 
        dpi=300,
        gridspec_kw={'hspace': 0.4} # Espace entre les graphiques
    )
    
    fig.set_facecolor(background_color)
    
    # Assurer que axs est une liste même s'il n'y a qu'une seule barre
    if number_of_bars == 1:
        axs = [axs]

    # --- 3. BOUCLE DE TRACÉ ET D'ANNOTATION ---
    for i, (index, row) in enumerate(df.iterrows()):
        ax = axs[i]
        
        share = row["percent"]
        values = [share, 100 - share]
        
        # Le fond de chaque axe doit être défini pour la couleur "noire"
        ax.set_facecolor(background_color) 

        # 3.1. Création du Waffle (avec les couleurs personnalisées)
        rows = 4
        columns = 25
        Waffle.make_waffle(
            ax=ax,
            rows=rows,
            columns=columns,
            values=values,
            colors=[share_color, complement_color],
        )
        
        # 3.2. Annotation du Continent (texte en gras)
        ax.text(
            x=-4,
            y=rows/2 - 0.5,
            s=f"{row['lab']}",
            fontsize=14,
            fontweight='bold',
            color="white",
            rotation=90,
            ha="center",
            va="center",
        )
        
        # 3.3. Annotation du Pourcentage (texte clair)
        ax.text(
            x=-2,
            y=rows/2 - 0.5,
            s=f"{share}%",
            fontsize=12,
            fontweight='normal',
            color="white",
            rotation=90,
            ha="center",
            va="center",
        )
    
    # --- 4. TITRE ET CRÉDITS ---
    
    # Titre principal
    fig_text(
        x=0.05,
        y=0.95,
        s=title_text,
        color="white",
        fontsize=14,
        ha="left"
    )
    
    # Crédits
    fig_text(
        x=0.05,
        y=0.02,
        s=credit_text,
        color="white",
        fontsize=9, 
        ha="left"
    )

    # --- 5. AFFICHAGE / SAUVEGARDE ---
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return f"Graphique sauvegardé à : {save_path}"
    else:
        plt.show()
        return fig


def plot_nutrition_beneficiaries(df, category_col, title="Bénéficiaires par catégorie"):
    """
    Fonction simplifiée pour visualiser les bénéficiaires nutrition par catégorie.
    
    Args:
        df: DataFrame avec les données
        category_col: Colonne de catégorisation  
        title: Titre du graphique
    """
    if df.empty:
        print("Pas de données disponibles")
        return
    
    import seaborn as sns
    
    # Compter par catégorie
    counts = df[category_col].value_counts()
    
    # Créer le graphique
    plt.figure(figsize=(10, 12))
    ax = sns.barplot(x=counts.values, y=counts.index, palette="viridis")
    
    # Ajouter les valeurs sur les barres
    for i, v in enumerate(counts.values):
        ax.text(v + 0.1, i, str(v), va='center', fontweight='bold')
    
    plt.title(f"{title}\nTotal: {len(df)}", fontweight='bold')
    plt.xlabel('Nombre de bénéficiaires')
    plt.ylabel(category_col.replace('_', ' ').title())
    plt.tight_layout()
    plt.show()


# --- Exemple d'utilisation (avec données simulées) ---
if __name__ == "__main__":
    # Test de la fonction waffle
    df_data = pd.DataFrame({
        'lab': ['Af', 'Ame', 'Asia', 'Eur', 'Ocea'],
        'percent': [21, 53, 32, 66, 59]
    })
    
    create_waffle_share_chart_final(df=df_data)
    
    # Test de la fonction nutrition
    df_nutrition = pd.DataFrame({
        'username': ['Agent1', 'Agent2', 'Agent1', 'Agent3', 'Agent2'],
        'manutrition_type': ['MAM', 'MAS', 'MAM', 'Normal', 'MAS']
    })
    
    plot_nutrition_beneficiaries(df_nutrition, 'username', 'Bénéficiaires par agent')

    # Exemple pour les données nutrition
    df_nutrition = pd.DataFrame({
        'lab': ['MAM', 'MAS', 'Normal'],
        'percent': [30, 45, 25]
    })

    create_waffle_share_chart_final(
        df=df_nutrition,
        title_text="RÉPARTITION DES TYPES DE MALNUTRITION",
        credit_text="Data: Programme Nutrition CARIS | Plot: Dashboard M&E"
    )