```{r, echo=FALSE}
reticulate::use_python(Sys.which("python"), required = TRUE)
reticulate::py_install(c(
  "pandas",
  "numpy",
  "matplotlib",
  "seaborn"
), pip = TRUE)
```
