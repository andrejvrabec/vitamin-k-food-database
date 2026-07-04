import os
import json
import sys
from jsonschema import validate, ValidationError

# Get repo root folder (parent of the script's parent folder)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
SCHEMA_DIR = os.path.join(REPO_ROOT, "schema")

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON file at {filepath}: {e}")
        sys.exit(1)

def load_schema(filename):
    schema_path = os.path.join(SCHEMA_DIR, filename)
    return load_json(schema_path)

def main():
    print("Starting Vitamin K Data Validation...")
    errors = []

    # 1. Load Schemas
    metadata_schema = load_schema("metadata.schema.json")
    category_schema = load_schema("category.schema.json")
    common_trans_schema = load_schema("common_translation.schema.json")
    food_trans_schema = load_schema("food_translation.schema.json")
    warfarin_schema = load_schema("warfarin_interaction.schema.json")
    coagulation_schema = load_schema("coagulation_influence.schema.json")

    # 2. Load and Validate metadata.json
    metadata_path = os.path.join(DATA_DIR, "metadata.json")
    if not os.path.exists(metadata_path):
        print(f"CRITICAL ERROR: metadata.json not found at {metadata_path}")
        sys.exit(1)
    
    metadata = load_json(metadata_path)
    try:
        validate(instance=metadata, schema=metadata_schema)
        print("[OK] metadata.json matches schema.")
    except ValidationError as ve:
        errors.append(f"metadata.json schema validation failed: {ve.message}")
        print("[FAIL] metadata.json schema validation failed.")

    # 2b. Load and Validate warfarin.json and coagulation.json
    warfarin_path = os.path.join(DATA_DIR, "interactions", "warfarin.json")
    warfarin_data = {}
    if os.path.exists(warfarin_path):
        warfarin_data = load_json(warfarin_path)
        try:
            validate(instance=warfarin_data, schema=warfarin_schema)
            print("[OK] interactions/warfarin.json matches schema.")
        except ValidationError as ve:
            errors.append(f"interactions/warfarin.json schema validation failed: {ve.message}")
            print("[FAIL] interactions/warfarin.json schema validation failed.")
    else:
        errors.append("CRITICAL: interactions/warfarin.json is missing.")

    coagulation_path = os.path.join(DATA_DIR, "interactions", "coagulation.json")
    coagulation_data = {}
    if os.path.exists(coagulation_path):
        coagulation_data = load_json(coagulation_path)
        try:
            validate(instance=coagulation_data, schema=coagulation_schema)
            print("[OK] interactions/coagulation.json matches schema.")
        except ValidationError as ve:
            errors.append(f"interactions/coagulation.json schema validation failed: {ve.message}")
            print("[FAIL] interactions/coagulation.json schema validation failed.")
    else:
        errors.append("CRITICAL: interactions/coagulation.json is missing.")

    if errors:
        print("\nValidation failed with errors:")
        for err in errors:
            print(f"- {err}")
        sys.exit(1)

    # Core metadata definitions
    languages = metadata.get("languages", [])
    valid_tags = set(metadata.get("tags", []))
    valid_categories = set(metadata.get("categories", []))
    valid_groups = set(metadata.get("groups", []))
    expected_units = {"g", "ml", "piece", "cup", "tbsp", "tsp"}

    # 3. Load and Validate Category files
    all_food_ids = set()
    food_by_id = {}
    category_foods = {} # category -> list of food dicts

    for category in valid_categories:
        cat_file = os.path.join(DATA_DIR, "categories", f"{category}.json")
        if not os.path.exists(cat_file):
            errors.append(f"Category '{category}' is defined in metadata, but file is missing at {cat_file}")
            continue

        cat_data = load_json(cat_file)
        try:
            validate(instance=cat_data, schema=category_schema)
            print(f"[OK] categories/{category}.json matches schema.")
        except ValidationError as ve:
            errors.append(f"categories/{category}.json schema validation failed: {ve.message}")
            print(f"[FAIL] categories/{category}.json schema validation failed.")
            continue

        category_foods[category] = cat_data.get("data", [])
        
        # Cross-reference item validation
        for food in cat_data.get("data", []):
            food_id = food.get("id")
            
            # Check unique food ID
            if food_id in all_food_ids:
                errors.append(f"Duplicate food ID '{food_id}' found in categories/{category}.json")
            else:
                all_food_ids.add(food_id)
                food_by_id[food_id] = food

            # Check category field matches filename
            food_category = food.get("category")
            if food_category != category:
                errors.append(f"Food item '{food_id}' in file {category}.json has mismatching category '{food_category}'")

            # Check tags are defined in metadata
            for tag in food.get("tags", []):
                if tag not in valid_tags:
                    errors.append(f"Food item '{food_id}' uses undefined tag '{tag}'")

            # Check group is defined in metadata
            relations = food.get("relations")
            if relations:
                group = relations.get("group")
                if group and group not in valid_groups:
                    errors.append(f"Food item '{food_id}' uses undefined group '{group}' in relations")

    translated_interaction_keys = {}

    # 4. Load and Validate common translations
    for lang in languages:
        common_trans_path = os.path.join(DATA_DIR, "i18n", lang, "common.json")
        if not os.path.exists(common_trans_path):
            errors.append(f"Common translation file missing for language '{lang}' at {common_trans_path}")
            continue

        common_trans = load_json(common_trans_path)
        try:
            validate(instance=common_trans, schema=common_trans_schema)
            print(f"[OK] i18n/{lang}/common.json matches schema.")
        except ValidationError as ve:
            errors.append(f"i18n/{lang}/common.json schema validation failed: {ve.message}")
            print(f"[FAIL] i18n/{lang}/common.json schema validation failed.")
            continue

        # Check all categories are translated
        translated_categories = common_trans.get("categories", {})
        for cat in valid_categories:
            if cat not in translated_categories:
                errors.append(f"Category '{cat}' is not translated in common.{lang}.json")

        # Check all tags are translated
        translated_tags = common_trans.get("tags", {})
        for tag in valid_tags:
            if tag not in translated_tags:
                errors.append(f"Tag '{tag}' is not translated in common.{lang}.json")

        # Check all units are translated
        translated_units = common_trans.get("units", {})
        for unit in expected_units:
            if unit not in translated_units:
                errors.append(f"Unit '{unit}' is not translated in common.{lang}.json")

        # Collect translated interaction keys
        interaction_keys = common_trans.get("interactions", {})
        translated_interaction_keys[lang] = set(interaction_keys.keys())

    # 5. Load and Validate food translations
    for category in valid_categories:
        for lang in languages:
            food_trans_path = os.path.join(DATA_DIR, "i18n", lang, f"{category}.json")
            if not os.path.exists(food_trans_path):
                errors.append(f"Translation file missing for category '{category}' and language '{lang}' at {food_trans_path}")
                continue

            food_trans = load_json(food_trans_path)
            try:
                validate(instance=food_trans, schema=food_trans_schema)
                print(f"[OK] i18n/{lang}/{category}.json matches schema.")
            except ValidationError as ve:
                errors.append(f"i18n/{lang}/{category}.json schema validation failed: {ve.message}")
                print(f"[FAIL] i18n/{lang}/{category}.json schema validation failed.")
                continue

            # Ensure all food items in category file are translated in this language file
            foods = category_foods.get(category, [])
            for food in foods:
                food_id = food.get("id")
                if food_id not in food_trans:
                    errors.append(f"Food item '{food_id}' is missing translation in i18n/{lang}/{category}.json")

    # 6. Validate relations
    for food_id, food in food_by_id.items():
        relations = food.get("relations")
        if relations:
            related_ids = relations.get("related_ids", [])
            for rel_id in related_ids:
                if rel_id not in all_food_ids:
                    errors.append(f"Food item '{food_id}' references non-existent related ID '{rel_id}'")

    # 6b. Cross-reference interaction checks
    # 6b.1. Validate warfarin.json
    for food_id, details in warfarin_data.items():
        if food_id not in all_food_ids:
            errors.append(f"warfarin.json references non-existent food ID '{food_id}'")
            continue
        
        # Check that food has the tag "affects_warfarin"
        food_tags = food_by_id[food_id].get("tags", [])
        if "affects_warfarin" not in food_tags:
            errors.append(f"Food item '{food_id}' is in warfarin.json but is missing the 'affects_warfarin' tag in its category file")

        # Validate recommendation_key translations
        rec_key = details.get("recommendation_key")
        for lang in languages:
            lang_keys = translated_interaction_keys.get(lang, set())
            if rec_key not in lang_keys:
                errors.append(f"Recommendation key '{rec_key}' in warfarin.json is not translated in common.{lang}.json")

    # 6b.2. Validate coagulation.json
    for food_id, details in coagulation_data.items():
        if food_id not in all_food_ids:
            errors.append(f"coagulation.json references non-existent food ID '{food_id}'")
            continue
        
        # Check that food has the tag "affects_coagulation"
        food_tags = food_by_id[food_id].get("tags", [])
        if "affects_coagulation" not in food_tags:
            errors.append(f"Food item '{food_id}' is in coagulation.json but is missing the 'affects_coagulation' tag in its category file")

    # 6b.3. Verify foods with tags are in the interaction files
    for food_id, food in food_by_id.items():
        tags = food.get("tags", [])
        if "affects_warfarin" in tags and food_id not in warfarin_data:
            errors.append(f"Food item '{food_id}' has 'affects_warfarin' tag but is missing from warfarin.json")
        if "affects_coagulation" in tags and food_id not in coagulation_data:
            errors.append(f"Food item '{food_id}' has 'affects_coagulation' tag but is missing from coagulation.json")

    # 7. Print final results
    if errors:
        print("\n[ERROR] Validation failed with errors:")
        for err in errors:
            print(f"- {err}")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Validation completed successfully! All data files are valid and cross-referenced correctly.")
        sys.exit(0)

if __name__ == "__main__":
    main()
