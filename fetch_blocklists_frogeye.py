#!/usr/bin/env python3

import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple

# URLs for Frogeye's blocklists
BLOCKLIST_URLS = {
    "First-party Trackers": "https://hostfiles.frogeye.fr/firstparty-trackers.txt",
    "First-party Only Trackers": "https://hostfiles.frogeye.fr/firstparty-only-trackers.txt",
    "Multi-party Trackers": "https://hostfiles.frogeye.fr/multiparty-trackers.txt",
    "Multi-party Only Trackers": "https://hostfiles.frogeye.fr/multiparty-only-trackers.txt"
}

def fetch_blocklist(url: str) -> Tuple[List[str], int]:
    """Fetch a blocklist from URL and return its domains and count."""
    response = requests.get(url)
    response.raise_for_status()
    domains = [line.strip() for line in response.text.splitlines() if line.strip() and not line.startswith('#')]
    return domains, len(domains)

def main():
    """Main function to fetch and process Frogeye's blocklists."""
    print("Starting to fetch Frogeye blocklists...")
    
    # Dictionary to store blocklist data
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
            category = name.split()[0] + ("-party" if "party" not in name else "") + " Trackers"
            blocklist_data["categories"][category]["blocklists"].append({
                "name": name,
                "url": url,
                "count": count,
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
                f.write(f"- Entries: {blocklist['count']}\n\n")

    # Save as JSON
    print("Saving blocklists to JSON...")
    with open("blocklists_frogeye.json", "w", encoding="utf-8") as f:
        json.dump(blocklist_data, f, indent=2)

    print("Successfully saved blocklists to blocklists_frogeye.md and blocklists_frogeye.json")

if __name__ == "__main__":
    main() 