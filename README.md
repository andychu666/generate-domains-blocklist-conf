# DNSCrypt-Proxy Domains Blocklist Generator

This project generates a comprehensive domains blocklist configuration for DNSCrypt-Proxy by combining multiple high-quality sources.

## Sources

1. **RethinkDNS**
   - Primary source with extensive categorization
   - Categories: ParentalControl, Security, Privacy
   - Regular updates and well-maintained lists
   - Source: https://rethinkdns.com/configure

2. **ShadowWhisperer**
   - Comprehensive categorized lists
   - Categories: Privacy, ParentalControl, Security
   - Community-maintained
   - Source: https://github.com/ShadowWhisperer/BlockLists

3. **NextDNS**
   - Recommended blocklists
   - Curated selection of high-quality blocklists
   - Regular updates
   - Source: https://github.com/nextdns/blocklists

4. **yokoffing**
   - Curated annoyance and privacy lists
   - Categories: Annoyances, Privacy
   - Source: https://github.com/yokoffing/filterlists

5. **Geoffrey Frogeye**
   - Specialized tracking protection lists
   - First-party and Multi-party trackers
   - Detailed categorization of trackers
   - Source: https://hostfiles.frogeye.fr/

6. **The Firebog**
   - Additional curated lists (v.firebog.net only)
   - Categories: Suspicious, Advertising, Tracking & Telemetry, Malicious
   - Carefully curated and reliable
   - Focused on specific threats
   - Source: https://v.firebog.net/

**Note**: This project is not affiliated with or endorsed by any of the above sources. It simply converts their publicly available blocklist configurations into DNSCrypt-Proxy compatible format.

## Usage

1. Install dependencies:
```powershell
uv venv
uv pip install -r requirements.txt
```

2. Run the fetch scripts to gather blocklists:
```powershell
python fetch_blocklists_rethinkdns.py
python fetch_blocklists_shadowwhisperer.py
python fetch_blocklists_nextdns.py
python fetch_blocklists_yokoffing.py
python fetch_blocklists_frogeye.py
python fetch_blocklists_firebog.py
```

3. Generate the configuration:
```powershell
python generate_domains_blocklist_conf.py
```

4. Copy `domains-blocklist.conf` to your DNSCrypt-Proxy configuration directory.

## Output Files

- `domains-blocklist.conf`: Main configuration file for DNSCrypt-Proxy
- `blocklists_*.json`: Intermediate files containing structured data
- `blocklists_*.md`: Documentation for each source's blocklists
- `debug_screenshots/`: Debug information and screenshots (gitignored)

## Local Additions

You can add your own domains to block by creating a file named `domains-blocklist-local-additions.txt` in your DNSCrypt-Proxy configuration directory.

## License

MIT License - See LICENSE file for details

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
- Bloat: Domains not required for software to function
- Chat: Chat Dialog Popups
- Cryptocurrency: Bitcoin, Ethereum, Mining, etc. (Not Malware)
- Dating: Dating Sites
- DNS: DNS Resolvers
- Dynamic: Dynamic DNS
- Fonts: Fonts
- Free: Free/Cheap Hosting, Free Blogs
- Gambling: Casino, Gambling, Poker sites
- Junk: Personally untrusted software, browser extensions, search engines, etc
- Malware: Malicious Sites, PUPs, Malware, Browser Hijackers, Phishing Sites
- Marketing: Marketing, Ebay Listing Tools, etc
- Marketing-Email: Email Based Marketing
- Microsoft: Apps, Bing, Bloat, Tiles, etc
- Remote: Domains used for remote sessions
- Risk: Bad ISP/Bots/Spam, Keyloggers, Sites used by compromised devices
- Scam: Fake freight, gift cards, products, support, pets, firearms, news, etc
- Shock: Gore, Gross, and Torture sites
- Top_Level: Top Level Domains. Sorted by continent, then by country
- Tracking: Analytics, Diagnostics, Location, Metrics, Public IP
- Tunnels: VPNs & Proxies
- Typo: Misspelling of websites / Typosquatting
- URL Shortener: URL Shorteners. Can be used to mask malicious domains

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

### NextDNS Categories (Recommended)
- Ads & Trackers Blocklists
- Privacy Blocklists
- Security Blocklists
- Adult Content Filters
- Regional Blocklists
- Custom Blocklists

### Yokoffing Categories (Curated)
- Annoyances
- Privacy Protection
- Adult Content
- Custom Filters

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
├── fetch_blocklists_nextdns.py     # NextDNS blocklist fetcher
├── fetch_blocklists_yokoffing.py   # Yokoffing blocklist fetcher
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
- [NextDNS](https://github.com/nextdns/blocklists) - Recommended high-quality blocklists
- [Yokoffing](https://github.com/yokoffing/filterlists) - Curated annoyance and privacy lists

21 March 2024 

<p align="center">21 March 2024</p> 