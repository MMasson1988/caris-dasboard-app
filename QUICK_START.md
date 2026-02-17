# 🚀 Quick Start Guide - Workflow Automation

## What Was Created

✅ **New Branch:** `workflow-automation-fresh`  
✅ **Unified Workflow:** `.github/workflows/unified-pipeline-deploy.yml`  
✅ **This Guide:** `QUICK_START.md`

## How It Works

### Automatic Execution Flow

```
1. Push changes → 2. Run pipelines → 3. Render QMD → 4. Commit results
```

**Triggers automatically when you push changes to:**
- Any Python file in `script/` folder
- Any `.qmd` file in root directory
- Any file in `data/` folder

### What Gets Executed

**6 Python Pipelines:**
1. `script/call-pipeline.py`
2. `script/garden_pipeline.py`
3. `script/muso_pipeline.py`
4. `script/nutrition_pipeline.py`
5. `script/oev_pipeline.py`
6. `script/ptme_pipeline.py`

**6 QMD Reports:**
1. `tracking-call.qmd`
2. `tracking-gardening.qmd`
3. `tracking-muso.qmd`
4. `tracking-nutrition.qmd`
5. `tracking-oev.qmd`
6. `tracking-ptme.qmd`

## Using the Workflow

### Option 1: Automatic Trigger (Recommended)

Simply push your changes:

```bash
# Make changes to a pipeline or QMD file
git add script/nutrition_pipeline.py
git commit -m "Update nutrition pipeline"
git push
```

The workflow will automatically:
1. ✅ Run all pipelines
2. ✅ Generate reports
3. ✅ Commit results back to repo

### Option 2: Manual Trigger

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Unified Pipeline & Deployment**
4. Click **Run workflow** button
5. Choose branch and click **Run workflow**

## Viewing Results

### On GitHub

1. Go to **Actions** tab
2. Click on latest workflow run
3. View execution logs and summary

### Locally

After workflow completes:

```bash
# Pull latest changes (includes generated outputs)
git pull

# View outputs
ls outputs/NUTRITION/
ls _site/

# Open HTML reports
open tracking-nutrition.html
```

## Generated Files

### Pipeline Outputs
```
outputs/
├── NUTRITION/
│   ├── depistage_filtered.xlsx
│   ├── enroled_final.xlsx
│   └── ...
├── MUSO/
├── GARDEN/
├── OEV/
└── PTME/
```

### Rendered Reports
```
tracking-nutrition.html
tracking-muso.html
tracking-gardening.html
tracking-oev.html
tracking-ptme.html
tracking-call.html

_site/
├── index.html
└── ...
```

## Next Steps

### Merge to Main

Once tested and working:

```bash
# Push workflow-automation-fresh branch
git push origin workflow-automation-fresh

# Create pull request on GitHub or merge locally:
git checkout main
git merge workflow-automation-fresh
git push origin main
```

---

**Branch:** `workflow-automation-fresh`  
**Created:** 2025-02-17  
**Status:** ✅ Ready to use
