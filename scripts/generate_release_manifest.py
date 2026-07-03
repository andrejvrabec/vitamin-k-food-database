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
    
    # 2. Try to load existing manifest (locally or from live URL)
    existing_manifest = None
    manifest_path = os.path.join(repo_root, "release_manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                existing_manifest = json.load(f)
            print("Loaded existing release_manifest.json from local workspace.")
        except Exception as e:
            print(f"Warning: Could not parse local manifest: {e}", file=sys.stderr)
            
    # Base URL parsing
    base_url = "https://andrejvrabec.github.io/vitamin-k-food-database/"
    remote_url = run_git(['remote', 'get-url', 'origin'])
    if remote_url:
        match = re.search(r'github\.com[:/]([^/]+)/([^.]+)(?:\.git)?', remote_url)
        if match:
            owner = match.group(1)
            repo = match.group(2)
            base_url = f"https://{owner}.github.io/{repo}/"
    print(f"Determined Base URL: {base_url}")

    if not existing_manifest:
        live_manifest_url = f"{base_url}release_manifest.json"
        print(f"Local manifest not found. Attempting to fetch live manifest from: {live_manifest_url}")
        try:
            import urllib.request
            with urllib.request.urlopen(live_manifest_url, timeout=5) as response:
                if response.status == 200:
                    existing_manifest = json.loads(response.read().decode('utf-8'))
                    print("Successfully loaded existing release_manifest.json from live deployed URL.")
        except Exception as e:
            print(f"Warning: Could not fetch live manifest: {e}", file=sys.stderr)
            
    # 3. Determine if this is a formal release tag build
    raw_tag = os.environ.get("GITHUB_REF_NAME") or os.environ.get("RELEASE_TAG")
    if not raw_tag and len(sys.argv) > 1:
        raw_tag = sys.argv[1]
        
    is_release = bool(raw_tag and re.match(r'^v\d+\.\d+\.\d+', raw_tag))
    
    if is_release:
        current_tag = raw_tag
        current_global_version = current_tag.lstrip('v')
        
        tags_str = run_git(['tag', '--sort=-v:refname'])
        tags = tags_str.splitlines() if tags_str else []
        
        previous_tag = None
        for t in tags:
            if t != current_tag:
                previous_tag = t
                break
                
        previous_global_version = previous_tag.lstrip('v') if previous_tag else None
        global_version_changed = (current_global_version != previous_global_version)
    else:
        # If not running on a release tag, reuse the versions from the existing manifest
        print("Build triggered outside of a formal release tag. Reusing existing manifest versions to keep them intact.")
        if existing_manifest:
            current_tag = existing_manifest.get("tag", "v0.0.0")
            previous_tag = existing_manifest.get("previous_tag")
            current_global_version = existing_manifest.get("global_version", "0.0.0")
            previous_global_version = existing_manifest.get("previous_global_version")
        else:
            current_tag = "v0.0.0"
            previous_tag = None
            current_global_version = "0.0.0"
            previous_global_version = None
        global_version_changed = False
            
    print(f"Current Tag: {current_tag} (Version: {current_global_version})")
    print(f"Previous Tag: {previous_tag} (Version: {previous_global_version})")
    print(f"Global Version Changed: {global_version_changed}")
    
    # 4. Find changed files using git diff if it is a release tag build
    changed_files = set()
    if is_release and previous_tag:
        diff_str = run_git(['diff', '--name-only', previous_tag])
        if diff_str:
            changed_files = set(diff_str.splitlines())

    # Helper function to check if a file was modified compared to the release tag or previous manifest hashes
    def was_file_modified(rel_path, current_sha):
        if is_release:
            return (not previous_tag) or (rel_path in changed_files)
        
        # If not a release build, compare hashes with existing manifest
        if not existing_manifest:
            return True
            
        files_section = existing_manifest.get("files", {})
        
        # metadata
        if rel_path == "data/metadata.json":
            return files_section.get("metadata", {}).get("sha256") != current_sha
            
        # categories
        match = re.match(r'^data/categories/([^/]+)\.json$', rel_path)
        if match:
            cat = match.group(1)
            return files_section.get("categories", {}).get(cat, {}).get("sha256") != current_sha
            
        # interactions
        match = re.match(r'^data/interactions/([^/]+)\.json$', rel_path)
        if match:
            int_file = match.group(1)
            return files_section.get("interactions", {}).get(int_file, {}).get("sha256") != current_sha
            
        # translations
        match = re.match(r'^data/i18n/([^/]+)/([^/]+)\.json$', rel_path)
        if match:
            lang = match.group(1)
            key = match.group(2)
            return files_section.get("translations", {}).get(lang, {}).get(key, {}).get("sha256") != current_sha
            
        return True

    # 5. Process global metadata
    metadata_rel = "data/metadata.json"
    metadata_sha = calculate_sha256(metadata_path)
    metadata_manifest = {
        "url": f"{base_url}{metadata_rel}",
        "sha256": metadata_sha,
        "changed": was_file_modified(metadata_rel, metadata_sha)
    }

    # 6. Process categories
    categories_manifest = {}
    for cat in categories:
        cat_filename = f"{cat}.json"
        cat_rel_path = f"data/categories/{cat_filename}"
        cat_abs_path = os.path.join(data_dir, "categories", cat_filename)
        
        cat_sha = calculate_sha256(cat_abs_path)
        categories_manifest[cat] = {
            "url": f"{base_url}{cat_rel_path}",
            "sha256": cat_sha,
            "changed": was_file_modified(cat_rel_path, cat_sha)
        }
        
    # 7. Process translations
    translations_manifest = {}
    for lang in languages:
        lang_trans = {}
        
        # common.json
        common_rel = f"data/i18n/{lang}/common.json"
        common_abs = os.path.join(data_dir, "i18n", lang, "common.json")
        if os.path.exists(common_abs):
            common_sha = calculate_sha256(common_abs)
            lang_trans["common"] = {
                "url": f"{base_url}{common_rel}",
                "sha256": common_sha,
                "changed": was_file_modified(common_rel, common_sha)
            }
            
        # Category translations
        for cat in categories:
            cat_trans_rel = f"data/i18n/{lang}/{cat}.json"
            cat_trans_abs = os.path.join(data_dir, "i18n", lang, f"{cat}.json")
            if os.path.exists(cat_trans_abs):
                cat_trans_sha = calculate_sha256(cat_trans_abs)
                lang_trans[cat] = {
                    "url": f"{base_url}{cat_trans_rel}",
                    "sha256": cat_trans_sha,
                    "changed": was_file_modified(cat_trans_rel, cat_trans_sha)
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
        interactions_manifest[int_file] = {
            "url": f"{base_url}{int_rel_path}",
            "sha256": int_sha,
            "changed": was_file_modified(int_rel_path, int_sha)
        }

    # 8. Build final manifest
    manifest = {
        "tag": current_tag,
        "previous_tag": previous_tag,
        "global_version": current_global_version,
        "previous_global_version": previous_global_version,
        "global_version_changed": global_version_changed,
        "files": {
            "metadata": metadata_manifest,
            "categories": categories_manifest,
            "translations": translations_manifest,
            "interactions": interactions_manifest
        }
    }
    
    # 9. Write manifest to release_manifest.json
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated release manifest at {manifest_path}")

if __name__ == "__main__":
    main()
