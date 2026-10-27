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

In the CLI, choose **8** to inspect one public URL, **9** to check the five suggested username profile URLs, or **10** to search the public web through DuckDuckGo HTML results. It records the HTTP response, final URL, page title, and available description metadata when a site permits access.

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

- Guided CLI for name, username, phone-format, and URL leads
- Public profile URL candidates and basic public-page checks\n- Optional DuckDuckGo public web search for name/username/keyword leads
- URL/domain parsing\n- Passive domain intelligence using public RDAP, DNS resolution, and certificate-transparency data for authorized domains
- Manually recorded findings with source URLs and confidence labels
- JSON case export
- Local-only web dashboard
- Tests

## Passive domain intelligence

Choose **11** in the CLI and enter a domain you own or are authorized to assess. The module queries public RDAP and Certificate Transparency sources and resolves DNS. It does not scan ports, exploit services, or establish that certificate-listed hosts are currently online. Public sources can fail or return incomplete data.

## Current limitations

This is an early-stage organizer. It does **not** provide general web search, reverse-image search, phone-owner lookup, private account data, or identity matching. Public search can be rate-limited or unavailable and does not guarantee comprehensive results. Name leads still require manual verification and careful review of each source.

## Tests

```bash
python -m unittest discover -s tests -v
```

Do not use this tool for harassment, doxxing, stalking, credential theft, or unauthorized access. Public information can still be inaccurate or sensitive.
