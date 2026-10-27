# Ultimate GOD

A lightweight, modular OSINT starter toolkit for **Termux and Kali Linux**. It organizes public-source research into a case file and produces a JSON report. It uses Python's standard library; no third-party packages are required.

> **Responsible use:** Use only information that is public or that you are authorized to access. This tool does not bypass logins, access private accounts, scrape private messages, or provide live location tracking. Search results and profile URLs are leads, not proof that accounts belong to the same person.

## Features

- Guided terminal workflow for names, usernames, phone-number formatting, and URLs
- Public profile URL candidates for selected services
- URL parsing and domain extraction
- Case notes and source/evidence records
- JSON report export
- Local-only web dashboard bound to `127.0.0.1`
- Works on Android Termux and Kali Linux with Python 3

## Install

```bash
git clone https://github.com/bikash403078-boop/Ultimate-GOD.git
cd Ultimate-GOD
python main.py
```

Run the local dashboard instead:

```bash
python webapp.py
```

Then open `http://127.0.0.1:8765` on the same device. Stop with Ctrl+C. The server intentionally binds to localhost, not the public network.

## Files

- `main.py` — interactive CLI
- `osint99/core.py` — case structure and public-source helpers
- `webapp.py` — local dashboard
- `tests/test_core.py` — basic unit tests

## Workflow

1. Create a case.
2. Enter a search lead.
3. Review suggested public-source URLs manually.
4. Add verified findings with source URLs and notes.
5. Export a JSON report.

The program does **not** automatically log into websites or claim that a suggested URL exists. Verify findings at the original source and record uncertainty.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Disclaimer

This is a research organizer, not a magical identity lookup engine. Public data can be outdated, inaccurate, or misleading. Follow applicable law, website terms, privacy rules, and organizational authorization. Do not use it for harassment, doxxing, stalking, credential theft, or unauthorized access.
