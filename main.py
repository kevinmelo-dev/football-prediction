from core.fetcher import run_fetch

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "fetch":
        run_fetch()
    else:
        print("Use: python main.py fetch")
