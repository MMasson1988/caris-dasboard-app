"""
Page Rapport HTML - Intégration du rapport Quarto
Utilise une technique avancée d'injection JavaScript pour créer un vrai modal popup
"""
import streamlit as st
from pathlib import Path
import base64


def create_modal_script(html_content: str) -> str:
    """
    Crée un script JavaScript qui injecte un modal dans le DOM parent de Streamlit.
    Cette technique contourne les limitations des iframes Streamlit.
    Utilise un encodage UTF-8 compatible avec JavaScript.
    """
    # Encoder le HTML en base64 avec support UTF-8
    # On utilise encodeURIComponent côté JS pour décoder correctement les accents
    import urllib.parse
    encoded_content = urllib.parse.quote(html_content, safe='')
    
    return f"""
    <script>
    (function() {{
        // Accéder au document parent (fenêtre Streamlit principale)
        var parentDoc = window.parent.document;
        
        // Vérifier si le modal existe déjà
        var existingModal = parentDoc.getElementById('rapport-modal-overlay');
        if (existingModal) {{
            existingModal.remove();
        }}
        
        // Créer le style CSS pour le modal
        var style = parentDoc.createElement('style');
        style.id = 'rapport-modal-style';
        style.textContent = `
            #rapport-modal-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-color: rgba(0, 0, 0, 0.85);
                z-index: 999999;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                padding: 15px;
                box-sizing: border-box;
                animation: fadeIn 0.3s ease-out;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            #rapport-modal-header {{
                width: 100%;
                max-width: 95vw;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
                padding: 10px 20px;
                background: linear-gradient(135deg, #2E8B57, #228B22);
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }}
            #rapport-modal-title {{
                color: white;
                font-size: 1.3rem;
                font-weight: bold;
                margin: 0;
            }}
            #rapport-modal-close {{
                background: linear-gradient(135deg, #dc3545, #c82333);
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 1rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.2s ease;
                box-shadow: 0 2px 10px rgba(220,53,69,0.4);
            }}
            #rapport-modal-close:hover {{
                transform: scale(1.05);
                box-shadow: 0 4px 15px rgba(220,53,69,0.6);
            }}
            #rapport-modal-content {{
                width: 100%;
                max-width: 95vw;
                height: calc(100vh - 100px);
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            }}
            #rapport-modal-iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}
        `;
        
        // Supprimer l'ancien style s'il existe
        var oldStyle = parentDoc.getElementById('rapport-modal-style');
        if (oldStyle) oldStyle.remove();
        parentDoc.head.appendChild(style);
        
        // Créer le modal
        var modal = parentDoc.createElement('div');
        modal.id = 'rapport-modal-overlay';
        modal.innerHTML = `
            <div id="rapport-modal-header">
                <h3 id="rapport-modal-title">📄 Rapport Nutrition - Mode Plein Écran</h3>
                <button id="rapport-modal-close" onclick="document.getElementById('rapport-modal-overlay').remove();">
                    ✕ Fermer (Échap)
                </button>
            </div>
            <div id="rapport-modal-content">
                <iframe id="rapport-modal-iframe"></iframe>
            </div>
        `;
        
        // Ajouter le modal au body parent
        parentDoc.body.appendChild(modal);
        
        // Décoder le HTML avec support UTF-8 complet
        var iframe = parentDoc.getElementById('rapport-modal-iframe');
        var htmlContent = decodeURIComponent('{encoded_content}');
        iframe.srcdoc = htmlContent;
        
        // Fermer avec Escape
        var escHandler = function(e) {{
            if (e.key === 'Escape') {{
                var m = parentDoc.getElementById('rapport-modal-overlay');
                if (m) m.remove();
                parentDoc.removeEventListener('keydown', escHandler);
            }}
        }};
        parentDoc.addEventListener('keydown', escHandler);
        
        // Fermer en cliquant sur l'overlay (pas sur le contenu)
        modal.addEventListener('click', function(e) {{
            if (e.target === modal) {{
                modal.remove();
            }}
        }});
    }})();
    </script>
    """


