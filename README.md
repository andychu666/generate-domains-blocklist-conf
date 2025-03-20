# DNSCrypt-Proxy Blocklist Generator

A utility to generate DNSCrypt-Proxy compatible domain blocklists using categorized data from multiple sources:
- RethinkDNS's public configuration
- ShadowWhisperer's BlockLists
- The Firebog's curated blocklists
- Geoffrey Frogeye's First-party Trackers

## Overview

This tool helps you create organized blocklist configurations for DNSCrypt-Proxy by:
1. Fetching categorized blocklist data from multiple sources
2. Converting the data into DNSCrypt-Proxy's blocklist format
3. Generating organized configuration files for different categories (Privacy, Security, ParentalControl)

## Prerequisites

- Python 3.13
- `uv` package manager (recommended) or pip
- DNSCrypt-Proxy's `generate-domains-blocklist.py` utility

## Installation

1. Clone this repository:
```bash
git clone https://github.com/andychu666/generate-domains-blocklist-conf.git
cd generate-domains-blocklist-conf
```

2. Create and activate a virtual environment:
```bash
# Using Python 3.13
uv venv .venv -p 3.13


# Activate the environment
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

3. Install dependencies:
```bash
uv pip install playwright
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

## Data Sources

This tool fetches blocklist configurations from:
1. RethinkDNS Configure Page (https://rethinkdns.com/configure)
2. ShadowWhisperer's BlockLists (https://github.com/ShadowWhisperer/BlockLists)
3. The Firebog's Curated Lists (https://firebog.net/)
4. Geoffrey Frogeye's First-party Trackers (https://hostfiles.frogeye.fr/)

**Note**: This project is not affiliated with or endorsed by RethinkDNS, ShadowWhisperer, The Firebog, or Geoffrey Frogeye. It simply converts their publicly available blocklist configurations into DNSCrypt-Proxy compatible format.

## Categories

The tool organizes blocklists from different sources into their respective categories:

### RethinkDNS Categories

#### Parental Controls
- Adult content
- Piracy
- Gambling
- Dating
- Social Media
- Chat platforms
- Gaming
- Streaming Media
- File Sharing

#### Security
- Malware
- Ransomware
- Phishing
- Cryptocurrency
- Scams
- Dynamic DNS
- URL Shorteners
- Other threats

#### Privacy
- Adware
- Spyware
- Trackers
- Marketing
- Microsoft telemetry
- Apple telemetry
- Google telemetry
- Smart TV telemetry

### ShadowWhisperer Categories

- Ads: Advertisements, Banners, Widgets & Push Notifications
- Adult: Porn / 18+ Content
- Apple: Bloat
- Bloat: Fonts, Surveys, Domains not required for software to function
- Chat: Chat Dialog Popups
- Cryptocurrency: Bitcoin, Ethereum, Mining, etc. (Not malware, but could be used by it)
- Dating: Dating Sites
- Dynamic: Dynamic DNS (DNS → IP)
- Free: Free/Cheap Hosting, Free Blogs
- Gambling: Casino, Gambling, Poker sites
- Junk: Personally Untrusted Antivirus, Browser Extensions, Search Engines, etc.
- Malware: Malicious Sites, PUPs, Malware, Browser Hijackers, Phishing Sites
- Marketing: Marketing, Ebay Listing Tools, etc.
- Microsoft: Apps, Bing, Bloat, Tiles, etc.
- Remote: Domains used for remote sessions
- Risk: Bad ISP/Bots/Spam, Keyloggers, Sites used by compromised devices
- Scam: Fake freight, gift cards, products, support, pet sales, firearms, news, etc.
- Shock: Gore, Gross, and Torture sites
- Tracking: Analytics, Diagnostics, Location, Metrics, Public IP
- Tunnels: VPNs & Proxies
- URL Shortener: URL Shorteners (Can be used to mask malicious domains)

### The Firebog Categories

#### Suspicious
- KADhosts
- Spammers
- Blacklists
- Referrer Spam
- Other suspicious domains

#### Advertising
- AdAway
- Adguard DNS
- Anti-Adblock
- Easylist
- Peter Lowe's Adservers
- Other ad domains

#### Tracking & Telemetry
- Easyprivacy
- Windows Spyware
- Smart TV tracking
- Multi-party trackers
- Analytics domains

#### Malicious
- Cryptojacking
- Malware domains
- Phishing Army
- Ransomware
- Scam domains
- Stalkerware

#### Other
- Adult content
- Facebook
- Custom filters

### Geoffrey Frogeye Categories

#### First-party Trackers
- Contains every hostname redirecting to a hand-picked list of first-party trackers
- Safe from false-positives
- Includes company domains for comprehensive blocking

#### First-party Only
- Same as First-party Trackers but without company domains
- Optimized for browser extensions like uBlock Origin
- Focused on specific tracking endpoints

#### Multi-party Trackers
- Contains hostnames redirecting to trackers from existing lists
- Sources include EasyPrivacy and AdGuard
- May have some false positives
- Includes company domains

#### Multi-party Only
- Same as Multi-party Trackers but without company domains
- Designed for use with other blocklists in regex-mode
- Focused on specific tracking endpoints

## Output Files

The tool generates several output files:

### Markdown Files
- `blocklists_rethinkdns.md`: RethinkDNS blocklists organized by category
- `blocklists_shadowwhisperer.md`: ShadowWhisperer blocklists organized by category
- `blocklists_firebog.md`: The Firebog's curated blocklists organized by category
- `blocklists_frogeye.md`: Geoffrey Frogeye's tracker blocklists organized by category

Each markdown file includes:
- Category and subcategory
- Blocklist name
- Number of entries (where available)
- Source URL

### JSON Files
- `blocklists_rethinkdns.json`
- `blocklists_shadowwhisperer.json`
- `blocklists_firebog.json`
- `blocklists_frogeye.json`

Structured JSON files containing the same data as the markdown files, useful for programmatic processing or integration with other tools.

### `domains-blocklist.conf`
The configuration file that lists URLs of blocklist sources for DNSCrypt-Proxy's `generate-domains-blocklist.py` utility. This file:
- Lists URLs of blocklist sources, one per line
- Supports file:// URLs for local additions
- Allows commenting out sources with # to disable them
- Follows DNSCrypt-Proxy's standard configuration format
- Used by `generate-domains-blocklist.py` to create an optimized and deduplicated domain blocklist

The generated configuration can be used with DNSCrypt-Proxy's `generate-domains-blocklist.py` to create a final blocklist that:
- Removes duplicates across all sources
- Handles overlapping patterns
- Respects the allowlist (domains-allowlist.txt)
- Supports time-restricted blocks

### Debug Screenshots
- `debug_screenshot_rethinkdns.png`
- `debug_screenshot_shadowwhisperer.png`
- `debug_screenshot_firebog.png`

Screenshots taken during the fetch process, useful for debugging or verification.

## Usage

1. Run the RethinkDNS fetch script:
```bash
python fetch_blocklists_rethinkdns.py
```

2. Run the ShadowWhisperer fetch script:
```bash
python fetch_blocklists_shadowwhisperer.py
```

3. Run the Firebog fetch script:
```bash
python fetch_blocklists_firebog.py
```

4. Run the Frogeye fetch script:
```bash
python fetch_blocklists_frogeye.py
```

5. Generate the combined DNSCrypt-Proxy configuration:
```bash
python generate_domains_blocklist_conf.py
```
This will create `domains-blocklist.conf` with all blocklists properly formatted, categorized, and deduplicated.

6. Use the generated configuration with DNSCrypt-Proxy's `generate-domains-blocklist.py`:
```bash
python /path/to/dnscrypt-proxy/utils/generate-domains-blocklist/generate-domains-blocklist.py \
    domains-blocklist.conf > blocklist.txt
```

## Integration with DNSCrypt-Proxy

This tool generates configuration files compatible with DNSCrypt-Proxy's domain blocking feature. You'll need:
1. DNSCrypt-Proxy's `generate-domains-blocklist.py` utility (from the DNSCrypt-Proxy repository)
2. The configuration file generated by this tool

For more information about DNSCrypt-Proxy's domain blocking feature, see:
- [DNSCrypt-Proxy Documentation](https://github.com/DNSCrypt/dnscrypt-proxy)

## Project Structure

```
generate-domains-blocklist-conf/
├── .gitattributes                   # Git attributes for line ending handling
├── .gitignore                       # Git ignore patterns
├── LICENSE                          # ISC License
├── README.md                        # This documentation
├── requirements.txt                 # Python dependencies
├── fetch_blocklists_rethinkdns.py  # RethinkDNS blocklist fetcher
├── fetch_blocklists_shadowwhisperer.py # ShadowWhisperer blocklist fetcher
├── fetch_blocklists_firebog.py     # The Firebog blocklist fetcher
├── fetch_blocklists_frogeye.py     # Geoffrey Frogeye's blocklist fetcher
└── generate_domains_blocklist_conf.py  # Configuration generator
```

Generated files (not tracked by git):
- `blocklists_*.md`: Markdown files containing blocklist data
- `blocklists_*.json`: JSON files containing structured blocklist data
- `debug_screenshot_*.png`: Debug screenshots from fetching process
- `domains-blocklist.conf`: Generated DNSCrypt-Proxy configuration

## License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [DNSCrypt-Proxy](https://github.com/DNSCrypt/dnscrypt-proxy) - For the domain blocking functionality
- [RethinkDNS](https://rethinkdns.com/configure) - Source of blocklist categorization data
- [ShadowWhisperer's BlockLists](https://github.com/ShadowWhisperer/BlockLists) - Additional blocklist source
- [The Firebog](https://firebog.net/) - Curated collection of blocklists 
- [Geoffrey Frogeye](https://hostfiles.frogeye.fr/) - Source of first-party tracker blocklists 