# Analyst Report: CASE-1 Suspicious PowerShell From Office

Severity: High
Status: Investigating
Source: Sophos Central

## Overview

Endpoint alert detected suspicious PowerShell launched from an Office parent process on `FIN-LAPTOP-022`.

## Extracted IOCs

- ipv4: 10.20.15.44
- sha256: 3b7f54a1f6b2b6ad6998f7e8c2a2d6d3d67bbf7fa69bb59bb1f79c03c9f45c87

## Timeline

- 2026-07-02T14:22:11Z [sophos_endpoint] Sophos Central alert observed

## Suggested MITRE Mappings

- T1059.001 PowerShell: suspicious PowerShell indicators were observed.
- T1204 User Execution: Office parent process suggests user interaction should be reviewed.

## Recommended Next Steps

- Confirm hostname and logged-in user.
- Review parent process and process tree.
- Check persistence locations.
- Determine if isolation is required.
