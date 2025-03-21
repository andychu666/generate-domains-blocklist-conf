import asyncio
from playwright.async_api import async_playwright
import json
import re

CATEGORIES = [
    'Ads',              # Advertisements, Banners, Widgets & Push Notifications
    'Adult',            # Porn / 18+ Content
    'Apple',            # Bloat
    'Bloat',            # Domains not required for software to function
    'Chat',             # Chat Dialog Popups
    'Cryptocurrency',   # Bitcoin, Ethereum, Mining, etc. (Not Malware)
    'Dating',           # Dating Sites
    'DNS',              # DNS Resolvers
    'Dynamic',          # Dynamic DNS
    'Fonts',            # Fonts
    'Free',             # Free/Cheap Hosting, Free Blogs
    'Gambling',         # Casino, Gambling, Poker sites
    'Junk',             # Personally untrusted software, browser extensions, search engines, etc
    'Malware',          # Malicious Sites, PUPs, Malware, Browser Hijackers, Phishing Sites
    'Marketing',        # Marketing, Ebay Listing Tools, etc
    'Marketing-Email',  # Email Based Marketing
    'Microsoft',        # Apps, Bing, Bloat, Tiles, etc
    'Remote',           # Domains used for remote sessions
    'Risk',             # Bad ISP/Bots/Spam, Keyloggers, Sites used by compromised devices
    'Scam',             # Fake freight, gift cards, products, support, pets, firearms, news, etc
    'Shock',            # Gore, Gross, and Torture sites
    'Top_Level',        # Top Level Domains. Sorted by continent, then by country
    'Tracking',         # Analytics, Diagnostics, Location, Metrics, Public IP
    'Tunnels',          # VPNs & Proxies
    'Typo',             # Misspelling of websites / Typosquatting
    'URL Shortener'     # URL Shorteners. Can be used to mask malicious domains
]

async def main():
    print("Starting to fetch ShadowWhisperer's BlockLists...")
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
        
        blocklist_data = []
        
        # Process each category
        for category in CATEGORIES:
            print(f"Fetching {category} blocklist...")
            url = f'https://raw.githubusercontent.com/ShadowWhisperer/BlockLists/master/Lists/{category}'
            
            try:
                await page.goto(url)
                content = await page.content()
                
                # Extract domains from the raw content
                domains = []
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('//'):
                        domains.append(line)
                
                if domains:
                    blocklist_data.append({
                        'name': category,
                        'url': url,
                        'entries': str(len(domains))
                    })
                    print(f"Found {len(domains)} domains in {category}")
            except Exception as e:
                print(f"Error fetching {category}: {str(e)}")
        
        print(f"\nFound {len(blocklist_data)} blocklist categories")
        
        # Organize blocklists
        categories = {"ShadowWhisperer": []}
        for item in blocklist_data:
            list_info = {
                'name': item['name'],
                'url': item['url'],
                'entries': item['entries']
            }
            categories["ShadowWhisperer"].append(list_info)
            print(f"Added {item['name']}")

        # Generate markdown content
        markdown_content = "# ShadowWhisperer BlockLists\n\n"
        markdown_content += "This document contains blocklists from ShadowWhisperer's repository.\n\n"
        
        for blocklist in categories["ShadowWhisperer"]:
            name = blocklist['name']
            entries = f"{blocklist['entries']} total entries" if blocklist['entries'] else ""
            
            markdown_content += f"## {name}\n"
            if entries:
                markdown_content += f"- Entries: {entries}\n"
            markdown_content += f"- URL: {blocklist['url']}\n\n"

        # Save to markdown file
        with open('blocklists_shadowwhisperer.md', 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print("Successfully saved blocklists to blocklists_shadowwhisperer.md")

        # Save to JSON file
        with open('blocklists_shadowwhisperer.json', 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)
        print("Successfully saved blocklists to blocklists_shadowwhisperer.json")
        
        await page.screenshot(path='debug_screenshot_shadowwhisperer.png')
        print("Saved debug screenshot to debug_screenshot_shadowwhisperer.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main()) 