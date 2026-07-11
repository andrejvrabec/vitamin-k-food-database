# Vitamin K Food Database

A public, open-source dataset containing Vitamin K levels in various foods. The database is stored as structured JSON files, optimized for easy consumption by applications, localized translations, and crowdsourced updates via GitHub.

## Directory Structure

```
├── schema/                     # JSON Schemas for file format validation
│   ├── metadata.schema.json
│   ├── category.schema.json
│   ├── common_translation.schema.json
│   ├── food_translation.schema.json
│   ├── warfarin_interaction.schema.json
│   └── coagulation_influence.schema.json
├── data/
│   ├── metadata.json           # Version, active languages, tags, and categories
│   ├── categories/             # Foods split by category
│   │   ├── vegetables.json
│   │   ├── fruits.json
│   │   └── ...
│   ├── interactions/           # Drug interactions & clotting data
│   │   ├── warfarin.json
│   │   └── coagulation.json
│   └── i18n/                   # Localized translation files
│       ├── en/                 # English translations
│       │   ├── common.json     # Common metadata translations (categories, units, tags)
│       │   ├── vegetables.json # Category-specific food translations
│       │   └── ...
│       └── sk/                 # Slovak translations
│           ├── common.json
│           ├── vegetables.json
│           └── ...
├── scripts/
│   └── validate_data.py        # Python script to check format integrity and coverage
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies for validation
```

---

## Data Sources & Quality Criteria

To maintain clinical reliability and data integrity, all food entries and interaction mappings must trace back to official, high-quality reference databases.

### Requirements for Adding New Sources
Whenever a new source is added to the database:
1. **Credibility & Authority:** Only official national/governmental food composition databases, peer-reviewed clinical studies, or recognized medical monographs are permitted. Ad-hoc recipe sites or unverified blogs are strictly prohibited.
2. **Traceability:** The source must be explicitly documented in the `source` attribute of the food item, specifying the database name and record identifier (e.g. food code, NDB ID, or publication ID).
3. **Standardized Base:** Nutritional values must be provided in micrograms ($\mu\text{g}$) per 100g (or 100mL) for base portions.

### Currently Integrated Sources
The database aggregates and cross-references data from the following verified databases:
- **USDA SR28 / FoodData Central:** The primary source for raw food components and portions (US Department of Agriculture).
- **CIQUAL 2025:** The French food composition table managed by ANSES, providing detailed Vitamin K1 and K2 measurements.
- **FDA Prescribing Information:** Official US Food and Drug Administration drug labels (e.g. Coumadin/Warfarin).
- **Stockley's Drug Interactions:** Standard reference handbook for clinical drug-drug and food-drug interactions.
- **MSKCC "About Herbs":** Memorial Sloan Kettering Cancer Center database for herbal and botanical components.
- **NIH NCCIH:** National Center for Complementary and Integrative Health resources.

