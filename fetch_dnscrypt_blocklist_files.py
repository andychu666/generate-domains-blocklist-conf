#!/usr/bin/env python3
"""
Fetch DNSCrypt domains blocklist generation files.

Downloads the following files from DNSCrypt repository:
- generate-domains-blocklist.py (main script)
- domains-blocklist.conf (configuration)
- domains-time-restricted.txt (time-restricted domains)
- domains-blocklist-local-additions.txt (local additions)
- domains-allowlist.txt (allowed domains)
"""

import requests
import sys
from pathlib import Path

def log_message(message: str) -> None:
    """Print a message to stderr for immediate output."""
    print(message, file=sys.stderr)

def download_file(url: str, output_path: Path) -> None:
    """
    Download a file from URL and save it to the specified path.
    
    Args:
        url: URL to download from
        output_path: Path where to save the file
    """
    try:
        log_message(f"Downloading {output_path.name} from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        
        output_path.write_text(response.text, encoding='utf-8')
        log_message(f"Successfully saved to {output_path}")
        
    except requests.RequestException as e:
        log_message(f"Error downloading {url}: {str(e)}")
        sys.exit(1)
    except IOError as e:
        log_message(f"Error writing to {output_path}: {str(e)}")
        sys.exit(1)

def main():
    """Download all required files from DNSCrypt repository."""
    base_url = "https://raw.githubusercontent.com/DNSCrypt/dnscrypt-proxy/master/utils/generate-domains-blocklist"
    output_dir = Path("generate-domains-blocklist")
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Files to download
    files = {
        "generate-domains-blocklist.py": f"{base_url}/generate-domains-blocklist.py",
        "domains-blocklist.conf": f"{base_url}/domains-blocklist.conf",
        "domains-time-restricted.txt": f"{base_url}/domains-time-restricted.txt",
        "domains-blocklist-local-additions.txt": f"{base_url}/domains-blocklist-local-additions.txt",
        "domains-allowlist.txt": f"{base_url}/domains-allowlist.txt"
    }
    
    # Download each file
    for filename, url in files.items():
        output_path = output_dir / filename
        download_file(url, output_path)
    
    # Make the script executable
    script_path = output_dir / "generate-domains-blocklist.py"
    if sys.platform != "win32":
        script_path.chmod(0o755)
    
    log_message("\nAll files downloaded successfully!")

if __name__ == "__main__":
    main() 