import os
import shutil
from pathlib import Path

def main():
    # Source path in WSL
    source_dir = Path(r"\\wsl.localhost\Ubuntu\home\phen\.agents\skills")
    
    # Target path on Windows
    target_dir = Path(os.path.expanduser("~")) / ".gemini" / "config" / "skills"
    
    print(f"Source (WSL): {source_dir}")
    print(f"Target (Windows): {target_dir}")
    
    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist.")
        print("Please ensure WSL is running and the path is correct.")
        return
        
    target_dir.mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    for item in source_dir.iterdir():
        if item.is_dir():
            dest = target_dir / item.name
            print(f"Copying {item.name}...")
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
            copied_count += 1
            
    print(f"\nSuccessfully copied {copied_count} skills to Windows Gemini configuration!")
    print("Restart your IDE/coding agent and they should now be fully discovered.")

if __name__ == "__main__":
    main()
