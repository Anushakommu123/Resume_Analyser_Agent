# Connect this project to your GitHub repository

Your repo already has unrelated code and you want this Resume Analyser code there instead. Follow these steps.

---

## Step 1: Prepare local repo (one-time)

Run in the project folder (`C:\Resume_Analyser_Agent`):

```powershell
# Unstage everything (including outputs/)
git reset

# Add only project files (outputs/ is now ignored)
git add .

# First commit
git commit -m "Initial commit: Resume Analyser Agent"
```

---

## Step 2: Add your GitHub repo as remote

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repo name:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

Example: if your repo is `https://github.com/anush/resume-analyzer`, run:

```powershell
git remote add origin https://github.com/anush/resume-analyzer.git
```

---

## Step 3: Replace the code on GitHub with this project

Because the code on GitHub is unrelated, you will **overwrite** the remote with this project.

**Option A – Overwrite the default branch (e.g. `main` or `master`)**

```powershell
# If your GitHub default branch is "main":
git branch -M main
git push -u origin main --force

# If your GitHub default branch is "master":
git push -u origin master --force
```

**Option B – Push to a new branch and then switch default on GitHub**

```powershell
git push -u origin master
```

Then on GitHub: **Settings → General → Default branch** → change to `master` and save. After that you can delete the old branch in the repo if you want.

---

## Step 4: Confirm

- Open your repo on GitHub in the browser.
- You should see this project’s files (e.g. `app/`, `main.py`, `requirements.txt`, `README.md`).

---

## Summary

| Step | Action |
|------|--------|
| 1 | `git reset` → `git add .` → `git commit -m "Initial commit: Resume Analyser Agent"` |
| 2 | `git remote add origin https://github.com/USERNAME/REPO.git` |
| 3 | `git push -u origin main --force` (or `master`, and use `--force` only if you want to replace existing code) |

**Note:** `--force` overwrites the history on the remote. Use it only when you are sure you want to replace the current contents of that branch.
