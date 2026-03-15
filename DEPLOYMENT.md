# Deployment Guide: GitHub & Streamlit Community Cloud

This guide walks you through the steps to take your `CombinedMarketAnalyzer` from your local machine, push it to GitHub, and deploy it live on the internet for free using Streamlit Community Cloud.

---

## Step 1: Prepare Your Project for Git

Before pushing to GitHub, you need to make sure you don't accidentally upload large cache files or your local virtual environment.

1. Open your terminal and navigate to your project folder:
   ```bash
   cd c:/Users/leyea/Documents/VibeCoding/Qwen/CombinedMarketAnalyzer
   ```

2. Create a `.gitignore` file. I have already created one for you, or you can create it with the following content:
   ```text
   # .gitignore
   __pycache__/
   *.py[cod]
   *$py.class
   .venv/
   venv/
   ENV/
   env/
   .qwen_combined_analyzer/
   cache/
   .pytest_cache/
   .streamlit/
   *.xlsx
   *.csv
   ```

## Step 2: Upload to GitHub

If you haven't already, create a free account on [GitHub](https://github.com/).

1. **Create a New Repository on GitHub:**
   - Go to github.com and click the **"+"** icon in the top right to select **"New repository"**.
   - Name it `CombinedMarketAnalyzer` (or whatever you prefer).
   - Keep it **Public** (Streamlit Community Cloud requires public repos for free tier apps).
   - Do **NOT** check "Add a README file" or "Add .gitignore" (we are pushing an existing project).
   - Click **Create repository**.

2. **Initialize Git Locally and Push:**
   Open your terminal (inside the `CombinedMarketAnalyzer` folder) and run these exact commands. *Note: Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with the actual URL GitHub gives you on the next page.*

   ```bash
   # Initialize an empty git repository
   git init

   # Add all your files to staging (respecting the .gitignore)
   git add .

   # Commit the files with a message
   git commit -m "Initial commit for Combined Market Analyzer"

   # Change the default branch name to main
   git branch -M main

   # Link your local folder to your new GitHub repository
   git remote add origin https://github.com/YOUR_USERNAME/CombinedMarketAnalyzer.git

   # Push your code up to GitHub
   git push -u origin main
   ```

   *If you've never used Git on this computer before, it might ask you to log in to GitHub during the `git push` step.*

---

## Step 3: Deploy to Streamlit Community Cloud

Now that your code is safely on GitHub, deploying it is incredibly simple.

1. Go to [share.streamlit.io](https://share.streamlit.io/) and create an account (or log in) using your GitHub account.
2. Once logged in, click the **"New app"** button.
3. Streamlit will ask for permission to view your GitHub repositories. Grant it.
4. Fill out the deployment form:
   - **Repository:** Start typing `CombinedMarketAnalyzer` and select your repo from the dropdown.
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. (Optional) You can customize the URL by clicking **Advanced settings**.
6. Click **Deploy!**

### What Happens Next?
Streamlit will automatically read your `requirements.txt` file, install dependencies like `yfinance` and `pandas`, and launch your `app.py`. Within a minute or two, you will see your app live on the web!

Whenever you make changes to your local code in the future, just run:
```bash
git add .
git commit -m "Update app"
git push
```
Streamlit will detect the new code on GitHub and update your live website automatically!
