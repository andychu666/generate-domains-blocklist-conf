# DNSCrypt-Proxy Domains Blocklist Generator

This project generates a comprehensive domains blocklist configuration for DNSCrypt-Proxy by combining multiple high-quality sources.

## Sources

1. **DNSCrypt Default Configuration**
   - Default blocklists from DNSCrypt-Proxy's generate-domains-blocklist utility
   - Includes essential security and privacy lists
   - Source: https://github.com/DNSCrypt/dnscrypt-proxy/blob/master/utils/generate-domains-blocklist/domains-blocklist.conf

2. **RethinkDNS**
   - Primary source with extensive categorization
   - Categories: ParentalControl, Security, Privacy
   - Regular updates and well-maintained lists
   - Source: https://rethinkdns.com/configure

3. **ShadowWhisperer**
   - Comprehensive categorized lists
   - Categories: Privacy, ParentalControl, Security
   - Community-maintained
   - Source: https://github.com/ShadowWhisperer/BlockLists

4. **NextDNS**
   - Recommended blocklists
   - Curated selection of high-quality blocklists
   - Regular updates
   - Source: https://github.com/nextdns/blocklists

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
```bash
uv venv
uv pip install -r requirements.txt
```

2. Fetch the official DNSCrypt default configuration:
```bash
python fetch_default_conf.py
```
This will download the official DNSCrypt domains blocklist configuration from the DNSCrypt repository.

3. Run the fetch scripts to gather blocklists:
```bash
python fetch_blocklists_rethinkdns.py
python fetch_blocklists_shadowwhisperer.py
python fetch_blocklists_nextdns.py
python fetch_blocklists_frogeye.py
python fetch_blocklists_firebog.py
```

4. Generate the configuration:
```bash
python generate_domains_blocklist_conf.py
```

5. Copy `domains-blocklist.conf` to your DNSCrypt-Proxy configuration directory.

6. Quick Generation (Optional):
If you want to generate the blocklist quickly while skipping any URLs that fail to load:
```bash
python generate_domains_blocklist.py -o dnscrypt-blocklist-domains.txt --ignore-retrieval-failure
```
This option is useful when some blocklist sources are temporarily unavailable but you still want to generate a configuration with the working sources.

## Output Files

- `domains-blocklist.conf`: Main configuration file for DNSCrypt-Proxy
  - Includes default DNSCrypt blocklists at the beginning
  - Automatically marks and comments out duplicate URLs
  - Organizes additional blocklists by source and category
- `blocklists_*.json`: Intermediate files containing structured data
- `blocklists_*.md`: Documentation for each source's blocklists
- `debug_screenshots/`: Debug information and screenshots (gitignored)


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
source .venv/bin/activate  # Linux/macOS
# OR
.\.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

## Project Structure

```
generate-domains-blocklist-conf/
├── .gitattributes                   # Git attributes for line ending handling
├── .gitignore                       # Git ignore patterns
├── LICENSE                          # ISC License
├── README.md                        # This documentation
├── requirements.txt                 # Python dependencies
├── fetch_blocklists_firebog.py     # The Firebog blocklist fetcher
├── fetch_blocklists_frogeye.py     # Geoffrey Frogeye's blocklist fetcher
├── fetch_blocklists_nextdns.py     # NextDNS blocklist fetcher
├── fetch_blocklists_rethinkdns.py  # RethinkDNS blocklist fetcher
├── fetch_blocklists_shadowwhisperer.py # ShadowWhisperer blocklist fetcher
├── fetch_default_conf.py           # DNSCrypt default configuration fetcher
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

## Latest Changes

- Added support for commenting out all ParentalControl entries from RethinkDNS by default
- Updated URL shortener categories to be commented out by default
- Improved error handling for failed blocklist retrievals
- Added support for ignoring retrieval failures with `--ignore-retrieval-failure` flag
- Updated dependencies to latest versions

Last updated: 25 March 2024 