#!/usr/bin/env python3
"""
Fetch and process The Firebog's blocklists.

This script fetches various blocklists from The Firebog (https://v.firebog.net/),
processes them, and saves the results in both markdown and JSON formats.

The script scrapes the website to get:
1. Categories of blocklists
2. Names and URLs of blocklists in each category
3. Additional metadata where available

Output files:
- blocklists_firebog.md: Human-readable markdown format
- blocklists_firebog.json: Machine-readable JSON format with standardized keys
- debug_screenshots/: Directory containing debug information
"""

import asyncio
from playwright.async_api import async_playwright
import json
import re
from pathlib import Path
import datetime
import sys
from typing import Dict, Any, List
import os

def log_message(message: str) -> None:
    """Print a message to stderr for immediate output."""
    print(message, file=sys.stderr)

async def save_debug_info(page, name: str) -> None:
    """
    Save debug information including page screenshot and HTML content.
    
    Args:
        page: Playwright page object
        name: Name of the section being debugged
    """
    debug_dir = Path("debug_screenshots")
    debug_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    log_message(f"Saving debug info for {name}...")
    
    # Save screenshot
    screenshot_file = debug_dir / f"firebog_{name.lower().replace(' ', '_')}_{timestamp}.png"
    await page.screenshot(path=str(screenshot_file))
    log_message(f"  - Screenshot saved to {screenshot_file}")
    
    # Save HTML content
    html_file = debug_dir / f"firebog_{name.lower().replace(' ', '_')}_{timestamp}.html"
    content = await page.content()
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(content)
    log_message(f"  - HTML content saved to {html_file}")

async def scrape_blocklists(page) -> Dict[str, List[Dict[str, str]]]:
    """
    Scrape blocklist data from the page, only keeping v.firebog.net hosted lists.
    
    Args:
        page: Playwright page object
        
    Returns:
        Dictionary mapping categories to lists of blocklist information
    """
    log_message("Scraping blocklist data...")
    raw_data = await page.evaluate('''
    () => {
        const results = {};
        const sections = document.querySelectorAll('h2');
        
        sections.forEach(section => {
            const sectionName = section.textContent.trim();
            if (sectionName.includes('Lists')) {
                const category = sectionName.replace(' Lists', '');
                results[category] = [];
                
                let ul = section.nextElementSibling;
                while (ul && ul.tagName !== 'UL') {
                    ul = ul.nextElementSibling;
                }
                
                if (ul) {
                    const links = ul.querySelectorAll('a');
                    links.forEach(link => {
                        const url = link.href;
                        // Only include URLs from v.firebog.net
                        if (url && url.includes('v.firebog.net')) {
                            // Extract a clean name from the URL
                            let name = url.split("/").pop();  // Get the last part of the URL
                            if (name.endsWith(".txt")) {
                                name = name.slice(0, -4);  // Remove .txt extension
                            }
                            name = name.replace(/([A-Z])/g, ' $1').trim();  // Add spaces before capitals
                            name = name.charAt(0).toUpperCase() + name.slice(1);  // Capitalize first letter
                            
                            results[category].push({
                                name: name,
                                url: url
                            });
                        }
                    });
                }
            }
        });
        return results;
    }
    ''')
    
    total_lists = sum(len(items) for items in raw_data.values())
    log_message(f"Found {len(raw_data)} categories with {total_lists} total v.firebog.net blocklists")
    for category, items in raw_data.items():
        log_message(f"  - {category}: {len(items)} blocklists")
    
    return raw_data

async def main():
    """Main function to fetch and process The Firebog's blocklists."""
    log_message("\n=== Starting Firebog Blocklist Fetcher (v.firebog.net only) ===\n")
    log_message("Initializing browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-web-security', '--no-sandbox']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        log_message("\nNavigating to Firebog page...")
        await page.goto('https://v.firebog.net/')
        
        log_message("Waiting for content to load...")
        await page.wait_for_selector('h2', timeout=30000)
        log_message("Page loaded successfully")
        
        # Save initial debug info
        await save_debug_info(page, "main_page")
        
        # Get all sections and their blocklists
        raw_data = await scrape_blocklists(page)
        
        log_message("\nProcessing blocklist data...")
        # Convert to standardized format
        blocklist_data = {
            "categories": {
                category: {
                    "description": f"Curated blocklists from The Firebog's {category} category (v.firebog.net)",
                    "blocklists": [
                        {
                            "name": item["name"],
                            "url": item["url"],
                            "entries": 0,
                            "source": "The Firebog (v.firebog.net)"
                        }
                        for item in items
                    ]
                }
                for category, items in raw_data.items()
                if items  # Only include categories that have blocklists
            }
        }
        
        # Generate markdown content
        log_message("\nGenerating markdown content...")
        markdown_content = "# The Firebog Blocklists (v.firebog.net)\n\n"
        markdown_content += "This document contains curated blocklists hosted at v.firebog.net, organized by category.\n\n"
        
        for category, data in blocklist_data["categories"].items():
            log_message(f"  - Processing {category} category")
            markdown_content += f"## {category}\n\n"
            markdown_content += f"{data['description']}\n\n"
            for blocklist in data["blocklists"]:
                markdown_content += f"### {blocklist['name']}\n"
                markdown_content += f"- Source: {blocklist['source']}\n"
                markdown_content += f"- URL: {blocklist['url']}\n"
                if blocklist["entries"] > 0:
                    markdown_content += f"- Entries: {blocklist['entries']}\n"
                markdown_content += "\n"

        # Save to markdown file
        log_message("\nSaving output files...")
        with open('blocklists_firebog.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        log_message("  ✓ Saved markdown to blocklists_firebog.md")

        # Save to JSON file
        with open('blocklists_firebog.json', 'w', encoding='utf-8') as f:
            json.dump(blocklist_data, f, indent=2, ensure_ascii=False)
        log_message("  ✓ Saved JSON to blocklists_firebog.json")
        
        await browser.close()
        log_message("\n=== Firebog Blocklist Fetcher Completed (v.firebog.net only) ===\n")

if __name__ == "__main__":
    asyncio.run(main()) 