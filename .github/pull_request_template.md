## Description
Please describe the changes proposed in this Pull Request (e.g., adding a new food, correcting Vitamin K values, fixing translations).

## Contribution Checklist
Before submitting, please make sure you have done the following:
- [ ] I have run the validation script locally (`python scripts/validate_data.py`) and it completed successfully.
- [ ] If I added new food items, tags, or categories, I translated them in all supported languages in the `data/i18n/` directory.
- [ ] All portions with units other than `"g"` (e.g., `cup`, `piece`, `tbsp`) have their `gram_equivalent` specified.
- [ ] If new relations are added, I verified that the related food IDs exist in the dataset.
- [ ] I have updated the version numbers in the modified category files and/or `metadata.json` according to the [VERSIONING.md](file:///f:/Projects/VitaminK/VitaminKDataSource/VERSIONING.md) guidelines (or left it for the maintainers to bump).
