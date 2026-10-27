"""Interactive CLI for Ultimate GOD."""
from .core import new_case, add_lead, add_finding, username_candidates, url_details, save_json


def ask(prompt: str) -> str:
    return input(prompt).strip()


def main() -> None:
    print("\n=== Ultimate GOD | Public-source OSINT ===")
    print("Use only public or authorized information. Suggested URLs are not verified.")
    case = new_case(ask("Case title: ") or "Quick research")
    while True:
        print("\n1) Add name lead  2) Username candidates  3) Phone-format lead")
        print("4) Inspect URL  5) Add sourced finding  6) View case  7) Export JSON  0) Exit")
        choice = ask("> ")
        try:
            if choice == "1":
                value = ask("Name/search phrase: ")
                if value:
                    add_lead(case, "name", value)
                    print("Saved as a search lead; it is not an identity confirmation.")
            elif choice == "2":
                value = ask("Username (without @ is fine): ")
                candidates = username_candidates(value)
                add_lead(case, "username", value)
                for item in candidates:
                    print(f"- {item['service']}: {item['url']} [not verified]")
            elif choice == "3":
                value = ask("Phone number in international format if known: ")
                if value:
                    add_lead(case, "phone-format-only", value)
                    print("Saved only. No owner lookup or location inference is performed.")
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
            elif choice == "0":
                print("Goodbye. Verify findings at their original sources.")
                break
            else:
                print("Choose one of the listed options.")
        except (ValueError, OSError) as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
