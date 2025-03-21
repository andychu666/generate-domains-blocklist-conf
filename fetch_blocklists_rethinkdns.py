#!/usr/bin/env python3
"""
Fetch and process RethinkDNS blocklists.

This script fetches various blocklists from RethinkDNS (https://rethinkdns.com/configure),
processes them, and saves the results in both markdown and JSON formats.

The script scrapes the website to get:
1. Categories of blocklists (Privacy, Security, ParentalControl)
2. Names and URLs of blocklists in each category
3. Entry counts and subcategories where available

Output files:
- blocklists_rethinkdns.md: Human-readable markdown format
- blocklists_rethinkdns.json: Machine-readable JSON format with standardized keys
- debug_screenshots/: Directory containing debug information
"""

import asyncio
from playwright.async_api import async_playwright
import json
import re
from pathlib import Path
import datetime

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
    
    # Save screenshot
    screenshot_file = debug_dir / f"rethinkdns_{name.lower().replace(' ', '_')}_{timestamp}.png"
    await page.screenshot(path=str(screenshot_file))
    
    # Save HTML content
    html_file = debug_dir / f"rethinkdns_{name.lower().replace(' ', '_')}_{timestamp}.html"
    content = await page.content()
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(content)

async def main():
    """Main function to fetch and process RethinkDNS blocklists."""
    print("Starting to fetch RethinkDNS blocklists...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-web-security', '--no-sandbox']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        print("Navigating to RethinkDNS configure page...")
        await page.goto('https://rethinkdns.com/configure')
        
        print("Waiting for content to load...")
        await page.wait_for_selector('.bl-item', timeout=30000)
        await page.wait_for_selector('.bl-item__url', timeout=30000)
        
        # Save initial debug info
        await save_debug_info(page, "main_page")
        
        # Scroll through the page to ensure all content is loaded
        for _ in range(3):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
        
        # Get all blocklist items
        print("Collecting blocklist data...")
        raw_data = await page.evaluate('''
        () => {
            const results = [];
            const items = document.querySelectorAll('.bl-item');
            
            items.forEach(item => {
                let category = '';
                let parent = item;
                while (parent && !category) {
                    if (parent.textContent.includes('Privacy')) {
                        category = 'Privacy';
                    } else if (parent.textContent.includes('Security')) {
                        category = 'Security';
                    } else if (parent.textContent.includes('ParentalControl')) {
                        category = 'ParentalControl';
                    }
                    parent = parent.parentElement;
                }
                
                const nameElem = item.querySelector('.bl-item__name');
                const urlElem = item.querySelector('.bl-item__url');
                const entriesText = item.textContent;
                const entriesMatch = entriesText.match(/(\\d+)\\s*total entries/);
                
                if (nameElem && urlElem) {
                    results.push({
                        name: nameElem.textContent.trim(),
                        url: urlElem.href,
                        category: category,
                        entries: entriesMatch ? parseInt(entriesMatch[1]) : 0
                    });
                }
            });
            return results;
        }
        ''')
        
        print(f"Found {len(raw_data)} blocklist items")
        
        # Convert to standardized format
        blocklist_data = {"categories": {}}
        
        for item in raw_data:
            category = item['category'] or 'Uncategorized'
            if category not in blocklist_data["categories"]:
                blocklist_data["categories"][category] = {
                    "description": f"Blocklists from RethinkDNS's {category} category",
                    "blocklists": []
                }
            
            name = item['name']
            sub_category = ''
            
            # Extract subcategory if present in name
            name_match = re.match(r'^(.*?)\s*\((.*?)\)\s*$', name)
            if name_match:
                name = name_match.group(1).strip()
                sub_category = name_match.group(2).strip()
            
            blocklist_info = {
                "name": name,
                "url": item['url'],
                "entries": item['entries'],
                "source": "RethinkDNS",
                "sub_category": sub_category
            }
            blocklist_data["categories"][category]["blocklists"].append(blocklist_info)

        # Generate markdown content
        print("Saving blocklists to markdown...")
        markdown_content = "# RethinkDNS Blocklists\n\n"
        markdown_content += "This document contains a comprehensive list of blocklists available through RethinkDNS (https://rethinkdns.com/configure), organized by category.\n\n"
        
        for category, data in blocklist_data["categories"].items():
            markdown_content += f"## {category}\n\n"
            markdown_content += f"{data['description']}\n\n"
            for blocklist in data["blocklists"]:
                name = blocklist['name']
                sub_cat = f" ({blocklist['sub_category']})" if blocklist['sub_category'] else ""
                
                markdown_content += f"### {name}{sub_cat}\n"
                markdown_content += f"- Source: {blocklist['source']}\n"
                markdown_content += f"- URL: {blocklist['url']}\n"
                if blocklist["entries"] > 0:
                    markdown_content += f"- Entries: {blocklist['entries']}\n"
                markdown_content += "\n"

        # Save to markdown file
        with open('blocklists_rethinkdns.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print("Successfully saved blocklists to blocklists_rethinkdns.md")

        # Save to JSON file
        with open('blocklists_rethinkdns.json', 'w', encoding='utf-8') as f:
            json.dump(blocklist_data, f, indent=2, ensure_ascii=False)
        print("Successfully saved blocklists to blocklists_rethinkdns.json")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())