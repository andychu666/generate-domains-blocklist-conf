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

def generate_conf_file(urls, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write('##################################################################################\n')
        f.write('#                                                                                #\n')
        f.write('#   RethinkDNS Blocklists Configuration                                         #\n')
        f.write('#   Generated from RethinkDNS blocklists data                                   #\n')
        f.write('#                                                                                #\n')
        f.write('#   URLs are organized by category and commented if duplicate                    #\n')
        f.write('#   Format: Category - Name (Entries count)                                     #\n')
        f.write('#                                                                                #\n')
        f.write('##################################################################################\n\n')
        
        # Track categories for section headers
        current_category = None
        
        # Sort URLs by category
        sorted_urls = sorted(urls.items(), key=lambda x: (x[1][0][0], x[1][0][1]))  # Sort by category, then name
        
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
    # Read the markdown file
    try:
        with open('blocklists_rethinkdns.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print("Error: blocklists_rethinkdns.md not found")
        return

    urls = parse_markdown_file('blocklists_rethinkdns.md')
    generate_conf_file(urls, 'domains-blocklists.conf')
    print("Successfully converted markdown to conf format!")

if __name__ == "__main__":
    main() 