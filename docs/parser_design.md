# Parser Design

Parsers are deliberately tolerant. The intake service preserves raw alert content even when extraction confidence is low.

Supported MVP patterns:

- generic key-value alert text
- generic JSON
- generic CSV
- Windows Event Log text
- Sysmon-like event text
- WAF-style alerts
- Proofpoint-style email alerts
- Sophos-style endpoint alerts
- DNS, proxy, and firewall-style network alerts

The parser extracts canonical fields when possible:

- source and destination IPs
- hostname
- username
- email
- domain
- URL
- file hashes
- file paths
- process fields
- event ID
- rule or signature
- HTTP method/path/status
- country and ASN
- timestamp

IOC extraction runs independently using regex-based detectors and normalizers. This keeps parsing resilient when vendor field names differ.
