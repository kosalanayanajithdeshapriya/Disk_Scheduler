"""
Disk Scheduling Algorithm Visualizer
Main Application File — Professional Edition

Algorithms: FCFS · SSTF · SCAN · C-SCAN · C-LOOK

Features:
  • Animated splash screen
  • Toast notification system
  • Keyboard shortcuts (F5/F6/F7/Ctrl+E/Delete)
  • Animated progress bar during calculation
  • Quick-stats ranking strip
  • Live input validation
  • Step-by-step head animation
  • 3-chart comparison window
  • File-dialog CSV export
"""

import tkinter as tk
from tkinter import messagebox, Menu, ttk, filedialog
import sys
import threading
import time
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

from algorithms import DiskScheduler
from utils import validate_input, format_result_text, calculate_statistics, export_results_to_csv, export_results_to_pdf
from gui_components import InputFrame, ResultsDisplay, VisualizationPanel, ComparisonChart, InlineComparisonPanel


# ─────────────────────────────────────────
#  GLOBAL THEME: ABYSS EDITION
# ─────────────────────────────────────────
THEME = {
    "bg_root":      "#0A0C10",
    "bg_sidebar":   "#11141D",
    "bg_card":      "#161B22",
    "bg_input":     "#1C2128",
    "bg_hover":     "#21262D",
    "accent_blue":  "#58A6FF",
    "accent_green": "#3FB950",
    "accent_orange": "#F78166",
    "accent_red":    "#F85149",
    "accent_purple": "#BC8CFF",
    "text_primary":  "#E6EDF3",
    "text_secondary": "#8B949E",
    "text_muted":    "#484F58",
    "border":        "#30363D",
    "status_bg":     "#010409",
    "status_text":   "#7D8590",
}

BTN_PRIMARY = {"bg": THEME["accent_blue"],   "activebackground": "#3A7AE8"}
BTN_SUCCESS = {"bg": THEME["accent_green"],  "activebackground": "#2E9A40"}
BTN_WARNING = {"bg": THEME["accent_orange"], "activebackground": "#D86B55"}
BTN_DANGER  = {"bg": THEME["accent_red"],    "activebackground": "#DA3633"}


def apply_hover(widget, normal_color, hover_color):
    widget.bind("<Enter>", lambda e: widget.config(bg=hover_color))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal_color))


