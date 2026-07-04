import os
import json
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORIES_DIR = os.path.join(REPO_ROOT, "data", "categories")

# Suffixes to strip for base ID matching
SUFFIXES_TO_STRIP = [
    r'_raw', r'_cooked', r'_frozen', r'_boiled', r'_drained', r'_chopped',
    r'_fresh', r'_canned', r'_without_skin', r'_with_skin', r'_heavy_syrup',
    r'_pack', r'_solids', r'_liquid', r'_solids_and_liquid', r'_dry',
    r'_dehydrated', r'_cnd_solliquids', r'_boiled_dr', r'_drained_solids',
    r'_with_salt', r'_without_salt', r'_unsalted', r'_salted', r'_prepared',
    r'_steamed', r'_microwaved', r'_baked', r'_roasted', r'_cnd', r'_lite',
    r'_light'
]

GROUP_RULES = [
    # 1. High Vitamin K Greens & Vegetables (high priority)
    ("spinach", ["spinach"]),
    ("kale", ["kale", "collard", "collards", "mustard_greens", "turnip_greens", "chard", "swiss_chard"]),
    ("broccoli", ["broccoli"]),
    ("cabbage", ["cabbage", "sauerkraut", "kohlrabi", "brussels", "sprout", "sprouts"]),
    ("lettuce", ["lettuce", "romaine", "iceberg", "salad_greens", "cress", "endive", "arugula"]),
    
    # 2. Specific Herbs
    ("parsley", ["parsley"]),
    ("basil", ["basil"]),
    ("thyme", ["thyme"]),
    ("ginger", ["ginger"]),
    ("cinnamon", ["cinnamon"]),
    ("garlic", ["garlic"]),
    
    # 3. Vegetables
    ("onion", ["onion", "onions", "scallion", "scallions", "leek", "leeks", "chives"]),
    ("potato", ["potato", "potatoes", "yam", "yams", "sweetpotato", "sweetpotatoes"]),
    ("tomato", ["tomato", "tomatoes"]),
    ("carrot", ["carrot", "carrots"]),
    ("squash", ["squash", "zucchini", "pumpkin"]),
    ("mushroom", ["mushroom", "mushrooms"]),
    ("asparagus", ["asparagus"]),
    ("celery", ["celery"]),
    ("cucumber", ["cucumber", "cucumbers"]),
    ("peas", ["pea", "peas"]),
    ("beans", ["bean", "beans", "lentil", "lentils"]),
    ("corn", ["corn", "maize"]),
    
    # 4. Specific Fruits
    ("apple", ["apple", "apples"]),
    ("apricot", ["apricot", "apricots"]),
    ("avocado", ["avocado", "avocados"]),
    ("banana", ["banana", "bananas"]),
    ("blackberry", ["blackberry", "blackberries"]),
    ("blueberry", ["blueberry", "blueberries"]),
    ("cherry", ["cherry", "cherries"]),
    ("cranberry", ["cranberry", "cranberries"]),
    ("fig", ["fig", "figs"]),
    ("grape", ["grape", "grapes", "raisin", "raisins"]),
    ("grapefruit", ["grapefruit", "grapefruits"]),
    ("kiwi", ["kiwi", "kiwis", "kiwifruit"]),
    ("citrus", ["lemon", "lemons", "lime", "limes"]),
    ("melon", ["melon", "melons", "watermelon", "cantaloupe", "honeydew"]),
    ("orange", ["orange", "oranges", "tangerine", "mandarin", "clementine"]),
    ("peach", ["peach", "peaches", "nectarine", "nectarines"]),
    ("pear", ["pear", "pears"]),
    ("pineapple", ["pineapple", "pineapples"]),
    ("plum", ["plum", "plums", "prune", "prunes"]),
    ("pomegranate", ["pomegranate", "pomegranates"]),
    ("raspberry", ["raspberry", "raspberries"]),
    ("strawberry", ["strawberry", "strawberries"]),
    
    # 5. Soy / Fermented
    ("natto", ["natto"]),
    ("soy", ["soy", "tofu", "edamame", "tempeh", "miso", "shoyu", "soybean", "soybeans"]),
    
    # 6. Oils & Fats
    ("mayonnaise", ["mayonnaise", "mayo"]),
    ("butter", ["butter"]),
    ("margarine", ["margarine", "spread", "spreads"]),
    ("oil", ["oil", "oils"]),
    ("dressing", ["dressing", "dressings"]),
    ("fat", ["fat", "fats", "shortening", "lard"]),
    
    # 7. Dairy & Eggs
    ("cheese", ["cheese", "cheddar", "mozzarella", "ricotta", "swiss", "provolone", "feta", "blue_cheese", "camembert", "queso"]),
    ("yogurt", ["yogurt", "kefir"]),
    ("cream", ["cream", "eggnog"]),
    ("egg", ["egg", "eggs", "yolk"]),
    ("milk", ["milk", "whey"]),
    
    # 8. Grains & Bakery
    ("bread", ["bread", "bagel", "bagels", "toast", "bun", "buns", "roll", "rolls", "croissant", "croissants"]),
    ("pasta", ["spaghetti", "macaroni", "noodle", "noodles", "pasta", "lasagna"]),
    ("rice", ["rice"]),
    ("cookie", ["cookie", "cookies", "cracker", "crackers", "biscuit", "biscuits", "wafer", "wafers"]),
    ("cereal", ["cereal", "cereals", "oat", "oats", "oatmeal", "granola"]),
    ("flour", ["flour", "starch", "semolina"]),
    ("pastry", ["cake", "cakes", "muffin", "muffins", "pie", "pies", "pastries", "pastry", "danish", "doughnut", "doughnuts", "waffle", "waffles", "pancake", "pancakes", "crepe", "puff", "crust"]),
    
    # 9. Meat & Poultry
    ("beef", ["beef", "veal", "steak", "hamburger"]),
    ("pork", ["pork", "bacon", "ham", "prosciutto"]),
    ("chicken", ["chicken", "broiler", "fryer"]),
    ("turkey", ["turkey"]),
    ("other_poultry", ["duck", "goose", "pheasant"]),
    ("other_meat", ["lamb", "mutton", "goat", "venison", "bison", "sausage", "frankfurter", "bologna", "salami"]),
    
    # 10. Seafood
    ("fish", ["fish", "salmon", "tuna", "cod", "herring", "sardine", "mackerel", "trout", "anchovy", "halibut", "haddock", "pollock", "tilapia", "catfish", "snapper"]),
    ("seafood", ["shrimp", "crab", "lobster", "oyster", "mussel", "clam", "scallop", "squid", "octopus", "seafood", "mollusks"]),
    
    # 11. Herbs & Spices (fallbacks)
    ("pepper", ["pepper", "peppers", "paprika", "chili", "cayenne"]),
    ("other_herbs_spices", ["oregano", "marjoram", "rosemary", "sage", "coriander", "cilantro", "dill", "mint", "clove", "cloves", "nutmeg", "turmeric", "cumin", "cardamom", "fennel", "anise", "saffron", "mustard_seed", "spices", "spice"]),
    
    # 12. Processed / Prepared
    ("soup", ["soup", "broth"]),
    ("pizza", ["pizza"]),
    ("sandwich", ["sandwich", "burger", "taco", "burrito", "hot_dog"]),
    ("snack", ["chips", "popcorn", "pretzel", "snack"]),
    ("candy", ["candy", "candies", "chocolate", "sweets", "fudge", "marshmallow", "cacao", "cocoa"]),
    ("baby_food", ["babyfood", "formula", "gerber", "infant"]),
    ("sauce", ["sauce", "gravy", "dip", "salsa"]),
    
    # 13. Beverages
    ("alcohol", ["wine", "beer", "spirit", "alcohol", "liqueur", "whiskey", "vodka", "rum", "gin", "cider"]),
    ("tea", ["tea"]),
    ("coffee", ["coffee", "caffeine", "espresso"]),
    ("juice", ["juice"]),
    ("beverages", ["water", "soda", "carbonated", "beverage", "drink"]),
    
    # 14. Nuts & Seeds
    ("nut", ["peanut", "almond", "cashew", "walnut", "hazelnut", "pecan", "pistachio", "macadamia", "chestnut", "nut", "nuts", "peanut_butter"]),
    ("seed", ["seed", "seeds", "pumpkin", "sunflower", "chia", "flax", "sesame", "poppy", "hemp"])
]

