# ==============================================================================
# Script d'installation OPTIMISÉ - CARIS MEAL Pipeline
# ==============================================================================

# Forcer la désactivation de renv au sein de la session
options(renv.config.activate = FALSE)

# Utilisation du dépôt binaire de Posit pour Ubuntu Noble (très rapide)
# Cela évite de recompiler les packages à partir des sources
options(repos = c(PPM = "https://packagemanager.posit.co/cran/__linux__/noble/latest"))

packages <- c(
  "dplyr", "RMySQL", "odbc", "DBI", "viridis", "ggplot2", 
  "ggrepel", "ggthemes", "plotly", "stringr", "RColorBrewer", 
  "tidytext", "purrr", "lubridate", "tidyr", "scales", 
  "extrafont", "forcats", "DT", "data.table", "readxl", 
  "writexl", "reticulate", "knitr", "rmarkdown"
)

# Fonction d'installation via utils pour court-circuiter renv
install_if_missing <- function(p) {
  if (!require(p, character.only = TRUE, quietly = TRUE)) {
    message(paste("📦 Installation du package :", p))
    # Installation propre sans interférence
    utils::install.packages(p, dependencies = TRUE)
  }
}

# 1. Installation des packages de base
invisible(lapply(packages, install_if_missing))

# 2. Configuration spécifique pour RETICULATE
if (require(reticulate)) {
  message("🐍 Configuration de reticulate pour GitHub Actions...")
  # On force l'utilisation du Python système détecté par le workflow
  reticulate::use_python(Sys.which("python"), required = TRUE)
}

# 3. Gestion des polices (silencieux pour éviter les blocages de rendu)
if (require(extrafont)) {
  try({
    extrafont::font_import(prompt = FALSE)
    extrafont::loadfonts(device = "pdf", quiet = TRUE)
  }, silent = TRUE)
}

message("✅ Environnement R prêt pour Quarto.")