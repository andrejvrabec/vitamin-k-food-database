# Versioning Strategy

This project uses Semantic Versioning (SemVer) adapted for data structures: `MAJOR.MINOR.PATCH`.
Unlike code libraries, versioning is tracked **exclusively at the global level** to simplify maintenance and automate change tracking.

---

## 1. Global Data Version (GitHub Release Tag)

The version of the entire database is defined **exclusively by the Git Tag** you assign when publishing a release on GitHub:
* **Format:** Must use Semantic Versioning with a `v` prefix (e.g. `v1.1.0`).
* **Manifest Automation:** The release pipeline automatically parses this tag to set the global version in the manifest. You never have to manually edit version strings inside the JSON files.

### PATCH (`x.y.z` -> `x.y.z+1`)
*For backward-compatible corrections and bug fixes.*
* Correcting spelling typos or descriptions in foods or translation files.
* Adjusting existing Vitamin K values or gram equivalents to be more accurate.
* Adding relation links (`related_ids`) between existing food items.

### MINOR (`x.y.z` -> `x.y+1.0`)
*For backward-compatible additions.*
* **Adding new food items** to any category.
* Adding new portion types to existing food items.
* Adding new tags or categories to the database.
* Adding a new supported language.

### MAJOR (`x.y.z` -> `x+1.0.0`)
*For backward-incompatible changes (breaking changes).*
* **Deleting a food item** or renaming its ID (`id`).
* Deleting a portion type from a food item.
* Removing existing tags, categories, or supported languages.
* Modifying the validation schemas (`schema/*.schema.json`) in a backward-incompatible way.

---

## 2. File-Level Change Tracking (Automated via SHA-256)

Individual category files (`data/categories/*.json`) and translation files (`data/i18n/**/*.json`) **do not contain version numbers**.

Instead:
1. When a new release is published, the release workflow automatically computes the **SHA-256 hash** of each file.
2. The hashes are compiled into `release_manifest.json`.
3. Client applications (like mobile apps) fetch this manifest, compare the file hashes against their locally cached versions, and download **only** the files that have changed.

### Production Endpoints

* **API Dashboard (Index URL):** `https://andrejvrabec.github.io/vitamin-k-food-database/`
* **Release Manifest JSON URL:** `https://andrejvrabec.github.io/vitamin-k-food-database/release_manifest.json`

