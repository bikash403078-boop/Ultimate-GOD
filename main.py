from osint99.wizard import run_guided_investigation

if __name__ == "__main__":
    try:
        run_guided_investigation()
    except (KeyboardInterrupt, EOFError):
        print("\nInvestigation cancelled.")
    except (ValueError, OSError) as exc:
        print(f"Input or file error: {exc}")