For detailed licensing information, usage rights, and official citations of these sources, please see [ATTRIBUTIONS.md](file:///f:/Projects/VitaminK/VitaminKDataSource/ATTRIBUTIONS.md).

---

## Data Schema & Rules

### 1. Root Metadata (`data/metadata.json`)
Defines the supported translation languages, valid categories, valid tags, valid relations groups, and data sources.
- Example:
  ```json
  {
    "languages": ["en", "sk"],
    "tags": ["green_leaves", "berries"],
    "categories": ["vegetables", "fruits"],
    "groups": ["broccoli", "spinach", "blueberry"],
    "sources": {
      "usda": {
        "name": "USDA FoodData Central / SR28",
        "url": "https://fdc.nal.usda.gov/",
        "license": "CC0-1.0"
      },
      "ciqual": {
        "name": "ANSES CIQUAL 2025",
        "url": "https://ciqual.anses.fr/",
        "license": "Open Licence 2.0"
      }
    }
  }
  ```

### 2. Category Files (`data/categories/<category_id>.json`)
Each file corresponds to a category named `<category_id>.json` and contains:
- `version`: Version of this specific file (e.g., `"0.1.0"`).
- `data`: An array of food items containing:
- `id`: Unique lowercase identifier (e.g., `spinach_raw`).
- `category`: Must match the `<category_id>` of the filename.
- `tags`: List of tags defined in `metadata.json`.
- `portions` (optional/`null`): A list of portion measurements. Can be set to `null` or omitted entirely for items where Vitamin K content is unknown or not relevant. **Requirement**: If portions are defined, there must be at least one portion with `amount` = 100 and `unit` = "g" (serving as the baseline 100g measurement).
  - `amount`: Number (e.g. `100` or `1`).
  - `unit`: One of `["g", "ml", "piece", "cup", "tbsp", "tsp"]`.
  - `vitamin_k_mcg`: Amount of Vitamin K in micrograms.
  - `vitamin_k1_100g_mcg` (optional): Amount of Vitamin K1 in micrograms (only allowed in the standard 100g portion).
  - `vitamin_k2_100g_mcg` (optional): Amount of Vitamin K2 in micrograms (only allowed in the standard 100g portion).
  - `gram_equivalent`: The equivalent weight in grams. **Required if the unit is NOT `"g"`**. If unit is `"g"`, it is omitted.
- `source`: Reference source for the data (e.g. USDA FoodData Central ID).
- `relations` (optional): Grouping and relation identifier (omitted if the food item does not belong to any obvious food group).
  - `group`: String grouping identifier. Must be registered in the global `"groups"` list of `metadata.json`.
  - `related_ids`: List of related food IDs (other variants in the category sharing the same base ID).

- Example:
  ```json
  {
    "version": "0.1.0",
    "data": [
      {
        "id": "spinach_raw",
        "category": "vegetables",
        "tags": ["green_leaves"],
        "portions": [
          { "amount": 100, "unit": "g", "vitamin_k_mcg": 482.9 },
          { "amount": 1, "unit": "cup", "gram_equivalent": 30, "vitamin_k_mcg": 144.9 }
        ],
        "source": "USDA FDC ID: 168462",
        "relations": {
          "group": "spinach",
          "related_ids": ["spinach_cooked"]
        }
      }
    ]
  }
  ```

### 3. Translation Files (`data/i18n/<lang>/`)
Translations are organized in language-specific directories (`en/`, `sk/` etc.) to keep files manageable:
- `<lang>/common.json`: Translates category names, tag names, and unit names.
- `<lang>/<category_id>.json`: Translates the food names, alternative names, and descriptions for that category.
  - Example for `en/vegetables.json`:
    ```json
    {
      "spinach_raw": {
        "name": "Spinach, raw",
        "alternative_names": ["raw spinach", "baby spinach"],
        "description": "Fresh raw spinach leaves."
      }
    }
    ```
  - Example for `sk/vegetables.json`:
    ```json
    {
      "spinach_raw": {
        "name": "Špenát, surový",
        "alternative_names": ["surový špenát", "listový špenát"],
        "description": "Čerstvé listy surového špenátu siateho."
      }
    }
    ```

### 4. Interaction Files (`data/interactions/`)
These files map food IDs to structured drug-interaction or coagulation properties:
- `data/interactions/warfarin.json`: Maps food IDs to their Warfarin interaction profile.
  - `effect`: E.g., `"decreases_efficacy"` or `"increases_bleeding_risk"`.
  - `severity`: `"mild"`, `"moderate"`, or `"high"`.
  - `mechanism`: Technical description of the biological mechanism.
  - `recommendation_key`: Localized recommendation text key (defined in `common.json` under `"interactions"`).
- `data/interactions/coagulation.json`: Maps food IDs to natural blood clotting properties.
  - `effect`: `"anticoagulant"`, `"procoagulant"`, or `"none"`.
  - `severity`: `"mild"`, `"moderate"`, or `"high"`.
  - `active_compounds`: List of active components (e.g. `["allicin", "salicylates"]`).

---

## Contributing & Development

We welcome contributions to add new foods, translate names, or update clinical interactions. To maintain data integrity, all updates are verified by an automated Python validation script.

* **Detailed Guidelines:** Please see [CONTRIBUTING.md](CONTRIBUTING.md) for full instructions on modifying files, formatting portions/tags, and submitting Pull Requests.
* **Code of Conduct:** Please review our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) to understand the behaviors expected of community members.
* **Local Setup & Validation:**
  ```bash
  pip install -r requirements.txt
  python scripts/validate_data.py
  ```

