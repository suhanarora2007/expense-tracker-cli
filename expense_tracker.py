import json
import os
import sys
from datetime import datetime

# Files where data is saved
DATA_FILE = "expenses.json"
BUDGET_FILE = "budgets.json"

DEFAULT_CATEGORY = "General"
OVERALL_KEY = "__overall__"  # reserved key used for the total monthly budget


# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

def load_expenses():
    """Loads expenses from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_expenses(expenses):
    """Saves expenses back to the JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(expenses, file, indent=4)


def load_budgets():
    """Loads budgets from the JSON file.

    Structure: { "<category or __overall__>": amount }
    Budgets are monthly by design (spend is always calculated for a given
    month, so the same budget number applies every month until changed).
    """
    if not os.path.exists(BUDGET_FILE):
        return {}
    try:
        with open(BUDGET_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def save_budgets(budgets):
    """Saves budgets back to the JSON file."""
    with open(BUDGET_FILE, "w") as file:
        json.dump(budgets, file, indent=4)


def normalize_category(category):
    """Keeps category names consistent (e.g. 'food' and 'Food' are the same)."""
    if not category:
        return DEFAULT_CATEGORY
    return category.strip().title()


# ---------------------------------------------------------------------------
# Expense commands
# ---------------------------------------------------------------------------

def add_expense(description, amount, category=None):
    """Add an expense, now with a category."""
    expenses = load_expenses()
    category = normalize_category(category)

    # Auto-generate a unique ID
    expense_id = (max(exp["id"] for exp in expenses) + 1) if expenses else 1

    new_expense = {
        "id": expense_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": description,
        "amount": float(amount),
        "category": category,
    }

    expenses.append(new_expense)
    save_expenses(expenses)
    print(f"✅ Expense added successfully (ID: {expense_id}, Category: {category})")

    # Give an immediate heads-up if this expense pushed a budget over the edge.
    warn_if_over_budget(category)


def update_expense(expense_id, description=None, amount=None, category=None):
    """Update an existing expense, including its category."""
    expenses = load_expenses()
    found = False

    for exp in expenses:
        if exp["id"] == int(expense_id):
            if description:
                exp["description"] = description
            if amount:
                exp["amount"] = float(amount)
            if category:
                exp["category"] = normalize_category(category)
            found = True
            break

    if found:
        save_expenses(expenses)
        print("✅ Expense updated successfully!")
    else:
        print("❌ Error: Expense ID not found.")


def delete_expense(expense_id):
    """Delete an expense."""
    expenses = load_expenses()
    initial_count = len(expenses)

    expenses = [exp for exp in expenses if exp["id"] != int(expense_id)]

    if len(expenses) < initial_count:
        save_expenses(expenses)
        print("✅ Expense deleted successfully!")
    else:
        print("❌ Error: Expense ID not found.")


def view_expenses(category=None):
    """View all expenses, optionally filtered by category."""
    expenses = load_expenses()

    if category:
        category = normalize_category(category)
        expenses = [exp for exp in expenses if exp.get("category", DEFAULT_CATEGORY) == category]

    if not expenses:
        print("No expenses recorded yet." if not category else f"No expenses recorded for category '{category}'.")
        return

    print(f"{'ID':<5} {'Date':<12} {'Category':<15} {'Description':<25} {'Amount':<10}")
    print("-" * 70)
    for exp in expenses:
        cat = exp.get("category", DEFAULT_CATEGORY)
        print(
            f"{exp['id']:<5} {exp['date']:<12} {cat:<15} {exp['description']:<25} ${exp['amount']:<10.2f}")


def view_categories():
    """List every category that has been used, with total spend per category."""
    expenses = load_expenses()
    if not expenses:
        print("No expenses recorded yet.")
        return

    totals = {}
    for exp in expenses:
        cat = exp.get("category", DEFAULT_CATEGORY)
        totals[cat] = totals.get(cat, 0.0) + exp["amount"]

    print(f"{'Category':<20} {'Total Spent':<15}")
    print("-" * 35)
    for cat, total in sorted(totals.items(), key=lambda x: -x[1]):
        print(f"{cat:<20} ${total:<14.2f}")


def view_summary(month=None, category=None, by_category=False):
    """View total summary, optionally filtered by month and/or category,
    or broken down by category."""
    expenses = load_expenses()
    current_year = str(datetime.now().year)

    if month:
        target_month = f"{int(month):02d}"
        expenses = [exp for exp in expenses if exp["date"].startswith(f"{current_year}-{target_month}")]
        label = f"Month {target_month}/{current_year}"
    else:
        label = "All Time"

    if category:
        category = normalize_category(category)
        expenses = [exp for exp in expenses if exp.get("category", DEFAULT_CATEGORY) == category]
        label += f", Category: {category}"

    print(f"--- Summary: {label} ---")

    if by_category and not category:
        totals = {}
        for exp in expenses:
            cat = exp.get("category", DEFAULT_CATEGORY)
            totals[cat] = totals.get(cat, 0.0) + exp["amount"]
        if not totals:
            print("No expenses found.")
        for cat, total in sorted(totals.items(), key=lambda x: -x[1]):
            print(f"  {cat:<18} ${total:.2f}")

    total = sum(exp["amount"] for exp in expenses)
    print(f"Total Expenses: ${total:.2f}")


# ---------------------------------------------------------------------------
# Budget commands
# ---------------------------------------------------------------------------

def set_budget(category, amount):
    """Set a monthly budget for a category, or 'overall' for a total cap."""
    budgets = load_budgets()
    key = OVERALL_KEY if category.strip().lower() == "overall" else normalize_category(category)
    budgets[key] = float(amount)
    save_budgets(budgets)
    label = "overall monthly budget" if key == OVERALL_KEY else f"'{key}' monthly budget"
    print(f"✅ Set {label} to ${float(amount):.2f}")


def get_month_spend(category=None, month=None):
    """Total spend for the given category (or all) in the given month (default: current month)."""
    expenses = load_expenses()
    target_month = month or datetime.now().strftime("%Y-%m")
    total = 0.0
    for exp in expenses:
        if not exp["date"].startswith(target_month):
            continue
        if category and exp.get("category", DEFAULT_CATEGORY) != category:
            continue
        total += exp["amount"]
    return total


def warn_if_over_budget(category):
    """Called right after adding an expense to flag any budget that's now exceeded."""
    budgets = load_budgets()
    if not budgets:
        return

    if category in budgets:
        spent = get_month_spend(category=category)
        limit = budgets[category]
        if spent > limit:
            print(f"⚠️  Over budget for '{category}': ${spent:.2f} spent of ${limit:.2f} budgeted.")

    if OVERALL_KEY in budgets:
        spent = get_month_spend()
        limit = budgets[OVERALL_KEY]
        if spent > limit:
            print(f"⚠️  Over your overall monthly budget: ${spent:.2f} spent of ${limit:.2f} budgeted.")


def view_budget(month=None):
    """Show every budget against actual spend for the given month (default: current month)."""
    budgets = load_budgets()
    if not budgets:
        print("No budgets set yet. Use: set-budget --category [cat|overall] --amt [num]")
        return

    target_month = month or datetime.now().strftime("%Y-%m")
    print(f"--- Budget Status: {target_month} ---")
    print(f"{'Category':<15} {'Budget':<10} {'Spent':<10} {'Remaining':<12} {'Status':<8}")
    print("-" * 60)

    # Overall first, if set
    if OVERALL_KEY in budgets:
        limit = budgets[OVERALL_KEY]
        spent = get_month_spend(month=target_month)
        remaining = limit - spent
        status = "OVER" if remaining < 0 else "OK"
        print(f"{'Overall':<15} ${limit:<9.2f} ${spent:<9.2f} ${remaining:<11.2f} {status:<8}")

    for cat, limit in budgets.items():
        if cat == OVERALL_KEY:
            continue
        spent = get_month_spend(category=cat, month=target_month)
        remaining = limit - spent
        status = "OVER" if remaining < 0 else "OK"
        print(f"{cat:<15} ${limit:<9.2f} ${spent:<9.2f} ${remaining:<11.2f} {status:<8}")


# ---------------------------------------------------------------------------
# CLI plumbing
# ---------------------------------------------------------------------------

def print_help():
    print("\nUsage: python expense_tracker.py [command] [options]")
    print("Commands:")
    print("  add --desc [text] --amt [number] [--category [text]]")
    print("                                      Add a new expense (category defaults to 'General')")
    print("  update --id [num]                  Update an expense (optional: --desc, --amt, --category)")
    print("  delete --id [num]                  Delete an expense by ID")
    print("  list [--category [text]]           View all recorded expenses (optionally by category)")
    print("  categories                         List all categories used and total spend per category")
    print("  summary [--month [1-12]] [--category [text]] [--by-category]")
    print("                                      View total summary, optionally filtered or broken down")
    print("  set-budget --category [text|overall] --amt [number]")
    print("                                      Set a monthly budget for a category or overall")
    print("  budget [--month [YYYY-MM]]          View budget vs actual spend for the month")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ["--help", "-h"]:
        print_help()
        return

    command = args[0]

    try:
        if command == "add":
            desc = args[args.index("--desc") + 1]
            amt = args[args.index("--amt") + 1]
            category = args[args.index("--category") + 1] if "--category" in args else None
            add_expense(desc, amt, category)

        elif command == "update":
            exp_id = args[args.index("--id") + 1]
            desc = args[args.index("--desc") + 1] if "--desc" in args else None
            amt = args[args.index("--amt") + 1] if "--amt" in args else None
            category = args[args.index("--category") + 1] if "--category" in args else None
            update_expense(exp_id, desc, amt, category)

        elif command == "delete":
            exp_id = args[args.index("--id") + 1]
            delete_expense(exp_id)

        elif command == "list":
            category = args[args.index("--category") + 1] if "--category" in args else None
            view_expenses(category)

        elif command == "categories":
            view_categories()

        elif command == "summary":
            month = args[args.index("--month") + 1] if "--month" in args else None
            category = args[args.index("--category") + 1] if "--category" in args else None
            by_category = "--by-category" in args
            view_summary(month, category, by_category)

        elif command == "set-budget":
            category = args[args.index("--category") + 1]
            amt = args[args.index("--amt") + 1]
            set_budget(category, amt)

        elif command == "budget":
            month = args[args.index("--month") + 1] if "--month" in args else None
            view_budget(month)

        else:
            print("Unknown command.")
            print_help()
    except (ValueError, IndexError):
        print("❌ Error: Invalid arguments or missing values.")
        print_help()


if __name__ == "__main__":
    main()
