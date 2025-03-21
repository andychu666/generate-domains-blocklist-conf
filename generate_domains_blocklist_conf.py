#!/usr/bin/env python3
"""
Generate DNSCrypt-Proxy domains blocklist configuration.

This script combines multiple blocklist sources into a single DNSCrypt-Proxy compatible
configuration file. It processes blocklists from:
1. RethinkDNS
2. ShadowWhisperer
3. The Firebog
4. Geoffrey Frogeye

Each source's JSON file should follow a standardized format with these keys:
- name: Name of the blocklist
- url: URL to fetch the blocklist
- entries: Number of entries in the blocklist

Output:
- domains-blocklist.conf: DNSCrypt-Proxy compatible configuration file
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import sys

def log_message(message: str) -> None:
    """Print a message to stderr for immediate output."""
    print(message, file=sys.stderr)

def load_json_file(filename: str) -> Dict[str, Any]:
    """
    Load and return JSON data from a file.
    
    Args:
        filename: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        log_message(f"Error: File {filename} not found")
        return {"categories": {}}
    except json.JSONDecodeError as e:
        log_message(f"Error: Invalid JSON in {filename}: {e}")
        return {"categories": {}}

def process_rethinkdns_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process RethinkDNS JSON format into standard format.
    
    Args:
        data: Raw JSON data from RethinkDNS
        
    Returns:
        Dictionary with standardized format containing:
        - categories: Dict of category names to their blocklists
        - Each blocklist has: name, url, entries
    """
    try:
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        if "categories" not in data:
            raise ValueError("Missing 'categories' key")
            
        categories = data["categories"]
        if not isinstance(categories, dict):
            raise ValueError("'categories' must be a dictionary")
            
        result = {"categories": {}}
        
        for category, category_data in categories.items():
            if not isinstance(category_data, dict):
                log_message(f"Warning: Invalid category data for {category}, skipping")
                continue
                
            blocklists = category_data.get("blocklists", [])
            if not isinstance(blocklists, list):
                log_message(f"Warning: Invalid blocklists data for {category}, skipping")
                continue
                
            processed_blocklists = []
            for item in blocklists:
                if not isinstance(item, dict):
                    continue
                    
                try:
                    processed_blocklists.append({
                        "name": str(item["name"]),
                        "url": str(item["url"]),
                        "entries": int(item.get("entries", 0)),
                        "source": "RethinkDNS",
                        "sub_category": str(item.get("sub_category", ""))
                    })
                except (KeyError, ValueError) as e:
                    log_message(f"Warning: Invalid blocklist entry in {category}: {e}")
                    continue
            
            if processed_blocklists:
                result["categories"][category] = {
                    "description": str(category_data.get("description", f"Blocklists from RethinkDNS's {category} category")),
                    "blocklists": processed_blocklists
                }
        
        return result
        
    except Exception as e:
        log_message(f"Error processing RethinkDNS data: {str(e)}")
        return {"categories": {}}

def process_shadowwhisperer_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process ShadowWhisperer JSON format into standard format.
    
    Args:
        data: Raw JSON data from ShadowWhisperer
        
    Returns:
        Dictionary with standardized format containing:
        - categories: Dict of category names to their blocklists
        - Each blocklist has: name, url, entries
    """
    try:
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
            
        result = {"categories": {}}
        
        # Get the blocklists array
        blocklists = data.get("ShadowWhisperer", [])
        if not isinstance(blocklists, list):
            raise ValueError("ShadowWhisperer data must contain a list of blocklists")
        
        # Create a single category containing all blocklists
        processed_blocklists = []
        for item in blocklists:
            if not isinstance(item, dict):
                continue
                
            try:
                processed_blocklists.append({
                    "name": str(item["name"]),
                    "url": str(item["url"]),
                    "entries": int(item.get("entries", 0)),
                    "source": "ShadowWhisperer"
                })
            except (KeyError, ValueError) as e:
                log_message(f"Warning: Invalid blocklist entry: {e}")
                continue
        
        if processed_blocklists:
            result["categories"]["ShadowWhisperer"] = {
                "description": "Comprehensive collection of categorized blocklists",
                "blocklists": processed_blocklists
            }
        
        return result
        
    except Exception as e:
        log_message(f"Error processing ShadowWhisperer data: {str(e)}")
        return {"categories": {}}

