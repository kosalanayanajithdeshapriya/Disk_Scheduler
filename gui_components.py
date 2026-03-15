"""
GUI Components — Disk Scheduling Visualizer
Professional Edition

Features:
  • Live input validation with green/red border feedback
  • ResultsDisplay: ranked summary table + scrollable detail text
  • VisualizationPanel: step-by-step head animation + Export Chart button
  • ComparisonChart: 3 subplots (bar, line, horizontal efficiency bar)
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ─────────────────────────────────────────────────────────────────────────────
#  Cross-platform font helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ui_font(size=10, bold=False):
    if sys.platform == "win32":   family = "Segoe UI"
    elif sys.platform == "darwin": family = "SF Pro Display"
    else:                          family = "DejaVu Sans"
    return (family, size, "bold" if bold else "normal")


def _mono_font(size=9, bold=False):
    if sys.platform == "win32":   family = "Consolas"
    elif sys.platform == "darwin": family = "Menlo"
    else:                          family = "DejaVu Sans Mono"
    return (family, size, "bold" if bold else "normal")


# ─────────────────────────────────────────────────────────────────────────────
#  Matplotlib & UI Theme: "Abyss" Professional Edition
# ─────────────────────────────────────────────────────────────────────────────

ABYSS_THEME = {
    "bg_root":      "#0A0C10",  # Darkest slate
    "bg_sidebar":   "#11141D",  # Sidebar depth
    "bg_card":      "#161B22",  # Card surface
    "bg_input":     "#1C2128",  # Input backdrop
    "bg_hover":     "#21262D",  # Interaction state
    "accent_blue":  "#58A6FF",  # Electric Blue (Primary)
    "accent_green": "#3FB950",  # Success Neon
    "accent_orange": "#F78166", # Coral warning
    "accent_red":    "#F85149", # Error Crimson
    "accent_purple": "#BC8CFF", # Look/Compare accent
    "text_primary":  "#E6EDF3",
    "text_secondary": "#8B949E",
    "text_muted":    "#484F58",
    "border":        "#30363D",
    "border_glow":   "rgba(88, 166, 255, 0.3)",
}

DARK_FIG  = ABYSS_THEME["bg_root"]
DARK_AXES = ABYSS_THEME["bg_card"]
DARK_EDGE = ABYSS_THEME["border"]
DARK_TEXT = ABYSS_THEME["text_primary"]
DARK_TICK = ABYSS_THEME["text_secondary"]
DARK_GRID = "#21262D"
DARK_LEG  = ABYSS_THEME["bg_sidebar"]

ALGO_COLOURS = {
    "FCFS":   ABYSS_THEME["accent_blue"],
    "SSTF":   "#D29922", # Golden rod
    "SCAN":   ABYSS_THEME["accent_green"],
    "C-SCAN": ABYSS_THEME["accent_orange"],
    "C-LOOK": ABYSS_THEME["accent_purple"],
}


def _style_axes(ax):
    ax.set_facecolor(DARK_AXES)
    ax.tick_params(colors=DARK_TICK, labelsize=9)
    ax.xaxis.label.set_color(DARK_TEXT)
    ax.yaxis.label.set_color(DARK_TEXT)
    ax.title.set_color(DARK_TEXT)
    ax.grid(color=DARK_GRID, linestyle="--", alpha=0.4, zorder=0)
    for spine in ax.spines.values():
        spine.set_edgecolor(DARK_EDGE)


# ─────────────────────────────────────────────────────────────────────────────
#  Shared widget builders
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
#  Modern Canvas Components (Rounded, Glass, Glossy)
# ─────────────────────────────────────────────────────────────────────────────

class ModernCard(tk.Frame):
    """A standard Frame with custom styling that avoids LabelFrame layout issues."""
    def __init__(self, parent, title="", theme=ABYSS_THEME, padding=16, **kwargs):
        super().__init__(parent, bg=theme["bg_card"], bd=1, relief="flat", 
                         highlightthickness=1, highlightbackground=theme["border"], **kwargs)
        self.theme = theme
        
        if title:
            self.header = tk.Label(self, text=title.upper(), font=_ui_font(9, bold=True),
                                   bg=theme["bg_card"], fg=theme["accent_blue"], pady=8)
            self.header.pack(fill="x", padx=20, anchor="w")
            
        self.content_frame = tk.Frame(self, bg=theme["bg_card"], padx=padding, pady=padding//2)
        self.content_frame.pack(fill="both", expand=True)


def _make_card(parent, title, theme):
    """Factory that returns a styled LabelFrame card."""
    return ModernCard(parent, title=title, theme=theme)


def _entry(parent, theme, width=50):
    e = tk.Entry(
        parent, width=width,
        font=_ui_font(10),
        bg=theme["bg_input"],
        fg=theme["text_primary"],
        insertbackground=theme["text_primary"],
        selectbackground=theme["accent_blue"],
        relief="flat", bd=0,
        highlightthickness=1,
        highlightbackground=theme["border"],
        highlightcolor=theme["accent_blue"],
    )
    return e


def _label(parent, text, theme, bold=False, secondary=False):
    color = theme["text_secondary"] if secondary else theme["text_primary"]
    return tk.Label(parent, text=text, font=_ui_font(10, bold=bold),
                    bg=theme["bg_card"], fg=color)


# ─────────────────────────────────────────────────────────────────────────────
#  InputFrame  –  live validation indicators
# ─────────────────────────────────────────────────────────────────────────────

class InputFrame:
    """Input parameters panel with live validation border feedback."""

    def __init__(self, parent, theme: dict):
        self.theme = theme
        self.card = _make_card(parent, "Input Parameters", theme)
        self.frame = self.card.content_frame
        self.card.pack(fill="both", expand=True, padx=4, pady=4)
        self._create_widgets()

    def _create_widgets(self):
        th = self.theme
        PAD = {"pady": 5, "padx": 10}
        
        # ── Hint ───────────────────────────────────────────────────
        tk.Label(
            self.frame,
            text=" Fill in the parameters below, then press  ⚡ Run All  [F5]",
            font=_ui_font(9),
            bg=th["bg_card"], fg=th["text_secondary"], anchor="w"
        ).pack(fill="x", **PAD)

        # ── Request Queue (Full Width) ──────────────────────────
        q_frame = tk.Frame(self.frame, bg=th["bg_card"])
        q_frame.pack(fill="x", **PAD)
        _label(q_frame, "Request Queue (comma-separated):", th, secondary=True).pack(anchor="w", pady=(0, 4))
        self.request_entry = _entry(q_frame, th)
        self.request_entry.pack(fill="x", ipady=8)

        # ── Parameters Grid ───────────────────────────────────────
        grid_f = tk.Frame(self.frame, bg=th["bg_card"])
        grid_f.pack(fill="x", **PAD)
        
        # Head Position
        h_col = tk.Frame(grid_f, bg=th["bg_card"])
        h_col.pack(side="left", expand=True, fill="x", padx=(0, 10))
        _label(h_col, "Initial Head Position:", th, secondary=True).pack(anchor="w", pady=(0, 4))
        self.head_entry = _entry(h_col, th)
        self.head_entry.pack(fill="x", ipady=8)
        
        # Disk Size
        s_col = tk.Frame(grid_f, bg=th["bg_card"])
        s_col.pack(side="left", expand=True, fill="x", padx=10)
        _label(s_col, "Disk Capacity (cyl):", th, secondary=True).pack(anchor="w", pady=(0, 4))
        self.disk_size_entry = _entry(s_col, th)
        self.disk_size_entry.pack(fill="x", ipady=8)

        # Direction
        d_col = tk.Frame(grid_f, bg=th["bg_card"])
        d_col.pack(side="left", expand=True, fill="x", padx=(10, 0))
        _label(d_col, "Scan Direction:", th, secondary=True).pack(anchor="w", pady=(0, 4))
        self.direction_var = tk.StringVar(value="right")
        self.dir_combo = ttk.Combobox(d_col, textvariable=self.direction_var, 
                                      values=["right", "left"], state="readonly", 
                                      style="Dark.TCombobox", height=10)
        self.dir_combo.pack(fill="x", ipady=4)

        # Bindings
        self.request_entry.bind("<FocusOut>", self._validate_requests)
        self.request_entry.bind("<FocusIn>",  lambda e: self._reset_border(self.request_entry))
        self.head_entry.bind("<FocusOut>", self._validate_head)
        self.head_entry.bind("<FocusIn>",  lambda e: self._reset_border(self.head_entry))
        self.disk_size_entry.bind("<FocusOut>", self._validate_disk_size)
        self.disk_size_entry.bind("<FocusIn>",  lambda e: self._reset_border(self.disk_size_entry))

    # ── validation helpers ─────────────────────────────────────────────
    def _reset_border(self, entry):
        entry.config(highlightbackground=self.theme["border"],
                     highlightcolor=self.theme["accent_blue"])

    def _mark_ok(self, entry):
        entry.config(highlightbackground=self.theme["accent_green"],
                     highlightcolor=self.theme["accent_green"])

    def _mark_err(self, entry):
        entry.config(highlightbackground=self.theme["accent_red"],
                     highlightcolor=self.theme["accent_red"])

    def _validate_requests(self, _event=None):
        val = self.request_entry.get()
        try:
            items = [int(x.strip()) for x in val.split(",") if x.strip()]
            if items:
                self._mark_ok(self.request_entry)
            else:
                self._mark_err(self.request_entry)
        except ValueError:
            self._mark_err(self.request_entry)

    def _validate_head(self, _event=None):
        try:
            int(self.head_entry.get())
            self._mark_ok(self.head_entry)
        except ValueError:
            self._mark_err(self.head_entry)

    def _validate_disk_size(self, _event=None):
        try:
            v = int(self.disk_size_entry.get())
            if v > 0:
                self._mark_ok(self.disk_size_entry)
            else:
                self._mark_err(self.disk_size_entry)
        except ValueError:
            self._mark_err(self.disk_size_entry)

    def get_values(self):
        return {
            "requests":  self.request_entry.get(),
            "head":      self.head_entry.get(),
            "disk_size": self.disk_size_entry.get(),
            "direction": self.direction_var.get(),
        }

    def clear(self):
        for e in (self.request_entry, self.head_entry, self.disk_size_entry):
            e.delete(0, tk.END)
            self._reset_border(e)
        self.direction_var.set("right")


# ─────────────────────────────────────────────────────────────────────────────
#  ResultsDisplay  –  summary table + tabbed details panel
# ─────────────────────────────────────────────────────────────────────────────

class ResultsDisplay:
    """
    Two-section panel:
      Top  → ranked summary table (canvas-drawn rows)
      Body → ttk.Notebook with 3 tabs:
               1. 📊 Per Algorithm  – metric cards, one per algo
               2. 📋 Summary        – key/value input params + stats
               3. 💡 Recommendation – highlighted winner card
    """

    MEDAL = {0: "🥇", 1: "🥈", 2: "🥉", 3: " 4.", 4: " 5."}

    def __init__(self, parent, theme: dict):
        self.theme = theme
        self.card = _make_card(parent, "Algorithm Results & Comparison", theme)
        self.frame = self.card.content_frame 
        # Pack the card itself into row3
        self.card.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        self._results_cache: dict = {}
        self._inputs_cache:  dict = {}
        self._create_widgets()

    def _create_widgets(self):
        th = self.theme

        # ── Ranking table ───────────────────────────────────────────
        self._table_outer = tk.Frame(
            self.frame, bg=th["bg_input"],
            highlightbackground=th["border"], highlightthickness=1,
        )
        self._table_outer.pack(fill="x", pady=(0, 6))

        hdr = tk.Frame(self._table_outer, bg=th["bg_sidebar"])
        hdr.pack(fill="x")
        for col, w in [("RANK", 6), ("ALGORITHM", 14), ("SEEK COUNT", 14),
                       ("AVG SEEK", 12), ("STATUS", 14)]:
            tk.Label(
                hdr, text=col, width=w,
                font=_ui_font(8, bold=True),
                bg=th["bg_sidebar"], fg=th["text_secondary"],
                anchor="center", pady=10,
            ).pack(side="left", padx=2)

        self._table_body = tk.Frame(self._table_outer, bg=th["bg_input"])
        self._table_body.pack(fill="x")
        self._show_table_placeholder()

        # ── Tabbed panel ────────────────────────────────────────────
        self._notebook = ttk.Notebook(self.frame, style="Dark.TNotebook")
        self._notebook.pack(fill="both", expand=True, pady=(0, 2))

        # Tab 1 – Per Algorithm
        self._tab_algo = tk.Frame(self._notebook, bg=th["bg_card"])
        self._notebook.add(self._tab_algo, text="  📊 Per Algorithm  ")

        # Tab 2 – Summary
        self._tab_summary = tk.Frame(self._notebook, bg=th["bg_card"])
        self._notebook.add(self._tab_summary, text="  📋 Summary  ")

        # Tab 3 – Recommendation
        self._tab_rec = tk.Frame(self._notebook, bg=th["bg_card"])
        self._notebook.add(self._tab_rec, text="  💡 Recommendation  ")

        self._show_tab_placeholder()

    # ── Placeholder helpers ────────────────────────────────────────────

    def _show_table_placeholder(self):
        for w in self._table_body.winfo_children():
            w.destroy()
        tk.Label(
            self._table_body,
            text="  Run all algorithms to see ranked comparison  ",
            font=_ui_font(9), pady=10,
            bg=self.theme["bg_input"], fg=self.theme["text_muted"],
        ).pack()

    def _show_tab_placeholder(self):
        for tab in (self._tab_algo, self._tab_summary, self._tab_rec):
            for w in tab.winfo_children():
                w.destroy()
        th = self.theme
        for tab in (self._tab_algo, self._tab_summary, self._tab_rec):
            tk.Label(
                tab,
                text="\n\n\n   No results yet.\n\n"
                     "   Enter parameters above and click  ⚡ Run All [F5]  to begin.\n",
                font=_ui_font(10),
                bg=th["bg_card"], fg=th["text_muted"],
                justify="left",
            ).pack(expand=True, fill="both", padx=20, pady=30)

    # ── Table population ───────────────────────────────────────────────

    def _populate_table(self, results: dict):
        th = self.theme
        for w in self._table_body.winfo_children():
            w.destroy()

        sorted_res = sorted(results.items(), key=lambda x: x[1]["seek_count"])
        best_seek  = sorted_res[0][1]["seek_count"]

        for rank, (name, res) in enumerate(sorted_res):
            is_best  = (rank == 0)
            row_bg   = th["bg_card"] if is_best else th["bg_input"]
            row_fg   = ALGO_COLOURS.get(name, th["text_primary"])
            medal    = self.MEDAL.get(rank, "")
            status   = "★ BEST" if is_best else f"+{res['seek_count'] - best_seek} cyl"
            st_color = th["accent_green"] if is_best else th["text_muted"]

            row = tk.Frame(self._table_body, bg=row_bg,
                           highlightbackground=th["border"], highlightthickness=1)
            row.pack(fill="x", pady=1)

            for text, w, color in [
                (medal,                        6,  th["text_primary"]),
                (name,                         14, row_fg),
                (f"{res['seek_count']} cyl",   14, th["text_primary"]),
                (f"{res['avg_seek_time']:.1f}", 12, th["accent_orange"]),
                (status,                        14, st_color),
            ]:
                tk.Label(
                    row, text=text, width=w,
                    font=_ui_font(9, bold=is_best),
                    bg=row_bg, fg=color,
                    anchor="center", pady=6,
                ).pack(side="left", padx=2)

    # ── Tab 1: Per Algorithm cards ─────────────────────────────────────

    def _populate_algo_tab(self, results: dict):
        th = self.theme
        for w in self._tab_algo.winfo_children():
            w.destroy()

        sorted_res = sorted(results.items(), key=lambda x: x[1]["seek_count"])
        best_seek  = sorted_res[0][1]["seek_count"]
        num_algos  = len(sorted_res)

        # All cards in one row (use a sub-frame for grid isolation)
        cards_grid_f = tk.Frame(self._tab_algo, bg=th["bg_card"])
        cards_grid_f.pack(fill="both", expand=True, padx=10, pady=10)

        for idx, (name, res) in enumerate(sorted_res):
            is_best = (res["seek_count"] == best_seek)
            colour  = ALGO_COLOURS.get(name, th["accent_blue"])

            card_outer = tk.Frame(
                cards_grid_f,
                bg=colour if is_best else th["border"],
                padx=2 if is_best else 1,
                pady=2 if is_best else 1,
            )
            card_outer.pack(side="left", padx=6, pady=6, fill="both", expand=True)

            card = tk.Frame(card_outer, bg=th["bg_input"], padx=10, pady=8)
            card.pack(fill="both", expand=True)

            # Hover effect
            def _enter(e, c=card):
                c.config(bg=th["bg_hover"])
                for child in c.winfo_children():
                    try:
                        child.config(bg=th["bg_hover"])
                        for sub in child.winfo_children():
                            try: sub.config(bg=th["bg_hover"])
                            except Exception: pass
                    except Exception: pass
            def _leave(e, c=card):
                c.config(bg=th["bg_input"])
                for child in c.winfo_children():
                    try:
                        child.config(bg=th["bg_input"])
                        for sub in child.winfo_children():
                            try: sub.config(bg=th["bg_input"])
                            except Exception: pass
                    except Exception: pass
            card.bind("<Enter>", _enter)
            card.bind("<Leave>", _leave)

            # ── Top: medal + name badge ──────────────
            top_row = tk.Frame(card, bg=th["bg_input"])
            top_row.pack(fill="x", pady=(0, 4))

            medal_txt = self.MEDAL.get(idx, "")
            tk.Label(top_row, text=medal_txt,
                     font=_ui_font(11), bg=th["bg_input"],
                     fg=th["text_primary"]).pack(side="left", padx=(0, 4))

            tk.Label(
                top_row, text=f" {name} ",
                font=_ui_font(10, bold=True),
                bg=colour, fg="white",
                padx=6, pady=2,
            ).pack(side="left")

            if is_best:
                tk.Label(
                    top_row, text="★ BEST",
                    font=_ui_font(8, bold=True),
                    bg=th["accent_green"], fg="white",
                    padx=4, pady=2,
                ).pack(side="right")

            # ── Divider ───────────────────────────────
            tk.Frame(card, bg=colour, height=2).pack(fill="x", pady=(2, 6))

            # ── Big seek number ───────────────────────
            tk.Label(
                card,
                text=f"{res['seek_count']}",
                font=_ui_font(22, bold=True),
                bg=th["bg_input"], fg=colour,
            ).pack()
            tk.Label(
                card, text="cylinders",
                font=_ui_font(7),
                bg=th["bg_input"], fg=th["text_muted"],
            ).pack(pady=(0, 4))

            # ── Metrics ───────────────────────────────
            for label, value in [
                ("Avg Seek",  f"{res['avg_seek_time']:.1f} cyl/req"),
                ("Steps",     f"{len(res['sequence'])}"),
            ]:
                mf = tk.Frame(card, bg=th["bg_input"])
                mf.pack(fill="x", pady=1)
                tk.Label(mf, text=label + ":",
                         font=_ui_font(7), bg=th["bg_input"],
                         fg=th["text_secondary"], anchor="w").pack(side="left")
                tk.Label(mf, text=value,
                         font=_ui_font(7, bold=True), bg=th["bg_input"],
                         fg=th["text_primary"], anchor="e").pack(side="right")

    # ── Tab 2: Summary ─────────────────────────────────────────────────

    def _populate_summary_tab(self, results: dict, inputs: dict):
        th = self.theme
        for w in self._tab_summary.winfo_children():
            w.destroy()

        sorted_res = sorted(results.items(), key=lambda x: x[1]["seek_count"])
        best_name  = sorted_res[0][0]
        worst_name = sorted_res[-1][0]
        best_seek  = sorted_res[0][1]["seek_count"]
        worst_seek = sorted_res[-1][1]["seek_count"]
        avg_seek   = sum(r["seek_count"] for r in results.values()) / len(results)

        outer = tk.Frame(self._tab_summary, bg=th["bg_card"])
        outer.pack(fill="both", expand=True, padx=20, pady=16)

        left_col  = tk.Frame(outer, bg=th["bg_card"])
        right_col = tk.Frame(outer, bg=th["bg_card"])
        left_col.pack(side="left",  fill="both", expand=True, padx=(0, 12))
        right_col.pack(side="right", fill="both", expand=True, padx=(12, 0))

        def _section(parent, title, rows):
            tk.Label(
                parent, text=title,
                font=_ui_font(10, bold=True),
                bg=th["bg_card"], fg=th["accent_blue"],
            ).pack(anchor="w", pady=(0, 6))
            box = tk.Frame(parent, bg=th["bg_input"],
                           highlightbackground=th["border"],
                           highlightthickness=1)
            box.pack(fill="x", pady=(0, 14))
            for label, value, vc in rows:
                r = tk.Frame(box, bg=th["bg_input"])
                r.pack(fill="x", padx=12, pady=5)
                tk.Label(r, text=label,
                         font=_ui_font(9), bg=th["bg_input"],
                         fg=th["text_secondary"], anchor="w").pack(side="left")
                tk.Label(r, text=value,
                         font=_ui_font(9, bold=True), bg=th["bg_input"],
                         fg=vc, anchor="e").pack(side="right")
                sep = tk.Frame(box, bg=th["border"], height=1)
                sep.pack(fill="x", padx=8)

        req_list = inputs.get("requests", [])
        req_str  = ", ".join(str(r) for r in req_list) if req_list else "—"

        _section(left_col, "📥 Input Parameters", [
            ("Request Queue",    req_str,                                   th["text_primary"]),
            ("Head Position",    str(inputs.get("head_start", "—")),        th["accent_blue"]),
            ("Disk Size",        f"{inputs.get('disk_size', '—')} cyl",     th["text_primary"]),
            ("Direction",        str(inputs.get("direction", "—")).upper(), th["accent_orange"]),
            ("Queue Length",     str(len(req_list)),                        th["text_secondary"]),
        ])

        _section(right_col, "📊 Statistical Summary", [
            ("Best Algorithm",   best_name,            th["accent_green"]),
            ("Best Seek Count",  f"{best_seek} cyl",   th["accent_green"]),
            ("Worst Algorithm",  worst_name,            th["accent_red"]),
            ("Worst Seek Count", f"{worst_seek} cyl",  th["accent_red"]),
            ("Average Seek",     f"{avg_seek:.1f} cyl", th["accent_orange"]),
            ("Perf. Range",      f"{worst_seek - best_seek} cyl", th["text_secondary"]),
        ])

    # ── Tab 3: Recommendation ──────────────────────────────────────────

    def _populate_recommendation_tab(self, results: dict):
        th = self.theme
        for w in self._tab_rec.winfo_children():
            w.destroy()

        sorted_res  = sorted(results.items(), key=lambda x: x[1]["seek_count"])
        best_name   = sorted_res[0][0]
        best_res    = sorted_res[0][1]
        best_colour = ALGO_COLOURS.get(best_name, th["accent_green"])
        savings     = sorted_res[-1][1]["seek_count"] - best_res["seek_count"]

        outer = tk.Frame(self._tab_rec, bg=th["bg_card"])
        outer.pack(fill="both", expand=True, padx=30, pady=30)

        # Winner banner
        banner = tk.Frame(outer, bg=best_colour, padx=3, pady=3)
        banner.pack(fill="x", pady=(0, 20))
        inner_banner = tk.Frame(banner, bg=th["bg_card"], padx=20, pady=18)
        inner_banner.pack(fill="x")

        tk.Label(
            inner_banner,
            text="🏆  RECOMMENDED ALGORITHM",
            font=_ui_font(9, bold=True),
            bg=th["bg_card"], fg=th["text_muted"],
        ).pack(anchor="w")

        tk.Label(
            inner_banner,
            text=f"  ★  {best_name}",
            font=_ui_font(32, bold=True),
            bg=th["bg_card"], fg=best_colour,
        ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            inner_banner,
            text=f"Lowest total seek count: {best_res['seek_count']} cylinders",
            font=_ui_font(11),
            bg=th["bg_card"], fg=th["text_secondary"],
        ).pack(anchor="w", pady=(2, 0))

        # Insight cards row
        insights_row = tk.Frame(outer, bg=th["bg_card"])
        insights_row.pack(fill="x", pady=(0, 14))

        insights = [
            ("Avg per Request", f"{best_res['avg_seek_time']:.2f} cyl", best_colour),
            ("Head Movements",  f"{len(best_res['sequence'])} steps",   th["accent_blue"]),
            ("Saves vs Worst",  f"{savings} cyl",                       th["accent_green"]),
        ]
        for label, value, color in insights:
            card = tk.Frame(insights_row, bg=th["bg_input"],
                            highlightbackground=th["border"],
                            highlightthickness=1)
            card.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(card, text=value, font=_ui_font(18, bold=True),
                     bg=th["bg_input"], fg=color, pady=6).pack()
            tk.Label(card, text=label, font=_ui_font(8),
                     bg=th["bg_input"], fg=th["text_muted"], pady=4).pack()

        # Recommendation text
        rec_box = tk.Frame(outer, bg=th["bg_input"],
                           highlightbackground=best_colour,
                           highlightthickness=2)
        rec_box.pack(fill="x", pady=(6, 0))
        tk.Label(
            rec_box,
            text=f"💡  Use {best_name} algorithm for optimal disk performance!\n"
                 f"    It achieves the minimum seek count of {best_res['seek_count']} cylinders,\n"
                 f"    saving up to {savings} cylinders compared to the worst-performing algorithm.",
            font=_ui_font(10),
            bg=th["bg_input"], fg=th["text_primary"],
            justify="left", padx=18, pady=14,
        ).pack(anchor="w")

    # ── Public API ─────────────────────────────────────────────────────

    def display_text(self, text: str = "", results: dict = None,
                     inputs: dict = None):
        """Populate all 3 tabs from results dict."""
        if not results:
            return
        self._results_cache = results
        self._inputs_cache  = inputs or {}

        # Resize card to accommodate new data
        self._populate_table(results)
        self._populate_algo_tab(results)
        self._populate_summary_tab(results, self._inputs_cache)
        self._populate_recommendation_tab(results)
        self._notebook.select(0)

    def clear(self):
        self._results_cache = {}
        self._inputs_cache  = {}
        self._show_table_placeholder()
        self._show_tab_placeholder()


# ─────────────────────────────────────────────────────────────────────────────
#  VisualizationPanel  –  head-movement chart + step animation + export
# ─────────────────────────────────────────────────────────────────────────────

class VisualizationPanel:
    """Chart panel with step-by-step animation and export-chart button."""

    def __init__(self, parent, theme: dict):
        self.theme          = theme
        self.current_canvas = None
        self.current_fig    = None
        self._anim_id       = None
        self._anim_step     = 0
        self._anim_seq      = []
        self._anim_dot      = None
        self._anim_ax       = None
        self.card           = _make_card(parent, "Head Movement Visualization", theme)
        self.frame          = self.card.content_frame
        # Pack the card itself into row3
        self.card.pack(side="right", fill="both", expand=True, padx=4, pady=4)
        self._create_widgets()

    def _create_widgets(self):
        th = self.theme

        # Control row
        ctrl = tk.Frame(self.frame, bg=th["bg_card"])
        ctrl.pack(pady=(0, 6), fill="x")

        tk.Label(ctrl, text="Algorithm:", font=_ui_font(10),
                 bg=th["bg_card"], fg=th["text_secondary"]).pack(side="left", padx=(0, 8))

        self.algo_var = tk.StringVar(value="FCFS")
        self.algo_combo = ttk.Combobox(
            ctrl, textvariable=self.algo_var,
            values=["FCFS", "SSTF", "SCAN", "C-SCAN", "C-LOOK"],
            state="readonly", width=12,
        )
        self.algo_combo.pack(side="left")

        # Animate button
        self._anim_btn = tk.Button(
            ctrl, text="▶  Animate",
            font=_ui_font(9, bold=True),
            bg=th["accent_blue"], fg="white",
            activebackground="#3A7AE8", activeforeground="white",
            relief="flat", padx=10, pady=4,
            cursor="hand2",
            command=self._start_animation,
            state="disabled",
        )
        self._anim_btn.pack(side="left", padx=12)

        # Export button
        self._export_btn = tk.Button(
            ctrl, text="💾  Export Chart",
            font=_ui_font(9, bold=True),
            bg=th["bg_input"], fg=th["text_secondary"],
            activebackground=th["bg_hover"], activeforeground=th["text_primary"],
            relief="flat", padx=10, pady=4,
            cursor="hand2",
            command=self._export_chart,
            state="disabled",
        )
        self._export_btn.pack(side="left")

        # Canvas area
        self.canvas_frame = tk.Frame(self.frame, bg=th["bg_card"])
        self.canvas_frame.pack(fill="both", expand=True)

        self._show_placeholder()

    def _show_placeholder(self):
        lbl = tk.Label(
            self.canvas_frame,
            text="📊  Calculate algorithms, then press  📊 Visualize  [F6]",
            font=_ui_font(10),
            bg=self.theme["bg_card"], fg=self.theme["text_muted"],
        )
        lbl.pack(fill="both", expand=True, pady=60)

    def _clear_canvas(self):
        self._stop_animation()
        for w in self.canvas_frame.winfo_children():
            w.destroy()
        if self.current_fig is not None:
            plt.close(self.current_fig)
            self.current_fig = None
        self.current_canvas = None

    # ── Visualize ──────────────────────────────────────────────────────

    def visualize(self, algo_name: str, result: dict, head_start: int, disk_size: int = 200):
        self._clear_canvas()
        th       = self.theme
        sequence = result["sequence"]
        y_pos    = list(range(len(sequence)))  # Steps are on Y axis (vertical)

        # "Abyss" High-Contrast Dark Theme Colors
        # Using a vibrant accent for the path to POP on dark
        path_colour = th["accent_blue"]
        dot_colour  = "#FFFFFF"
        
        fig = Figure(figsize=(6.4, 4.8), dpi=100, facecolor=DARK_FIG)
        ax  = fig.add_subplot(111)
        
        # Style the axes
        ax.set_facecolor(DARK_AXES)
        ax.tick_params(colors=DARK_TICK, labelsize=9)
        
        # Border/Spines styling
        for spine in ax.spines.values():
            spine.set_edgecolor(DARK_EDGE)
            spine.set_linewidth(1.2)
        
        # Grid settings - essential for professional look
        ax.grid(color=DARK_GRID, linestyle="--", alpha=0.3, zorder=0)
        
        # Move cylinder axis to top (Lecture Slide style)
        ax.xaxis.set_label_position('top')
        ax.xaxis.set_ticks_position('top')
        
        # Draw the path with arrows
        for i in range(len(sequence) - 1):
            x1, x2 = sequence[i], sequence[i+1]
            y1, y2 = y_pos[i], y_pos[i+1]
            
            # Draw line segment
            ax.plot([x1, x2], [y1, y2], color=path_colour, linewidth=2, zorder=4, alpha=0.85)
            
            # Add micro-arrows for movement direction
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            # Use small offset to position arrow head
            scale = 0.08
            dx = (x2 - x1) * scale
            dy = (y2 - y1) * scale
            ax.annotate("", xy=(mid_x + dx, mid_y + dy), xytext=(mid_x, mid_y),
                        arrowprops=dict(arrowstyle="-|>", color=path_colour, lw=1.2, 
                                        mutation_scale=12, alpha=0.9), zorder=5)

        # Markers at each request
        ax.scatter(sequence, y_pos, color=path_colour, s=40, zorder=6, 
                   edgecolors=dot_colour, linewidths=1.2)

        # Labels for cylinder numbers at the top
        # We ensure labels have high contrast (DARK_TEXT)
        ticks = sorted(list(set([0, disk_size - 1] + sequence)))
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticks, rotation=0, fontsize=8, color=DARK_TEXT)

        # Set labels with proper colors and padding
        ax.set_xlabel("Cylinder Number", fontsize=10, fontweight="bold", labelpad=15, color=DARK_TEXT)
        ax.set_ylabel("Service Sequence (Top → Bottom)", fontsize=10, fontweight="bold", labelpad=10, color=DARK_TEXT)
        
        ax.set_title(
            f"{algo_name.upper()}   •   Total Head Movement: {result['seek_count']} cyl",
            fontsize=11, fontweight="bold", pad=30, color=th["accent_blue"]
        )

        # Limits and Inversion
        ax.set_xlim(-5, disk_size + 5)
        ax.set_ylim(-0.8, len(sequence) - 0.2)
        ax.invert_yaxis() # Step 0 at top

        # Show step numbers on y-axis for "Detailed Professional" feel
        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"S-{i}" for i in y_pos], fontsize=7, color=DARK_TICK)

        fig.tight_layout(pad=2.0)

        # Animation dot
        self._anim_dot, = ax.plot([], [], "o",
                                   color=dot_colour, markersize=10,
                                   markeredgecolor=th["accent_green"], markeredgewidth=2,
                                   zorder=10)

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()

        toolbar_frame = tk.Frame(self.canvas_frame, bg=DARK_FIG)
        toolbar_frame.pack(side="bottom", fill="x")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.config(bg=DARK_FIG)
        for child in toolbar.winfo_children():
            try:
                child.config(bg=DARK_FIG, fg=DARK_TEXT, activebackground=self.theme["bg_hover"])
            except Exception:
                pass
        toolbar.update()

        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        self.current_canvas = canvas
        self.current_fig    = fig
        self._anim_seq      = sequence
        self._anim_ax       = ax

        # Enable buttons
        self._anim_btn.config(state="normal")
        self._export_btn.config(state="normal")

    # ── Step animation ─────────────────────────────────────────────────

    def _start_animation(self):
        if not self._anim_seq or self._anim_ax is None:
            return
        self._stop_animation()
        self._anim_step = 0
        self._anim_btn.config(text="⏹  Stop", command=self._stop_animation)
        self._animate_step()

    def _animate_step(self):
        if self._anim_step >= len(self._anim_seq):
            self._anim_btn.config(text="▶  Animate", command=self._start_animation)
            self._anim_dot.set_data([], [])
            if self.current_canvas:
                self.current_canvas.draw_idle()
            return

        x = self._anim_seq[self._anim_step]
        y = self._anim_step
        self._anim_dot.set_data([x], [y])
        if self.current_canvas:
            self.current_canvas.draw_idle()

        self._anim_step += 1
        self._anim_id = self.frame.after(120, self._animate_step)

    def _stop_animation(self):
        if self._anim_id is not None:
            self.frame.after_cancel(self._anim_id)
            self._anim_id = None
        self._anim_btn.config(text="▶  Animate", command=self._start_animation)

    # ── Export ─────────────────────────────────────────────────────────

    def _export_chart(self):
        if self.current_fig is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")],
            initialfile="head_movement_chart.png",
            title="Save Chart",
        )
        if path:
            self.current_fig.savefig(path, dpi=150, bbox_inches="tight",
                                     facecolor=DARK_FIG)

    def clear(self):
        self._clear_canvas()
        self._anim_btn.config(state="disabled", text="▶  Animate")
        self._export_btn.config(state="disabled")
        self._show_placeholder()


# ─────────────────────────────────────────────────────────────────────────────
#  ComparisonChart  –  3-subplot comparison
# ─────────────────────────────────────────────────────────────────────────────

class ComparisonChart:
    """
    Three subplots:
      1. Bar chart — total seek count
      2. Line chart — avg seek time per request
      3. Horizontal bar — efficiency ranking (shortest = top)
    """

    PALETTE = ["#4F8EF7", "#3DDC84", "#FF8C42", "#FF6B8A", "#A78BFA"]

    def __init__(self, parent, theme: dict):
        self.theme = theme
        self.fig   = None
        self.frame = tk.Frame(parent, bg=DARK_FIG)

    def create_bar_chart(self, results: dict):
        th = self.theme

        algorithms  = list(results.keys())
        seek_counts = [results[a]["seek_count"]    for a in algorithms]
        avg_seeks   = [results[a]["avg_seek_time"] for a in algorithms]
        best_idx    = seek_counts.index(min(seek_counts))

        # 3 subplots
        fig = Figure(figsize=(13, 5), dpi=100, facecolor=DARK_FIG)
        ax1 = fig.add_subplot(131)
        ax2 = fig.add_subplot(132)
        ax3 = fig.add_subplot(133)
        for ax in (ax1, ax2, ax3):
            _style_axes(ax)

        # ── 1. Total seek bar chart ──────────────────────────────────
        colors = [ALGO_COLOURS.get(a, self.PALETTE[i % len(self.PALETTE)])
                  for i, a in enumerate(algorithms)]
        colors[best_idx] = th["accent_green"]

        # Ensure no grid is used in ComparisonChart subplots
        bars = ax1.bar(
            algorithms, seek_counts,
            color=colors, edgecolor=DARK_FIG, linewidth=1.4,
            width=0.55, zorder=3,
        )
        bars[best_idx].set_edgecolor(th["accent_green"])
        bars[best_idx].set_linewidth(2.4)

        max_seek = max(seek_counts)
        ax1.set_ylim(0, max_seek * 1.22)
        for i, (bar, cnt) in enumerate(zip(bars, seek_counts)):
            label = f"{cnt}" + ("\n★ BEST" if i == best_idx else "")
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_seek * 0.015,
                label, ha="center", va="bottom", fontsize=8, fontweight="bold",
                color=th["accent_green"] if i == best_idx else DARK_TEXT,
            )
        ax1.set_xlabel("Algorithm",                    fontsize=10, fontweight="bold")
        ax1.set_ylabel("Total Seek Count (cylinders)", fontsize=10, fontweight="bold")
        ax1.set_title("Total Seek Comparison",         fontsize=11, fontweight="bold", pad=10)
        
        # Rotate labels to prevent overlap
        ax1.tick_params(axis='x', rotation=30)
        
        best_patch = mpatches.Patch(color=th["accent_green"], label="Best")
        ax1.legend(handles=[best_patch], fontsize=8,
                   facecolor=DARK_LEG, edgecolor=DARK_EDGE, labelcolor=DARK_TEXT)

        # ── 2. Avg seek line chart ───────────────────────────────────
        x = list(range(len(algorithms)))
        ax2.plot(
            x, avg_seeks,
            color=th["accent_blue"], linewidth=2.2,
            marker="D", markersize=7,
            markerfacecolor=th["accent_blue"],
            markeredgecolor=DARK_FIG, markeredgewidth=1.4,
            zorder=4,
        )
        ax2.fill_between(x, avg_seeks, min(avg_seeks), alpha=0.1, color=th["accent_blue"])
        for xi, yi in zip(x, avg_seeks):
            ax2.text(xi, yi + max(avg_seeks) * 0.03, f"{yi:.1f}",
                     ha="center", va="bottom", fontsize=8,
                     color=DARK_TEXT, fontweight="bold")
        ax2.set_xticks(x)
        ax2.set_xticklabels(algorithms, fontsize=9)
        ax2.set_ylim(0, max(avg_seeks) * 1.25)
        ax2.set_xlabel("Algorithm",                      fontsize=10, fontweight="bold")
        ax2.set_ylabel("Avg Seek / Request (cylinders)", fontsize=10, fontweight="bold")
        ax2.set_title("Average Seek Time",               fontsize=11, fontweight="bold", pad=10)

        # ── 3. Horizontal efficiency ranking ────────────────────────
        sorted_items = sorted(zip(algorithms, seek_counts), key=lambda t: t[1])
        s_algos  = [t[0] for t in sorted_items]
        s_counts = [t[1] for t in sorted_items]
        h_colors = [ALGO_COLOURS.get(a, self.PALETTE[0]) for a in s_algos]

        hbars = ax3.barh(s_algos, s_counts, color=h_colors,
                         edgecolor=DARK_FIG, linewidth=1, height=0.55, zorder=3)
        # best gets a highlight outline
        hbars[0].set_edgecolor(th["accent_green"])
        hbars[0].set_linewidth(2.2)

        max_cnt = max(s_counts)
        for bar, cnt in zip(hbars, s_counts):
            ax3.text(
                cnt + max_cnt * 0.015,
                bar.get_y() + bar.get_height() / 2,
                f"{cnt}", va="center", ha="left", fontsize=8,
                color=DARK_TEXT, fontweight="bold",
            )
        ax3.set_xlim(0, max_cnt * 1.2)
        ax3.invert_yaxis()   # best at top
        ax3.set_xlabel("Total Seek Count", fontsize=10, fontweight="bold")
        ax3.set_title("Efficiency Ranking\n(Best at Top)", fontsize=11, fontweight="bold", pad=10)

        # Prevent label overlap in middle chart too
        ax2.tick_params(axis='x', rotation=30)
        
        fig.tight_layout(pad=1.2)
        self.fig = fig

        # Embed
        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()

        toolbar_frame = tk.Frame(self.frame, bg=DARK_FIG)
        toolbar_frame.pack(side="bottom", fill="x")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.config(bg=DARK_FIG)
        for child in toolbar.winfo_children():
            try:
                child.config(bg=DARK_FIG)
            except Exception:
                pass
        toolbar.update()

        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        return canvas


# ─────────────────────────────────────────────────────────────────────────────
#  InlineComparisonPanel  –  embeddable comparison chart panel for main window
# ─────────────────────────────────────────────────────────────────────────────

class InlineComparisonPanel:
    """
    Wraps ComparisonChart for use inside the main window's notebook tab.
    Provides refresh() to re-render charts in place, and clear() for reset.
    """

    def __init__(self, parent, theme: dict):
        self.theme  = theme
        self._fig   = None
        self._chart = None
        self.frame  = _make_card(parent, "Algorithm Performance Comparison", theme)
        self._build_placeholder()

    def _build_placeholder(self):
        th = self.theme
        self._placeholder = tk.Label(
            self.frame,
            text="📈  Run all algorithms [F5] to see the comparison charts here.",
            font=_ui_font(10),
            bg=th["bg_card"], fg=th["text_muted"],
        )
        self._placeholder.pack(expand=True, fill="both", pady=60)
        self._chart_frame = None

    def _clear_chart(self):
        if self._chart_frame and self._chart_frame.winfo_exists():
            for w in self._chart_frame.winfo_children():
                w.destroy()
            self._chart_frame.destroy()
            self._chart_frame = None
        if self._fig is not None:
            plt.close(self._fig)
            self._fig = None

    def refresh(self, results: dict):
        """Re-render the 3-subplot comparison with fresh results."""
        # Hide placeholder
        if self._placeholder and self._placeholder.winfo_exists():
            self._placeholder.pack_forget()

        self._clear_chart()

        self._chart_frame = tk.Frame(self.frame, bg=DARK_FIG)
        self._chart_frame.pack(fill="both", expand=True)

        self._chart = ComparisonChart(self._chart_frame, self.theme)
        self._chart.frame.pack(fill="both", expand=True)
        self._chart.create_bar_chart(results)
        if self._chart.fig is not None:
            self._fig = self._chart.fig

    def clear(self):
        self._clear_chart()
        if self._placeholder and self._placeholder.winfo_exists():
            self._placeholder.pack(expand=True, fill="both", pady=60)
        else:
            self._build_placeholder()