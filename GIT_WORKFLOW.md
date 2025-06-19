# Git Workflow for Cursor + Replit Agent Development

## Overview
This workflow prevents merge conflicts when working with both Cursor IDE and Replit Agent on the same project.

## Branch Strategy

### Main Branches
- `main` - Production-ready code
- `cursor-work` - Your development branch for Cursor IDE
- `agent-work` - Replit Agent development branch

### Feature Branches
- `cursor-features/[feature-name]` - Specific features in Cursor
- `agent-features/[feature-name]` - Specific features by Agent

## Setup Commands

```bash
# Initialize git (if not already done)
git init

# Create and switch to cursor work branch
git checkout -b cursor-work

# Create agent work branch
git checkout -b agent-work

# Return to main
git checkout main
```

## Daily Workflow

### Before Starting Work in Cursor:
```bash
# Sync with latest changes
git checkout main
git pull origin main

# Create or switch to your cursor branch
git checkout cursor-work
git merge main

# Or create a new feature branch
git checkout -b cursor-features/new-feature
```

### Before Asking Agent to Work:
```bash
# Commit your current work
git add .
git commit -m "WIP: Describe what you're working on"
git push origin cursor-work

# Tell the agent which files you've been editing
```

### When Agent Works:
- Agent will work on `agent-work` branch or create `agent-features/[name]`
- Agent avoids files you're actively editing
- Agent creates new files when possible
- Agent documents changes in commits

### Merging Back:
```bash
# Test your changes first
git checkout cursor-work
# Test your features

# Merge cursor work to main
git checkout main
git merge cursor-work
git push origin main

# Agent will merge their work separately
```

## Communication Protocol

### Tell the Agent:
- "I'm working on files: [list of files]"
- "I'm working on [specific feature]"
- "Avoid touching [specific files/folders]"

### Agent Will:
- Work on different files when possible
- Create new files for new features
- Document all changes clearly
- Coordinate with your active work

## Conflict Resolution

If conflicts occur:
```bash
# See what files conflict
git status

# Edit conflicted files manually
# Look for <<<<<<< ======= >>>>>>> markers

# Add resolved files
git add [resolved-files]

# Complete the merge
git commit -m "Resolve merge conflicts"
```

## File Ownership Guidelines

### You Own (Cursor):
- Frontend styling/CSS
- Specific business logic you're implementing
- Templates you're actively designing
- Configuration files you're tweaking

### Agent Owns:
- New route implementations
- Database models and migrations
- Backend utility functions
- New feature scaffolding

### Shared (Coordinate):
- Main application files (app.py, routes.py)
- Template base files
- Configuration files

## Best Practices

1. **Commit Early, Commit Often**
   - Small commits are easier to merge
   - Descriptive commit messages help

2. **Sync Before Starting**
   - Always pull latest before new work
   - Reduces conflict likelihood

3. **Communicate Changes**
   - Tell agent what you're working on
   - Agent will document their changes

4. **Test Before Merging**
   - Verify your changes work
   - Test combined changes

5. **Use Descriptive Branch Names**
   - `cursor-features/user-dashboard`
   - `agent-features/ai-integration`

## Quick Commands Reference

```bash
# Check current status
git status
git branch

# Switch branches
git checkout [branch-name]

# Create new branch
git checkout -b [new-branch-name]

# Save work in progress
git add .
git commit -m "WIP: [description]"

# Push your branch
git push origin [branch-name]

# See differences
git diff
git diff [branch1] [branch2]

# Merge branch to main
git checkout main
git merge [branch-name]
```

This workflow ensures smooth collaboration between you and the agent while maintaining code integrity.