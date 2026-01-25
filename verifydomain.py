import json
import logging
import sys
import os
import re
import requests
from typing import List, Dict, Tuple, Set
from datetime import datetime, timezone
from collections import defaultdict

# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger("domain_verifier")

TIMEOUT = 10
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)
DOMAINS_FILE = "domains.json"
LOG_FILE = "log.json"

def load_log_data(filepath: str) -> List[Dict]:
    """Load log data from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Ensure it's a list
            return data if isinstance(data, list) else [data]
    except Exception as e:
        logger.error(f"Failed to load log from {filepath}: {e}")
        return []

def extract_domains_from_log(log_data: List[Dict]) -> Dict[str, Dict]:
    """Extract domains from log.json and organize by verification status."""
    domains_info = {}
    
    if not log_data:
        return domains_info
    
    # Get the first (latest) log entry
    latest_log = log_data[0] if log_data else {}
    
    # Extract domains from summary details
    if 'summary' in latest_log and 'details' in latest_log['summary']:
        details = latest_log['summary']['details']
        for domain, domain_info in details.items():
            domains_info[domain.lower()] = {
                "domain": domain,
                "crawl_count": domain_info.get("count", 0),
                "subdomains": domain_info.get("subdomains", []),
                "verified": False,
                "accessible": False,
                "status_code": None
            }
    
    return domains_info

def is_valid_domain(domain: str) -> bool:
    """Check if domain format is valid."""
    domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(domain_pattern, domain))

def verify_domain_exists(domain: str) -> Tuple[bool, int]:
    """Verify if a domain is actually accessible and exists. Returns (is_accessible, status_code)."""
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.head(f"http://{domain}", timeout=TIMEOUT, headers=headers, allow_redirects=True)
        return response.status_code < 400, response.status_code
    except requests.exceptions.Timeout:
        try:
            response = requests.get(f"http://{domain}", timeout=TIMEOUT, headers=headers, stream=True)
            return response.status_code < 400, response.status_code
        except Exception as e:
            return False, 0
    except Exception as e:
        return False, 0

def load_domains_from_file(filepath: str) -> Tuple[List[str], List[Dict]]:
    """Load domains from JSON or text file. Returns tuple of (domain_strings, original_data)."""
    domains = []
    original_data = []
    try:
        if filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    original_data = data
                    # Handle list of objects with 'domain' field
                    for item in data:
                        if isinstance(item, dict) and 'domain' in item:
                            domains.append(item['domain'])
                        elif isinstance(item, str):
                            domains.append(item)
                elif isinstance(data, dict):
                    # Handle nested structure
                    for value in data.values():
                        if isinstance(value, list):
                            domains.extend(value)
                        elif isinstance(value, str):
                            domains.append(value)
        else:
            # Assume text file with one domain per line
            with open(filepath, 'r') as f:
                domains = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed to load domains from {filepath}: {e}")
    
    return domains, original_data

def verify_domains(domains: List[str], original_data: List[Dict], verbose: bool = False) -> Dict:
    """Verify a list of domains and preserve original data structure."""
    results = {
        "verified": [],
        "invalid": [],
        "not_accessible": []
    }
    
    # Create mapping of domain to original data
    domain_map = {}
    if original_data:
        for item in original_data:
            if isinstance(item, dict) and 'domain' in item:
                domain_map[item['domain'].lower()] = item
    
    total = len(domains)
    logger.info(f"Starting domain verification for {total} domains...")
    
    for idx, domain in enumerate(domains, 1):
        domain = domain.strip().lower()
        original_item = domain_map.get(domain, {"domain": domain})
        
        # Check format validity
        if not is_valid_domain(domain):
            results["invalid"].append(original_item)
            if verbose:
                logger.warning(f"[{idx}/{total}] Invalid format: {domain}")
            continue
        
        # Check if domain exists
        is_accessible, status_code = verify_domain_exists(domain)
        if is_accessible:
            original_item["accessible"] = True
            original_item["status_code"] = status_code
            results["verified"].append(original_item)
            logger.info(f"[{idx}/{total}] ✓ {domain} ({status_code})")
        else:
            original_item["accessible"] = False
            original_item["status_code"] = status_code
            results["not_accessible"].append(original_item)
            logger.warning(f"[{idx}/{total}] ✗ {domain} (not accessible)")
    
    return results

def merge_with_log_entry(original_log: Dict, verified_domains: List[Dict]) -> Dict:
    """Merge verification results back into log entry format."""
    updated_log = original_log.copy()
    
    # Count verified vs not verified
    verified_count = sum(1 for d in verified_domains if d.get("accessible", False))
    not_verified_count = len(verified_domains) - verified_count
    
    # Update summary with verification info
    if 'summary' not in updated_log:
        updated_log['summary'] = {}
    
    updated_log['summary']['verification'] = {
        "verified_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_domains_checked": len(verified_domains),
        "accessible": verified_count,
        "not_accessible": not_verified_count
    }
    
    # Add verification details to each domain in details
    if 'details' in updated_log['summary']:
        details = updated_log['summary']['details']
        for verified_domain in verified_domains:
            domain = verified_domain.get("domain", "").lower()
            if domain in details:
                details[domain]['accessible'] = verified_domain.get("accessible", False)
                details[domain]['status_code'] = verified_domain.get("status_code", None)
    
    return updated_log


def save_results(verified_domains: List[Dict], verified_log: Dict):
    """Save verification results to files."""
    try:
        # Save verified domains in original format
        with open("verified_domains.json", 'w') as f:
            json.dump(verified_domains, f, indent=4)
        logger.info(f"Verified domains saved to verified_domains.json ({len(verified_domains)} domains)")
        
        # Save updated log with verification data
        with open("verified_log.json", 'w') as f:
            json.dump([verified_log], f, indent=4)
        logger.info("Verification log saved to verified_log.json")
        
    except Exception as e:
        logger.error(f"Failed to save results: {e}")

def main(verbose: bool = False):
    """Main entry point for domain verification - processes domains.json and log.json."""
    
    # Check if default files exist
    if not os.path.exists(DOMAINS_FILE):
        logger.error(f"File not found: {DOMAINS_FILE}")
        sys.exit(1)
    
    if not os.path.exists(LOG_FILE):
        logger.error(f"File not found: {LOG_FILE}")
        sys.exit(1)
    
    logger.info(f"Loading domains from {DOMAINS_FILE}")
    logger.info(f"Loading log from {LOG_FILE}")
    
    # Load log data
    log_data = load_log_data(LOG_FILE)
    if not log_data:
        logger.error("No log data found")
        sys.exit(1)
    
    original_log = log_data[0]
    
    # Extract domains from log
    domains_from_log = extract_domains_from_log(log_data)
    
    # Load domains.json for additional metadata
    domains_data, _ = load_domains_from_file(DOMAINS_FILE)
    if isinstance(domains_data, list) and domains_data:
        domains_json_list = domains_data
    else:
        domains_json_list = []
    
    total_log_domains = len(domains_from_log)
    logger.info(f"Extracted {total_log_domains} domains from log")
    
    if not domains_from_log:
        logger.error("No domains found in log")
        sys.exit(1)
    
    # Verify each domain
    verified_domains = []
    total = total_log_domains
    
    logger.info(f"Starting verification of {total} domains...\n")
    
    for idx, (domain_lower, domain_info) in enumerate(domains_from_log.items(), 1):
        domain = domain_info["domain"]
        
        # Check format validity
        if not is_valid_domain(domain):
            logger.warning(f"[{idx}/{total}] Invalid format: {domain}")
            continue
        
        # Verify domain exists
        is_accessible, status_code = verify_domain_exists(domain)
        domain_info["accessible"] = is_accessible
        domain_info["status_code"] = status_code
        
        # Find corresponding entry in domains.json to enrich data
        enriched_domain = domain_info.copy()
        for domains_entry in domains_json_list:
            if isinstance(domains_entry, dict) and domains_entry.get("domain", "").lower() == domain_lower:
                # Merge with domains.json data, keeping verification fields
                enriched_domain = {**domains_entry, **domain_info}
                break
        
        verified_domains.append(enriched_domain)
        
        status_emoji = "✓" if is_accessible else "✗"
        status_text = f"({status_code})" if status_code else "(timeout)"
        if is_accessible:
            logger.info(f"[{idx}/{total}] {status_emoji} {domain} {status_text}")
        else:
            logger.warning(f"[{idx}/{total}] {status_emoji} {domain} {status_text}")
    
    # Merge verification results back into log
    verified_log = merge_with_log_entry(original_log, verified_domains)
    
    # Display summary
    accessible_count = sum(1 for d in verified_domains if d.get("accessible", False))
    print("\n" + "="*60)
    print("DOMAIN VERIFICATION SUMMARY")
    print("="*60)
    print(f"Total domains verified: {len(verified_domains)}")
    print(f"Accessible: {accessible_count}")
    print(f"Not accessible: {len(verified_domains) - accessible_count}")
    print("="*60 + "\n")
    
    # Save results
    save_results(verified_domains, verified_log)
    
    logger.info("Domain verification completed!")

if __name__ == "__main__":
    # Check for verbose flag
    verbose = "--verbose" in sys.argv
    main(verbose=verbose)
