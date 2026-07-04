# Contributing to Vitamin K Food Database

Thank you for your interest in contributing to the Vitamin K Food Database! Contributions from the community help keep this database accurate, comprehensive, and up-to-date.

By contributing to this project, you agree to abide by our code of conduct and contribution guidelines.

---

## How Can I Contribute?

You can contribute in several ways:
1. **Add New Food Items:** Add foods that are missing from the current categories.
2. **Correct Existing Data:** Fix typos, spelling mistakes, or incorrect Vitamin K values.
3. **Translate Content:** Translate food names, descriptions, or portion sizes into supported languages (e.g., English, Slovak).
4. **Update Clinical Interactions:** Add or refine data regarding how foods affect blood clotting (coagulation) or interact with anticoagulants (Warfarin).

---

## Development & Contribution Workflow

This project is a static JSON database, meaning updates are made directly to JSON files and verified using automated Python validation scripts.

### 1. Prerequisites
To run validation scripts locally, you need **Python 3.x** installed.

### 2. Step-by-Step Process

1. **Fork the Repository:** Create a fork of this repository on GitHub and clone it locally.
2. **Make Your Changes:**
   * **Categories:** Add or edit foods in `data/categories/<category_id>.json`.
   * **Translations:** Translate the food items in `data/i18n/<lang>/<category_id>.json` and common terms in `data/i18n/<lang>/common.json`.
   * **Interactions:** Add drug/clotting interaction properties in `data/interactions/warfarin.json` or `data/interactions/coagulation.json`.
3. **Verify Your Changes (Mandatory):**
   Run the validation suite locally using the command line:
   ```bash
   python scripts/validate_data.py
   ```
   *The validation script checks that all files match their JSON schemas, tags are validly registered, and translations and interaction IDs match the core food categories.* **Your Pull Request cannot be merged if validation checks fail.**
4. **Commit and Push:**
   * Do not commit build artifacts (like `release_manifest.json`, which is automatically ignored).
   * Write clean, descriptive commit messages (e.g., `data: add raw avocado to fruits and translate to sk`).
5. **Submit a Pull Request (PR):**
   * Open a PR against the `main` branch of the parent repository.
   * Provide a brief summary of what was added or changed, and cite any reliable clinical or nutritional sources (especially for interaction and coagulation updates).

---

## Data Structure & Validation Rules

To keep the database clean and prevent bugs in consuming apps, all changes must strictly follow these rules:

### 1. Food IDs
* Food IDs must be unique across the entire database.
* Use `snake_case` (e.g., `spinach_raw`, `st_johns_wort`).

### 2. Portions & Null Values
* For typical foods, include portion sizes (with `amount`, `unit`, `vitamin_k_mcg`, and `gram_equivalent` if the unit is not `"g"`). Each food with portions must have at least one baseline portion where `amount` is `100` and `unit` is `"g"`.
* If a food item is added **only** for drug interactions and does not have standard nutritional Vitamin K values (e.g., St. John's Wort supplement), set the `portions` field to `null` instead of an empty array:
  ```json
  "portions": null
  ```

### 3. Tags
* Every food item can have an array of tags (e.g., `["green_leaves", "raw", "affects_warfarin"]`).
* All tags used in category files must be registered in the central `data/metadata.json` file.
* **Special tags:** Use `affects_warfarin` or `affects_coagulation` to flag foods that have clinical interaction details.

### 4. Translation Files
* For every food item added to a category, a matching key **must** be created in all translation files under `data/i18n/<lang>/<category_id>.json`.
* If you add a new category or tag, translate its display name in `data/i18n/<lang>/common.json`.

### 5. Interaction Files
* If a food item has the `affects_warfarin` tag, it **must** have an entry in `data/interactions/warfarin.json` detailing the `effect`, `severity`, `mechanism`, and `recommendation_key`.
* If a food item has the `affects_coagulation` tag, it **must** have an entry in `data/interactions/coagulation.json` detailing the `effect`, `severity`, and `active_compounds`.
* All interaction keys and recommendations must have translations registered in the `"interactions"` section of `data/i18n/<lang>/common.json`.

---

## Need Help?

If you have any questions or are unsure about how to format your data, feel free to open an **Issue** on GitHub, and the maintainers will guide you!
