# GitHub Setup Instructions

Follow these steps to push the MedSearch project to GitHub:

## 1. Initialize a Git Repository

```bash
cd medsearch
git init
```

## 2. Add All Files to the Repository

```bash
git add .
```

## 3. Commit the Changes

```bash
git commit -m "Initial commit"
```

## 4. Create a New Repository on GitHub

1. Go to [GitHub](https://github.com/)
2. Click on the "+" icon in the top right corner
3. Select "New repository"
4. Enter "medsearch" as the repository name
5. Add a description (optional)
6. Choose whether to make the repository public or private
7. Click "Create repository"

## 5. Link Your Local Repository to GitHub

Replace `yourusername` with your GitHub username:

```bash
git remote add origin https://github.com/yourusername/medsearch.git
```

## 6. Push Your Code to GitHub

```bash
git push -u origin main
```

If your default branch is named "master" instead of "main", use:

```bash
git push -u origin master
```

## 7. Verify the Repository

Go to `https://github.com/yourusername/medsearch` to verify that your code has been pushed successfully.

## Additional Git Commands

### Check the Status of Your Repository

```bash
git status
```

### View Commit History

```bash
git log
```

### Create a New Branch

```bash
git checkout -b feature-name
```

### Switch Between Branches

```bash
git checkout branch-name
```

### Pull Latest Changes from GitHub

```bash
git pull origin main
```
