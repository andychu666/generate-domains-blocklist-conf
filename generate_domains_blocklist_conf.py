#!/usr/bin/env python3
"""
Generate DNSCrypt-Proxy domains blocklist configuration.

This script combines multiple blocklist sources into a single DNSCrypt-Proxy compatible
configuration file. It processes blocklists from:
1. Official DNSCrypt default configuration
2. RethinkDNS
3. ShadowWhisperer
4. The Firebog
5. Geoffrey Frogeye

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

def load_dnscrypt_default_conf() -> str:
    """
    Load the official DNSCrypt default configuration.
    
    Returns:
        String containing the default configuration content
    """
    try:
        with open("blocklists_dnscrypt_default.md", 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        log_message("Warning: blocklists_dnscrypt_default.md not found. Run fetch_default_conf.py first.")
        return ""
    except IOError as e:
        log_message(f"Error reading DNSCrypt default configuration: {str(e)}")
        return ""

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
        - Each blocklist has: name, url, entries, description
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
        
        # Process each main category
        for category, category_data in categories.items():
            if not isinstance(category_data, dict):
                log_message(f"Warning: Invalid category data for {category}, skipping")
                continue
                
            # Initialize category with description and total entries
            result["categories"][category] = {
                "description": category_data.get("description", f"Blocklists from RethinkDNS's {category} category"),
                "total_entries": category_data.get("total_entries", 0),
                "blocklists": []
            }
            
            # Process subcategories
            subcategories = category_data.get("subcategories", {})
            for subcat_name, subcat_data in subcategories.items():
                if not isinstance(subcat_data, dict):
                    continue
                    
                # Process entries in subcategory
                entries = subcat_data.get("entries", [])
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                        
                    try:
                        # Create blocklist entry with enhanced metadata
                        blocklist = {
                            "name": str(entry["name"]),
                            "url": str(entry["url"]) if isinstance(entry["url"], str) else entry["url"][0],
                            "entries": int(entry.get("entries", 0)),
                            "source": "RethinkDNS",
                            "sub_category": subcat_name,
                            "format": entry.get("format", ""),
                            "pack": entry.get("pack", []),
                            "level": entry.get("level", []),
                            "subgroup": entry.get("subgroup", ""),
                            "description": subcat_data.get("description", "")
                        }
                        result["categories"][category]["blocklists"].append(blocklist)
                    except (KeyError, ValueError) as e:
                        log_message(f"Warning: Invalid blocklist entry in {category}/{subcat_name}: {e}")
                        continue
        
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

def write_configuration(blocklists, output_file):
    """Write the configuration to a file."""
    with open(output_file, "w", encoding="utf-8") as f:
        current_section = None
        
        for blocklist in blocklists:
            section = blocklist.get("section", "")
            name = blocklist.get("name", "")
            category = blocklist.get("category", "")
            
            # Update section tracking
            if section != current_section:
                current_section = section
                f.write("\n")
                f.write("#" * 80 + "\n")
                f.write(f"# {section}\n")
                f.write("#" * 80 + "\n\n")
            
            # Determine if this entry should be commented
            should_comment = True
            
            # Check if this is in the Privacy section
            if section == "Privacy":
                # First check if it's in the comment list
                if any(comment in name or comment in category for comment in privacy_comment_list):
                    should_comment = True
                # Then check if it should be uncommented
                elif any(base in name or (base == category and name in ["Normal", "Light"]) for base in privacy_uncomment_list):
                    should_comment = False
            
            # Write the entry name and metadata
            if "category" in blocklist:
                f.write(f"{'# ' if should_comment else ''}{name}\n")
                f.write(f"# Category: {blocklist['category']}\n")
            else:
                f.write(f"{'# ' if should_comment else ''}{name}\n")
            
            if "entries" in blocklist:
                f.write(f"# Entries: {blocklist['entries']}\n")
            
            # Write URL with appropriate commenting
            if "url" in blocklist:
                url = blocklist["url"]
                if should_comment:
                    f.write(f"# {url}\n")
                else:
                    f.write(f"{url}\n")
                f.write("\n")  # Add blank line after every URL
            else:
                f.write("\n")  # Add blank line if no URL

def write_blocklist_conf(output_file: str, sources: Dict[str, Any]) -> None:
    """
    Write the blocklist configuration file.
    
    Args:
        output_file: Path to the output configuration file
        sources: Dictionary mapping source names to their data
    """
    # Define lists that should be commented out in Security category
    security_comment_list = [
        "Dynamic DNS Providers",  # Keep commented out as requested
        "Child Protection",       # Keep commented out as requested
        "URL Shorteners"         # Keep commented out as requested
    ]
    
    # Define lists to uncomment in the Privacy section
    privacy_uncomment_list = [
        "Light",  # For Lite privacy
        "Aggressive",  # For aggressive privacy
        "liteprivacy",  # Added for RethinkDNS lite privacy
        "aggressiveprivacy",  # Added for RethinkDNS aggressive privacy
        "scams & phishing"  # Added to uncomment scams & phishing packs
    ]
    
    # Define lists to ensure stay commented in the Privacy section
    privacy_comment_list = [
        "Ultimate",  # HaGeZi Ultimate
        "Tracking Aggressive",  # Lightswitch05 Tracking Aggressive
        "1Hosts Xtra",
        "Typo",  # Added to exclude typo protection
        "Top_Level",  # Added to exclude top level domains
        "Prigent-Adult"  # Added to comment out Prigent-Adult from Firebog
    ]
    
    # Define ShadowWhisperer categories to comment out
    shadowwhisperer_comment_list = [
        "Adult",
        "Apple",
        "Chat",
        "Dating",
        "DNS",
        "Dynamic",  # Added
        "Microsoft",
        "Top_Level",  # Too strict, may break functionality
        "Typo",      # Resource intensive with low benefit
        "UrlShortener",  # Updated to match the actual path
        "URL Shortener"  # Keep the old one for backward compatibility
    ]
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("##################################################################################\n")
            f.write("# DNSCrypt-Proxy Domains Blocklist Configuration\n")
            f.write("# Generated by generate_domains_blocklist_conf.py\n")
            f.write("##################################################################################\n\n")
            
            # Write DNSCrypt default configuration
            default_conf = load_dnscrypt_default_conf()
            if default_conf:
                f.write(default_conf)
                f.write("\n")
            
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
                    f.write("# Source: https://rethinkdns.com/configure\n")
                    f.write("# License: Mozilla Public License Version 2.0\n\n")
                elif source_name == "ShadowWhisperer":
                    f.write("# Source: https://github.com/ShadowWhisperer/BlockLists\n")
                    f.write("# Note: Direct categorized blocklists from ShadowWhisperer\n\n")
                elif source_name == "The Firebog":
                    f.write("# Source: https://v.firebog.net/\n")
                    f.write("# Note: Only using curated lists hosted directly at v.firebog.net\n\n")
                elif source_name == "Geoffrey Frogeye":
                    f.write("# Source: https://hostfiles.frogeye.fr/\n\n")
                
                # Process each category
                for category_name, category_data in categories.items():
                    if not isinstance(category_data, dict):
                        continue
                        
                    # Write category header with description and total entries
                    f.write(f"# {category_name}\n")
                    if "description" in category_data:
                        f.write(f"# {category_data['description']}\n")
                    if "total_entries" in category_data:
                        f.write(f"# Total Entries: {category_data['total_entries']:,}\n\n")
                    
                    # Process each blocklist in the category
                    for blocklist in category_data.get("blocklists", []):
                        if not isinstance(blocklist, dict):
                            continue
                            
                        # Write blocklist name and metadata
                        f.write(f"# {blocklist.get('name', 'Unnamed Blocklist')}\n")
                        
                        # Handle ShadowWhisperer categories
                        if source_name == "ShadowWhisperer":
                            url = blocklist.get("url", "").lower()
                            should_comment = any(cat.lower() in url.lower() for cat in shadowwhisperer_comment_list)
                        
                        # Handle RethinkDNS ParentalControl category
                        elif source_name == "RethinkDNS" and category_name == "ParentalControl":
                            should_comment = True  # Always comment out ParentalControl entries
                        
                        # Handle Security category
                        elif source_name == "RethinkDNS" and category_name == "Security":
                            should_comment = any(item in blocklist.get("name", "") for item in security_comment_list)
                            # Ensure Full and Extra are uncommented
                            if "Full" in blocklist.get("name", "") or "Extra" in blocklist.get("name", ""):
                                should_comment = False
                        
                        # Handle Privacy category
                        elif source_name == "RethinkDNS" and category_name == "Privacy":
                            should_comment = True  # Default to comment out
                            
                            # Check for Lite and Aggressive privacy settings
                            if "pack" in blocklist:
                                pack_list = blocklist["pack"]
                                if isinstance(pack_list, list):
                                    if any(name in pack_list for name in privacy_uncomment_list):
                                        should_comment = False
                            elif any(name in blocklist.get("name", "").lower() for name in privacy_uncomment_list):
                                should_comment = False
                            
                            # Always comment out items in privacy_comment_list
                            if any(name in blocklist.get("name", "") for name in privacy_comment_list):
                                should_comment = True
                        
                        # Handle The Firebog
                        elif source_name == "The Firebog":
                            should_comment = any(item in blocklist.get("url", "") for item in privacy_comment_list)
                        
                        else:
                            should_comment = False
                        
                        # Write URL with appropriate commenting
                        if "url" in blocklist:
                            url = blocklist["url"]
                            if should_comment:
                                f.write(f"# {url}\n")
                            else:
                                f.write(f"{url}\n")
                            f.write("\n")  # Add blank line after every URL
                        else:
                            f.write("\n")  # Add blank line if no URL
                
                f.write("\n")
                
        log_message(f"Successfully generated {output_file}")
        
    except Exception as e:
        log_message(f"Error writing configuration: {str(e)}")

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
    
    # 4. Frogeye (Specialized tracking lists)
    try:
        frogeye_data = load_json_file("blocklists_frogeye.json")
        sources["Geoffrey Frogeye"] = frogeye_data  # Already in correct format
        log_message("Loaded Geoffrey Frogeye data")
    except Exception as e:
        log_message(f"Error loading Frogeye data: {str(e)}")
    
    # 5. The Firebog (Curated lists)
    try:
        firebog_data = load_json_file("blocklists_firebog.json")
        sources["The Firebog"] = process_firebog_data(firebog_data)
        log_message("Loaded The Firebog data")
    except Exception as e:
        log_message(f"Error loading The Firebog data: {str(e)}")
    
    # Generate the configuration file
    write_blocklist_conf("domains-blocklist.conf", sources)

if __name__ == "__main__":
    main() 