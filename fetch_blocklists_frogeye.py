#!/usr/bin/env python3
"""
Fetch and process Geoffrey Frogeye's tracker blocklists.

This script fetches various tracker blocklists from Geoffrey Frogeye's hostfiles.frogeye.fr,
processes them, and saves the results in both markdown and JSON formats.

The script handles four types of blocklists:
1. First-party Trackers - Hand-picked list of first-party trackers
2. First-party Only Trackers - First-party trackers without company domains
3. Multi-party Trackers - Trackers from existing lists like EasyPrivacy
4. Multi-party Only Trackers - Multi-party trackers without company domains

Output files:
- blocklists_frogeye.md: Human-readable markdown format
- blocklists_frogeye.json: Machine-readable JSON format with standardized keys
"""

import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple
import datetime
import os

# URLs for Frogeye's blocklists
BLOCKLIST_URLS = {
    "First-party Trackers": "https://hostfiles.frogeye.fr/firstparty-trackers.txt",
    "First-party Only Trackers": "https://hostfiles.frogeye.fr/firstparty-only-trackers.txt",
    "Multi-party Trackers": "https://hostfiles.frogeye.fr/multiparty-trackers.txt",
    "Multi-party Only Trackers": "https://hostfiles.frogeye.fr/multiparty-only-trackers.txt"
}

def save_debug_info(name: str, domains: List[str], count: int) -> None:
    """
    Save debug information including sample domains and statistics.
    
    Args:
        name: Name of the blocklist
        domains: List of domains in the blocklist
        count: Total number of domains
    """
    debug_dir = Path("debug_screenshots")
    debug_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_file = debug_dir / f"frogeye_{name.lower().replace(' ', '_')}_{timestamp}.txt"
    
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(f"Debug information for {name}\n")
        f.write(f"Timestamp: {datetime.datetime.now().isoformat()}\n")
        f.write(f"Total domains: {count}\n\n")
        f.write("Sample domains (first 10):\n")
        for domain in domains[:10]:
            f.write(f"- {domain}\n")
        f.write("\nSample domains (last 10):\n")
        for domain in domains[-10:]:
            f.write(f"- {domain}\n")

def fetch_blocklist(url: str) -> Tuple[List[str], int]:
    """
    Fetch a blocklist from URL and return its domains and count.
    
    Args:
        url: URL of the blocklist to fetch
        
    Returns:
        Tuple containing:
        - List of domains from the blocklist
        - Number of domains in the list
    """
    with urllib.request.urlopen(url) as response:
        content = response.read().decode('utf-8')
        domains = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith('#')]
        return domains, len(domains)

def main():
    """Main function to fetch and process Frogeye's blocklists."""
    print("Starting to fetch Frogeye blocklists...")
    
    # Dictionary to store blocklist data with standardized format
    blocklist_data = {
        "categories": {
            "First-party Trackers": {
                "description": "Contains every hostname redirecting to a hand-picked list of first-party trackers. Safe from false-positives.",
                "blocklists": []
            },
            "First-party Only": {
                "description": "Same as First-party Trackers but without company domains. For browser extensions like uBlock Origin.",
                "blocklists": []
            },
            "Multi-party Trackers": {
                "description": "Contains hostnames redirecting to trackers found in existing lists (EasyPrivacy, AdGuard). May have false positives.",
                "blocklists": []
            },
            "Multi-party Only": {
                "description": "Same as Multi-party Trackers but without company domains. For use with other blocklists in regex-mode.",
                "blocklists": []
            }
        }
    }

    # Fetch and process each blocklist
    for name, url in BLOCKLIST_URLS.items():
        print(f"Fetching {name}...")
        try:
            domains, count = fetch_blocklist(url)
            # Save debug information
            save_debug_info(name, domains, count)
            
            category = name.split()[0] + ("-party" if "party" not in name else "") + " Trackers"
            blocklist_data["categories"][category]["blocklists"].append({
                "name": name,
                "url": url,
                "entries": count,  # Using standardized key "entries" instead of "count"
                "source": "Geoffrey Frogeye's First-party Trackers"
            })
        except Exception as e:
            print(f"Error fetching {name}: {e}")

    # Save as markdown
    print("Saving blocklists to markdown...")
    with open("blocklists_frogeye.md", "w", encoding="utf-8") as f:
        f.write("# Geoffrey Frogeye's Tracker Blocklists\n\n")
        for category, data in blocklist_data["categories"].items():
            f.write(f"## {category}\n\n")
            f.write(f"{data['description']}\n\n")
            for blocklist in data["blocklists"]:
                f.write(f"### {blocklist['name']}\n")
                f.write(f"- Source: {blocklist['source']}\n")
                f.write(f"- URL: {blocklist['url']}\n")
                f.write(f"- Entries: {blocklist['entries']}\n\n")

    # Save as JSON
    print("Saving blocklists to JSON...")
    with open("blocklists_frogeye.json", "w", encoding="utf-8") as f:
        json.dump(blocklist_data, f, indent=2)

    print("Successfully saved blocklists to blocklists_frogeye.md and blocklists_frogeye.json")

if __name__ == "__main__":
    main() 