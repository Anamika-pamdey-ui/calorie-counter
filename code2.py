import csv
import os
from datetime import datetime
import json

FOODS_FILE = "foods.csv"
LOG_FILE = "food_log.csv"
GOALS_FILE = "goals.json"

# --------- Built-in starter foods (per 100g unless noted) ----------
STARTER_FOODS = [
    # name, unit, qty_per_unit, kcal, protein, carbs, fat
    ("Boiled Rice", "g", 100, 130, 2.7, 28.0, 0.3),
    ("Roti (Wheat)", "g", 50, 120, 3.6, 18.0, 3.0),  # avg per 1 roti ~50g dough
    ("Dal (Cooked)", "g", 100, 116, 7.0, 16.0, 1.2),
    ("Chole (Cooked)", "g", 100, 164, 8.9, 27.4, 2.6),
    ("Paneer", "g", 100, 296, 21.0, 6.0, 22.0),
    ("Chicken Breast (cooked)", "g", 100, 165, 31.0, 0.0, 3.6),
    ("Egg (1 large)", "serving", 1, 78, 6.0, 0.6, 5.0),
    ("Milk (Toned)", "ml", 200, 124, 6.6, 9.8, 6.6),  # per 200 ml
    ("Banana (1 medium)", "serving", 1, 105, 1.3, 27.0, 0.3),
    ("Apple (1 medium)", "serving", 1, 95, 0.5, 25.0, 0.3),
    ("Curd (Dahi)", "g", 100, 61, 3.5, 4.7, 3.3),
    ("Poha (Cooked)", "g", 100, 130, 2.5, 23.0, 2.5),
    ("Maggi (Cooked)", "g", 100, 210, 5.0, 31.0, 7.0),
    ("Aloo Paratha", "serving", 1, 320, 8.0, 45.0, 12.0),
    ("Biryani (Chicken)", "g", 100, 170, 8.0, 20.0, 6.0),
]

# -------------------- Helpers --------------------
def ensure_files():
    if not os.path.exists(FOODS_FILE):
        with open(FOODS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "unit", "qty_per_unit", "kcal", "protein", "carbs", "fat"])
            for row in STARTER_FOODS:
                writer.writerow(row)

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "meal", "name", "amount", "unit", "kcal", "protein", "carbs", "fat"])

    if not os.path.exists(GOALS_FILE):
        with open(GOALS_FILE, "w", encoding="utf-8") as f:
            json.dump({"calories": None, "protein": None}, f)

