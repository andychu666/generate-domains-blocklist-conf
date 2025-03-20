import asyncio
from playwright.async_api import async_playwright
import json
import re

async def main():
    print("Starting to fetch Firebog blocklists...")
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
        
        print("Navigating to Firebog page...")
        await page.goto('https://v.firebog.net/')
        
        print("Waiting for content to load...")
        await page.wait_for_selector('h2', timeout=30000)  # Wait for section headers
        
        # Get all sections and their blocklists
        print("Collecting blocklist data...")
        blocklist_data = await page.evaluate('''
        () => {
            const results = {};
            const sections = document.querySelectorAll('h2');
            
            sections.forEach(section => {
                const sectionName = section.textContent.trim();
                if (sectionName.includes('Lists')) {
                    const category = sectionName.replace(' Lists', '');
                    results[category] = [];
                    
                    // Find the next ul element after this section header
                    let ul = section.nextElementSibling;
                    while (ul && ul.tagName !== 'UL') {
                        ul = ul.nextElementSibling;
                    }
                    
                    if (ul) {
                        const links = ul.querySelectorAll('a');
                        links.forEach(link => {
                            const name = link.textContent.trim();
                            const url = link.href;
                            // Only include raw URLs that can be used as blocklists
                            if (url && !url.includes('javascript:') && 
                                (url.includes('raw.githubusercontent.com') || 
                                 url.includes('v.firebog.net') ||
                                 url.includes('hosts.txt') ||
                                 url.includes('list.txt') ||
                                 url.includes('blocklist.txt') ||
                                 url.endsWith('.txt'))) {
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
        
        print(f"Found blocklists in {len(blocklist_data)} categories")
        
        # Generate markdown content
        markdown_content = "# Firebog Blocklists\n\n"
        markdown_content += "This document contains a comprehensive list of blocklists available through Firebog (https://v.firebog.net/), organized by category.\n\n"
        
        for category, lists in blocklist_data.items():
            markdown_content += f"## {category}\n\n"
            for blocklist in lists:
                markdown_content += f"### {blocklist['name']}\n"
                markdown_content += f"- URL: {blocklist['url']}\n\n"

        # Save to markdown file
        with open('blocklists_firebog.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print("Successfully saved blocklists to blocklists_firebog.md")

        # Save to JSON file
        with open('blocklists_firebog.json', 'w', encoding='utf-8') as f:
            json.dump(blocklist_data, f, indent=2, ensure_ascii=False)
        print("Successfully saved blocklists to blocklists_firebog.json")
        
        await page.screenshot(path='debug_screenshot_firebog.png')
        print("Saved debug screenshot to debug_screenshot_firebog.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main()) 