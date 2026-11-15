#!/usr/bin/env python3
"""AI OS desktop window (Tkinter, ships with Python on Windows and Linux)."""
import queue
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import aios_core as core

BG, PANEL, FG, MUTED = "#12141a", "#1b1e27", "#e6e8ee", "#8b92a5"
ACCENT, USER, WARN = "#7aa2f7", "#9ece6a", "#e0af68"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI OS")
        self.geometry("860x620")
        self.minsize(540, 380)
        self.configure(bg=BG)

        self.cfg = core.load_config()
        self.events = queue.Queue()
        self.busy = False
        self.agent = core.Agent(
            self.cfg,
            approve=self._approve_from_worker,
            on_event=lambda kind, text: self.events.put(("event", kind, text)),
        )
        self._build()
        self._refresh_status()
        self._say("AI OS", "Hi. Tell me what you want done on this computer. "
                           "I'll ask before I change anything.", ACCENT)
        self.after(100, self._pump)

    # ---- layout ---------------------------------------------------------
    def _build(self):
        top = tk.Frame(self, bg=PANEL)
        top.pack(fill="x")
        tk.Label(top, text="AI OS", bg=PANEL, fg=ACCENT, font=("Segoe UI", 13, "bold")
                 ).pack(side="left", padx=12, pady=8)

        self.mode = tk.StringVar(value=self.cfg["provider"])
        box = ttk.Combobox(top, textvariable=self.mode, width=8, state="readonly",
                           values=("auto", "claude", "ollama"))
        box.pack(side="left", padx=4)
        box.bind("<<ComboboxSelected>>", self._mode_changed)

        self.status = tk.Label(top, text="", bg=PANEL, fg=MUTED, font=("Segoe UI", 9))
        self.status.pack(side="left", padx=10)

        for text, cmd in (("New chat", self._clear), ("Claude key...", self._set_key)):
            tk.Button(top, text=text, command=cmd, bg=PANEL, fg=FG, relief="flat",
                      activebackground=BG, activeforeground=FG
                      ).pack(side="right", padx=6, pady=6)

        self.log = tk.Text(self, bg=BG, fg=FG, wrap="word", relief="flat", padx=14, pady=10,
                           font=("Segoe UI", 11), state="disabled", insertbackground=FG)
        self.log.pack(fill="both", expand=True)
        self.log.tag_config("who", font=("Segoe UI", 9, "bold"))
        self.log.tag_config("muted", foreground=MUTED)

        bottom = tk.Frame(self, bg=PANEL)
        bottom.pack(fill="x")
        self.entry = tk.Entry(bottom, bg=BG, fg=FG, insertbackground=FG, relief="flat",
                              font=("Segoe UI", 12))
        self.entry.pack(side="left", fill="x", expand=True, padx=12, pady=12, ipady=6)
        self.entry.bind("<Return>", lambda e: self._send())
        self.entry.focus_set()
        self.send_btn = tk.Button(bottom, text="Send", command=self._send, bg=ACCENT, fg=BG,
                                  relief="flat", padx=16, font=("Segoe UI", 10, "bold"))
        self.send_btn.pack(side="right", padx=12)

    # ---- helpers --------------------------------------------------------
    def _say(self, who, text, color):
        self.log.configure(state="normal")
        self.log.tag_config(f"c{color}", foreground=color)
        self.log.insert("end", who + "\n", ("who", f"c{color}"))
        self.log.insert("end", text.strip() + "\n\n")
        self.log.configure(state="disabled")
        self.log.see("end")

    def _note(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text.strip() + "\n\n", ("muted",))
        self.log.configure(state="disabled")
        self.log.see("end")

    def _refresh_status(self):
        p = core.resolve_provider(self.cfg)
        self.status.configure(text=f"using {p.name} ({p.model})")

    def _mode_changed(self, _evt=None):
        self.cfg["provider"] = self.mode.get()
        core.save_config(self.cfg)
        self._refresh_status()

    def _clear(self):
        self.agent.reset()
        self._note("New conversation started.")

    def _set_key(self):
        key = simpledialog.askstring("Claude API key", "Paste your Claude API key:",
                                     show="*", parent=self)
        if key and key.strip():
            self.cfg["claude_api_key"] = key.strip()
            core.save_config(self.cfg)
            self._refresh_status()
            self._note("Claude key saved on this computer.")

    # ---- worker <-> UI --------------------------------------------------
    def _approve_from_worker(self, tool, summary):
        done, box = threading.Event(), {"ok": False}
        self.events.put(("approve", summary, done, box))
        done.wait(timeout=300)
        return box["ok"]

    def _send(self):
        text = self.entry.get().strip()
        if not text or self.busy:
            return
        self.entry.delete(0, "end")
        self._say("You", text, USER)
        self.busy = True
        self.send_btn.configure(state="disabled")
        threading.Thread(target=self._worker, args=(text,), daemon=True).start()

    def _worker(self, text):
        try:
            self.events.put(("reply", self.agent.chat(text)))
        except core.ProviderError as e:
            self.events.put(("error", str(e)))
        except Exception as e:  # keep the window alive whatever happens
            self.events.put(("error", f"Unexpected error: {e}"))

    def _finish(self):
        self.busy = False
        self.send_btn.configure(state="normal")
        self.entry.focus_set()

    def _pump(self):
        try:
            while True:
                item = self.events.get_nowait()
                kind = item[0]
                if kind == "event":
                    _, ekind, text = item
                    if ekind == "say":
                        self._say("AI OS", text, ACCENT)
                    elif ekind == "tool":
                        self._note("> " + text.splitlines()[0])
                    else:
                        self._note(f"[{ekind}] {text}")
                elif kind == "approve":
                    _, summary, done, box = item
                    box["ok"] = messagebox.askyesno(
                        "AI OS wants to make a change", summary + "\n\nAllow this?",
                        icon="warning", default="no", parent=self)
                    done.set()
                elif kind == "reply":
                    self._say("AI OS", item[1], ACCENT)
                    self._finish()
                elif kind == "error":
                    self._say("Error", item[1], WARN)
                    self._finish()
        except queue.Empty:
            pass
        self.after(100, self._pump)


if __name__ == "__main__":
    App().mainloop()
