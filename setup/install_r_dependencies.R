# Script R pour l'installation des packages via renv dans GitHub Actions
cat("Initialisation de renv...\n")

# Installer renv si necessaire
if (!require('renv', quietly = TRUE)) {
  install.packages('renv', repos = 'https://cran.rstudio.com/')
}

# Restaurer les packages depuis renv.lock
cat("Restauration des packages R depuis renv.lock...\n")
renv::restore(confirm = FALSE)

# Verifier que les packages essentiels sont installes
cat("Verification de l installation des packages...\n")
essential_packages <- c( 'DT', 'readxl', 'writexl', 'viridis', 'tidyr', 'dplyr', 'ggplot2', 'lubridate', 'data.table', 'reticulate')
missing <- c()
for (pkg in essential_packages) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    missing <- c(missing, pkg)
  }
}

if (length(missing) > 0) {
  cat("ERROR: Packages essentiels manquants:", paste(missing, collapse = ', '), "\n")
  stop("Installation de packages R echouee")
} else {
  cat("SUCCESS: Tous les packages essentiels sont installes!\n")
}