---

## Releasing & Data Consumption (API)

This project uses **GitHub Pages** as a high-performance, CDN-backed static API to distribute the dataset to consuming applications (like mobile apps, websites, or services).

### 1. For Developers (API & Data Sync)

Consuming applications should use the static endpoints hosted on GitHub Pages for fast, rate-limit-free access with full CORS support.

* **Base URL:** `https://andrejvrabec.github.io/vitamin-k-food-database/`
* **Release Manifest:** `https://andrejvrabec.github.io/vitamin-k-food-database/release_manifest.json`

#### Recommended Synchronization Strategy
To minimize network traffic and keep the local application database up-to-date, implement the following check loop:
1. Fetch the small release manifest at `https://andrejvrabec.github.io/vitamin-k-food-database/release_manifest.json`.
2. Compare the `global_version` against the version stored in the client application's local cache.
3. If they differ:
   - Identify which categories have `"changed": true`.
   - Download only the modified category JSON files (e.g., `https://andrejvrabec.github.io/vitamin-k-food-database/data/categories/<category_id>.json`).
   - If `global_version_changed` is a major version bump, perform any necessary database migrations/wipes if required.
   - Save the new version number locally.

#### Direct Data Links & Explanations

* **Global Metadata File:** `https://andrejvrabec.github.io/vitamin-k-food-database/data/metadata.json`
  - *Description:* Defines the global database schema/version, active languages, tags list, and category lists. Used by client apps to learn what categories and translations exist.
* **Category Food Files:** `https://andrejvrabec.github.io/vitamin-k-food-database/data/categories/<category_id>.json`
  - *Description:* Houses the raw food items, portions, sources, and tags for a specific category. E.g., `vegetables.json`.
* **Common Translations:** `https://andrejvrabec.github.io/vitamin-k-food-database/data/i18n/<lang>/common.json`
  - *Description:* Translates tag names, category names, and portion units into the target language (e.g. `data/i18n/sk/common.json` for Slovak).
* **Category Food Translations:** `https://andrejvrabec.github.io/vitamin-k-food-database/data/i18n/<lang>/<category_id>.json`
  - *Description:* Translates category-specific food names, alternative names, and descriptions (e.g. `data/i18n/sk/vegetables.json`).
* **Warfarin Interactions:** `https://andrejvrabec.github.io/vitamin-k-food-database/data/interactions/warfarin.json`
  - *Description:* Houses structured details on food-drug interactions with Warfarin.
* **Coagulation Influences:** `https://andrejvrabec.github.io/vitamin-k-food-database/data/interactions/coagulation.json`
  - *Description:* Houses structured details on natural procoagulant and anticoagulant properties of foods.


---

### 2. For Maintainers (How to Release)

When you make changes to the data, translations, or schemas:

1. **Verify locally:** Run `python scripts/validate_data.py` (or let the pre-commit hook run) to ensure all checks pass.
2. **Commit and push:** Push the changes to the `main` branch. (You do not need to edit version strings inside any JSON files).
3. **Publish GitHub Release:**
   - Go to the **Releases** tab on GitHub and draft a new release.
   - Set the release tag format using Semantic Versioning (e.g., **`v1.1.0`** or **`v2.0.0`** depending on whether additions or breaking deletes were made).
   - Publish the release.
   - The GitHub Actions workflow will automatically trigger, parse the version directly from your release tag, generate the release manifest with SHA-256 hashes, and publish the updated dataset to GitHub Pages.

---

## Medical Disclaimer

> [!WARNING]
> **This database is for informational and educational purposes only.** It is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified healthcare provider with any questions you may have regarding a medical condition, dietary changes, or drug-nutrient interactions (such as Warfarin / anticoagulation therapy). Reliance on any information provided in this dataset is solely at your own risk. The contributors, authors, and maintainers of this repository assume no liability or responsibility for any adverse effects, injuries, or damages arising from the use of this data.


