# Expense Tracker CLI

A command-line interface application built in Python to track and manage personal expenses — with categories and monthly budgets.

## How to Run

Open your terminal, navigate to the project directory, and use the commands below.

```
# Add an expense (category defaults to "General" if you skip it)
python expense_tracker.py add --desc "Lunch" --amt 20 --category food

# Update an expense (any of --desc, --amt, --category)
python expense_tracker.py update --id 1 --category "Transport"

# Delete an expense
python expense_tracker.py delete --id 1

# View all expenses
python expense_tracker.py list

# View expenses in one category only
python expense_tracker.py list --category food

# List every category you've used, with total spend each
python expense_tracker.py categories

# View total summary
python expense_tracker.py summary

# View summary for a specific month
python expense_tracker.py summary --month 8

# View summary broken down by category
python expense_tracker.py summary --by-category

# Set a monthly budget for a category
python expense_tracker.py set-budget --category food --amt 3000

# Set an overall monthly budget (across all categories)
python expense_tracker.py set-budget --category overall --amt 15000

# Check budget status (spent vs. budgeted) for the current month
python expense_tracker.py budget

# Check budget status for a specific month
python expense_tracker.py budget --month 2026-08
```

## Categories

Every expense has a category (e.g. Food, Clothes, Transport). If you don't
pass `--category`, it defaults to "General". Category names are normalized
(`food` and `Food` are treated as the same category) so your totals don't
get split up by casing.

## Budgets

Budgets are monthly and can be set per category or overall (`--category overall`)
using `set-budget`. When you add an expense, you'll get an automatic
⚠️ warning right there in the terminal if it pushes you over budget for that
category or overall. Run `budget` any time to see a full spent-vs-budgeted
breakdown for the month.

## Data Files

- `expenses.json` — all recorded expenses
- `budgets.json` — your category and overall budgets

Both are created automatically the first time you use the app.
