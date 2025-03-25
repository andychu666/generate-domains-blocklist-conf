#!/usr/bin/env python3
"""
Fetch the official DNSCrypt domains blocklist configuration.

This script downloads the official DNSCrypt domains blocklist configuration from:
https://raw.githubusercontent.com/DNSCrypt/dnscrypt-proxy/master/utils/generate-domains-blocklist/domains-blocklist.conf

The configuration is saved as blocklists_dnscrypt_default.md for reference and use by
generate_domains_blocklist_conf.py.
"""

import requests
import sys
from pathlib import Path

def log_message(message: str) -> None:
    """Print a message to stderr for immediate output."""
    print(message, file=sys.stderr)

def fetch_default_conf() -> None:
    """
    Fetch the official DNSCrypt domains blocklist configuration.
    
    Downloads the configuration file and saves it as blocklists_dnscrypt_default.md.
    Handles network errors and file writing gracefully.
    """
    url = "https://raw.githubusercontent.com/DNSCrypt/dnscrypt-proxy/master/utils/generate-domains-blocklist/domains-blocklist.conf"
    output_file = "blocklists_dnscrypt_default.md"
    
    try:
        # Download the configuration
        log_message(f"Downloading DNSCrypt default configuration from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        log_message(f"Successfully saved default configuration to {output_file}")
        
    except requests.RequestException as e:
        log_message(f"Error downloading configuration: {str(e)}")
        sys.exit(1)
    except IOError as e:
        log_message(f"Error writing to file {output_file}: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_default_conf() 