def load_foods():
    foods = []
    with open(FOODS_FILE, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            foods.append({
                "name": row["name"],
                "unit": row["unit"],
                "qty_per_unit": float(row["qty_per_unit"]),
                "kcal": float(row["kcal"]),
                "protein": float(row["protein"]),
                "carbs": float(row["carbs"]),
                "fat": float(row["fat"]),
            })
    return foods

def save_food(food):
    with open(FOODS_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([food["name"], food["unit"], food["qty_per_unit"], food["kcal"], food["protein"], food["carbs"], food["fat"]])

def load_goals():
    with open(GOALS_FILE, encoding="utf-8") as f:
        return json.load(f)

def save_goals(goals):
    with open(GOALS_FILE, "w", encoding="utf-8") as f:
        json.dump(goals, f)

def fmt_row(cols, widths):
    return " | ".join(str(c).ljust(w) for c, w in zip(cols, widths))

def input_float(prompt, min_val=None):
    while True:
        try:
            v = float(input(prompt).strip())
            if min_val is not None and v < min_val:
                print(f"Enter a number >= {min_val}.")
                continue
            return v
        except ValueError:
            print("Please enter a valid number.")

# -------------------- Features --------------------
def search_foods(foods, query):
    q = query.lower()
    return [f for f in foods if q in f["name"].lower()]

def add_custom_food():
    print("\nAdd a custom food:")
    name = input("Name: ").strip()
    unit = input("Unit (g/ml/serving): ").strip().lower() or "g"
    qty = input_float("Quantity per unit (e.g., 100 for per 100g, 1 for per serving): ", 0.0001)
    kcal = input_float("Calories for that unit: ", 0)
    protein = input_float("Protein (g): ", 0)
    carbs = input_float("Carbs (g): ", 0)
    fat = input_float("Fat (g): ", 0)

    food = {"name": name, "unit": unit, "qty_per_unit": qty, "kcal": kcal, "protein": protein, "carbs": carbs, "fat": fat}
    save_food(food)
    print(f"✅ Saved '{name}' to foods.\n")

def log_meal(foods):
    print("\nLog a meal:")
    meal = input("Meal (Breakfast/Lunch/Snack/Dinner): ").strip().title() or "Meal"
    query = input("Search food name: ").strip()
    matches = search_foods(foods, query)

    if not matches:
        print("No matches. Tip: add it as a custom food from main menu.")
        return

    print("\nSelect a food:")
    for i, f in enumerate(matches, 1):
        print(f"{i}. {f['name']}  ({f['qty_per_unit']}{f['unit']} -> {f['kcal']} kcal)")
    idx = int(input_float("Choice #: ", 1)) - 1
    if idx < 0 or idx >= len(matches):
        print("Invalid choice.")
        return

    chosen = matches[idx]
    amount = input_float(f"How much did you eat (in {chosen['unit']})? ", 0.0001)

    # scale nutrients
    scale = amount / chosen["qty_per_unit"]
    kcal = round(chosen["kcal"] * scale, 1)
    protein = round(chosen["protein"] * scale, 1)
    carbs = round(chosen["carbs"] * scale, 1)
    fat = round(chosen["fat"] * scale, 1)

    # write to log
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([today(), meal, chosen["name"], amount, chosen["unit"], kcal, protein, carbs, fat])

    print(f"✅ Logged: {meal} • {chosen['name']} • {amount}{chosen['unit']} • {kcal} kcal (P{protein}/C{carbs}/F{fat})\n")

def today():
    return datetime.now().strftime("%Y-%m-%d")

def read_logs(date_str):
    entries = []
    with open(LOG_FILE, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["date"] == date_str:
                entries.append({
                    "meal": row["meal"],
                    "name": row["name"],
                    "amount": float(row["amount"]),
                    "unit": row["unit"],
                    "kcal": float(row["kcal"]),
                    "protein": float(row["protein"]),
                    "carbs": float(row["carbs"]),
                    "fat": float(row["fat"]),
                })
    return entries

def show_day(date_str):
    entries = read_logs(date_str)
    print(f"\n===== {date_str} =====")
    if not entries:
        print("No entries yet.\n")
        return

    widths = [10, 22, 10, 6, 8, 8, 8]
    print(fmt_row(["Meal", "Food", "Amount", "Unit", "Kcal", "Prot", "Carb"], widths))
    print("-" * 78)

    totals = {"kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    for e in entries:
        print(fmt_row([
            e["meal"][:10],
            e["name"][:22],
            f"{e['amount']:.0f}",
            e["unit"],
            f"{e['kcal']:.0f}",
            f"{e['protein']:.1f}",
            f"{e['carbs']:.1f}",
        ], widths))
        totals["kcal"] += e["kcal"]
        totals["protein"] += e["protein"]
        totals["carbs"] += e["carbs"]
        totals["fat"] += e["fat"]

    print("-" * 78)
    print(f"Totals: {int(totals['kcal'])} kcal  |  Protein {totals['protein']:.1f} g  |  Carbs {totals['carbs']:.1f} g  |  Fat {totals['fat']:.1f} g")

    goals = load_goals()
    if goals.get("calories") or goals.get("protein"):
        rem_c = None if goals["calories"] is None else int(goals["calories"] - totals["kcal"])
        rem_p = None if goals["protein"] is None else round(goals["protein"] - totals["protein"], 1)
        print("Goals:", end=" ")
        if goals["calories"] is not None:
            print(f"{int(goals['calories'])} kcal (remaining {rem_c})", end="  ")
        if goals["protein"] is not None:
            print(f"| Protein {goals['protein']} g (remaining {rem_p} g)", end="")
        print()
    print()

def set_goals():
    print("\nSet daily goals (leave blank to skip):")
    cal_in = input("Calories goal (kcal): ").strip()
    pro_in = input("Protein goal (g): ").strip()

    goals = load_goals()
    goals["calories"] = None if cal_in == "" else float(cal_in)
    goals["protein"] = None if pro_in == "" else float(pro_in)
    save_goals(goals)
    print("✅ Goals updated.\n")

# -------------------- Main Loop --------------------
def main():
    ensure_files()
    foods = load_foods()

    while True:
        print("=== Calorie Counter ===")
        print("1) Log a meal")
        print("2) Show today")
        print("3) Show another day")
        print("4) Add custom food")
        print("5) Set daily goals")
        print("6) List foods (search)")
        print("7) Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            foods = load_foods()  # refresh in case new foods added
            log_meal(foods)
        elif choice == "2":
            show_day(today())
        elif choice == "3":
            d = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(d, "%Y-%m-%d")
            except ValueError:
                print("Invalid date.\n"); continue
            show_day(d)
        elif choice == "4":
            add_custom_food()
        elif choice == "5":
            set_goals()
        elif choice == "6":
            q = input("Search text: ").strip()
            matches = search_foods(load_foods(), q)
            if not matches:
                print("No foods found.\n"); continue
            widths = [25, 10, 14, 6, 6, 6, 6]
            print(fmt_row(["Name", "Unit", "Qty/Unit", "Kcal", "Prot", "Carb", "Fat"], widths))
            print("-" * 86)
            for f in matches[:50]:
                print(fmt_row([
                    f["name"][:25], f["unit"], f["qty_per_unit"], int(f["kcal"]),
                    round(f["protein"],1), round(f["carbs"],1), round(f["fat"],1)
                ], widths))
            print()
        elif choice == "7":
            print("Bye! 👋"); break
        else:
            print("Invalid option.\n")

if __name__ == "__main__":
    main()
  