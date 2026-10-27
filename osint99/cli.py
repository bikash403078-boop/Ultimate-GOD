"""Interactive CLI for Ultimate GOD."""
from .core import new_case, add_lead, add_finding, username_candidates, url_details, save_json
from .collector import check_public_url, check_username


def ask(prompt: str) -> str:
    return input(prompt).strip()


def main() -> None:
    print("\n=== Ultimate GOD | Public-source OSINT ===")
    print("Use only public or authorized information. Checks may be blocked or inconclusive.")
    case = new_case(ask("Case title: ") or "Quick research")
    while True:
        print("\n1) Add name lead  2) Username candidates  3) Phone-format lead")
        print("4) Inspect URL  5) Add sourced finding  6) View case  7) Export JSON")
        print("8) Check public URL  9) Check username profile candidates  0) Exit")
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
            elif choice == "0":
                print("Goodbye. Verify findings at their original sources.")
                break
            else:
                print("Choose one of the listed options.")
        except (ValueError, OSError) as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
