# Ultimate GOD

A lightweight, modular OSINT starter toolkit for **Termux and Kali Linux**. It organizes public-source research into case files and JSON reports using Python's standard library.

> **Responsible use:** Use only information that is public or that you are authorized to access. This tool does not bypass logins, access private accounts, scrape private messages, or provide live location tracking. A profile URL responding successfully does not prove that it exists as a real account or belongs to a particular person.

## Install and run

```bash
git clone https://github.com/bikash403078-boop/Ultimate-GOD.git
cd Ultimate-GOD
python -m unittest discover -s tests -v
python main.py
```

## Public URL checks

Run `python main.py` to start the automatic guided workflow directly; there is no separate operations menu. It asks for username, phone/WhatsApp lead, local image path, public social profile URL, name/search terms, and an authorized domain in sequence. Press Enter or type `skip` for unknown fields. It automatically attempts relevant public-source checks and saves one combined JSON report. It records the HTTP response, final URL, page title, and available description metadata when a site permits access.

- `http-success` means the URL returned a successful HTTP response, **not** that an account is authentic.
- `http-error` may mean missing, blocked, or rate-limited.
- `network-error` is inconclusive.
- Some platforms return generic pages, bot checks, or soft 404s; verify results manually.

Checks are limited to ordinary public HTTP(S) requests; no login, bypass, or bulk scraping is performed. Use reasonable frequency and follow each site's rules.

## Local web dashboard

```bash
python webapp.py
```

Open `http://127.0.0.1:8765` on the same device. The server binds to localhost.

## Features

- Guided investigation wizard: name, username, phone lead, social URL, local image, and authorized domain; unknown fields can be skipped\n- Combined JSON report with source links, public search leads, username checks, page extraction, domain intelligence, and local image hash/optional metadata
- Public profile URL candidates and basic public-page checks\n- Optional DuckDuckGo public web search for name/username/keyword leads
- URL/domain parsing\n- Passive domain intelligence using public RDAP, DNS resolution, and certificate-transparency data for authorized domains
- Manually recorded findings with source URLs and confidence labels
- JSON case export
- Local-only web dashboard
- Tests

## Guided investigation\n\nEnter whatever inputs you have in the guided prompts and press Enter or type `skip` for unknown fields. The workflow combines public search attempts, username candidate checks, extraction from a supplied public page, passive domain data for an authorized domain, and local image hashing (optional EXIF support if Pillow is installed). It writes a single JSON report. Phone numbers are stored only as leads; the tool does not identify phone owners or retrieve private WhatsApp data. It does not search for, infer, or display Aadhaar/passport numbers. Government ID verification should use official, consent-based channels. It does not log into social platforms, collect private account history, or scrape behind-login content.\n\n## Passive domain intelligence

Choose **11** in the CLI and enter a domain you own or are authorized to assess. The module queries public RDAP and Certificate Transparency sources and resolves DNS. It does not scan ports, exploit services, or establish that certificate-listed hosts are currently online. Public sources can fail or return incomplete data.

## Current limitations

This is an early-stage organizer. It does **not** provide general web search, reverse-image search, phone-owner lookup, private account data, or identity matching. Public search can be rate-limited or unavailable and does not guarantee comprehensive results. Name leads still require manual verification and careful review of each source.

## Tests

```bash
python -m unittest discover -s tests -v
```

Do not use this tool for harassment, doxxing, stalking, credential theft, or unauthorized access. Public information can still be inaccurate or sensitive.