def process_firebog_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process The Firebog JSON format to use only v.firebog.net URLs and improve categorization.
    
    Args:
        data: Raw JSON data from The Firebog
        
    Returns:
        Dictionary with standardized format containing filtered and well-categorized blocklists
    """
    try:
        if not isinstance(data, dict) or "categories" not in data:
            raise ValueError("Invalid Firebog data format")
            
        result = {"categories": {}}
        
        # Define better category descriptions
        category_descriptions = {
            "Suspicious": "Suspicious domains that may be involved in malicious activities",
            "Advertising": "Advertisement networks and tracking domains",
            "Tracking & Telemetry": "Domains used for user tracking and data collection",
            "Malicious": "Known malware, phishing, and scam domains",
            "Other": "Additional curated blocklists from The Firebog"
        }
        
        # Track if we found any v.firebog.net URLs
        found_firebog_urls = False
        seen_urls = set()  # Track unique URLs
        
        for category, category_data in data["categories"].items():
            if not isinstance(category_data, dict):
                continue
                
            blocklists = category_data.get("blocklists", [])
            if not isinstance(blocklists, list):
                continue
                
            processed_blocklists = []
            for item in blocklists:
                if not isinstance(item, dict):
                    continue
                    
                # Only include URLs from v.firebog.net
                url = item.get("url", "").strip()
                if not url or "v.firebog.net" not in url.lower():
                    continue
                    
                # Skip if we've seen this URL before
                if url in seen_urls:
                    continue
                    
                seen_urls.add(url)
                found_firebog_urls = True
                
                # Extract a clean name from the URL
                name = url.split("/")[-1]  # Get the last part of the URL
                if name.endswith(".txt"):
                    name = name[:-4]  # Remove .txt extension
                name = name.replace("hosts", "").replace(".", " ").strip()  # Clean up common patterns
                name = " ".join(word.capitalize() for word in name.split())  # Capitalize words
                
                try:
                    processed_blocklists.append({
                        "name": name or "Firebog Curated List",  # Fallback name if empty
                        "url": url,
                        "entries": int(item.get("entries", 0)),
                        "source": "The Firebog (v.firebog.net)"
                    })
                except (KeyError, ValueError) as e:
                    log_message(f"Warning: Invalid Firebog blocklist entry in {category}: {e}")
                    continue
            
            if processed_blocklists:
                result["categories"][category] = {
                    "description": category_descriptions.get(category, f"Curated blocklists from The Firebog's {category} category"),
                    "blocklists": processed_blocklists
                }
        
        if not found_firebog_urls:
            log_message("Warning: No v.firebog.net URLs found in The Firebog data")
            
        return result
        
    except Exception as e:
        log_message(f"Error processing Firebog data: {str(e)}")
        return {"categories": {}}

def process_nextdns_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process NextDNS JSON data into standardized format.
    
    Args:
        data: Dictionary containing NextDNS JSON data
        
    Returns:
        Dictionary with standardized blocklist data
    """
    if not data or "categories" not in data:
        log_message("Warning: Invalid NextDNS data format")
        return {"categories": {}}
    
    return data

