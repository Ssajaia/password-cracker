ZIP Wordlist Tester

Purpose (short): This repository contains an educational ZIP wordlist tester intended only for authorized, defensive, and research use against files you own or have explicit permission to test. It intentionally does not include large/real password lists (e.g. rockyou.txt).

Quick summary

Do not upload rockyou.txt or other real password dumps to this repo.

The code is provided for learning and testing on your own files.

Before publishing publicly, sanitize examples, use a synthetic test wordlist, and include clear responsible-use documentation.

What’s in this repo

crack.py — the ZIP wordlist tester (the script you provided). DO NOT run this against third-party files.

test-wordlist.txt — a tiny, safe, synthetic wordlist (one-line examples). Use this for demonstrations.

EXAMPLES/ — (optional) small generated test zips you create for demos.

README.md (this file)

LICENSE (recommended: MIT) — see license section below.

RESPONSIBLE_USE.md (recommended) — short rules for lawful usage.

Safety & Legal notice — read this first

Authorized use only. Only run this tool against ZIP archives that you own or for which you have explicit, documented permission to test. Unauthorized access to systems or data is illegal in many jurisdictions.

No bundled wordlists. This repository intentionally does not contain rockyou.txt or any other leaked/real password lists. Use test-wordlist.txt to demonstrate functionality.

Limit public distribution. If you plan to publish this repository publicly, consider publishing only a sanitized, non-executable example or pseudocode — or keep the repo private / share on request with vetted researchers.

No warranty / no liability. Use at your own risk (see LICENSE and disclaimer below).

How to create a safe test ZIP (recommended)

Run these commands locally to create a sample ZIP that is password protected with one of the test passwords:

# create a small file
printf "hello-world" > sample.txt
# create a password-protected ZIP (requires zip installed)
zip -P hunter2 sample.zip sample.txt
# the password above is `hunter2` — add that to test-wordlist.txt if you want

Important: Only create and test archives you own.

Usage

Basic usage (example):

python3 crack.py sample.zip

Notes:

The script expects a wordlist file path called rockyou.txt by default. Before publishing, change self.wordlist_path in the script to test-wordlist.txt or accept a command-line flag for a wordlist path.

The script tries Python zipfile first and optionally verifies with 7z if installed.
