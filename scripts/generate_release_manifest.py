import os
import json
import subprocess
import sys
import re
import hashlib

def run_git(args):
    try:
        res = subprocess.run(['git'] + args, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e.stderr}", file=sys.stderr)
        return None

def calculate_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    print("Generating release manifest (Fully Automated Release Versioning)...")
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(repo_root, "data")
    
    # 1. Load current metadata.json
    metadata_path = os.path.join(data_dir, "metadata.json")
    if not os.path.exists(metadata_path):
        print(f"Error: metadata.json not found at {metadata_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    categories = metadata.get("categories", [])
    languages = metadata.get("languages", [])
    
    # 2. Determine current tag and previous tag from Git
    current_tag = os.environ.get("GITHUB_REF_NAME") or os.environ.get("RELEASE_TAG")
    if not current_tag and len(sys.argv) > 1:
        current_tag = sys.argv[1]
        
    if not current_tag:
        current_tag = "v0.0.0"
        
    current_global_version = current_tag.lstrip('v')
    
    tags_str = run_git(['tag', '--sort=-v:refname'])
    tags = tags_str.splitlines() if tags_str else []
    
    previous_tag = None
    for t in tags:
        if t != current_tag:
            previous_tag = t
            break
            
    previous_global_version = previous_tag.lstrip('v') if previous_tag else None
            
    print(f"Current Tag: {current_tag} (Version: {current_global_version})")
    print(f"Previous Tag: {previous_tag} (Version: {previous_global_version})")
    
    # 3. Determine base URL using remote origin URL
    base_url = "https://andrejvrabec.github.io/vitamin-k-food-database/"
    remote_url = run_git(['remote', 'get-url', 'origin'])
    if remote_url:
        match = re.search(r'github\.com[:/]([^/]+)/([^.]+)(?:\.git)?', remote_url)
        if match:
            owner = match.group(1)
            repo = match.group(2)
            base_url = f"https://{owner}.github.io/{repo}/"
    print(f"Determined Base URL: {base_url}")

    # 4. Find all changed files using git diff if previous tag exists
    changed_files = set()
    if previous_tag:
        diff_str = run_git(['diff', '--name-only', previous_tag])
        if diff_str:
            changed_files = set(diff_str.splitlines())

    # 5. Process global metadata
    metadata_rel = "data/metadata.json"
    global_changed = (metadata_rel in changed_files)
    metadata_sha = calculate_sha256(metadata_path)
    
    metadata_manifest = {
        "url": f"{base_url}{metadata_rel}",
        "sha256": metadata_sha,
        "changed": (not previous_tag) or global_changed
    }

    # 6. Process categories
    categories_manifest = {}
    for cat in categories:
        cat_filename = f"{cat}.json"
        cat_rel_path = f"data/categories/{cat_filename}"
        cat_abs_path = os.path.join(data_dir, "categories", cat_filename)
        
        cat_sha = calculate_sha256(cat_abs_path)
        cat_changed = (cat_rel_path in changed_files)
        
        categories_manifest[cat] = {
            "url": f"{base_url}{cat_rel_path}",
            "sha256": cat_sha,
            "changed": (not previous_tag) or cat_changed
        }
        
    # 7. Process translations
    translations_manifest = {}
    for lang in languages:
        lang_trans = {}
        
        # 1. common.json
        common_rel = f"data/i18n/{lang}/common.json"
        common_abs = os.path.join(data_dir, "i18n", lang, "common.json")
        if os.path.exists(common_abs):
            common_sha = calculate_sha256(common_abs)
            lang_trans["common"] = {
                "url": f"{base_url}{common_rel}",
                "sha256": common_sha,
                "changed": (not previous_tag) or (common_rel in changed_files)
            }
            
        # 2. Category translations
        for cat in categories:
            cat_trans_rel = f"data/i18n/{lang}/{cat}.json"
            cat_trans_abs = os.path.join(data_dir, "i18n", lang, f"{cat}.json")
            if os.path.exists(cat_trans_abs):
                cat_trans_sha = calculate_sha256(cat_trans_abs)
                lang_trans[cat] = {
                    "url": f"{base_url}{cat_trans_rel}",
                    "sha256": cat_trans_sha,
                    "changed": (not previous_tag) or (cat_trans_rel in changed_files)
                }
                
        translations_manifest[lang] = lang_trans

    # 7b. Process interactions
    interactions_manifest = {}
    interaction_files = ["warfarin", "coagulation"]
    for int_file in interaction_files:
        int_filename = f"{int_file}.json"
        int_rel_path = f"data/interactions/{int_filename}"
        int_abs_path = os.path.join(data_dir, "interactions", int_filename)
        
        int_sha = calculate_sha256(int_abs_path)
        int_changed = (int_rel_path in changed_files)
        
        interactions_manifest[int_file] = {
            "url": f"{base_url}{int_rel_path}",
            "sha256": int_sha,
            "changed": (not previous_tag) or int_changed
        }

    # 8. Build final manifest
    manifest = {
        "tag": current_tag,
        "previous_tag": previous_tag,
        "global_version": current_global_version,
        "previous_global_version": previous_global_version,
        "global_version_changed": (current_global_version != previous_global_version),
        "files": {
            "metadata": metadata_manifest,
            "categories": categories_manifest,
            "translations": translations_manifest,
            "interactions": interactions_manifest
        }
    }
    
    # 9. Write manifest to release_manifest.json
    manifest_path = os.path.join(repo_root, "release_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated release manifest at {manifest_path}")

if __name__ == "__main__":
    main()
