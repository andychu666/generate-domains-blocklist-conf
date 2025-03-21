# DNSCrypt-Proxy Blocklist Generator

A utility to generate DNSCrypt-Proxy compatible domain blocklists using categorized data from multiple sources in a prioritized order:
1. RethinkDNS's public configuration (Primary source)
2. The Firebog's curated v.firebog.net lists
3. ShadowWhisperer's BlockLists (Additional lists)
4. Geoffrey Frogeye's First-party Trackers (Specialized tracking lists)

## Overview

This tool helps you create organized blocklist configurations for DNSCrypt-Proxy by:
1. Fetching categorized blocklist data from multiple trusted sources
2. Converting the data into DNSCrypt-Proxy's blocklist format
3. Generating organized configuration files with clear section markers
4. Prioritizing reliable and well-maintained blocklists

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

This tool fetches blocklist configurations in a specific order to ensure reliability:

1. RethinkDNS Configure Page (Primary Source)
   - https://rethinkdns.com/configure
   - Comprehensive categorization
   - Regular updates
   - Well-maintained lists

2. The Firebog Curated Lists
   - https://v.firebog.net/
   - Only uses lists hosted directly at v.firebog.net
   - Carefully curated and reliable
   - Focused on specific threats

3. ShadowWhisperer's BlockLists
   - https://github.com/ShadowWhisperer/BlockLists
   - Additional specialized lists
   - Community-maintained

4. Geoffrey Frogeye's First-party Trackers
   - https://hostfiles.frogeye.fr/
   - Specialized tracking protection
   - Detailed categorization of trackers

**Note**: This project is not affiliated with or endorsed by RethinkDNS, ShadowWhisperer, The Firebog, or Geoffrey Frogeye. It simply converts their publicly available blocklist configurations into DNSCrypt-Proxy compatible format.

## Categories

The tool organizes blocklists from different sources into their respective categories:

### RethinkDNS Categories (Primary)

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

### The Firebog Categories (Curated v.firebog.net Lists)

#### Suspicious
- Domains with suspicious behavior
- Potential threats
- Spam sources
- Blacklisted domains

#### Advertising
- Advertisement networks
- Tracking domains
- Ad servers
- Marketing platforms

#### Tracking & Telemetry
- User tracking endpoints
- Data collection services
- Analytics platforms
- Telemetry servers

#### Malicious
- Known malware domains
- Phishing sites
- Scam domains
- Cryptojacking

#### Other
- Additional curated lists
- Special purpose blocklists

### ShadowWhisperer Categories (Additional)

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

### Geoffrey Frogeye Categories (Specialized)

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

### Configuration File
- `domains-blocklist.conf`: The main DNSCrypt-Proxy configuration file
  - Clear section markers for each source
  - Organized by priority and category
  - Includes entry counts and descriptions
  - Local additions support

### Markdown Files
- `blocklists_rethinkdns.md`: Primary source blocklists
- `blocklists_firebog.md`: Curated v.firebog.net lists
- `blocklists_shadowwhisperer.md`: Additional specialized lists
- `blocklists_frogeye.md`: Tracking protection lists

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