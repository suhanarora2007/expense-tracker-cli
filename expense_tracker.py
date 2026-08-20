import json
import os
import sys
from datetime import datetime

# File where expenses will be saved
DATA_FILE = "expenses.json"


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


def add_expense(description, amount):
    """Requirement 1: Add an expense."""
    expenses = load_expenses()

    # Auto-generate a unique ID
    expense_id = len(expenses) + 1 if expenses else 1

    new_expense = {
        "id": expense_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": description,
        "amount": float(amount)
    }

    expenses.append(new_expense)
    save_expenses(expenses)
    print(f" Expense added successfully (ID: {expense_id})")


def update_expense(expense_id, description=None, amount=None):
    """Requirement 2: Update an existing expense."""
    expenses = load_expenses()
    found = False

    for exp in expenses:
        if exp["id"] == int(expense_id):
            if description:
                exp["description"] = description
            if amount:
                exp["amount"] = float(amount)
            found = True
            break

    if found:
        save_expenses(expenses)
        print(" Expense updated successfully!")
    else:
        print(" Error: Expense ID not found.")


def delete_expense(expense_id):
    """Requirement 3: Delete an expense."""
    expenses = load_expenses()
    initial_count = len(expenses)

    expenses = [exp for exp in expenses if exp["id"] != int(expense_id)]

    if len(expenses) < initial_count:
        save_expenses(expenses)
        print(" Expense deleted successfully!")
    else:
        print(" Error: Expense ID not found.")


def view_expenses():
    """Requirement 4: View all expenses."""
    expenses = load_expenses()
    if not expenses:
        print("No expenses recorded yet.")
        return

    print(f"{'ID':<5} {'Date':<12} {'Description':<25} {'Amount':<10}")
    print("-" * 55)
    for exp in expenses:
        print(
            f"{exp['id']:<5} {exp['date']:<12} {exp['description']:<25} ${exp['amount']:<10.2f}")


def view_summary(month=None):
    """Requirement 5 & 6: View total summary or filtered by specific month."""
    expenses = load_expenses()
    total = 0.0
    current_year = str(datetime.now().year)

    if month:
        # Pad single digit months (e.g., '8' -> '08')
        target_month = f"{int(month):02d}"
        print(f"--- Summary for Month: {target_month}/{current_year} ---")
        for exp in expenses:
            exp_date = exp["date"]  # Format: YYYY-MM-DD
            if exp_date.startswith(f"{current_year}-{target_month}"):
                total += exp["amount"]
    else:
        print("--- Total Summary ---")
        for exp in expenses:
            total += exp["amount"]

    print(f"Total Expenses: ${total:.2f}")


def print_help():
    print("\nUsage: python expense_tracker.py [command] [options]")
    print("Commands:")
    print("  add --desc [text] --amt [number]   Add a new expense")
    print(
        "  update --id [num]                  Update an expense (optional: --desc, --amt)")
    print("  delete --id [num]                  Delete an expense by ID")
    print("  list                               View all recorded expenses")
    print("  summary                            View total summary of expenses")
    print(
        "  summary --month [1-12]             View summary for a specific month")


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
            add_expense(desc, amt)

        elif command == "update":
            exp_id = args[args.index("--id") + 1]
            desc = args[args.index("--desc") + 1] if "--desc" in args else None
            amt = args[args.index("--amt") + 1] if "--amt" in args else None
            update_expense(exp_id, desc, amt)

        elif command == "delete":
            exp_id = args[args.index("--id") + 1]
            delete_expense(exp_id)

        elif command == "list":
            view_expenses()

        elif command == "summary":
            if "--month" in args:
                month = args[args.index("--month") + 1]
                view_summary(month)
            else:
                view_summary()
        else:
            print("Unknown command.")
            print_help()
    except (ValueError, IndexError):
        print("❌ Error: Invalid arguments or missing values.")
        print_help()


if __name__ == "__main__":
    main()
