"""
File Verification Script
Run this to verify all Python files are present and have content
"""

import os
from pathlib import Path

def verify_files():
    print("=" * 70)
    print("  VERIFYING ALL PYTHON FILES IN APP FOLDER")
    print("=" * 70)
    print()
    
    base_path = Path("app")
    
    folders = {
        "core": 5,
        "models": 6,
        "services": 5,
        "routes": 3,
        "utils": 2,
    }
    
    total_files = 0
    total_size = 0
    
    for folder, expected_count in folders.items():
        folder_path = base_path / folder
        print(f"📁 {folder}/")
        
        if not folder_path.exists():
            print(f"  ❌ Folder does not exist!")
            continue
        
        py_files = list(folder_path.glob("*.py"))
        
        for file in sorted(py_files):
            size = file.stat().st_size
            status = "✓" if size > 0 or file.name == "__init__.py" else "⚠"
            print(f"  {status} {file.name} ({size:,} bytes)")
            total_files += 1
            total_size += size
        
        print(f"  Found: {len(py_files)}/{expected_count} files")
        print()
    
    # Check root files
    print(f"📁 app/ (root)")
    for file in ["__init__.py", "main.py"]:
        file_path = base_path / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✓ {file} ({size:,} bytes)")
            total_files += 1
            total_size += size
        else:
            print(f"  ❌ {file} (missing)")
    
    print()
    print("=" * 70)
    print(f"  TOTAL: {total_files} files | {total_size:,} bytes")
    print("=" * 70)
    print()
    
    if total_files == 23:
        print("✅ SUCCESS! All 23 Python files are present!")
        print()
        print("You're ready to run:")
        print("  python -m app.main")
    else:
        print(f"⚠ WARNING: Expected 23 files, found {total_files}")
        print()
        print("Try:")
        print("  1. Press F5 in File Explorer to refresh")
        print("  2. Close and reopen your IDE")
        print("  3. Run this script again")
    
    print()
    print("=" * 70)
    
    return total_files == 23

if __name__ == "__main__":
    verify_files()
    input("\nPress Enter to exit...")
