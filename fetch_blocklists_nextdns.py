#!/usr/bin/env python3
"""
Fetch NextDNS recommended blocklists.

This script fetches the recommended blocklists from NextDNS's GitHub repository
and saves them in a structured format for use with DNSCrypt-Proxy.

Output files:
- blocklists_nextdns.json: Structured blocklist data
- blocklists_nextdns.md: Documentation of the blocklists
- debug_screenshots/: Debug information and screenshots
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
import asyncio
from playwright.async_api import async_playwright

def log_message(message: str) -> None:
    """Print a message to stderr for immediate output."""
    print(message, file=sys.stderr)

async def fetch_nextdns_data() -> Dict[str, Any]:
    """
    Fetch NextDNS recommended blocklists data.
    
    Returns:
        Dictionary containing the structured blocklist data
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Create debug_screenshots directory if it doesn't exist
        Path("debug_screenshots").mkdir(exist_ok=True)
        
        try:
            # Fetch the raw JSON file
            url = "https://raw.githubusercontent.com/nextdns/blocklists/main/blocklists/nextdns-recommended.json"
            await page.goto(url)
            content = await page.content()
            
            # Save debug screenshot
            await page.screenshot(path="debug_screenshots/nextdns_recommended.png")
            
            # Extract the JSON content
            json_text = await page.evaluate("document.querySelector('pre').textContent")
            data = json.loads(json_text)
            
            # Process the data into our standard format
            result = {
                "categories": {
                    "NextDNS Recommended": {
                        "description": "Recommended blocklists from NextDNS",
                        "blocklists": []
                    }
                }
            }
            
            # Process sources
            for source in data.get("sources", []):
                url = source.get("url")
                if not url:
                    continue
                    
                # Extract name from URL
                name = url.split("/")[-1]
                if name.endswith(".txt"):
                    name = name[:-4]
                name = name.replace("-", " ").replace("_", " ").title()
                
                result["categories"]["NextDNS Recommended"]["blocklists"].append({
                    "name": name,
                    "url": url,
                    "format": source.get("format", "unknown"),
                    "source": "NextDNS Recommended"
                })
            
            return result
            
        except Exception as e:
            log_message(f"Error fetching NextDNS data: {str(e)}")
            return {"categories": {}}
        finally:
            await browser.close()

def save_markdown(data: Dict[str, Any]) -> None:
    """
    Save blocklist data as markdown documentation.
    
    Args:
        data: Dictionary containing the blocklist data
    """
    try:
        with open("blocklists_nextdns.md", "w", encoding="utf-8") as f:
            f.write("# NextDNS Recommended Blocklists\n\n")
            
            for category, category_data in data["categories"].items():
                f.write(f"## {category}\n")
                if "description" in category_data:
                    f.write(f"{category_data['description']}\n\n")
                
                for blocklist in category_data.get("blocklists", []):
                    f.write(f"### {blocklist['name']}\n")
                    f.write(f"- URL: {blocklist['url']}\n")
                    f.write(f"- Format: {blocklist.get('format', 'unknown')}\n")
                    f.write("\n")
                    
        log_message("Generated blocklists_nextdns.md")
        
    except Exception as e:
        log_message(f"Error saving markdown: {str(e)}")

async def main():
    """Main function to fetch and save NextDNS blocklist data."""
    log_message("Fetching NextDNS recommended blocklists...")
    
    # Fetch the data
    data = await fetch_nextdns_data()
    
    # Save as JSON
    try:
        with open("blocklists_nextdns.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        log_message("Generated blocklists_nextdns.json")
    except Exception as e:
        log_message(f"Error saving JSON: {str(e)}")
    
    # Save as markdown
    save_markdown(data)
    
    log_message("NextDNS blocklist fetching completed")

if __name__ == "__main__":
    asyncio.run(main()) 