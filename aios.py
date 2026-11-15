#!/usr/bin/env python3
"""AI OS terminal: talk to your computer in plain English.

  python aios.py            chat
  python aios.py ask "..."  one question, then exit
  python aios.py setup      pick Claude / local model, save your API key
  python aios.py status     show which AI is active
"""
import argparse
import getpass
import sys

import aios_core as core


def cli_approve(tool, summary):
    print("\n  AI OS wants to do this:")
    print("    " + summary.replace("\n", "\n    "))
    try:
        return input("  Allow? [y/N] ").strip().lower() in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def cli_event(kind, text):
    if kind == "say":
        print(f"\n{text}")
    elif kind == "tool":
        print("  > " + text.splitlines()[0])
    elif kind in ("denied", "notice"):
        print(f"  [{kind}] {text}")


def show_status(cfg):
    p = core.resolve_provider(cfg)
    print(f"Mode    : {cfg['provider']}  (active: {p.name}, model: {p.model})")
    print(f"Claude  : API key {'set' if core.get_claude_key(cfg) else 'NOT set'}")
    state = "running" if core.ollama_running(cfg) else "not reachable"
    print(f"Ollama  : {state} at {cfg['ollama_url']}")


def setup(cfg):
    print("AI OS setup (press Enter to keep the current value)\n")
    mode = input(f"Which AI? auto / claude / ollama [{cfg['provider']}]: ").strip().lower()
    if mode in ("auto", "claude", "ollama"):
        cfg["provider"] = mode
    elif mode:
        print("  Unknown choice, keeping", cfg["provider"])
    if cfg["provider"] in ("auto", "claude"):
        key = getpass.getpass("Claude API key (hidden): ").strip()
        if key:
            cfg["claude_api_key"] = key
        model = input(f"Claude model [{cfg['claude_model']}]: ").strip()
        if model:
            cfg["claude_model"] = model
    if cfg["provider"] in ("auto", "ollama"):
        model = input(f"Ollama model [{cfg['ollama_model']}]: ").strip()
        if model:
            cfg["ollama_model"] = model
    core.save_config(cfg)
    print(f"\nSaved to {core.config_path()}")


HELP = """Commands:
  /provider auto|claude|ollama   switch AI
  /status                        show which AI is active
  /clear                         forget this conversation
  /exit                          quit"""


def slash(line, agent):
    """Returns True to quit."""
    parts = line.split()
    cmd = parts[0].lower()
    if cmd in ("/exit", "/quit"):
        return True
    if cmd == "/clear":
        agent.reset()
        print("Conversation cleared.")
    elif cmd == "/status":
        show_status(agent.cfg)
    elif cmd == "/provider" and len(parts) == 2 and parts[1] in ("auto", "claude", "ollama"):
        agent.cfg["provider"] = parts[1]
        core.save_config(agent.cfg)
        show_status(agent.cfg)
    else:
        print(HELP)
    return False


def repl(agent):
    print("AI OS - say what you want done. /help for commands, /exit to quit.")
    show_status(agent.cfg)
    while True:
        try:
            line = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not line:
            continue
        if line.startswith("/"):
            if slash(line, agent):
                return
            continue
        try:
            print("\n" + agent.chat(line))
        except core.ProviderError as e:
            print(f"\n[error] {e}\nTry /status, or run: python aios.py setup")


def main():
    ap = argparse.ArgumentParser(description="AI OS terminal")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("setup")
    sub.add_parser("status")
    ask = sub.add_parser("ask")
    ask.add_argument("text", nargs="+")
    args = ap.parse_args()

    cfg = core.load_config()
    if args.cmd == "setup":
        setup(cfg)
        return 0
    if args.cmd == "status":
        show_status(cfg)
        return 0

    agent = core.Agent(cfg, approve=cli_approve, on_event=cli_event)
    if args.cmd == "ask":
        try:
            print(agent.chat(" ".join(args.text)))
        except core.ProviderError as e:
            print(f"[error] {e}", file=sys.stderr)
            return 1
        return 0
    repl(agent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
