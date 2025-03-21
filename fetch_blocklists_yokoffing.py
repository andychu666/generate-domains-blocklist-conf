#!/usr/bin/env python3
"""
Fetch and process blocklists from yokoffing's repository.

This script scrapes blocklists from https://github.com/yokoffing/filterlists/tree/main
and processes them into a standardized format. It fetches the following lists:
- adult_annoyance_list.txt
- annoyance_list.txt
- antipaywall_filters_without_element_hiding.txt
- block_third_party_fonts.txt
- clean_reading_experience.txt
- click2load.txt
- combined_annoyances_without_element_hiding
- enhanced_site_protection.txt
- personal.txt
- privacy_essentials.txt
- youtube_clear_view.txt

Output files:
- blocklists_yokoffing.json: Structured data about the blocklists
- blocklists_yokoffing.md: Markdown documentation of the blocklists
Debug files:
- debug_screenshots/yokoffing_*.png: Screenshots of the scraping process
- debug_screenshots/yokoffing_*.html: HTML content for debugging
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any
import sys
from datetime import datetime
from playwright.async_api import async_playwright

def log_message(message: str) -> None:
    """Print a message to stderr for immediate output."""
    print(message, file=sys.stderr)

async def save_debug_info(page, prefix: str, debug_dir: Path) -> None:
    """
    Save debug information including screenshots and HTML content.
    
    Args:
        page: Playwright page object
        prefix: Prefix for the debug files
        debug_dir: Directory to save debug files
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create debug directory if it doesn't exist
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    # Save screenshot
    screenshot_path = debug_dir / f"{prefix}_{timestamp}.png"
    await page.screenshot(path=str(screenshot_path), full_page=True)
    
    # Save HTML content
    html_path = debug_dir / f"{prefix}_{timestamp}.html"
    html_content = await page.content()
    html_path.write_text(html_content, encoding='utf-8')
    
    log_message(f"Saved debug info: {screenshot_path} and {html_path}")

async def fetch_blocklist_entries(page, url: str) -> int:
    """
    Fetch the number of entries in a blocklist by counting non-empty lines.
    
    Args:
        page: Playwright page object
        url: URL of the raw blocklist content
        
    Returns:
        Number of entries in the blocklist
    """
    try:
        await page.goto(url)
        content = await page.content()
        
        # Extract the raw content from the page
        raw_content = await page.evaluate("document.querySelector('pre').textContent")
        
        # Count non-empty, non-comment lines
        entries = sum(1 for line in raw_content.splitlines() 
                     if line.strip() and not line.strip().startswith('!') 
                     and not line.strip().startswith('#'))
        
        return entries
    except Exception as e:
        log_message(f"Error fetching entries from {url}: {str(e)}")
        return 0

async def main() -> None:
    """Main function to fetch and process yokoffing's blocklists."""
    log_message("Starting yokoffing Blocklist Fetcher...")
    
    # Define the blocklists to fetch
    blocklists = [
        "adult_annoyance_list.txt",
        "annoyance_list.txt",
        "antipaywall_filters_without_element_hiding.txt",
        "block_third_party_fonts.txt",
        "clean_reading_experience.txt",
        "click2load.txt",
        "combined_annoyances_without_element_hiding",
        "enhanced_site_protection.txt",
        "personal.txt",
        "privacy_essentials.txt",
        "youtube_clear_view.txt"
    ]
    
    base_url = "https://github.com/yokoffing/filterlists"
    raw_base_url = "https://raw.githubusercontent.com/yokoffing/filterlists/main"
    
    # Initialize results dictionary
    results = {
        "categories": {
            "Annoyances": {
                "description": "Blocklists for various web annoyances from yokoffing's collection",
                "blocklists": []
            },
            "Privacy": {
                "description": "Privacy-focused blocklists from yokoffing's collection",
                "blocklists": []
            }
        }
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        debug_dir = Path("debug_screenshots")
        
        # Save initial debug info
        await save_debug_info(page, "yokoffing_main", debug_dir)
        
        for blocklist in blocklists:
            try:
                raw_url = f"{raw_base_url}/{blocklist}"
                entries = await fetch_blocklist_entries(page, raw_url)
                
                # Determine category based on blocklist name
                category = "Privacy" if any(x in blocklist for x in ["privacy", "protection", "personal"]) else "Annoyances"
                
                # Create a clean name from the filename
                name = blocklist.replace("_", " ").replace(".txt", "").title()
                
                # Add blocklist information
                results["categories"][category]["blocklists"].append({
                    "name": name,
                    "url": raw_url,
                    "entries": entries,
                    "source": "yokoffing"
                })
                
                log_message(f"Processed {name} with {entries} entries")
                
            except Exception as e:
                log_message(f"Error processing {blocklist}: {str(e)}")
                continue
        
        await browser.close()
    
    # Save results as JSON
    output_file = Path("blocklists_yokoffing.json")
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    log_message(f"Saved results to {output_file}")
    
    # Generate markdown documentation
    markdown = ["# yokoffing Blocklists\n"]
    markdown.append("Collection of curated blocklists from yokoffing's repository.\n")
    
    for category, data in results["categories"].items():
        markdown.append(f"## {category}\n")
        markdown.append(f"{data['description']}\n")
        
        for blocklist in data["blocklists"]:
            markdown.append(f"### {blocklist['name']}")
            markdown.append(f"- Source: yokoffing")
            markdown.append(f"- Entries: {blocklist['entries']}")
            markdown.append(f"- URL: {blocklist['url']}\n")
    
    markdown_file = Path("blocklists_yokoffing.md")
    markdown_file.write_text("\n".join(markdown), encoding='utf-8')
    log_message(f"Generated documentation in {markdown_file}")

if __name__ == "__main__":
    asyncio.run(main()) 