"""Interactive CLI for Ultimate GOD."""
from .core import new_case, add_lead, add_finding, username_candidates, url_details, save_json
from .collector import check_public_url, check_username, search_public_web
from .domainintel import investigate_domain


def ask(prompt: str) -> str:
    return input(prompt).strip()


def main() -> None:
    print("\n=== Ultimate GOD | Public-source OSINT ===")
    print("Use only public or authorized information. Checks may be blocked or inconclusive.")
    case = new_case(ask("Case title: ") or "Quick research")
    while True:
        print("\n1) Add name lead  2) Username candidates  3) Phone-format lead")
        print("4) Inspect URL  5) Add sourced finding  6) View case  7) Export JSON")
        print("8) Check public URL  9) Check username candidates  10) Search public web")
        print("11) Passive domain intelligence  12) Extract public page  0) Exit")
        choice = ask("> ")
        try:
            if choice == "1":
                value = ask("Name/search phrase: ")
                if value:
                    add_lead(case, "name", value)
                    print("Saved as a search lead. This app does not yet run a general web search.")
            elif choice == "2":
                value = ask("Username: ")
                for item in username_candidates(value):
                    print(f"- {item['service']}: {item['url']} [candidate, not verified]")
                add_lead(case, "username", value)
            elif choice == "3":
                value = ask("Phone number in international format if known: ")
                if value:
                    add_lead(case, "phone-format-only", value)
                    print("Saved only; no owner lookup or location inference is performed.")
            elif choice == "4":
                print(url_details(ask("URL or domain: ")))
            elif choice == "5":
                title = ask("Finding title: ")
                url = ask("Public source URL: ")
                notes = ask("What did you observe? ")
                confidence = ask("Confidence (unverified/low/medium/high) [unverified]: ") or "unverified"
                add_finding(case, title, url, notes, confidence)
                print("Finding saved.")
            elif choice == "6":
                print(f"Title: {case['title']} | Leads: {len(case['leads'])} | Findings: {len(case['findings'])}")
                for i, item in enumerate(case["leads"], 1):
                    print(f" L{i}. [{item['type']}] {item['value']}")
                for i, item in enumerate(case["findings"], 1):
                    print(f" F{i}. {item['title']} — {item['source_url']} ({item['confidence']})")
            elif choice == "7":
                path = ask("Output file [ultimate_god_case.json]: ") or "ultimate_god_case.json"
                print(f"Exported: {save_json(case, path)}")
            elif choice == "8":
                result = check_public_url(ask("Public URL: "))
                print(result)
                add_finding(case, "Public URL check: " + result["result"], result["final_url"],
                            f"HTTP status: {result['status']}; title: {result['page_title']}; "
                            f"description: {result['description']}; note: {result['note']}", "unverified")
            elif choice == "9":
                username = ask("Username: ")
                results = check_username(username)
                add_lead(case, "username", username)
                for result in results:
                    print(f"\n{result['service']}: {result['url']}")
                    print(f"Result: {result['result']} | HTTP: {result['status']}")
                    print(f"Title: {result['page_title'] or '(none)'}")
                    print(f"Description: {result['description'] or '(none)'}")
                    print(result["note"])
                    add_finding(case, f"{result['service']} public URL check: {result['result']}",
                                result["final_url"], f"HTTP status: {result['status']}; "
                                f"title: {result['page_title']}; description: {result['description']}; "
                                f"note: {result['note']}", "unverified")
            elif choice == "10":
                query = ask("Public web search query (name/username/keywords): ")
                results = search_public_web(query)
                if not results:
                    print("No results parsed. Search may be blocked or have changed format; try manually.")
                for i, item in enumerate(results, 1):
                    print(f"{i}. {item['title']}\n   {item['url']}\n   {item.get('snippet', '')}")
                    add_finding(case, "Public web result: " + item["title"], item["url"],
                                "Search result lead for query: " + query + ". Verify the page and identity manually.",
                                "unverified")
            elif choice == "11":
                domain = ask("Domain you own or are authorized to assess (e.g. example.com): ")
                report = investigate_domain(domain)
                print("\\n=== Passive domain intelligence ===")
                print(f"Domain: {report['domain']} | Collected: {report['collected_at']}")
                print(f"DNS addresses: {report['dns'] or '(none returned)'}")
                print(f"Certificate names ({len(report['certificates'])}):")
                for name in report["certificates"][:100]:
                    print(" - " + name)
                print(f"Registration: {report['registration'] or '(unavailable)'}")
                print(f"Source status: {report['summary']}")
                if report["errors"]:
                    print(f"Source errors: {report['errors']}")
                for source in report["sources"]:
                    add_finding(case, "Domain source: " + source["name"], source["url"],
                                "Status: " + source["status"] + "; domain: " + domain, "unverified")
                path = ask("Save full domain report [ultimate_god_domain_report.json]: ") or "ultimate_god_domain_report.json"
                from pathlib import Path
                import json
                Path(path).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
                print(f"Saved full report: {path}")
            elif choice == "12":
                from .collector import fetch_public_page
                url = ask("Public page URL: ")
                page = fetch_public_page(url)
                print(f"\\nTitle: {page['title'] or '(none)'}")
                print(f"URL: {page['final_url']} | HTTP: {page['status']}")
                print(f"Description: {page['description'] or '(none)'}")
                print(f"\\nExtracted text (up to 12,000 chars):\\n{page['text'] or '(no readable text)'}")
                print(f"\\nLinks found: {len(page['links'])}")
                for link in page["links"][:30]:
                    print(" - " + link)
                add_finding(case, "Public page extracted: " + (page["title"] or page["final_url"]),
                            page["final_url"], "Description: " + page["description"] + "\\nText excerpt: " + page["text"][:2000],
                            "unverified")
            elif choice == "0":
                print("Goodbye. Verify findings at their original sources.")
                break
            else:
                print("Choose one of the listed options.")
        except (ValueError, OSError) as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
