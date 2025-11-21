import argparse

from ingest_watcher.bootstrap import IngestWatcherConfig, build_app

def cmd_watch(args: argparse.Namespace) -> int:
    """Watch the root path for changes and ingest the changes."""
    
    config = IngestWatcherConfig(root_path=args.root_path)
    app = build_app(config)

    print(f"Watching {args.root_path} for changes...")
    return 0

def main() -> int:
    """Ingest Watcher main function."""
    
    print("Hello, World!")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
