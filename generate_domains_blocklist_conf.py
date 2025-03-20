import re
from collections import defaultdict

def parse_markdown_file(md_file):
    urls = defaultdict(list)  # URL -> [(category, name, entries)]
    current_category = ""
    current_name = ""
    current_entries = ""
    
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if line.startswith('## '):
            current_category = line[3:].strip()
        elif line.startswith('### '):
            current_name = line[4:].strip()
        elif line.startswith('- Entries:'):
            current_entries = line.split('Entries:')[1].strip()
        elif line.startswith('- URL:'):
            url = line[7:].strip()
            urls[url].append((current_category, current_name, current_entries))
    
    return urls

def generate_conf_file(urls_rethink, urls_shadow, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write('##################################################################################\n')
        f.write('#                                                                                #\n')
        f.write('#   Combined Blocklists Configuration                                            #\n')
        f.write('#   Generated from RethinkDNS and ShadowWhisperer blocklists                    #\n')
        f.write('#                                                                                #\n')
        f.write('#   URLs are organized by category and commented if duplicate                    #\n')
        f.write('#   Format: Category - Name (Entries count)                                     #\n')
        f.write('#                                                                                #\n')
        f.write('##################################################################################\n\n')
        
        # Combine all URLs
        all_urls = defaultdict(list)
        for url, entries in urls_rethink.items():
            for entry in entries:
                all_urls[url].append(('RethinkDNS: ' + entry[0], entry[1], entry[2]))
        
        for url, entries in urls_shadow.items():
            for entry in entries:
                all_urls[url].append(('ShadowWhisperer: ' + entry[0], entry[1], entry[2]))
        
        # Track categories for section headers
        current_category = None
        
        # Sort URLs by category
        sorted_urls = sorted(all_urls.items(), key=lambda x: (x[1][0][0], x[1][0][1]))  # Sort by category, then name
        
        for url, entries in sorted_urls:
            category, name, entry_count = entries[0]  # Take first occurrence for category header
            
            # Write category header if changed
            if category != current_category:
                f.write(f'\n# {category}\n')
                current_category = category
            
            # If URL has multiple entries, it's a duplicate - comment it out and add all categories
            if len(entries) > 1:
                categories_str = ', '.join(f'{e[0]}: {e[1]}' for e in entries)
                f.write(f'# DUPLICATE in: {categories_str}\n')
                f.write(f'# {url}\n\n')
            else:
                f.write(f'# {name} ({entry_count})\n')
                f.write(f'{url}\n\n')

def main():
    # Read both markdown files
    try:
        urls_rethink = parse_markdown_file('blocklists_rethinkdns.md')
        print("Successfully parsed RethinkDNS blocklists")
    except FileNotFoundError:
        print("Warning: blocklists_rethinkdns.md not found")
        urls_rethink = {}

    try:
        urls_shadow = parse_markdown_file('blocklists_shadowwhisperer.md')
        print("Successfully parsed ShadowWhisperer blocklists")
    except FileNotFoundError:
        print("Warning: blocklists_shadowwhisperer.md not found")
        urls_shadow = {}

    if not urls_rethink and not urls_shadow:
        print("Error: No blocklist files found")
        return

    generate_conf_file(urls_rethink, urls_shadow, 'domains-blocklists.conf')
    print("Successfully generated combined conf file!")

if __name__ == "__main__":
    main() 