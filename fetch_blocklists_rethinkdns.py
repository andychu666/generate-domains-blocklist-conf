#!/usr/bin/env python3
"""
Fetch and process RethinkDNS blocklists.

This script fetches blocklist configuration from RethinkDNS's official repository
and organizes them according to RethinkDNS's official categorization
(https://rethinkdns.com/configure).

License Information:
- This script is released under the ISC License
- The RethinkDNS configuration data is used under the Mozilla Public License Version 2.0
- Source: https://github.com/serverless-dns/blocklists

Modifications from original RethinkDNS data:
- Reorganized data structure to match official RethinkDNS categories
- Added metadata and statistics
- Enhanced documentation format
- Added entry counts from RethinkDNS configure page
"""

import asyncio
import aiohttp
import json
from pathlib import Path
import datetime
from typing import Dict, List, Any, Optional
import re

class BlocklistProcessor:
    def __init__(self):
        self.source_url = "https://raw.githubusercontent.com/serverless-dns/blocklists/main/config.json"
        self.configure_url = "https://rethinkdns.com/configure"
        self.output_data = {
            "metadata": {
                "last_updated": "",
                "source": self.source_url,
                "configure_source": self.configure_url,
                "license": {
                    "script": "ISC License",
                    "data": "Mozilla Public License Version 2.0",
                    "source_repo": "https://github.com/serverless-dns/blocklists"
                }
            },
            "statistics": {
                "total_blocklists": 0,
                "total_entries": 0,
                "categories": {}
            },
            "categories": {
                "ParentalControl": {
                    "description": "Block adult & pirated content, online gambling & dating, and social media",
                    "total_entries": 0,
                    "subcategories": {
                        "Adult": {
                            "description": "Blocks over 30,000 adult websites",
                            "total_entries": 0,
                            "entries": []
                        },
                        "Piracy": {
                            "description": "Blocks torrents, dubious video streaming and file sharing websites",
                            "total_entries": 0,
                            "entries": []
                        },
                        "Gambling": {
                            "description": "Blocks over 2000+ online gambling websites",
                            "total_entries": 0,
                            "entries": []
                        },
                        "Dating": {
                            "description": "Blocks over 3000+ online dating websites",
                            "total_entries": 0,
                            "entries": []
                        },
                        "SocialMedia": {
                            "description": "Blocks popular social media including Facebook, Instagram, and WhatsApp",
                            "total_entries": 0,
                            "entries": []
                        }
                    }
                },
                "Security": {
                    "description": "Block malware, ransomware, cryptoware, phishers, and other threats",
                    "total_entries": 0,
                    "subcategories": {
                        "Full": {
                            "description": "Blocks over 150,000 malware, spam, scamware, phishing, and other threats",
                            "total_entries": 0,
                            "entries": []
                        },
                        "Extra": {
                            "description": "Blocks over 10,000+ cryptoware and spyware websites",
                            "total_entries": 0,
                            "entries": []
                        }
                    }
                },
                "Privacy": {
                    "description": "Block adware, spyware, scareware, and trackers",
                    "total_entries": 0,
                    "subcategories": {
                        "Lite": {
                            "description": "Blocks over 50,000+ adware and trackers through some of the most well-curated blacklists",
                            "total_entries": 0,
                            "entries": []
                        },
                        "Aggressive": {
                            "description": "Blocks over 100,000+ adware, spyware, and trackers through some of the most extensive blacklists",
                            "total_entries": 0,
                            "entries": []
                        },
                        "Extreme": {
                            "description": "Blocks over 1,000,000+ suspected websites",
                            "total_entries": 0,
                            "entries": []
                        }
                    }
                }
            }
        }

    async def fetch_entry_counts(self) -> Dict[str, int]:
        """Fetch entry counts from RethinkDNS configure page."""
        print(f"Fetching entry counts from {self.configure_url}")
        counts = {}
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(self.configure_url)
                
                # Wait for blocklists to load
                await page.wait_for_selector(".bl-item__count", timeout=30000)
                
                # Get all blocklist items
                items = await page.query_selector_all(".bl-item")
                for item in items:
                    name = await item.query_selector(".bl-item__name")
                    count = await item.query_selector(".bl-item__count")
                    
                    if name and count:
                        name_text = await name.text_content()
                        count_text = await count.text_content()
                        # Extract number from count text (e.g., "1,234 entries" -> 1234)
                        count_num = int(re.sub(r'[^0-9]', '', count_text))
                        counts[name_text.strip()] = count_num
                
                await browser.close()
                return counts
        except Exception as e:
            print(f"Warning: Failed to fetch entry counts: {e}")
            return {}

    async def fetch_config(self) -> Dict[str, Any]:
        """Fetch RethinkDNS configuration from GitHub."""
        print(f"Fetching configuration from {self.source_url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(self.source_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch config: {response.status}")
                
                text = await response.text()
                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    print(f"Debug: JSON decode error. Response preview: {text[:500]}")
                    raise Exception(f"Failed to parse config: {e}")

    def determine_category(self, entry: Dict[str, Any]) -> tuple[str, str]:
        """Determine the category and subcategory for a blocklist entry."""
        group = entry.get("group", "").lower()
        pack = entry.get("pack", [])
        level = entry.get("level", [])

        # ParentalControl subcategories
        if "adult" in pack or any("porn" in p.lower() for p in pack):
            return "ParentalControl", "Adult"
        elif "piracy" in pack or "torrents" in pack or "file-hosts" in pack:
            return "ParentalControl", "Piracy"
        elif "gambling" in pack:
            return "ParentalControl", "Gambling"
        elif "dating" in pack:
            return "ParentalControl", "Dating"
        elif "socialmedia" in pack or "facebook" in pack:
            return "ParentalControl", "SocialMedia"
        
        # Security subcategories
        elif any(p in pack for p in ["malware", "phishing", "scams", "spam"]):
            return "Security", "Full"
        elif any(p in pack for p in ["crypto", "spyware"]):
            return "Security", "Extra"
        
        # Privacy subcategories based on pack and level
        elif "liteprivacy" in pack or (pack and level and max(level) <= 0):
            return "Privacy", "Lite"
        elif "aggressiveprivacy" in pack or (pack and level and max(level) == 1):
            return "Privacy", "Aggressive"
        elif "extremeprivacy" in pack or (pack and level and max(level) >= 2):
            return "Privacy", "Extreme"
        
        # Default categorization based on group
        elif "privacy" in group:
            return "Privacy", "Lite"
        elif "security" in group:
            return "Security", "Full"
        elif "parental" in group:
            return "ParentalControl", "Adult"
        
        return "", ""  # Uncategorized

    def process_entry(self, entry: Dict[str, Any], entry_counts: Dict[str, int]) -> Dict[str, Any]:
        """Process a single blocklist entry."""
        if not entry.get("vname") or not entry.get("url"):
            return None

        name = entry.get("vname", "")
        processed = {
            "name": name,
            "format": entry.get("format", []),
            "url": entry.get("url", []),
            "pack": entry.get("pack", []),
            "level": entry.get("level", []),
            "subgroup": entry.get("subg", ""),
            "entries": entry_counts.get(name, 0),  # Add entry count
            "raw_data": entry
        }
        return processed

    def organize_data(self, config: Dict[str, Any], entry_counts: Dict[str, int]) -> None:
        """Organize the configuration data into categories."""
        if "conf" not in config:
            raise Exception("Invalid config format: 'conf' key not found")

        entries = config["conf"]
        category_stats = {cat: 0 for cat in self.output_data["categories"].keys()}
        total_entries = 0

        # Process each entry
        for entry in entries:
            processed_entry = self.process_entry(entry, entry_counts)
            if not processed_entry:
                continue

            category, subcategory = self.determine_category(entry)
            if not category or not subcategory:
                continue

            # Add to appropriate category/subcategory
            self.output_data["categories"][category]["subcategories"][subcategory]["entries"].append(processed_entry)
            category_stats[category] += 1
            
            # Update entry counts
            entry_count = processed_entry["entries"]
            self.output_data["categories"][category]["total_entries"] += entry_count
            self.output_data["categories"][category]["subcategories"][subcategory]["total_entries"] += entry_count
            total_entries += entry_count

        # Update statistics
        self.output_data["statistics"]["total_blocklists"] = sum(category_stats.values())
        self.output_data["statistics"]["total_entries"] = total_entries
        self.output_data["statistics"]["categories"] = category_stats
        self.output_data["metadata"]["last_updated"] = datetime.datetime.utcnow().isoformat()

    def generate_markdown(self) -> str:
        """Generate markdown documentation."""
        markdown = "# RethinkDNS Blocklists\n\n"
        
        # Add license and metadata
        markdown += "## License Information\n\n"
        markdown += "- Script: ISC License\n"
        markdown += "- Data: Mozilla Public License Version 2.0\n"
        markdown += f"- Source: {self.output_data['metadata']['source']}\n"
        markdown += f"- Configure: {self.output_data['metadata']['configure_source']}\n"
        markdown += f"- Last Updated: {self.output_data['metadata']['last_updated']}\n\n"

        # Add statistics
        markdown += "## Statistics\n\n"
        markdown += f"Total Blocklists: {self.output_data['statistics']['total_blocklists']}\n"
        markdown += f"Total Entries: {self.output_data['statistics']['total_entries']:,}\n\n"
        markdown += "### Categories:\n"
        for category, count in self.output_data['statistics']['categories'].items():
            cat_data = self.output_data["categories"][category]
            markdown += f"- {category}: {count} blocklists, {cat_data['total_entries']:,} entries\n"
        markdown += "\n"

        # Add categories and their entries
        for category, cat_data in self.output_data["categories"].items():
            markdown += f"## {category}\n\n"
            markdown += f"{cat_data['description']}\n"
            markdown += f"Total Entries: {cat_data['total_entries']:,}\n\n"

            for subcat, subcat_data in cat_data["subcategories"].items():
                markdown += f"### {subcat}\n\n"
                markdown += f"{subcat_data['description']}\n"
                markdown += f"Total Entries: {subcat_data['total_entries']:,}\n\n"
                
                for entry in subcat_data["entries"]:
                    markdown += self._format_entry_markdown(entry)

        return markdown

    def _format_entry_markdown(self, entry: Dict[str, Any]) -> str:
        """Format a single entry for markdown."""
        markdown = f"#### {entry['name']}\n"
        if entry['entries']:
            markdown += f"- Entries: {entry['entries']:,}\n"
        markdown += f"- Format: {', '.join(entry['format']) if isinstance(entry['format'], list) else entry['format']}\n"
        
        if isinstance(entry['url'], list):
            markdown += "- URLs:\n"
            for url in entry['url']:
                if url:  # Only add non-empty URLs
                    markdown += f"  * {url}\n"
        elif entry['url']:  # Only add if URL is non-empty
            markdown += f"- URL: {entry['url']}\n"
        
        if entry['pack']:
            markdown += f"- Pack: {', '.join(entry['pack'])}\n"
        if entry['level']:
            markdown += f"- Level: {', '.join(map(str, entry['level']))}\n"
        markdown += "\n"
        return markdown

async def main():
    """Main function to fetch and process RethinkDNS blocklists."""
    processor = BlocklistProcessor()
    
    try:
        print("Fetching and processing RethinkDNS blocklists...")
        
        # Fetch both configuration and entry counts concurrently
        config, entry_counts = await asyncio.gather(
            processor.fetch_config(),
            processor.fetch_entry_counts()
        )
        
        processor.organize_data(config, entry_counts)

        # Save JSON output
        with open('blocklists_rethinkdns.json', 'w', encoding='utf-8') as f:
            json.dump(processor.output_data, f, indent=2, ensure_ascii=False)
        print("Successfully saved JSON data to blocklists_rethinkdns.json")

        # Save markdown documentation
        markdown_content = processor.generate_markdown()
        with open('blocklists_rethinkdns.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print("Successfully saved markdown documentation to blocklists_rethinkdns.md")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())