def write_blocklist_conf(output_file: str, sources: Dict[str, Any]) -> None:
    """
    Write the blocklist configuration file.
    
    Args:
        output_file: Path to the output configuration file
        sources: Dictionary mapping source names to their data
        
    Each source's data should contain:
    - categories: Dict of category names to their blocklists
    - Each blocklist has: name, url, entries
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("##################################################################################\n")
            f.write("# DNSCrypt-Proxy Domains Blocklist Configuration\n")
            f.write("# Generated by generate_domains_blocklist_conf.py\n")
            f.write("##################################################################################\n\n")
            
            # Write local additions section
            f.write("# Local additions\n")
            f.write("file:domains-blocklist-local-additions.txt\n\n")
            
            # Process each source
            for source_name, source_data in sources.items():
                if not isinstance(source_data, dict) or "categories" not in source_data:
                    log_message(f"Warning: Invalid data format for {source_name}, skipping")
                    continue
                
                categories = source_data["categories"]
                if not categories:
                    log_message(f"Warning: No categories found for {source_name}")
                    continue
                
                # Write source header with clear section marker
                f.write(f"##################################################################################\n")
                f.write(f"# {source_name} Blocklists\n")
                if source_name == "RethinkDNS":
                    f.write("# Source: https://rethinkdns.com/configure\n\n")
                elif source_name == "ShadowWhisperer":
                    f.write("# Source: https://github.com/ShadowWhisperer/BlockLists\n")
                    f.write("# Note: Direct categorized blocklists from ShadowWhisperer\n\n")
                elif source_name == "The Firebog":
                    f.write("# Source: https://v.firebog.net/\n")
                    f.write("# Note: Only using curated lists hosted directly at v.firebog.net\n\n")
                elif source_name == "Geoffrey Frogeye":
                    f.write("# Source: https://hostfiles.frogeye.fr/\n\n")
                
                # Process each category
                for category, category_data in categories.items():
                    if not isinstance(category_data, dict):
                        continue
                        
                    # Write category header
                    f.write(f"# {category}\n")
                    if "description" in category_data:
                        f.write(f"# {category_data['description']}\n")
                    
                    # Process blocklists
                    blocklists = category_data.get("blocklists", [])
                    for blocklist in blocklists:
                        if not isinstance(blocklist, dict):
                            continue
                            
                        # Write blocklist entry with description from CATEGORIES comments
                        if source_name == "ShadowWhisperer":
                            category_desc = {
                                'Ads': 'Advertisements, Banners, Widgets & Push Notifications',
                                'Adult': 'Porn / 18+ Content',
                                'Apple': 'Bloat',
                                'Bloat': 'Domains not required for software to function',
                                'Chat': 'Chat Dialog Popups',
                                'Cryptocurrency': 'Bitcoin, Ethereum, Mining, etc. (Not Malware)',
                                'Dating': 'Dating Sites',
                                'DNS': 'DNS Resolvers',
                                'Dynamic': 'Dynamic DNS',
                                'Fonts': 'Fonts',
                                'Free': 'Free/Cheap Hosting, Free Blogs',
                                'Gambling': 'Casino, Gambling, Poker sites',
                                'Junk': 'Personally untrusted software, browser extensions, search engines, etc',
                                'Malware': 'Malicious Sites, PUPs, Malware, Browser Hijackers, Phishing Sites',
                                'Marketing': 'Marketing, Ebay Listing Tools, etc',
                                'Marketing-Email': 'Email Based Marketing',
                                'Microsoft': 'Apps, Bing, Bloat, Tiles, etc',
                                'Remote': 'Domains used for remote sessions',
                                'Risk': 'Bad ISP/Bots/Spam, Keyloggers, Sites used by compromised devices',
                                'Scam': 'Fake freight, gift cards, products, support, pets, firearms, news, etc',
                                'Shock': 'Gore, Gross, and Torture sites',
                                'Top_Level': 'Top Level Domains. Sorted by continent, then by country',
                                'Tracking': 'Analytics, Diagnostics, Location, Metrics, Public IP',
                                'Tunnels': 'VPNs & Proxies',
                                'Typo': 'Misspelling of websites / Typosquatting',
                                'URL Shortener': 'URL Shorteners. Can be used to mask malicious domains'
                            }
                            if blocklist["name"] in category_desc:
                                f.write(f"# {blocklist['name']}: {category_desc[blocklist['name']]}\n")
                            else:
                                f.write(f"# {blocklist['name']}\n")
                        else:
                            if "name" in blocklist:
                                f.write(f"# {blocklist['name']}\n")
                        if "sub_category" in blocklist and blocklist["sub_category"]:
                            f.write(f"# Category: {blocklist['sub_category']}\n")
                        if "entries" in blocklist and blocklist["entries"] > 0:
                            f.write(f"# Entries: {blocklist['entries']}\n")
                        if "url" in blocklist:
                            f.write(f"{blocklist['url']}\n")
                        f.write("\n")
                
                f.write("\n")
                
        log_message(f"Successfully generated {output_file}")
        
    except Exception as e:
        log_message(f"Error writing configuration file: {str(e)}")

def main():
    """Main function to generate the blocklist configuration."""
    log_message("Starting to generate domains-blocklist.conf...")
    
    # Load and process each source in a specific order
    sources = {}
    
    # 1. RethinkDNS (Primary source)
    try:
        rethinkdns_data = load_json_file("blocklists_rethinkdns.json")
        sources["RethinkDNS"] = process_rethinkdns_data(rethinkdns_data)
        log_message("Loaded RethinkDNS data")
    except Exception as e:
        log_message(f"Error loading RethinkDNS data: {str(e)}")
    
    # 2. ShadowWhisperer (Comprehensive categorized lists)
    try:
        shadowwhisperer_data = load_json_file("blocklists_shadowwhisperer.json")
        sources["ShadowWhisperer"] = process_shadowwhisperer_data(shadowwhisperer_data)
        log_message("Loaded ShadowWhisperer data")
    except Exception as e:
        log_message(f"Error loading ShadowWhisperer data: {str(e)}")
    
    # 3. NextDNS (Recommended blocklists)
    try:
        nextdns_data = load_json_file("blocklists_nextdns.json")
        sources["NextDNS"] = process_nextdns_data(nextdns_data)
        log_message("Loaded NextDNS data")
    except Exception as e:
        log_message(f"Error loading NextDNS data: {str(e)}")
    
    # 4. yokoffing (Curated annoyance and privacy lists)
    try:
        yokoffing_data = load_json_file("blocklists_yokoffing.json")
        sources["yokoffing"] = yokoffing_data  # Already in correct format
        log_message("Loaded blocklists_yokoffing.json")
    except Exception as e:
        log_message(f"Error loading yokoffing data: {str(e)}")
    
    # 5. Frogeye (Specialized tracking lists)
    try:
        frogeye_data = load_json_file("blocklists_frogeye.json")
        sources["Geoffrey Frogeye"] = frogeye_data  # Already in correct format
        log_message("Loaded blocklists_frogeye.json")
    except Exception as e:
        log_message(f"Error loading Frogeye data: {str(e)}")
    
    # 6. The Firebog (Additional curated lists)
    try:
        firebog_data = load_json_file("blocklists_firebog.json")
        if "categories" in firebog_data:
            sources["The Firebog"] = firebog_data
            log_message("Loaded The Firebog data")
    except Exception as e:
        log_message(f"Error loading The Firebog data: {str(e)}")
    
    # Generate configuration file
    write_blocklist_conf("domains-blocklist.conf", sources)
    log_message("Generated domains-blocklist.conf")

if __name__ == "__main__":
    main() 