# ─────────────────────────────────────────
#  PREMIUM MODERN SPLASH SCREEN
# ─────────────────────────────────────────
class SplashScreen:
    """Modern, high-fidelity splash screen with pulsing animation."""

    DURATION_MS = 3000
    BG_COLOR = "#0A0D12" # Deeper midnight
    ACCENT   = "#4F8EF7" # Electric Blue
    GLOW     = "#2A3A5A" # Subtle Glow

    def __init__(self, root):
        self.root = root
        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)
        self.splash.configure(bg=self.BG_COLOR)

        # Center on screen
        w, h = 550, 400
        sw = self.splash.winfo_screenwidth()
        sh = self.splash.winfo_screenheight()
        self.splash.geometry(f"{w}x{h}+{(sw - w)//2}+{(sh - h)//2}")
        
        # Ensure it's on top
        self.splash.lift()
        self.splash.attributes("-topmost", True)

        self._build()
        self._pulse_direction = 1
        self._pulse_scale = 1.0
        self._progress = 0
        self._shimmer_offset = 0
        
        self._animate_pulse()
        self._advance_progress()

    def _build(self):
        # Main Canvas for all animations
        self.cv = tk.Canvas(
            self.splash, width=550, height=400,
            bg=self.BG_COLOR, highlightthickness=0
        )
        self.cv.pack(fill="both", expand=True)

        # Draw decorative background elements
        self._draw_background_decor()

        # Load logo for center
        try:
            logo_path = resource_path(os.path.join("assets", "logo.png"))
            self.logo_orig = tk.PhotoImage(file=logo_path).subsample(4, 4)
            self.logo_item = self.cv.create_image(275, 150, image=self.logo_orig)
        except:
            # Fallback icon if logo missing
            self.logo_item = self.cv.create_text(
                275, 150, text="⬡", 
                font=("Segoe UI", 60, "bold"), fill=self.ACCENT
            )

        # Pulsing Glow Circle (Layered behind logo)
        self.glow_circle = self.cv.create_oval(
            225, 100, 325, 200, 
            outline="", fill=self.GLOW, stipple="gray25"
        )
        self.cv.tag_lower(self.glow_circle)

        # Title with High-Contrast Text
        self.title_text = "DISK SCHEDULING VISUALIZER"
        self.title_label = self.cv.create_text(
            275, 260, text=self.title_text,
            font=("Segoe UI", 18, "bold"), fill="#FFFFFF"
        )

        self.subtitle = self.cv.create_text(
            275, 290, text="ADVANCED OPERATING SYSTEMS TOOLKIT",
            font=("Segoe UI", 9, "bold"), fill=self.ACCENT
        )

        # Custom Progress Bar Frame (Glassmorphism style)
        self.pb_bg = self.cv.create_rectangle(
            125, 335, 425, 342, 
            fill="#1E232B", outline="#2A313C", width=1
        )
        self.pb_fill = self.cv.create_rectangle(
            125, 335, 125, 342, 
            fill=self.ACCENT, outline=""
        )

        self.status = self.cv.create_text(
            275, 365, text="INITIALIZING SYSTEM CORE...",
            font=("Segoe UI", 8), fill="#5C6080"
        )

    def _draw_background_decor(self):
        """Draw some professional aesthetic lines/dots."""
        # Corner accents
        self.cv.create_line(0, 0, 50, 0, fill=self.ACCENT, width=2)
        self.cv.create_line(0, 0, 0, 50, fill=self.ACCENT, width=2)
        self.cv.create_line(550, 400, 500, 400, fill=self.ACCENT, width=2)
        self.cv.create_line(550, 400, 550, 350, fill=self.ACCENT, width=2)
        
        # Subtle horizontal circuit lines (Using dark grey to simulate transparency)
        for y in range(50, 400, 100):
            self.cv.create_line(0, y, 550, y, fill="#1A1D23", dash=(2, 4))

    def _animate_pulse(self):
        if not self.splash.winfo_exists(): return

        # Pulse the glow circle
        self._pulse_scale += 0.02 * self._pulse_direction
        if self._pulse_scale > 1.3 or self._pulse_scale < 0.9:
            self._pulse_direction *= -1
        
        r = 50 * self._pulse_scale
        self.cv.coords(self.glow_circle, 275-r, 150-r, 275+r, 150+r)

        # Text shimmer effect
        self._shimmer_offset = (self._shimmer_offset + 1) % len(self.title_text)
        # We can't easily do per-character colors in one text item, 
        # but we can alternate the whole title brightness or position
        
        self.splash.after(50, self._animate_pulse)

    def _advance_progress(self):
        if not self.splash.winfo_exists(): return
        
        self._progress += 1.5
        if self._progress > 100: self._progress = 100
        
        # Update progress bar fill
        x_end = 125 + (300 * (self._progress / 100))
        self.cv.coords(self.pb_fill, 125, 335, x_end, 342)

        # Dynamic status messages
        if self._progress < 30:
            msg = "PREPARING NEURAL ENGINE..."
        elif self._progress < 60:
            msg = "LOADING SCHEDULING ALGORITHMS..."
        elif self._progress < 90:
            msg = "CALIBRATING VISUALIZATION INTERFACE..."
        else:
            msg = "SYSTEM READY"
        self.cv.itemconfig(self.status, text=msg)

        if self._progress < 100:
            self.splash.after(35, self._advance_progress)

    def destroy(self):
        if self.splash.winfo_exists():
            self.splash.destroy()


# ─────────────────────────────────────────
#  TOAST NOTIFICATION
# ─────────────────────────────────────────
class Toast:
    """Slide-in / fade-out toast in the top-right corner."""

    _ICONS = {"success": "✔", "error": "✘", "info": "ℹ", "warning": "⚠"}
    _COLORS = {
        "success": ("#3DDC84", "#1B5E20"),
        "error":   ("#FF5252", "#7F0000"),
        "info":    ("#4F8EF7", "#0D47A1"),
        "warning": ("#FF8C42", "#6D3A00"),
    }

    def __init__(self, root, message, kind="success", duration=3000):
        self.root = root
        fg, bg = self._COLORS.get(kind, self._COLORS["info"])
        icon = self._ICONS.get(kind, "ℹ")

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=bg)

        # Rounded border via Frame
        outer = tk.Frame(self.win, bg=fg, padx=2, pady=2)
        outer.pack(fill="both", expand=True)
        inner = tk.Frame(outer, bg=bg, padx=18, pady=12)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text=icon, font=("Segoe UI", 16, "bold"),
                 bg=bg, fg=fg).pack(side="left", padx=(0, 12))

        tk.Label(inner, text=message,
                 font=("Segoe UI", 10), bg=bg, fg="#E8EAED",
                 wraplength=300, justify="left").pack(side="left")

        self.win.update_idletasks()
        w = self.win.winfo_reqwidth()
        h = self.win.winfo_reqheight()
        sw = root.winfo_x() + root.winfo_width()
        sy = root.winfo_y()

        # Start off-screen right, slide in
        self._x_target = sw - w - 20
        self._x_start  = sw + 20
        self._y        = sy + 60
        self.win.geometry(f"{w}x{h}+{self._x_start}+{self._y}")
        self.win.deiconify()

        self._slide_in()
        self.root.after(duration, self._fade_out)

    def _slide_in(self):
        x = int(self.win.winfo_x())
        if x > self._x_target:
            self.win.geometry(f"+{x - 18}+{self._y}")
            self.win.after(15, self._slide_in)

    def _fade_out(self):
        try:
            alpha = self.win.attributes("-alpha")
            if alpha > 0.05:
                self.win.attributes("-alpha", alpha - 0.08)
                self.win.after(30, self._fade_out)
            else:
                self.win.destroy()
        except Exception:
            pass