def render_rapport():
    """Affiche le rapport HTML Quarto intégré."""
    
    st.title("📄 Rapport Nutrition Institutionnel")
    st.markdown("---")
    
    st.markdown("""
    <div style='background-color: #e8f5e9; padding: 15px; border-radius: 10px; border-left: 4px solid #2E8B57; margin-bottom: 20px;'>
        <h4 style='margin: 0; color: #2E8B57;'>ℹ️ À propos de ce rapport</h4>
        <p style='margin: 10px 0 0 0;'>
            Ce rapport est généré automatiquement via Quarto et contient l'analyse complète 
            du programme nutrition pour les bailleurs et la direction.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chemin vers le rapport HTML
    base_path = Path(__file__).parent.parent.parent
    rapport_paths = [
        base_path / "_site" / "tracking-nutrition.html",
        base_path / "tracking-nutrition.html",
        base_path / "rapport_nutrition.html"
    ]
    
    rapport_path = None
    for path in rapport_paths:
        if path.exists():
            rapport_path = path
            break
    
    if rapport_path and rapport_path.exists():
        # Lire le contenu pour le bouton plein écran
        try:
            with open(rapport_path, 'r', encoding='utf-8') as f:
                html_content_full = f.read()
        except:
            html_content_full = None
        
        # État pour déclencher le popup
        if "trigger_popup" not in st.session_state:
            st.session_state.trigger_popup = False
        
        # Mode normal - Options d'affichage
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.info(f"📂 Rapport chargé depuis: `{rapport_path.relative_to(base_path)}`")
        
        with col2:
            # Bouton télécharger
            if html_content_full:
                st.download_button(
                    label="📥 Télécharger",
                    data=html_content_full,
                    file_name="rapport_nutrition.html",
                    mime="text/html",
                    use_container_width=True
                )
        
        with col3:
            # Bouton pour ouvrir le popup modal
            if st.button("🔗 Plein écran", use_container_width=True):
                st.session_state.trigger_popup = True
        
        # Si le popup est déclenché, injecter le JavaScript
        if st.session_state.trigger_popup and html_content_full:
            # Injecter le script qui crée le modal dans le parent
            modal_script = create_modal_script(html_content_full)
            st.components.v1.html(modal_script, height=0)
            # Réinitialiser le trigger
            st.session_state.trigger_popup = False
        
        # Afficher le rapport dans un iframe (version normale)
        st.markdown("### 📊 Rapport Complet")
        
        # Lire le contenu HTML
        try:
            with open(rapport_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Afficher dans un iframe scrollable
            st.components.v1.html(
                f"""
                <div style="width: 100%; height: 600px; overflow: auto; border: 1px solid #ddd; border-radius: 10px;">
                    <iframe 
                        srcdoc="{html_content.replace('"', '&quot;')}" 
                        width="100%" 
                        height="100%" 
                        frameborder="0"
                        style="border: none;">
                    </iframe>
                </div>
                """,
                height=620
            )
            
        except Exception as e:
            st.warning(f"Impossible d'afficher le rapport directement: {e}")
            
            # Alternative: afficher un lien de téléchargement
            with open(rapport_path, 'rb') as f:
                st.download_button(
                    label="📥 Télécharger le rapport HTML",
                    data=f.read(),
                    file_name="rapport_nutrition.html",
                    mime="text/html"
                )
    
    else:
        st.warning("""
        ⚠️ **Rapport non trouvé**
        
        Le rapport HTML Quarto n'a pas été généré ou n'est pas accessible.
        
        Pour générer le rapport, exécutez la commande suivante dans le terminal:
        
        ```bash
        quarto render tracking-nutrition.qmd
        ```
        
        Fichiers recherchés:
        - `_site/tracking-nutrition.html`
        - `tracking-nutrition.html`
        - `rapport_nutrition.html`
        """)
        
        # Proposer de générer le rapport
        st.markdown("---")
        st.markdown("### 🔧 Actions")
        
        if st.button("🚀 Générer le rapport (si Quarto est installé)", use_container_width=True):
            import subprocess
            try:
                result = subprocess.run(
                    ["quarto", "render", "tracking-nutrition.qmd"],
                    cwd=str(base_path),
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    st.success("✅ Rapport généré avec succès! Rechargez la page.")
                    st.rerun()
                else:
                    st.error(f"Erreur lors de la génération:\n```\n{result.stderr}\n```")
                    
            except FileNotFoundError:
                st.error("❌ Quarto n'est pas installé ou n'est pas dans le PATH.")
            except subprocess.TimeoutExpired:
                st.error("❌ Timeout lors de la génération du rapport.")
            except Exception as e:
                st.error(f"❌ Erreur: {e}")
    
    # Informations supplémentaires
    st.markdown("---")
    st.markdown("### 📋 Informations sur le rapport")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown("""
        **Contenu du rapport:**
        - 📊 Statistiques de dépistage
        - 👶 Suivi des enrôlements
        - 📈 Tendances temporelles
        - 🏢 Analyse par bureau
        - 📍 Couverture géographique
        """)
    
    with col_info2:
        st.markdown("""
        **Format et destination:**
        - 📄 Format: HTML autonome
        - 🎯 Audience: Bailleurs, Direction
        - 📅 Fréquence: Mensuelle
        - 🔒 Confidentialité: Interne
        """)
