import asyncio
from playwright.async_api import async_playwright
import json
import re

async def main():
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
        # Wait for specific elements to appear
        await page.wait_for_selector('.bl-item', timeout=30000)
        await page.wait_for_selector('.bl-item__url', timeout=30000)
        
        # Scroll through the page to ensure all content is loaded
        for _ in range(3):
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
        
        # Get all blocklist items
        print("Collecting blocklist data...")
        blocklist_data = await page.evaluate('''
        () => {
            const results = [];
            const items = document.querySelectorAll('.bl-item');
            
            items.forEach(item => {
                // Get the parent section to determine category
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
                        entries: entriesMatch ? entriesMatch[1] : ''
                    });
                }
            });
            return results;
        }
        ''')
        
        print(f"Found {len(blocklist_data)} blocklist items")
        
        # Print first few items for debugging
        for i, item in enumerate(blocklist_data[:3]):
            print(f"\nItem {i}:")
            print(f"Name: {item['name']}")
            print(f"URL: {item['url']}")
            print(f"Category: {item['category']}")
            print(f"Entries: {item['entries']}")

        # Organize by category
        categories = {}
        for item in blocklist_data:
            category = item['category'] or 'Uncategorized'
            if category not in categories:
                categories[category] = []
            
            name = item['name']
            sub_category = ''
            
            # Extract subcategory if present in name
            name_match = re.match(r'^(.*?)\s*\((.*?)\)\s*$', name)
            if name_match:
                name = name_match.group(1).strip()
                sub_category = name_match.group(2).strip()
            
            list_info = {
                'name': name,
                'sub_category': sub_category,
                'url': item['url'],
                'entries': item['entries']
            }
            categories[category].append(list_info)
            print(f"Added {name} to {category}")

        # Generate markdown content
        markdown_content = "# RethinkDNS Blocklists\n\n"
        markdown_content += "This document contains a comprehensive list of blocklists available through RethinkDNS, organized by category.\n\n"
        
        for category, lists in categories.items():
            markdown_content += f"## {category}\n\n"
            for blocklist in lists:
                name = blocklist['name']
                sub_cat = f" ({blocklist['sub_category']})" if blocklist['sub_category'] else ""
                entries = f"{blocklist['entries']} total entries" if blocklist['entries'] else ""
                
                markdown_content += f"### {name}{sub_cat}\n"
                if entries:
                    markdown_content += f"- Entries: {entries}\n"
                markdown_content += f"- URL: {blocklist['url']}\n\n"

        # Save to markdown file
        with open('blocklists_rethinkdns.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print("Successfully saved blocklists to blocklists_rethinkdns.md")

        # Save to JSON file
        with open('blocklists_rethinkdns.json', 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)
        print("Successfully saved blocklists to blocklists_rethinkdns.json")
        
        await page.screenshot(path='debug_screenshot_rethinkdns.png')
        print("Saved debug screenshot to debug_screenshot_rethinkdns.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())