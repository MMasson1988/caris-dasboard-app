# Script pour mettre à jour renv.lock avec les packages nécessaires

cat("🔧 Mise à jour de renv avec les packages nécessaires...\n")

# Liste des packages nécessaires
packages_needed <- c(
  'dplyr', 'ggplot2', 'plotly', 'DT', 'data.table',
  'readxl', 'writexl', 'reticulate', 'viridis', 
  'scales', 'lubridate', 'tidyr', 'forcats', 'RMySQL',
  'odbc', 'DBI', 'ggrepel', 'ggthemes',
  'stringr', 'RColorBrewer', 'tidytext', 'purrr', 'extrafont'
)

# Installer les packages manquants
cat("📦 Installation des packages manquants...\n")
for (pkg in packages_needed) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    cat("Installation de", pkg, "\n")
    renv::install(pkg)
  }
}

# Mettre à jour le snapshot
cat("📸 Mise à jour du renv.lock...\n")
renv::snapshot(confirm = FALSE)

cat("✅ renv.lock mis à jour avec", length(packages_needed), "packages\n")