# ─────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────
class DiskSchedulerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Disk Scheduling Algorithm Visualizer")
        self.root.geometry("1440x900")
        self.root.minsize(1100, 720)
        self.root.configure(bg=THEME["bg_root"])
        self.root.withdraw()          # hide until splash done

        try:
            self.root.iconbitmap("icon.ico")
        except Exception:
            pass

        self.results        = {}
        self.current_inputs = {}

        self._configure_ttk_styles()
        self.create_menu()
        self.create_widgets()
        self.center_window()
        self._bind_shortcuts()

        # Show splash, then reveal main window
        self.splash = SplashScreen(root)
        root.after(SplashScreen.DURATION_MS, self._after_splash)

    # ── TTK STYLES ───────────────────────────────────────────────────
    def _configure_ttk_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Dark.TCombobox",
            fieldbackground=THEME["bg_input"],
            background=THEME["bg_input"],
            foreground=THEME["text_primary"],
            selectbackground=THEME["accent_blue"],
            selectforeground=THEME["text_primary"],
            arrowcolor=THEME["text_secondary"],
            bordercolor=THEME["border"],
            lightcolor=THEME["border"],
            darkcolor=THEME["border"],
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", THEME["bg_input"])],
            foreground=[("readonly", THEME["text_primary"])],
        )
        style.configure(
            "Dark.Vertical.TScrollbar",
            background=THEME["bg_sidebar"],
            troughcolor=THEME["bg_card"],
            arrowcolor=THEME["text_secondary"],
            bordercolor=THEME["bg_card"],
        )
        style.configure(
            "Indeterminate.Horizontal.TProgressbar",
            troughcolor=THEME["bg_card"],
            background=THEME["accent_blue"],
            bordercolor=THEME["bg_card"],
        )
        style.configure(
            "Calc.Horizontal.TProgressbar",
            troughcolor=THEME["bg_card"],
            background=THEME["accent_green"],
        )
        style.configure(
            "Dark.TNotebook",
            background=THEME["bg_card"],
            bordercolor=THEME["border"],
            tabmargins=[0, 0, 0, 0],
        )
        style.configure(
            "Dark.TNotebook.Tab",
            background=THEME["bg_input"],
            foreground=THEME["text_secondary"],
            font=("Segoe UI", 10),
            padding=[14, 8],
            bordercolor=THEME["border"],
        )
        style.map(
            "Dark.TNotebook.Tab",
            background=[("selected", THEME["bg_card"]), ("active", THEME["bg_hover"])],
            foreground=[("selected", THEME["accent_blue"]), ("active", THEME["text_primary"])],
            font=[("selected", ("Segoe UI", 10, "bold"))],
        )

    # ── SPLASH FINISH ─────────────────────────────────────────────────
    def _after_splash(self):
        self.splash.destroy()
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    # ── MENU BAR ─────────────────────────────────────────────────────
    def create_menu(self):
        menubar = Menu(
            self.root,
            bg=THEME["bg_sidebar"], fg=THEME["text_primary"],
            activebackground=THEME["accent_blue"], activeforeground="white",
            relief="flat", bd=0,
        )
        self.root.config(menu=menubar)

        file_menu = Menu(
            menubar, tearoff=0,
            bg=THEME["bg_sidebar"], fg=THEME["text_primary"],
            activebackground=THEME["accent_blue"], activeforeground="white",
        )
        menubar.add_cascade(label="  File  ", menu=file_menu)
        file_menu.add_command(label="Export Results (CSV)    Ctrl+E", command=self.export_results)
        file_menu.add_command(label="Export PDF Report         Ctrl+P", command=self.export_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        help_menu = Menu(
            menubar, tearoff=0,
            bg=THEME["bg_sidebar"], fg=THEME["text_primary"],
            activebackground=THEME["accent_blue"], activeforeground="white",
        )
        menubar.add_cascade(label="  Help  ", menu=help_menu)
        help_menu.add_command(label="About",          command=self.show_about)
        help_menu.add_command(label="Algorithm Info", command=self.show_algorithm_info)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)

    # ── KEYBOARD SHORTCUTS ─────────────────────────────────────────────
    def _bind_shortcuts(self):
        self.root.bind("<F5>",           lambda e: self.calculate_all())
        self.root.bind("<F6>",           lambda e: self.visualize_selected())
        self.root.bind("<F7>",           lambda e: self.show_comparison())
        self.root.bind("<Control-e>",    lambda e: self.export_results())
        self.root.bind("<Control-E>",    lambda e: self.export_results())
        self.root.bind("<Control-p>",    lambda e: self.export_pdf())
        self.root.bind("<Control-P>",    lambda e: self.export_pdf())
        self.root.bind("<Delete>",       lambda e: self.clear_all())

    # ── MAIN WIDGETS ─────────────────────────────────────────────────
    def create_widgets(self):
        # 1. Sidebar
        self.sidebar = tk.Frame(self.root, bg=THEME["bg_sidebar"], width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar_content()

        # 2. Main Content Wrapper
        self.main_content = tk.Frame(self.root, bg=THEME["bg_root"])
        self.main_content.pack(side="right", fill="both", expand=True)

        # 3. Top Header (Dashboard Style)
        self._build_header()

        # 4. Central Dashboard Container (Flexible, no scroll)
        self.dashboard_container = tk.Frame(self.main_content, bg=THEME["bg_root"])
        self.dashboard_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # --- Bento Layout ---
        # Row 1: Input Parameters (Fixed height-ish)
        self.input_frame = InputFrame(self.dashboard_container, THEME)
        # InputFrame.__init__ handles its own packing into row1/content_inner

        # Row 2: Progress & Quick Stats
        self._stats_container = tk.Frame(self.dashboard_container, bg=THEME["bg_root"])
        self._stats_container.pack(fill="x", pady=5)
        self._build_progress_bar(self._stats_container)
        self._build_quick_stats(self._stats_container)
        
        # Row 3: Results & Flexible Charts (Expanding)
        self.row3 = tk.Frame(self.dashboard_container, bg=THEME["bg_root"])
        self.row3.pack(fill="both", expand=True, pady=5)

        # 3a. Results table (left)
        self.results_display = ResultsDisplay(self.row3, THEME)
        
        # 3b. Right-side Notebook for Viz/Comparison (switchable)
        self._right_nb = ttk.Notebook(self.row3, style="Dark.TNotebook")
        self._right_nb.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self._viz_tab = tk.Frame(self._right_nb, bg=THEME["bg_root"])
        self._comp_tab = tk.Frame(self._right_nb, bg=THEME["bg_root"])
        self._right_nb.add(self._viz_tab, text="  📊  Visualization  ")
        self._right_nb.add(self._comp_tab, text="  📈  Comparison  ")

        self.viz_panel = VisualizationPanel(self._viz_tab, THEME)
        self.inline_comparison = InlineComparisonPanel(self._comp_tab, THEME)
        self.inline_comparison.frame.pack(fill="both", expand=True, padx=4, pady=4)

        self._build_status_bar()

    def _build_sidebar_content(self):
        # Brand/Logo area
        logo_area = tk.Frame(self.sidebar, bg=THEME["bg_sidebar"], pady=30)
        logo_area.pack(fill="x")
        
        try:
            # Load new professional logo from assets folder
            logo_path = resource_path(os.path.join("assets", "logo.png"))
            self.logo_img = tk.PhotoImage(file=logo_path).subsample(5, 5) 
            self.logo_lbl = tk.Label(logo_area, image=self.logo_img, bg=THEME["bg_sidebar"])
            self.logo_lbl.pack(pady=(0, 10))
        except Exception as e:
            # Fallback to icon if logo fails to load
            tk.Label(logo_area, text="⬡", font=("Segoe UI", 42, "bold"), 
                     bg=THEME["bg_sidebar"], fg=THEME["accent_blue"]).pack()

        tk.Label(logo_area, text="DISK SCHEDULER", font=("Segoe UI", 12, "bold"), 
                 bg=THEME["bg_sidebar"], fg=THEME["text_primary"]).pack()
        tk.Label(logo_area, text="PRO PLATFORM", font=("Segoe UI", 8, "bold"), 
                 bg=THEME["bg_sidebar"], fg=THEME["accent_blue"], pady=5).pack()

        # Separator
        tk.Frame(self.sidebar, bg=THEME["border"], height=1).pack(fill="x", padx=20, pady=20)

        # Nav items
        self.nav_btns = {}
        self.nav_indicators = {}
        nav_items = [
            ("Dashboard", "🏠", self._nav_dashboard),
            ("Visualize", "📊", self.visualize_selected),
            ("Comparison", "📈", self.show_comparison),
            ("PDF Report", "📄", self.export_pdf),
            ("CSV Export", "💾", self.export_results),
            ("Clear All",  "🗑", self.clear_all),
        ]
        
        for text, icon, cmd in nav_items:
            f = tk.Frame(self.sidebar, bg=THEME["bg_sidebar"])
            f.pack(fill="x")
            
            # Active Indicator Bar (Hidden by default)
            ind = tk.Frame(f, bg=THEME["accent_blue"], width=4)
            ind.pack(side="left", fill="y")
            ind.pack_forget() 
            self.nav_indicators[text] = ind

            btn = tk.Button(f, text=f"  {icon}   {text}", anchor="w",
                            font=("Segoe UI", 10), bg=THEME["bg_sidebar"], fg=THEME["text_secondary"],
                            activebackground=THEME["bg_hover"], activeforeground=THEME["accent_blue"],
                            relief="flat", bd=0, padx=20, pady=12, cursor="hand2", command=cmd)
            btn.pack(side="left", fill="x", expand=True)
            self.nav_btns[text] = btn
            apply_hover(btn, THEME["bg_sidebar"], THEME["bg_hover"])

        # Default active
        self._set_active_nav("Dashboard")

    def _set_active_nav(self, name):
        """Highlighted active sidebar item."""
        for n, btn in self.nav_btns.items():
            if n == name:
                btn.config(fg=THEME["accent_blue"], bg=THEME["bg_hover"])
                if n in self.nav_indicators: self.nav_indicators[n].pack(side="left", fill="y")
            else:
                btn.config(fg=THEME["text_secondary"], bg=THEME["bg_sidebar"])
                if n in self.nav_indicators: self.nav_indicators[n].pack_forget()

    def _nav_dashboard(self):
        self._set_active_nav("Dashboard")
        self._toast("Dashboard Overview", "info")
        self._set_status("Viewing Platform Overview", THEME["accent_blue"])

    def _build_header(self):
        header = tk.Frame(self.main_content, bg=THEME["bg_root"], height=100)
        header.pack(fill="x", padx=30, pady=(20, 10))
        header.pack_propagate(False)

        title_f = tk.Frame(header, bg=THEME["bg_root"])
        title_f.pack(side="left", fill="both", expand=True)
        
        tk.Label(title_f, text="Platform Overview", font=("Segoe UI", 24, "bold"),
                 bg=THEME["bg_root"], fg=THEME["text_primary"]).pack(anchor="w")
        tk.Label(title_f, text="Analyze and compare algorithm efficiency metrics", font=("Segoe UI", 10),
                 bg=THEME["bg_root"], fg=THEME["text_secondary"]).pack(anchor="w")

        # Action Buttons in Header
        btn_f = tk.Frame(header, bg=THEME["bg_root"])
        btn_f.pack(side="right", fill="y")
        
        self.run_btn = tk.Button(btn_f, text="  ⚡   RUN ALL ALGORITHMS  ", command=self.calculate_all,
                                font=("Segoe UI", 10, "bold"), bg=THEME["accent_blue"], fg="white",
                                activebackground="#3A7AE8", activeforeground="white",
                                relief="flat", bd=0, padx=30, pady=12, cursor="hand2")
        self.run_btn.pack(side="right", pady=15)
        apply_hover(self.run_btn, THEME["accent_blue"], "#3A7AE8")

    def _build_progress_bar(self, parent):
        """Thin progress bar shown only during calculation."""
        self._prog_frame = tk.Frame(parent, bg=THEME["bg_root"])
        # No pack yet
        self._progress_bar = ttk.Progressbar(
            self._prog_frame,
            style="Calc.Horizontal.TProgressbar",
            orient="horizontal", mode="indeterminate",
        )

    def _build_quick_stats(self, parent):
        """Ranked algorithm summary strip with badge indicators."""
        self._stats_frame = tk.Frame(parent, bg=THEME["bg_card"], padx=20, pady=12,
                                    highlightthickness=1, highlightbackground=THEME["border"])
        
        inner = tk.Frame(self._stats_frame, bg=THEME["bg_card"])
        inner.pack(fill="x")

        tk.Label(inner, text="🏆  ALGORITHM RANKINGS", font=("Segoe UI", 8, "bold"),
                 bg=THEME["bg_card"], fg=THEME["text_muted"]).pack(side="left", padx=(0, 20))

        self._stat_labels = {}
        self._stat_badges = {}
        ALGO_ORDER = ["FCFS", "SSTF", "SCAN", "C-SCAN", "C-LOOK"]
        for algo in ALGO_ORDER:
            # Badge container
            b = tk.Frame(inner, bg=THEME["bg_input"], padx=8, pady=4,
                         highlightthickness=1, highlightbackground=THEME["border"])
            b.pack(side="left", padx=5)
            self._stat_badges[algo] = b
            
            lbl = tk.Label(b, text=f"{algo}: —", font=("Segoe UI", 8, "bold"),
                          bg=THEME["bg_input"], fg=THEME["text_secondary"])
            lbl.pack()
            self._stat_labels[algo] = lbl

        if not self._stats_frame.winfo_ismapped():
            self._stats_frame.pack(padx=30, pady=(0, 10), fill="x")

    def _update_quick_stats(self):
        if not self.results:
            return
        
        sorted_res = sorted(self.results.items(), key=lambda x: x[1]["seek_count"])
        best_name = sorted_res[0][0]

        for algo, lbl in self._stat_labels.items():
            badge = self._stat_badges.get(algo)
            if algo in self.results:
                res = self.results[algo]
                is_best = (algo == best_name)
                
                if is_best:
                    lbl.config(text=f"🥇 {algo}: {res['seek_count']}", fg="white", bg=THEME["accent_green"])
                    badge.config(bg=THEME["accent_green"], highlightbackground=THEME["accent_green"])
                else:
                    lbl.config(text=f"{algo}: {res['seek_count']}", fg=THEME["text_primary"], bg=THEME["bg_input"])
                    badge.config(bg=THEME["bg_input"], highlightbackground=THEME["border"])
            else:
                lbl.config(text=f"{algo}: —", fg=THEME["text_muted"], bg=THEME["bg_input"])
                badge.config(bg=THEME["bg_input"], highlightbackground=THEME["border"])

        if not self._stats_frame.winfo_ismapped():
            self._stats_frame.pack(padx=30, pady=(0, 10), fill="x")

    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg=THEME["status_bg"], height=26)
        bar.pack(side="bottom", fill="x")
        bar.pack_propagate(False)

        self._status_dot = tk.Label(
            bar, text="●", font=("Segoe UI", 9),
            bg=THEME["status_bg"], fg=THEME["accent_green"],
        )
        self._status_dot.pack(side="left", padx=(10, 4))

        self.status_var = tk.StringVar(value="Ready  —  Press F5 to run all algorithms")
        tk.Label(
            bar, textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg=THEME["status_bg"], fg=THEME["status_text"],
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        tk.Label(
            bar,
            text="Disk Scheduling Visualizer  v2.0",
            font=("Segoe UI", 8),
            bg=THEME["status_bg"], fg=THEME["text_muted"],
        ).pack(side="right", padx=12)

    # ── UTILITIES ─────────────────────────────────────────────────────
    def _set_status(self, msg, color=None):
        self.status_var.set(msg)
        if color:
            self._status_dot.config(fg=color)

    def _toast(self, message, kind="success"):
        Toast(self.root, message, kind=kind)

    def _show_progress(self):
        self._progress_bar.pack(fill="x", pady=(2, 0))
        self._progress_bar.start(12)
        self.root.update_idletasks()

    def _hide_progress(self):
        self._progress_bar.stop()
        self._progress_bar.pack_forget()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── ACTIONS ───────────────────────────────────────────────────────
    def calculate_all(self):
        try:
            self._set_status("Calculating…", THEME["accent_orange"])
            self._show_progress()
            self.root.update()

            inputs = self.input_frame.get_values()
            requests, head_start, disk_size = validate_input(
                inputs["requests"], inputs["head"], inputs["disk_size"]
            )
            self.current_inputs = {
                "requests":   requests,
                "head_start": head_start,
                "disk_size":  disk_size,
                "direction":  inputs["direction"],
            }

            scheduler    = DiskScheduler(requests, head_start, disk_size, inputs["direction"])
            self.results = scheduler.get_all_results()

            self.display_results()
            self.viz_panel.algo_combo.set("FCFS")
            self._update_quick_stats()

            best_name, best_res = scheduler.get_best_algorithm()
            self._set_status(
                f"✓  All algorithms calculated — Best: {best_name}  ({best_res['seek_count']} cyl)",
                THEME["accent_green"],
            )
            self._toast(
                f"Calculated {len(self.results)} algorithms!\n"
                f"Best: {best_name}  ({best_res['seek_count']} cyl)",
                kind="success",
            )
            # Auto-populate inline comparison tab
            self.inline_comparison.refresh(self.results)

        except ValueError as e:
            self._set_status("Input validation error", THEME["accent_red"])
            self._toast(str(e), kind="error")
        except Exception as e:
            self._set_status("Calculation error", THEME["accent_red"])
            self._toast(f"An error occurred:\n{e}", kind="error")
        finally:
            self._hide_progress()

    def display_results(self):
        if not self.results:
            return

        best_algo = min(self.results.items(), key=lambda x: x[1]["seek_count"])
        output    = "=" * 70 + "\n"
        output   += "INPUT PARAMETERS\n"
        output   += "=" * 70 + "\n"
        output   += f"Request Queue        : {self.current_inputs['requests']}\n"
        output   += f"Initial Head Position: {self.current_inputs['head_start']}\n"
        output   += f"Disk Size            : {self.current_inputs['disk_size']} cylinders\n"
        output   += f"Direction            : {self.current_inputs['direction'].upper()}\n\n"

        for algo_name, result in self.results.items():
            is_best  = (algo_name == best_algo[0])
            output  += format_result_text(algo_name, result, is_best)

        stats   = calculate_statistics(self.results)
        output += "=" * 70 + "\n"
        output += "STATISTICAL SUMMARY\n"
        output += "=" * 70 + "\n"
        output += f"Best Performance : {best_algo[0]} ({best_algo[1]['seek_count']} cylinders)\n"
        output += (
            f"Worst Performance: "
            f"{max(self.results.items(), key=lambda x: x[1]['seek_count'])[0]} "
            f"({stats['max_seek']} cylinders)\n"
        )
        output += f"Average Seek     : {stats['avg_seek']:.2f} cylinders\n"
        output += f"Performance Range: {stats['range']} cylinders\n\n"
        output += f"RECOMMENDATION:\nUse {best_algo[0]} algorithm for optimal performance!\n"

        self.results_display.display_text(output, self.results, self.current_inputs)

    def visualize_selected(self):
        if not self.results:
            self._toast("No data — press F5 to run algorithms first.", kind="warning")
            return
        try:
            self._set_active_nav("Visualize")
            self._right_nb.select(0)  # Select Visualization tab
            algo_name = self.viz_panel.algo_var.get()
            self.viz_panel.visualize(algo_name, self.results[algo_name], 
                                     self.current_inputs["head_start"],
                                     self.current_inputs["disk_size"])
            self._set_status(f"Visualized  {algo_name}", THEME["accent_blue"])
        except Exception as e:
            self._toast(f"Visualization Error:\n{e}", kind="error")

    def show_comparison(self):
        """Switch to the inline Comparison tab (no separate window)."""
        if not self.results:
            self._toast("No data — press F5 to run algorithms first.", kind="warning")
            return
        try:
            self._set_active_nav("Comparison")
            # Switch right notebook to tab index 1 (Comparison)
            self._right_nb.select(1)
            self._set_status("Comparison chart — inline view", THEME["accent_orange"])
        except Exception as e:
            self._toast(f"Chart Error:\n{e}", kind="error")

    def export_results(self):
        if not self.results:
            self._toast("No data — press F5 to run algorithms first.", kind="warning")
            return
        try:
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                initialfile="disk_scheduler_results.csv",
                title="Export Results",
            )
            if not path:
                return
            export_results_to_csv(self.results, path)
            self._toast(f"Results exported successfully!\n{path}", kind="success")
            self._set_status(f"Exported → {path}", THEME["accent_green"])
        except Exception as e:
            self._toast(f"Export Error:\n{e}", kind="error")

    def export_pdf(self):
        if not self.results:
            self._toast("No data — press F5 to run algorithms first.", kind="warning")
            return
        try:
            path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Document", "*.pdf"), ("All Files", "*.*")],
                initialfile="disk_scheduler_report.pdf",
                title="Export PDF Report",
            )
            if not path:
                return
            self._set_status("Generating PDF report…", THEME["accent_orange"])
            self._show_progress()
            self.root.update()
            export_results_to_pdf(self.results, self.current_inputs, path)
            self._hide_progress()
            self._toast(f"PDF report saved!\n{path}", kind="success")
            self._set_status(f"PDF exported → {path}", THEME["accent_green"])
        except Exception as e:
            self._hide_progress()
            self._toast(f"PDF Export Error:\n{e}", kind="error")

    def clear_all(self):
        self.input_frame.clear()
        self.results_display.clear()
        self.viz_panel.clear()
        self.inline_comparison.clear()
        self._right_nb.select(0)     # back to Head Movement tab
        self.results        = {}
        self.current_inputs = {}

        # Hide quick-stats strip
        if self._stats_frame.winfo_ismapped():
            self._stats_frame.pack_forget()

        self._set_status("All data cleared — Ready", THEME["accent_red"])
        self._toast("All data cleared.", kind="info")

    # ── DIALOGS ───────────────────────────────────────────────────────
    def show_about(self):
        win = tk.Toplevel(self.root)
        win.title("About")
        win.geometry("420x320")
        win.resizable(False, False)
        win.configure(bg=THEME["bg_card"])
        win.attributes("-topmost", True)

        # Header strip
        hdr = tk.Frame(win, bg=THEME["bg_sidebar"], height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⬡  Disk Scheduling Visualizer",
                 font=("Segoe UI", 14, "bold"),
                 bg=THEME["bg_sidebar"], fg="white").pack(side="left", padx=20, pady=12)

        body = tk.Frame(win, bg=THEME["bg_card"], padx=30, pady=20)
        body.pack(fill="both", expand=True)

        for text, font, color in [
            ("Version 2.0 — Professional Edition", ("Segoe UI", 10), THEME["accent_blue"]),
            ("", None, None),
            ("Compare 5 disk scheduling algorithms:", ("Segoe UI", 10), THEME["text_secondary"]),
            ("FCFS  ·  SSTF  ·  SCAN  ·  C-SCAN  ·  C-LOOK", ("Segoe UI", 10, "bold"), THEME["text_primary"]),
            ("", None, None),
            ("Keyboard Shortcuts", ("Segoe UI", 10, "bold"), THEME["accent_orange"]),
            ("F5 Run  ·  F6 Visualize  ·  F7 Comparison Tab", ("Segoe UI", 9), THEME["text_secondary"]),
            ("Ctrl+E CSV Export  ·  Ctrl+P PDF  ·  Delete Clear", ("Segoe UI", 9), THEME["text_secondary"]),
            ("", None, None),
            ("© 2026  —  Educational Project", ("Segoe UI", 9), THEME["text_muted"]),
        ]:
            if font:
                tk.Label(body, text=text, font=font, bg=THEME["bg_card"], fg=color).pack(anchor="w", pady=1)

        tk.Button(
            body, text="OK", command=win.destroy,
            font=("Segoe UI", 10, "bold"),
            bg=THEME["accent_blue"], fg="white",
            activebackground="#3A7AE8", activeforeground="white",
            relief="flat", padx=24, pady=6, cursor="hand2",
        ).pack(pady=(12, 0))

    def show_algorithm_info(self):
        win = tk.Toplevel(self.root)
        win.title("Algorithm Reference")
        win.geometry("720x620")
        win.configure(bg=THEME["bg_root"])
        win.resizable(True, True)

        hdr = tk.Frame(win, bg=THEME["bg_sidebar"], height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📘  Algorithm Reference Guide",
                 font=("Segoe UI", 13, "bold"),
                 bg=THEME["bg_sidebar"], fg="white").pack(side="left", padx=20, pady=8)

        text_frame = tk.Frame(win, bg=THEME["bg_root"])
        text_frame.pack(fill="both", expand=True, padx=16, pady=16)

        scrollbar = ttk.Scrollbar(text_frame, style="Dark.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")

        t = tk.Text(
            text_frame, wrap="word", font=("Consolas", 10),
            bg=THEME["bg_card"], fg=THEME["text_primary"],
            insertbackground=THEME["text_primary"],
            selectbackground=THEME["accent_blue"],
            padx=18, pady=18, relief="flat", bd=0,
            yscrollcommand=scrollbar.set,
        )
        t.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=t.yview)

        info = """
DISK SCHEDULING ALGORITHMS — REFERENCE GUIDE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. FCFS  (First Come First Serve)
   • Services requests in the exact order they arrive.
   • Simple and fair — no starvation possible.
   ✦ Best for: light loads where fairness matters.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. SSTF  (Shortest Seek Time First)
   • Always moves to the closest pending request.
   • Lower total seek time than FCFS, but may cause starvation.
   ✦ Best for: minimising seek time in moderate loads.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. SCAN  (Elevator Algorithm)
   • Head sweeps to one end of the disk, then reverses.
   • Better throughput than FCFS under heavy loads.
   ✦ Best for: heavy, uniformly distributed loads.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. C-SCAN  (Circular SCAN)
   • Head sweeps to the end, then jumps to the start.
   • Provides more uniform waiting time than SCAN.
   ✦ Best for: systems requiring consistent response time.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. C-LOOK
   • Like C-SCAN but jumps between the first/last request.
   • Avoids unnecessary travel to disk boundaries.
   ✦ Best for: most scenarios — typically most efficient.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TYPICAL PERFORMANCE RANKING:
  1. SSTF   ★★★★★  (Minimum total seek)
  2. C-LOOK ★★★★☆  (Near-optimal, no boundary waste)
  3. C-SCAN ★★★☆☆  (Uniform waiting time)
  4. SCAN   ★★☆☆☆  (Good throughput)
  5. FCFS   ★☆☆☆☆  (Simplest — highest seek count)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        t.insert("1.0", info)
        t.config(state="disabled")

    def show_shortcuts(self):
        win = tk.Toplevel(self.root)
        win.title("Keyboard Shortcuts")
        win.geometry("360x260")
        win.resizable(False, False)
        win.configure(bg=THEME["bg_card"])

        hdr = tk.Frame(win, bg=THEME["bg_sidebar"], height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⌨  Keyboard Shortcuts",
                 font=("Segoe UI", 12, "bold"),
                 bg=THEME["bg_sidebar"], fg="white").pack(side="left", padx=16, pady=8)

        body = tk.Frame(win, bg=THEME["bg_card"], padx=24, pady=16)
        body.pack(fill="both", expand=True)

        shortcuts = [
            ("F5",       "Run All Algorithms"),
            ("F6",       "Visualize Selected"),
            ("F7",       "Show Comparison"),
            ("Ctrl + E", "Export to CSV"),
            ("Delete",   "Clear All"),
        ]
        for key, desc in shortcuts:
            row = tk.Frame(body, bg=THEME["bg_card"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=key, font=("Consolas", 10, "bold"),
                     bg=THEME["bg_input"], fg=THEME["accent_blue"],
                     padx=8, pady=3, width=10).pack(side="left")
            tk.Label(row, text=f"  {desc}", font=("Segoe UI", 10),
                     bg=THEME["bg_card"], fg=THEME["text_primary"]).pack(side="left")


# ─────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────
def main():
    root = tk.Tk()
    app  = DiskSchedulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()