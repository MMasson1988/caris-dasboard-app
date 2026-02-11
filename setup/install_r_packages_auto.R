# ============================================================================
# INSTALLATION AUTOMATIQUE DES PACKAGES R - caris-dashboard-app
# ============================================================================

# Packages R détectés dans le projet
required_packages <- c(
  # === BASE R ET DONNÉES ===
  "base", "utils", "stats", "graphics", "datasets",
  
  # === TRAITEMENT DONNÉES ===
  "dplyr", "tidyr", "readr", "readxl", "writexl",
  "data.table", "tibble", "purrr", "stringr",
  
  # === VISUALISATION ===
  "ggplot2", "plotly", "DT", "htmlwidgets",
  "leaflet", "shiny", "shinydashboard",
  
  # === QUARTO ET RAPPORTS ===
  "rmarkdown", "knitr", "quarto", "flexdashboard",
  
  # === DATES ET TEMPS ===
  "lubridate", "hms",
  
  # === BASE DE DONNÉES ===
  "DBI", "RMySQL", "odbc", "RODBC",
  
  # === STATISTIQUES ===
  "broom", "modelr", "forcats",
  
  # === UTILITAIRES ===
  "here", "fs", "glue", "magrittr",
  
  # === DÉVELOPPEMENT ===
  "devtools", "usethis", "testthat"
)

# Installer renv si nécessaire
if (!require(renv, quietly = TRUE)) {
  install.packages("renv")
}

# Initialiser renv si nécessaire
if (!file.exists("renv.lock") || !dir.exists("renv")) {
  cat("🔧 Initialisation de renv...\n")
  renv::init(restart = FALSE)
}

# Activer renv
renv::activate()

# Fonction pour installer les packages manquants
install_if_missing <- function(packages) {
  for (pkg in packages) {
    if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
      cat(paste("📦 Installation de", pkg, "...\n"))
      try({
        renv::install(pkg)
      }, silent = FALSE)
    } else {
      cat(paste("✅", pkg, "déjà installé\n"))
    }
  }
}

# Installer tous les packages
cat("🚀 Installation des packages R...\n")
install_if_missing(required_packages)

# Sauvegarder l'état
cat("💾 Sauvegarde de l'environnement renv...\n")
renv::snapshot()

cat("✅ Configuration R terminée!\n")