# Compile rules for boundary/snake_case matching
COMPILE_RULES = []
for group_id, patterns in GROUP_RULES:
    regex_parts = []
    for pattern in patterns:
        regex_parts.append(r'\b' + re.escape(pattern) + r'\b')
        regex_parts.append(r'(?:^|_)' + re.escape(pattern) + r'(?:_|$)')
    regex = re.compile('|'.join(regex_parts), re.IGNORECASE)
    COMPILE_RULES.append((group_id, regex))

def get_calculated_group(food_id):
    for group_id, regex in COMPILE_RULES:
        if regex.search(food_id):
            return group_id
    return None

def get_base_id(food_id):
    base = food_id
    changed = True
    while changed:
        changed = False
        for suffix in SUFFIXES_TO_STRIP:
            new_base = re.sub(suffix + r'$', '', base)
            if new_base != base:
                base = new_base
                changed = True
    return base.strip('_')

def main():
    print("Starting food groups migration...")
    
    for filename in os.listdir(CATEGORIES_DIR):
        if not filename.endswith(".json"):
            continue
            
        filepath = os.path.join(CATEGORIES_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        items = data.get("data", [])
        if not items:
            continue
            
        # 1. Assign groups first
        for item in items:
            # Check if there is an existing relations group
            existing_relations = item.get("relations")
            if existing_relations and existing_relations.get("group"):
                # Preserve existing group
                continue
                
            group = get_calculated_group(item["id"])
            if group:
                if "relations" not in item:
                    item["relations"] = {}
                item["relations"]["group"] = group
            else:
                # Omit relations entirely if no obvious group is found
                if "relations" in item:
                    # Clean up group if it was somehow empty/None
                    if "group" in item["relations"]:
                        del item["relations"]["group"]
                    if not item["relations"]:
                        del item["relations"]
                        
        # 2. Build map of base IDs for grouping related items within this category file
        base_groups = {} # base_id -> list of food items
        for item in items:
            relations = item.get("relations")
            if relations and relations.get("group"):
                # Only link if the food item belongs to a registered group
                base_id = get_base_id(item["id"])
                if base_id not in base_groups:
                    base_groups[base_id] = []
                base_groups[base_id].append(item)
                
        # 3. Populate related_ids for matching base IDs
        for base_id, group_items in base_groups.items():
            if len(group_items) > 1:
                item_ids = [item["id"] for item in group_items]
                for item in group_items:
                    # Determine other variant IDs
                    related = sorted([i for i in item_ids if i != item["id"]])
                    if related:
                        item["relations"]["related_ids"] = related
            else:
                # Remove related_ids if there's only 1 item left in the base group
                for item in group_items:
                    if "related_ids" in item["relations"]:
                        del item["relations"]["related_ids"]

        # 4. Clean up any empty relations fields
        for item in items:
            if "relations" in item and not item["relations"]:
                del item["relations"]

        # Write the updated file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Successfully processed {filename}")

if __name__ == "__main__":
    main()
