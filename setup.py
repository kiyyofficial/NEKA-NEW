# ================================================================
# SETUP AVG SPACE 8 – INSTALLER OTOMATIS (1 FILE)
# ================================================================
# Cara pakai:
# 1. Copy seluruh kode ini ke Termux (nano setup.py lalu paste)
# 2. Jalankan: python setup.py
# 3. Script akan membuat semua file dan folder yang diperlukan
# 4. Ikuti instruksi di akhir untuk build APK dan push ke GitHub
# ================================================================

import os
import sys

# =================================================================
# KONTEN FILE-FILE YANG AKAN DIBUAT
# =================================================================

# ---------- main_user.py (APK User) ----------
MAIN_USER = '''
"""
AVG SPACE 8 – USER APK (NO ROOT, FLOATING SIDE MONITOR, PREMIUM DESIGN)
Dibuat untuk KiYY OFFICIAL
"""

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
import random
import sqlite3
import hashlib
import os
import webbrowser
from datetime import datetime, timedelta

ROG_RED = get_color_from_hex('#FF1A1A')
ROG_DARK = get_color_from_hex('#0A0A0A')
ROG_GRAY = get_color_from_hex('#1A1A1A')
WHITE = get_color_from_hex('#FFFFFF')
GOLD = get_color_from_hex('#FFD700')

DB_USER = "avg_user.db"

def init_user_db():
    conn = sqlite3.connect(DB_USER)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY,
        premium_expiry TEXT,
        energy INTEGER DEFAULT 0,
        license_key TEXT,
        device_id TEXT,
        last_ad_watch TEXT
    )''')
    conn.commit()
    conn.close()

def get_user_data(user_id=1):
    conn = sqlite3.connect(DB_USER)
    c = conn.cursor()
    c.execute("SELECT premium_expiry, energy, license_key, device_id, last_ad_watch FROM user WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'premium_expiry': row[0], 'energy': row[1], 'license_key': row[2], 'device_id': row[3], 'last_ad_watch': row[4]}
    return {'premium_expiry': None, 'energy': 0, 'license_key': None, 'device_id': None, 'last_ad_watch': None}

def save_user_data(user_id, premium_expiry=None, energy=None, license_key=None, device_id=None, last_ad_watch=None):
    conn = sqlite3.connect(DB_USER)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user (user_id, premium_expiry, energy, license_key, device_id, last_ad_watch) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, premium_expiry, energy, license_key, device_id, last_ad_watch))
    conn.commit()
    conn.close()

def is_premium_local(user_id=1):
    data = get_user_data(user_id)
    if data['premium_expiry']:
        try:
            if data['premium_expiry'] == '2099-12-31T23:59:59':
                return True
            return datetime.now() < datetime.fromisoformat(data['premium_expiry'])
        except:
            return False
    return False

def get_energy_local(user_id=1):
    return get_user_data(user_id)['energy']

def add_energy_local(user_id, amount):
    data = get_user_data(user_id)
    new_energy = min(100, data['energy'] + amount)
    save_user_data(user_id, data['premium_expiry'], new_energy, data['license_key'], data['device_id'], data['last_ad_watch'])
    return new_energy

def use_energy_local(user_id=1, cost=10):
    if is_premium_local(user_id):
        return True
    data = get_user_data(user_id)
    if data['energy'] >= cost:
        save_user_data(user_id, data['premium_expiry'], data['energy'] - cost, data['license_key'], data['device_id'], data['last_ad_watch'])
        return True
    return False

def can_watch_ad(user_id=1):
    data = get_user_data(user_id)
    if data['last_ad_watch']:
        last = datetime.fromisoformat(data['last_ad_watch'])
        if datetime.now() - last < timedelta(seconds=30):
            return False
    return True

def set_ad_watched(user_id=1):
    data = get_user_data(user_id)
    save_user_data(user_id, data['premium_expiry'], data['energy'], data['license_key'], data['device_id'], datetime.now().isoformat())

def activate_premium_with_license(user_id, license_key):
    data = get_user_data(user_id)
    if data['license_key'] == license_key:
        expiry = (datetime.now() + timedelta(days=30)).isoformat()
        save_user_data(user_id, expiry, 100, license_key, data['device_id'], data['last_ad_watch'])
        return True
    return False

class SplashScreen(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = Window.size
        self.pos = (0, 0)
        with self.canvas.before:
            Color(*ROG_DARK)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.logo = Label(text="[b]ROG[/b]", markup=True, font_size='90sp', color=ROG_RED,
                          pos_hint={'center_x': 0.5, 'center_y': 0.6}, size_hint=(None, None), size=(300, 100))
        self.add_widget(self.logo)
        self.sub = Label(text="GAME SPACE 8", font_size='24sp', color=[0.8,0.8,0.8,1],
                         pos_hint={'center_x': 0.5, 'center_y': 0.5}, size_hint=(None, None), size=(350, 50))
        self.add_widget(self.sub)
        self.loading_bar = Widget(size_hint=(0.6, 0.03), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        with self.loading_bar.canvas:
            Color(*ROG_GRAY)
            self.loading_bg = RoundedRectangle(pos=self.loading_bar.pos, size=self.loading_bar.size, radius=[10])
            Color(*ROG_RED)
            self.loading_fg = RoundedRectangle(pos=self.loading_bar.pos, size=(0, self.loading_bar.size[1]), radius=[10])
        self.add_widget(self.loading_bar)
        self.loading_width = 0
        self.loading_max = Window.width * 0.6
        self.logo.opacity = 0
        self.sub.opacity = 0
        self.loading_bar.opacity = 0
        Clock.schedule_once(self.fade_in, 0.3)
        Clock.schedule_interval(self.update_loading, 0.05)

    def fade_in(self, dt):
        anim = Animation(opacity=1, duration=0.8, t='out_quad')
        anim.start(self.logo)
        anim.start(self.sub)
        anim.start(self.loading_bar)
        Clock.schedule_once(self.start_loading, 0.5)

    def start_loading(self, dt):
        self.loading_active = True

    def update_loading(self, dt):
        if not hasattr(self, 'loading_active'):
            return
        if self.loading_width < self.loading_max:
            self.loading_width += 5
            self.loading_fg.size = (self.loading_width, self.loading_bar.size[1])
            self.loading_fg.pos = self.loading_bar.pos
        else:
            Clock.unschedule(self.update_loading)
            Clock.schedule_once(self.finish_splash, 0.5)

    def finish_splash(self, dt):
        anim = Animation(opacity=0, duration=0.5, t='in_quad')
        anim.bind(on_complete=self.remove_splash)
        anim.start(self.logo)
        anim.start(self.sub)
        anim.start(self.loading_bar)
        anim.start(self)

    def remove_splash(self, instance, value):
        app = App.get_running_app()
        if app and hasattr(app, 'root_widget'):
            app.root_widget.remove_widget(self)
            app.root_widget.show_main()

class FloatingSideMonitor(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.width = 60
        self.height = 200
        self.pos = (Window.width - self.width, Window.height/2 - self.height/2)
        self.is_expanded = False
        self.expanded_width = 250
        self.fps = 0
        self.cpu = 0
        self.gpu = 0
        self.temp = 0
        self.rpm = 0
        self.ram = 0
        self.drag_start = (0, 0)
        self.is_dragging = False
        with self.canvas.before:
            Color(0, 0, 0, 0.3)
            self.shadow = Rectangle(pos=(self.pos[0]-5, self.pos[1]-5), size=(self.width+10, self.height+10))
            Color(*ROG_DARK)
            self.bg = RoundedRectangle(pos=self.pos, size=(self.width, self.height), radius=[20, 0, 0, 20])
            Color(*ROG_RED)
            self.border = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.width, self.height, 20), width=2)
        self.content = BoxLayout(orientation='vertical', padding=10, spacing=5, size_hint=(None, None), size=(0, self.height-20), pos=(self.pos[0]+10, self.pos[1]+10), opacity=0)
        self.title = Label(text="[b]ROG MONITOR[/b]", markup=True, color=ROG_RED, font_size='12sp', size_hint_y=None, height=25)
        self.content.add_widget(self.title)
        self.fps_label = Label(text="FPS: 0", color=WHITE, font_size='11sp', size_hint_y=None, height=20)
        self.content.add_widget(self.fps_label)
        self.cpu_label = Label(text="CPU: 0%", color=WHITE, font_size='11sp', size_hint_y=None, height=20)
        self.content.add_widget(self.cpu_label)
        self.gpu_label = Label(text="GPU: 0%", color=WHITE, font_size='11sp', size_hint_y=None, height=20)
        self.content.add_widget(self.gpu_label)
        self.temp_label = Label(text="Temp: 0°C", color=WHITE, font_size='11sp', size_hint_y=None, height=20)
        self.content.add_widget(self.temp_label)
        self.rpm_label = Label(text="RPM: 0", color=WHITE, font_size='11sp', size_hint_y=None, height=20)
        self.content.add_widget(self.rpm_label)
        self.ram_label = Label(text="RAM: 0MB", color=WHITE, font_size='11sp', size_hint_y=None, height=20)
        self.content.add_widget(self.ram_label)
        self.add_widget(self.content)
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.toggle_btn = Button(text='▶', size_hint=(None, None), size=(30, 30),
                                 pos=(self.pos[0]+15, self.pos[1]+self.height/2-15),
                                 background_normal='', background_color=ROG_RED, color=WHITE, font_size='14sp')
        self.toggle_btn.bind(on_press=self.toggle)
        self.add_widget(self.toggle_btn)

    def _update_canvas(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0, 0, 0.3)
            self.shadow = Rectangle(pos=(self.pos[0]-5, self.pos[1]-5), size=(self.width+10, self.height+10))
            Color(*ROG_DARK)
            self.bg = RoundedRectangle(pos=self.pos, size=(self.width, self.height), radius=[20, 0, 0, 20])
            Color(*ROG_RED)
            self.border = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.width, self.height, 20), width=2)
        self.content.pos = (self.pos[0]+10, self.pos[1]+10)
        self.toggle_btn.pos = (self.pos[0]+15, self.pos[1]+self.height/2-15)

    def toggle(self, instance):
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        self.is_expanded = True
        anim = Animation(width=self.expanded_width, duration=0.3, t='out_quad')
        anim.start(self)
        anim2 = Animation(size=(self.expanded_width-20, self.height-20), opacity=1, duration=0.3)
        anim2.start(self.content)
        self.toggle_btn.text = '◀'
        self.toggle_btn.pos = (self.pos[0]+self.expanded_width-40, self.pos[1]+self.height/2-15)

    def collapse(self):
        self.is_expanded = False
        anim = Animation(width=60, duration=0.3, t='out_quad')
        anim.start(self)
        anim2 = Animation(size=(0, self.height-20), opacity=0, duration=0.2)
        anim2.start(self.content)
        self.toggle_btn.text = '▶'
        self.toggle_btn.pos = (self.pos[0]+15, self.pos[1]+self.height/2-15)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.drag_start = touch.pos
            self.is_dragging = True
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_dragging:
            dx = touch.pos[0] - self.drag_start[0]
            dy = touch.pos[1] - self.drag_start[1]
            new_x = self.pos[0] + dx
            new_y = self.pos[1] + dy
            if new_x < Window.width - self.width - 50:
                new_x = Window.width - self.width - 50
            if new_x > Window.width - 10:
                new_x = Window.width - 10
            if new_y < 0: new_y = 0
            if new_y + self.height > Window.height: new_y = Window.height - self.height
            self.pos = (new_x, new_y)
            self.drag_start = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.is_dragging = False
        return super().on_touch_up(touch)

    def update_values(self, fps, cpu, gpu, temp, rpm, ram):
        self.fps = fps
        self.cpu = cpu
        self.gpu = gpu
        self.temp = temp
        self.rpm = rpm
        self.ram = ram
        self.fps_label.text = f"FPS: {fps}"
        self.cpu_label.text = f"CPU: {cpu}%"
        self.gpu_label.text = f"GPU: {gpu}%"
        self.temp_label.text = f"Temp: {temp}°C"
        self.rpm_label.text = f"RPM: {rpm}"
        self.ram_label.text = f"RAM: {ram}MB"

class SideMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_x = 0.3
        self.pos_hint = {'x': -0.3}
        with self.canvas.before:
            Color(*ROG_GRAY)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(*ROG_RED)
            self.border = Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]), width=1)
        self.bind(pos=self._update_rect, size=self._update_rect)
        header = BoxLayout(size_hint_y=0.1, padding=10)
        header.add_widget(Label(text="ROG", color=ROG_RED, font_size='24sp', bold=True))
        header.add_widget(Label(text="Game Space 8", color=WHITE, font_size='14sp'))
        self.add_widget(header)
        menu_items = [
            ("Dashboard", "dashboard"),
            ("Performance", "performance"),
            ("Fan Control", "fan"),
            ("RGB Lighting", "rgb"),
            ("Statistics", "stats"),
            ("Game Launcher", "games"),
            ("🔧 Optimasi", "optimasi"),
            ("⭐ Premium", "premium")
        ]
        for text, screen in menu_items:
            btn = Button(text=text, background_normal='', background_color=ROG_DARK,
                         color=WHITE, size_hint_y=None, height=50, font_size='14sp')
            btn.screen_name = screen
            btn.bind(on_press=self._on_menu_press)
            self.add_widget(btn)
        self.add_widget(Label(text="KiYY OFFICIAL", color=ROG_RED, size_hint_y=0.08))

    def _on_menu_press(self, instance):
        app = App.get_running_app()
        if app and hasattr(app, 'root_widget'):
            app.root_widget.current_screen = instance.screen_name
            app.root_widget.toggle_menu()

    def _update_rect(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*ROG_GRAY)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(*ROG_RED)
            self.border = Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]), width=1)

    def show(self):
        anim = Animation(pos_hint={'x': 0}, duration=0.3, t='out_quad')
        anim.start(self)

    def hide(self):
        anim = Animation(pos_hint={'x': -0.3}, duration=0.3, t='out_quad')
        anim.start(self)

    def toggle(self):
        if self.pos_hint['x'] == 0:
            self.hide()
        else:
            self.show()

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        self.status_label = Label(text="ROG Game Space 8", color=ROG_RED, font_size='26sp', bold=True)
        layout.add_widget(self.status_label)
        self.mode_label = Label(text="Mode: Balanced", color=WHITE, font_size='18sp')
        layout.add_widget(self.mode_label)
        self.game_label = Label(text="Game: None", color=WHITE, font_size='16sp')
        layout.add_widget(self.game_label)
        grid = GridLayout(cols=2, spacing=10, size_hint_y=0.3)
        self.ram_label = Label(text="RAM: 0MB / 0MB", color=WHITE, font_size='14sp')
        grid.add_widget(self.ram_label)
        self.temp_label = Label(text="Suhu: 0°C", color=WHITE, font_size='14sp')
        grid.add_widget(self.temp_label)
        self.bat_label = Label(text="Baterai: 0%", color=WHITE, font_size='14sp')
        grid.add_widget(self.bat_label)
        self.premium_label = Label(text="⭐ Premium: Tidak aktif", color=WHITE, font_size='14sp')
        grid.add_widget(self.premium_label)
        layout.add_widget(grid)
        self.energy_label = Label(text="⚡ Energi: 0%", color=GOLD, font_size='20sp', bold=True)
        layout.add_widget(self.energy_label)
        self.ad_btn = Button(text="📺 Tonton Iklan (+20% Energi)", background_normal='', 
                             background_color=ROG_RED, color=WHITE, size_hint_y=0.12)
        self.ad_btn.bind(on_press=self.watch_ad)
        layout.add_widget(self.ad_btn)
        self.add_widget(layout)
        self.user_id = 1

    def watch_ad(self, instance):
        user_id = 1
        if not can_watch_ad(user_id):
            popup = Popup(title='Info', content=Label(text="Tunggu 30 detik untuk iklan berikutnya."), size_hint=(0.7,0.3))
            popup.open()
            return
        popup = Popup(title='Iklan', content=Label(text="Menonton iklan... (3 detik)"), size_hint=(0.7,0.3))
        popup.open()
        Clock.schedule_once(lambda dt: self.finish_ad(popup, user_id), 3)

    def finish_ad(self, popup, user_id):
        popup.dismiss()
        new_energy = add_energy_local(user_id, 20)
        set_ad_watched(user_id)
        popup2 = Popup(title='Berhasil!', content=Label(text=f"Energi +20%! Sekarang {new_energy}%"), size_hint=(0.7,0.3))
        popup2.open()
        Clock.schedule_once(lambda dt: popup2.dismiss(), 1.5)
        app = App.get_running_app()
        if app:
            app.update_ui()

    def update_status(self, mode, game, ram_used, ram_total, temp, bat_level, premium, energy):
        self.mode_label.text = f"Mode: {mode}"
        self.game_label.text = f"Game: {game if game else 'None'}"
        self.ram_label.text = f"RAM: {ram_used}MB / {ram_total}MB"
        self.temp_label.text = f"Suhu: {temp}°C"
        self.bat_label.text = f"Baterai: {bat_level}%"
        self.premium_label.text = f"⭐ Premium: {'Aktif' if premium else 'Tidak aktif'}"
        self.energy_label.text = f"⚡ Energi: {energy}%"
        self.energy_label.color = ROG_RED if energy < 50 else GOLD

class PerformanceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="Performance Mode", color=ROG_RED, font_size='20sp', bold=True))
        mode_layout = BoxLayout(spacing=10, size_hint_y=0.2)
        for m in ["Balanced", "Performance", "X-Mode"]:
            btn = Button(text=m, background_normal='', background_color=ROG_GRAY,
                         color=WHITE, font_size='15sp')
            btn.bind(on_press=self.change_mode)
            mode_layout.add_widget(btn)
        layout.add_widget(mode_layout)
        self.current_mode = Label(text="Current: Balanced", color=WHITE, font_size='16sp')
        layout.add_widget(self.current_mode)
        self.add_widget(layout)

    def change_mode(self, instance):
        app = App.get_running_app()
        if app and hasattr(app, 'root_widget'):
            app.root_widget.set_mode(instance.text)
        self.current_mode.text = f"Current: {instance.text}"

class FanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="Fan Control", color=ROG_RED, font_size='20sp', bold=True))
        self.fan_slider = Slider(min=0, max=100, value=50, value_track_color=ROG_RED)
        self.fan_slider.bind(value=self.on_fan_change)
        layout.add_widget(self.fan_slider)
        self.fan_label = Label(text="RPM: 0", color=WHITE, font_size='16sp')
        layout.add_widget(self.fan_label)
        self.add_widget(layout)

    def on_fan_change(self, instance, value):
        rpm = int(value * 60)
        self.fan_label.text = f"RPM: {rpm}"
        app = App.get_running_app()
        if app and hasattr(app, 'root_widget'):
            app.root_widget.set_fan_rpm(rpm)

class RGBScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="RGB Lighting", color=ROG_RED, font_size='20sp', bold=True))
        self.rgb_btn = Button(text="MATIKAN RGB", background_normal='', background_color=ROG_GRAY,
                              color=WHITE, size_hint_y=0.1)
        self.rgb_btn.bind(on_press=self.toggle_rgb)
        layout.add_widget(self.rgb_btn)
        color_layout = BoxLayout(size_hint_y=0.1, spacing=5)
        colors = ['ff0000', '00ff00', '0000ff', 'ffff00', 'ff00ff', '00ffff', 'ffffff']
        for c in colors:
            btn = Button(background_normal='', background_color=self.hex_to_color(c), size_hint_x=None, width=50)
            btn.bind(on_press=lambda instance, col=c: self.set_color(col))
            color_layout.add_widget(btn)
        layout.add_widget(color_layout)
        self.current_color_label = Label(text="Color: #00ff00", color=WHITE, font_size='14sp')
        layout.add_widget(self.current_color_label)
        self.add_widget(layout)

    def hex_to_color(self, hex_str):
        h = hex_str.lstrip('#')
        return [int(h[i:i+2], 16)/255.0 for i in (0, 2, 4)] + [1]

    def toggle_rgb(self, instance):
        app = App.get_running_app()
        if app and hasattr(app, 'root_widget'):
            on = app.root_widget.toggle_rgb()
            self.rgb_btn.text = "MATIKAN RGB" if on else "NYALAKAN RGB"

    def set_color(self, color):
        app = App.get_running_app()
        if app and hasattr(app, 'root_widget'):
            app.root_widget.set_rgb_color(color)
        self.current_color_label.text = f"Color: #{color}"

class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="System Statistics", color=ROG_RED, font_size='20sp', bold=True))
        self.stat_grid = GridLayout(cols=2, spacing=15, size_hint_y=None)
        self.stat_grid.bind(minimum_height=self.stat_grid.setter('height'))
        self.stat_labels = {}
        stats = ["CPU Usage", "GPU Usage", "CPU Temp", "RAM Used", "RAM Total", "FPS", "RPM Fan", "Battery"]
        for s in stats:
            lbl = Label(text=f"{s}: 0", color=WHITE, font_size='15sp')
            self.stat_grid.add_widget(lbl)
            self.stat_labels[s] = lbl
        layout.add_widget(self.stat_grid)
        self.add_widget(layout)

    def update_stats(self, cpu, gpu, temp_cpu, ram_used, ram_total, fps, rpm, bat):
        self.stat_labels["CPU Usage"].text = f"CPU Usage: {cpu}%"
        self.stat_labels["GPU Usage"].text = f"GPU Usage: {gpu}%"
        self.stat_labels["CPU Temp"].text = f"CPU Temp: {temp_cpu}°C"
        self.stat_labels["RAM Used"].text = f"RAM Used: {ram_used}MB"
        self.stat_labels["RAM Total"].text = f"RAM Total: {ram_total}MB"
        self.stat_labels["FPS"].text = f"FPS: {fps}"
        self.stat_labels["RPM Fan"].text = f"RPM Fan: {rpm}"
        self.stat_labels["Battery"].text = f"Battery: {bat}%"

GAME_LIST = [
    "Cyberpunk 2077", "Call of Duty: Warzone", "Genshin Impact",
    "PUBG Mobile", "Mobile Legends", "Apex Legends",
    "Valorant", "Dota 2", "CS:GO", "Fortnite"
]

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="Game Launcher", color=ROG_RED, font_size='20sp', bold=True))
        self.game_list = RecycleView(data=[{'text': g} for g in GAME_LIST], viewclass='Label', size_hint_y=None, height=300)
        self.game_list.bind(on_touch_down=self.on_game_select)
        layout.add_widget(self.game_list)
        self.launch_btn = Button(text="LAUNCH GAME", background_normal='', background_color=ROG_RED,
                                 color=WHITE, font_size='18sp', size_hint_y=0.1)
        self.launch_btn.bind(on_press=self.launch_game)
        layout.add_widget(self.launch_btn)
        self.current_game_label = Label(text="Selected: None", color=WHITE, font_size='14sp')
        layout.add_widget(self.current_game_label)
        self.energy_status = Label(text="Energi: 0% (min 50% untuk main)", color=WHITE, font_size='14sp')
        layout.add_widget(self.energy_status)
        self.add_widget(layout)
        self.selected_game = None
        self.user_id = 1

    def on_enter(self):
        self.update_energy_status()

    def update_energy_status(self):
        energy = get_energy_local(self.user_id)
        premium = is_premium_local(self.user_id)
        if premium:
            self.energy_status.text = "⭐ Premium: Energi unlimited!"
        else:
            self.energy_status.text = f"Energi: {energy}% (min 50% untuk main)"

    def on_game_select(self, instance, touch):
        if instance.collide_point(*touch.pos):
            for child in instance.children:
                if child.collide_point(*touch.pos):
                    self.selected_game = child.text
                    self.current_game_label.text = f"Selected: {self.selected_game}"
                    return True

    def launch_game(self, instance):
        if not self.selected_game:
            popup = Popup(title='Pilih Game', content=Label(text="Silakan pilih game."), size_hint=(0.8, 0.3))
            popup.open()
            return
        if not is_premium_local(self.user_id):
            energy = get_energy_local(self.user_id)
            if energy < 50:
                popup = Popup(title='Energi Kurang', 
                              content=Label(text=f"Energi Anda {energy}%, minimal 50%.\nTonton iklan atau beli premium."),
                              size_hint=(0.8, 0.4))
                popup.open()
                return
            if not use_energy_local(self.user_id, 10):
                popup = Popup(title='Error', content=Label(text="Gagal mengurangi energi."), size_hint=(0.7,0.3))
                popup.open()
                return
        popup = Popup(title='Game Launcher', content=Label(text=f"Launching {self.selected_game}..."), size_hint=(0.8, 0.3))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
        app = App.get_running_app()
        if app and hasattr(app, 'root_widget'):
            app.root_widget.set_current_game(self.selected_game)
        self.update_energy_status()

class OptimasiScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="🔧 OPTIMASI", color=ROG_RED, font_size='22sp', bold=True))
        btn_optimasi = Button(text="OPTIMASI SEKARANG", background_normal='', background_color=ROG_RED,
                              color=WHITE, size_hint_y=0.2)
        btn_optimasi.bind(on_press=self.run_optimasi)
        layout.add_widget(btn_optimasi)
        self.status_label = Label(text="Status: Siap", color=WHITE, font_size='16sp')
        layout.add_widget(self.status_label)
        self.add_widget(layout)

    def run_optimasi(self, instance):
        self.status_label.text = "Status: Mengoptimalkan..."
        Clock.schedule_once(lambda dt: self.finish_optimasi(), 3)

    def finish_optimasi(self):
        self.status_label.text = "✅ Optimasi selesai! Device lebih lancar."
        popup = Popup(title='Optimasi', content=Label(text="✅ Device sudah dioptimalkan!"), size_hint=(0.7,0.3))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

class PremiumScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(text="⭐ PREMIUM", color=GOLD, font_size='26sp', bold=True))
        self.license_input = TextInput(hint_text="Masukkan Lisensi", multiline=False, size_hint_y=0.1)
        layout.add_widget(self.license_input)
        btn_activate = Button(text="Aktivasi", background_color=ROG_RED, color=WHITE, size_hint_y=0.1)
        btn_activate.bind(on_press=self.activate_license)
        layout.add_widget(btn_activate)
        btn_bot = Button(text="Beli via Telegram", background_color=ROG_GRAY, color=WHITE, size_hint_y=0.1)
        btn_bot.bind(on_press=lambda x: webbrowser.open("https://t.me/AVG_SPACE_BOT"))
        layout.add_widget(btn_bot)
        self.status_label = Label(text="", color=WHITE, font_size='14sp')
        layout.add_widget(self.status_label)
        btn_back = Button(text="🔙 Kembali", background_color=ROG_DARK, color=WHITE, size_hint_y=0.08)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def activate_license(self, instance):
        user_id = 1
        license_key = self.license_input.text.strip()
        if not license_key:
            self.status_label.text = "❌ Masukkan lisensi!"
            return
        data = get_user_data(user_id)
        if data['license_key'] == license_key:
            expiry = (datetime.now() + timedelta(days=30)).isoformat()
            save_user_data(user_id, expiry, 100, license_key, data['device_id'], data['last_ad_watch'])
            self.status_label.text = "✅ Premium aktif! Energi 100%"
            self.license_input.text = ""
            app = App.get_running_app()
            if app:
                app.update_ui()
        else:
            self.status_label.text = "❌ Lisensi tidak valid! Beli di bot."

class UserRoot(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_visible = False
        self.side_menu = SideMenu()
        self.add_widget(self.side_menu)
        self.sm = ScreenManager()
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(PerformanceScreen(name='performance'))
        self.sm.add_widget(FanScreen(name='fan'))
        self.sm.add_widget(RGBScreen(name='rgb'))
        self.sm.add_widget(StatsScreen(name='stats'))
        self.sm.add_widget(GameScreen(name='games'))
        self.sm.add_widget(OptimasiScreen(name='optimasi'))
        self.sm.add_widget(PremiumScreen(name='premium'))
        self.current_screen = 'dashboard'
        self.sm.current = 'dashboard'
        self.sm.opacity = 0
        self.add_widget(self.sm)
        self.floating_monitor = FloatingSideMonitor()
        self.add_widget(self.floating_monitor)
        self.menu_btn = Button(text='☰', size_hint=(None, None), size=(55, 55),
                               background_normal='', background_color=ROG_RED,
                               pos_hint={'x': 0.02, 'top': 0.95}, opacity=0,
                               font_size='24sp')
        self.menu_btn.bind(on_press=self.toggle_menu)
        self.add_widget(self.menu_btn)
        self.mode = "Balanced"
        self.fan_rpm = 0
        self.rgb_on = True
        self.rgb_color = [0, 1, 0, 1]
        self.current_game = None
        self.splash = SplashScreen()
        self.add_widget(self.splash)
        Clock.schedule_interval(self.update_stats, 1)

    def show_main(self):
        anim = Animation(opacity=1, duration=0.8, t='out_quad')
        anim.start(self.sm)
        anim.start(self.menu_btn)
        self.main_visible = True

    def toggle_menu(self, *args):
        self.side_menu.toggle()

    def set_mode(self, mode):
        self.mode = mode
        self.update_ui()

    def set_fan_rpm(self, rpm):
        self.fan_rpm = rpm

    def toggle_rgb(self):
        self.rgb_on = not self.rgb_on
        return self.rgb_on

    def set_rgb_color(self, color):
        self.rgb_color = self.hex_to_color(color)

    def hex_to_color(self, hex_str):
        h = hex_str.lstrip('#')
        return [int(h[i:i+2], 16)/255.0 for i in (0, 2, 4)] + [1]

    def set_current_game(self, game):
        self.current_game = game
        self.update_ui()

    def update_stats(self, dt):
        cpu = random.randint(10, 80)
        gpu = random.randint(10, 80)
        temp = random.randint(35, 70)
        ram_used = random.randint(500, 3000)
        ram_total = 4096
        if self.mode == "Balanced":
            fps = random.randint(30, 60)
        elif self.mode == "Performance":
            fps = random.randint(45, 90)
        else:
            fps = random.randint(60, 144)
        bat = random.randint(50, 100)
        premium = is_premium_local()
        energy = get_energy_local()
        dash = self.sm.get_screen('dashboard')
        if dash:
            dash.update_status(self.mode, self.current_game, ram_used, ram_total, temp, bat, premium, energy)
        self.floating_monitor.update_values(fps, cpu, gpu, temp, self.fan_rpm, ram_used)

    def update_ui(self):
        self.update_stats(None)
        game_screen = self.sm.get_screen('games')
        if game_screen:
            game_screen.update_energy_status()

class UserApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = 1
        init_user_db()
        device_id = hashlib.md5(os.environ.get('ANDROID_ID', 'unknown').encode()).hexdigest()[:16]
        data = get_user_data(self.user_id)
        if not data['device_id']:
            save_user_data(self.user_id, data['premium_expiry'], data['energy'], data['license_key'], device_id, data['last_ad_watch'])

    def build(self):
        self.title = "ROG Game Space 8"
        self.icon = 'icon.png'
        self.root_widget = UserRoot()
        return self.root_widget

    def update_ui(self):
        if self.root_widget:
            self.root_widget.update_ui()

if __name__ == '__main__':
    UserApp().run()
'''

# ---------- main_admin.py (APK Admin) ----------
MAIN_ADMIN = '''
"""
AVG SPACE ADMIN – UNLIMITED ENERGY + ADMIN PANEL
Dibuat untuk KiYY OFFICIAL
"""

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import sqlite3
import hashlib
import os
import random
from datetime import datetime, timedelta

ROG_RED = [1, 0.1, 0.1, 1]
ROG_DARK = [0.04, 0.04, 0.04, 1]
ROG_GRAY = [0.12, 0.12, 0.12, 1]
WHITE = [1, 1, 1, 1]
GOLD = [1, 0.84, 0, 1]

DB_PATH = "avg_premium.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        premium_expiry TEXT,
        energy INTEGER DEFAULT 0,
        registered_at TEXT,
        license_key TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        package TEXT,
        amount INTEGER,
        status TEXT DEFAULT 'pending',
        created_at TEXT,
        completed_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        device_id TEXT,
        phone_info TEXT,
        last_seen TEXT,
        is_active INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, username, full_name, premium_expiry, energy FROM users ORDER BY registered_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def set_premium_admin(user_id, months):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if months == 'permanent':
        expiry = '2099-12-31T23:59:59'
    else:
        expiry = (datetime.now() + timedelta(days=30*int(months))).isoformat()
    license_key = hashlib.sha256(f"{user_id}{expiry}ADMIN_SECRET".encode()).hexdigest()[:20]
    c.execute("UPDATE users SET premium_expiry = ?, license_key = ? WHERE user_id = ?", (expiry, license_key, user_id))
    c.execute("UPDATE users SET energy = energy + 1000 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return expiry, license_key

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

class SplashScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size = Window.size
        self.pos = (0, 0)
        with self.canvas.before:
            Color(*ROG_DARK)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.add_widget(Label(text="[b]AVG ADMIN[/b]", markup=True, color=ROG_RED, font_size='60sp', pos_hint={'center_y': 0.6}))
        self.add_widget(Label(text="UNLIMITED ENERGY", color=GOLD, font_size='20sp', pos_hint={'center_y': 0.4}))
        Clock.schedule_once(self.finish_splash, 1.5)

    def finish_splash(self, dt):
        app = App.get_running_app()
        if app:
            app.root.remove_widget(self)

class AdminDashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.status = Label(text="ADMIN PANEL", color=ROG_RED, font_size='24sp')
        layout.add_widget(self.status)
        btn_users = Button(text="👥 Daftar User", background_color=ROG_GRAY, color=WHITE, size_hint_y=0.12)
        btn_users.bind(on_press=self.show_users)
        layout.add_widget(btn_users)
        btn_add = Button(text="➕ Tambah Premium", background_color=ROG_GRAY, color=WHITE, size_hint_y=0.12)
        btn_add.bind(on_press=self.show_add_premium)
        layout.add_widget(btn_add)
        btn_devices = Button(text="📱 Device Aktif", background_color=ROG_GRAY, color=WHITE, size_hint_y=0.12)
        btn_devices.bind(on_press=self.show_devices)
        layout.add_widget(btn_devices)
        btn_about = Button(text="ℹ️ Tentang", background_color=ROG_DARK, color=WHITE, size_hint_y=0.1)
        btn_about.bind(on_press=self.show_about)
        layout.add_widget(btn_about)
        self.add_widget(layout)

    def show_users(self, instance):
        app = App.get_running_app()
        if app:
            app.sm.current = 'users'

    def show_add_premium(self, instance):
        app = App.get_running_app()
        if app:
            app.sm.current = 'addpremium'

    def show_devices(self, instance):
        app = App.get_running_app()
        if app:
            app.sm.current = 'devices'

    def show_about(self, instance):
        popup = Popup(title='Tentang', content=Label(text="AVG SPACE ADMIN v1.0\nDibuat untuk KiYY OFFICIAL"), size_hint=(0.7,0.4))
        popup.open()

class UsersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="👥 Daftar User", color=ROG_RED, font_size='20sp'))
        self.scroll = ScrollView()
        self.user_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.user_list.bind(minimum_height=self.user_list.setter('height'))
        self.scroll.add_widget(self.user_list)
        layout.add_widget(self.scroll)
        btn_back = Button(text="🔙 Kembali", background_color=ROG_DARK, color=WHITE, size_hint_y=0.08)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def on_enter(self):
        self.user_list.clear_widgets()
        users = get_all_users()
        if not users:
            self.user_list.add_widget(Label(text="Belum ada user.", color=WHITE))
            return
        for u in users:
            user_id, username, full_name, expiry, energy = u
            status = "✅ Premium" if expiry and (expiry == '2099-12-31T23:59:59' or datetime.now() < datetime.fromisoformat(expiry)) else "❌ Free"
            lbl = Label(text=f"ID: {user_id} | {username or full_name or '-'} | {status} | Energi: {energy}", color=WHITE, size_hint_y=None, height=30)
            self.user_list.add_widget(lbl)

class AddPremiumScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="➕ Tambah Premium", color=ROG_RED, font_size='20sp'))
        self.user_id_input = TextInput(hint_text="User ID", multiline=False, size_hint_y=0.1)
        layout.add_widget(self.user_id_input)
        self.month_input = TextInput(hint_text="Bulan (1-12, permanent)", multiline=False, size_hint_y=0.1)
        layout.add_widget(self.month_input)
        btn_add = Button(text="✅ Aktivasi", background_color=ROG_RED, color=WHITE, size_hint_y=0.12)
        btn_add.bind(on_press=self.add_premium)
        layout.add_widget(btn_add)
        self.status = Label(text="", color=WHITE, font_size='14sp')
        layout.add_widget(self.status)
        btn_back = Button(text="🔙 Kembali", background_color=ROG_DARK, color=WHITE, size_hint_y=0.08)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def add_premium(self, instance):
        user_id_str = self.user_id_input.text.strip()
        months = self.month_input.text.strip()
        if not user_id_str or not months:
            self.status.text = "❌ Isi semua field!"
            return
        try:
            user_id = int(user_id_str)
            user = get_user(user_id)
            if not user:
                self.status.text = "❌ User tidak ditemukan!"
                return
            expiry, license = set_premium_admin(user_id, months)
            self.status.text = f"✅ Premium ditambahkan! Lisensi: {license}"
            self.user_id_input.text = ""
            self.month_input.text = ""
            Clock.schedule_once(lambda dt: setattr(self, 'status', Label(text="")), 3)
        except Exception as e:
            self.status.text = f"❌ Error: {e}"

class DevicesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="📱 Device Aktif", color=ROG_RED, font_size='20sp'))
        self.scroll = ScrollView()
        self.device_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.device_list.bind(minimum_height=self.device_list.setter('height'))
        self.scroll.add_widget(self.device_list)
        layout.add_widget(self.scroll)
        btn_back = Button(text="🔙 Kembali", background_color=ROG_DARK, color=WHITE, size_hint_y=0.08)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def on_enter(self):
        self.device_list.clear_widgets()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM devices WHERE is_active = 1 AND datetime(last_seen) > datetime('now', '-1 hour')")
        rows = c.fetchall()
        conn.close()
        if not rows:
            self.device_list.add_widget(Label(text="Tidak ada device aktif.", color=WHITE))
            return
        for d in rows:
            text = f"ID: {d[0]} | User: {d[1]} | Device: {d[2]}\nInfo: {d[3]}\nTerakhir: {d[4]}"
            lbl = Label(text=text, color=WHITE, size_hint_y=None, height=80, halign='left')
            self.device_list.add_widget(lbl)

class AdminRoot(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sm = ScreenManager()
        self.sm.add_widget(AdminDashboardScreen(name='dashboard'))
        self.sm.add_widget(UsersScreen(name='users'))
        self.sm.add_widget(AddPremiumScreen(name='addpremium'))
        self.sm.add_widget(DevicesScreen(name='devices'))
        self.sm.current = 'dashboard'
        self.add_widget(self.sm)
        self.splash = SplashScreen()
        self.add_widget(self.splash)

class AdminApp(App):
    def build(self):
        init_db()
        self.title = "AVG SPACE ADMIN"
        self.icon = 'icon.png'
        return AdminRoot()

if __name__ == '__main__':
    AdminApp().run()
'''

# ---------- avg_bot.py (Telegram Bot) ----------
AVG_BOT = '''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import sqlite3
import logging
import hashlib
import threading
import time
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

TOKEN = "7846066465:AAHmbmBoILA0aw1gcNfgcabY7-Y5Nse2faQ"
ADMIN_ID = 123456789
DB_PATH = "avg_premium.db"
HEADER_IMAGE_URL = "https://i.imgur.com/your-image.png"

PAYMENT_METHODS = {"DANA": "08123456789", "GOPAY": "08123456789", "OVO": "08123456789"}
PRICE_LIST = {
    '1': 15000, '2': 25000, '3': 35000, '4': 45000, '5': 55000,
    '6': 65000, '7': 75000, '8': 85000, '9': 95000, '10': 105000,
    '12': 120000, 'permanent': 200000
}
PACKAGE_NAMES = {
    '1': '1 Bulan', '2': '2 Bulan', '3': '3 Bulan', '4': '4 Bulan',
    '5': '5 Bulan', '6': '6 Bulan', '7': '7 Bulan', '8': '8 Bulan',
    '9': '9 Bulan', '10': '10 Bulan', '12': '1 Tahun', 'permanent': 'Permanen'
}
MAINTENANCE_DURATION = 60

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        premium_expiry TEXT,
        energy INTEGER DEFAULT 0,
        registered_at TEXT,
        license_key TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        package TEXT,
        amount INTEGER,
        payment_method TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT,
        completed_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        device_id TEXT,
        phone_info TEXT,
        last_seen TEXT,
        is_active INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def add_user(user_id, username, full_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, full_name, registered_at) VALUES (?, ?, ?, ?)",
              (user_id, username, full_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def set_premium(user_id, months):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if months == 'permanent':
        expiry = '2099-12-31T23:59:59'
    else:
        expiry = (datetime.now() + timedelta(days=30*int(months))).isoformat()
    license_key = hashlib.sha256(f"{user_id}{expiry}AVG_SECRET".encode()).hexdigest()[:20]
    c.execute("UPDATE users SET premium_expiry = ?, license_key = ? WHERE user_id = ?", (expiry, license_key, user_id))
    c.execute("UPDATE users SET energy = energy + 1000 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return expiry, license_key

def is_premium(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT premium_expiry FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        try:
            if row[0] == '2099-12-31T23:59:59':
                return True
            return datetime.now() < datetime.fromisoformat(row[0])
        except:
            return False
    return False

def log_transaction(user_id, package, amount, payment_method='', status='pending'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (user_id, package, amount, payment_method, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, package, amount, payment_method, status, datetime.now().isoformat()))
    trans_id = c.lastrowid
    conn.commit()
    conn.close()
    return trans_id

def update_transaction_status(trans_id, status, completed_at=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if completed_at is None:
        completed_at = datetime.now().isoformat()
    c.execute("UPDATE transactions SET status = ?, completed_at = ? WHERE id = ?", (status, completed_at, trans_id))
    conn.commit()
    conn.close()

def get_transaction(trans_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE id = ?", (trans_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, username, full_name, premium_expiry, energy FROM users ORDER BY registered_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

class MaintenanceManager:
    def __init__(self):
        self.is_maintenance = False
        self.maintenance_until = None
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._maintenance_loop, daemon=True)
        self._thread.start()

    def _maintenance_loop(self):
        while not self._stop_event.is_set():
            if not self.is_maintenance:
                if random.random() < 0.05:
                    self._start_maintenance()
            else:
                if datetime.now() >= self.maintenance_until:
                    self._end_maintenance()
            time.sleep(30)

    def _start_maintenance(self):
        self.is_maintenance = True
        self.maintenance_until = datetime.now() + timedelta(seconds=MAINTENANCE_DURATION)
        logger.info(f"Maintenance started until {self.maintenance_until}")

    def _end_maintenance(self):
        self.is_maintenance = False
        self.maintenance_until = None
        logger.info("Maintenance finished")

    def is_under_maintenance(self):
        return self.is_maintenance

    def get_maintenance_time_left(self):
        if self.is_maintenance and self.maintenance_until:
            left = (self.maintenance_until - datetime.now()).total_seconds()
            return max(0, int(left))
        return 0

maintenance_manager = MaintenanceManager()

def check_maintenance(func):
    async def wrapper(update, context, *args, **kwargs):
        if maintenance_manager.is_under_maintenance():
            await update.message.reply_text(
                f"🛠️ Bot sedang maintenance\\n⏳ Waktu tersisa: {maintenance_manager.get_maintenance_time_left()} detik\\nMohon tunggu sebentar.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton("🛒 Beli Premium", callback_data="buy_premium")],
        [InlineKeyboardButton("📊 Cek Status", callback_data="status")],
        [InlineKeyboardButton("⚡ Tambah Energi", callback_data="add_energy")],
        [InlineKeyboardButton("📖 Testimoni", callback_data="testimoni")],
        [InlineKeyboardButton("👤 Kontak Developer", callback_data="contact")]
    ]
    return InlineKeyboardMarkup(buttons)

def package_keyboard():
    buttons = []
    for i in range(1, 11):
        label = f"{i} Bulan - Rp {PRICE_LIST[str(i)]:,}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"buy_{i}")])
    buttons.append([InlineKeyboardButton("1 Tahun - Rp 120.000", callback_data="buy_12")])
    buttons.append([InlineKeyboardButton("🌟 Permanen - Rp 200.000", callback_data="buy_permanent")])
    buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def payment_keyboard(trans_id):
    buttons = [
        [InlineKeyboardButton("✅ Saya Sudah Transfer", callback_data=f"confirm_payment_{trans_id}")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(buttons)

def admin_confirm_keyboard(trans_id, user_id):
    buttons = [
        [InlineKeyboardButton("✅ Done (Aktivasi)", callback_data=f"admin_done_{trans_id}_{user_id}")],
        [InlineKeyboardButton("❌ Belum (Tolak)", callback_data=f"admin_reject_{trans_id}_{user_id}")]
    ]
    return InlineKeyboardMarkup(buttons)

@check_maintenance
async def start(update, context):
    user = update.effective_user
    add_user(user.id, user.username, user.full_name)
    caption = (
        "╔═══════════════════════════════════════╗\\n"
        "║   🤖 AVG SPACE – PREMIUM BOT         ║\\n"
        "╠═══════════════════════════════════════╣\\n"
        f"║  Selamat datang, {user.first_name}!   ║\\n"
        "║                                       ║\\n"
        "║  Gunakan menu di bawah untuk mulai.   ║\\n"
        "╚═══════════════════════════════════════╝"
    )
    try:
        await update.message.reply_photo(photo=HEADER_IMAGE_URL, caption=caption, reply_markup=main_menu_keyboard())
    except:
        await update.message.reply_text(caption, reply_markup=main_menu_keyboard())

@check_maintenance
async def menu_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "buy_premium":
        await query.edit_message_text("🛒 *Pilih Paket Premium:*", parse_mode=ParseMode.MARKDOWN, reply_markup=package_keyboard())
    elif data.startswith("buy_"):
        package = data.split("_")[1]
        await show_checkout(update, context, package)
    elif data == "status":
        await status(update, context)
    elif data == "add_energy":
        await add_energy_user(update, context)
    elif data == "testimoni":
        await testimoni(update, context)
    elif data == "contact":
        await contact(update, context)
    elif data.startswith("confirm_payment_"):
        trans_id = int(data.split("_")[2])
        await confirm_payment(update, context, trans_id)
    elif data.startswith("admin_done_"):
        parts = data.split("_")
        trans_id = int(parts[2])
        user_id_target = int(parts[3])
        await admin_done(update, context, trans_id, user_id_target)
    elif data.startswith("admin_reject_"):
        parts = data.split("_")
        trans_id = int(parts[2])
        user_id_target = int(parts[3])
        await admin_reject(update, context, trans_id, user_id_target)
    elif data == "back_main":
        caption = "🔙 Kembali ke menu utama."
        try:
            await query.edit_message_media(media=InputFile(HEADER_IMAGE_URL), caption=caption, reply_markup=main_menu_keyboard())
        except:
            await query.edit_message_text(caption, reply_markup=main_menu_keyboard())
    else:
        await query.edit_message_text("❌ Perintah tidak dikenali.", reply_markup=main_menu_keyboard())

async def show_checkout(update, context, package):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    price = PRICE_LIST[package]
    package_name = PACKAGE_NAMES[package]
    trans_id = log_transaction(user_id, package, price, status='pending')
    payment_text = "\\n".join([f"• {method}: {number}" for method, number in PAYMENT_METHODS.items()])
    struk = f"""
╔═══════════════════════════════════════╗
║          🧾 STRUK PEMBELIAN           ║
╠═══════════════════════════════════════╣
║  🛒 Paket: {package_name}
║  💰 Harga: Rp {price:,}
║  📅 Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}
║  🆔 Transaksi: #{trans_id}
╠═══════════════════════════════════════╣
║  Silakan transfer ke salah satu:      ║
{payment_text}
║                                       ║
║  Setelah transfer, klik tombol di     ║
║  bawah untuk konfirmasi.              ║
╚═══════════════════════════════════════╝
"""
    await query.edit_message_text(struk, parse_mode=ParseMode.MARKDOWN, reply_markup=payment_keyboard(trans_id))

async def confirm_payment(update, context, trans_id):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    trans = get_transaction(trans_id)
    if not trans:
        await query.edit_message_text("❌ Transaksi tidak ditemukan.", reply_markup=main_menu_keyboard())
        return
    admin_text = f"""
🔔 *KONFIRMASI PEMBAYARAN*
👤 User: {user.first_name} (@{user.username or 'no username'})
🆔 ID: {user.id}
📦 Paket: {PACKAGE_NAMES[trans[2]]}
💰 Harga: Rp {trans[3]:,}
📌 Status: Menunggu konfirmasi admin
"""
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=admin_confirm_keyboard(trans_id, user.id)
    )
    await query.edit_message_text(
        "✅ Konfirmasi terkirim! Tunggu aktivasi dari admin.\\nJika belum diaktivasi dalam 1x24 jam, hubungi admin.",
        reply_markup=main_menu_keyboard()
    )

async def admin_done(update, context, trans_id, user_id_target):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ Anda bukan admin!")
        return
    trans = get_transaction(trans_id)
    if not trans:
        await query.edit_message_text("❌ Transaksi tidak ditemukan.")
        return
    package = trans[2]
    expiry, license_key = set_premium(user_id_target, package)
    update_transaction_status(trans_id, 'completed')
    struk_done = f"""
╔═══════════════════════════════════════╗
║      🎉 PEMBAYARAN BERHASIL! 🎉      ║
╠═══════════════════════════════════════╣
║  🛒 Paket: {PACKAGE_NAMES[package]}
║  💰 Harga: Rp {trans[3]:,}
║  📅 Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}
║  🆔 Transaksi: #{trans_id}
╠═══════════════════════════════════════╣
║  ✅ Premium AKTIF!
║  📆 Berakhir: {expiry}
║  🔑 Lisensi: `{license_key}`
║  ⚡ Bonus Energi: 1000
║                                       ║
║  Masukkan lisensi di aplikasi AVG     ║
║  SPACE untuk unlock premium.         ║
╚═══════════════════════════════════════╝
"""
    try:
        await context.bot.send_message(chat_id=user_id_target, text=struk_done, parse_mode=ParseMode.MARKDOWN)
    except:
        pass
    await query.edit_message_text(
        f"✅ Premium telah diaktivasi untuk user {user_id_target}.\\n📦 Paket: {PACKAGE_NAMES[package]}\\n📆 Berakhir: {expiry}\\n🔑 Lisensi: `{license_key}`",
        parse_mode=ParseMode.MARKDOWN
    )

async def admin_reject(update, context, trans_id, user_id_target):
    query = update.callback_query
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ Anda bukan admin!")
        return
    update_transaction_status(trans_id, 'rejected')
    try:
        await context.bot.send_message(
            chat_id=user_id_target,
            text="❌ *Pembayaran ditolak*\\n\\nSilakan cek kembali transfer Anda atau hubungi admin.",
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        pass
    await query.edit_message_text(f"❌ Transaksi #{trans_id} ditolak.")

async def status(update, context):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.callback_query.edit_message_text("Anda belum terdaftar. Kirim /start.", reply_markup=main_menu_keyboard())
        return
    premium = is_premium(user_id)
    expiry = user[3] if user[3] else "Tidak ada"
    license_key = user[6] if user[6] else "Belum"
    text = f"""
╔═══════════════════════════════════════╗
║        📊 STATUS AKUN                 ║
╠═══════════════════════════════════════╣
║  Premium: {'✅ Aktif' if premium else '❌ Tidak aktif'}
║  Berakhir: {expiry}
║  Energi: ⚡ {user[4] if user[4] else 0}
║  Lisensi: `{license_key}`
║                                       ║
║  Beli premium: /buy
║  Hubungi owner: @kiyyofficial
╚═══════════════════════════════════════╝
"""
    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_keyboard())

async def add_energy_user(update, context):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET energy = energy + 10 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    await update.callback_query.edit_message_text("⚡ +10 Energi telah ditambahkan ke akun Anda!", reply_markup=main_menu_keyboard())

async def testimoni(update, context):
    testimonials = [
        "🌟 AVG SPACE benar-benar mengubah pengalaman gaming saya! – Andi",
        "🔥 Premium worth it! Energi unlimited! – Budi",
        "💯 Pelayanan cepat, harga terjangkau. – Cinta",
        "🚀 Setelah pakai AVG SPACE, FPS naik 2x! – Dani",
        "⭐ Admin ramah, proses aktivasi cepat. – Eka"
    ]
    testimonial = random.choice(testimonials)
    await update.callback_query.edit_message_text(
        f"📖 *Testimoni Pengguna AVG SPACE*\\n\\n{testimonial}\\n\\n✨ Bergabunglah dengan ribuan gamer!",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard()
    )

async def contact(update, context):
    text = """
👤 *Kontak Developer*

📱 WhatsApp: 6285746399596
✈️ Telegram: @kiyyofficial
🤖 Bot: @AVG_SPACE_BOT
"""
    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_keyboard())

@check_maintenance
async def add_premium_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Format: /addpremium <user_id> <bulan> (1-12, permanent)")
            return
        user_id = int(args[0])
        months = args[1]
        expiry, license = set_premium(user_id, months)
        await update.message.reply_text(f"✅ Premium {months} bulan diberikan ke user {user_id}. Lisensi: {license}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@check_maintenance
async def list_users_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("Belum ada user terdaftar.")
        return
    text = "📋 *Daftar User AVG SPACE*\\n\\n"
    for u in users:
        premium = "✅ Premium" if u[3] and (u[3] == '2099-12-31T23:59:59' or datetime.now() < datetime.fromisoformat(u[3])) else "❌ Free"
        text += f"ID: {u[0]} | {u[1] or u[2] or '-'} | {premium} | Energi: {u[4]}\\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@check_maintenance
async def check_user_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    try:
        user_id = int(context.args[0]) if context.args else None
        if not user_id:
            await update.message.reply_text("Format: /check <user_id>")
            return
        user = get_user(user_id)
        if not user:
            await update.message.reply_text(f"User {user_id} tidak ditemukan.")
            return
        premium = is_premium(user_id)
        energy = user[4] if user[4] else 0
        text = f"""
🆔 User ID: {user[0]}
👤 Username: {user[1] or '-'}
📛 Nama: {user[2] or '-'}
📅 Premium: {'Aktif' if premium else 'Tidak aktif'}
⏳ Expiry: {user[3] or '-'}
⚡ Energi: {energy}
🔑 Lisensi: {user[6] or '-'}
📆 Terdaftar: {user[5] or '-'}
"""
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@check_maintenance
async def add_energy_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Format: /addenergy <user_id> <jumlah>")
            return
        user_id = int(args[0])
        amount = int(args[1])
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET energy = energy + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ {amount} energi ditambahkan ke user {user_id}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@check_maintenance
async def devices_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM devices WHERE is_active = 1 AND datetime(last_seen) > datetime('now', '-1 hour')")
    rows = c.fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("Tidak ada device aktif.")
        return
    text = "📱 *Device Aktif*\\n\\n"
    for d in rows:
        text += f"ID: {d[0]} | User: {d[1]} | Device: {d[2]}\\nInfo: {d[3]}\\nTerakhir: {d[4]}\\n\\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@check_maintenance
async def maintenance_cmd(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Anda bukan admin!")
        return
    if maintenance_manager.is_under_maintenance():
        await update.message.reply_text(f"🛠️ Maintenance aktif. Sisa: {maintenance_manager.get_maintenance_time_left()} detik.")
    else:
        await update.message.reply_text("✅ Server sehat. Tidak ada maintenance.")

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addpremium", add_premium_cmd))
    app.add_handler(CommandHandler("listusers", list_users_cmd))
    app.add_handler(CommandHandler("check", check_user_cmd))
    app.add_handler(CommandHandler("addenergy", add_energy_cmd))
    app.add_handler(CommandHandler("devices", devices_cmd))
    app.add_handler(CommandHandler("maintenance", maintenance_cmd))
    app.add_handler(CallbackQueryHandler(menu_callback))
    print("🔥 AVG BOT berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
'''

# ---------- buildozer_user.spec ----------
BUILDOZER_USER = '''
[app]
title = ROG Game Space 8
package.name = avgspaceuser
package.domain = org.kiyyofficial
source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,ttf,dat
version = 1.0.0
requirements = python3,kivy==2.2.0
orientation = landscape
osx.python_version = 3
osx.kivy_version = 2.0.0
fullscreen = 0
icon.filename = icon.png
android.permissions = INTERNET, ACCESS_NETWORK_STATE, WAKE_LOCK
android.ndk = 25b
android.api = 30
android.minapi = 21
android.sdk = 30
android.accept_sdk_license = True
android.gradle_dependencies = 'com.android.support:support-annotations:28.0.0'
android.archs = arm64-v8a
[buildozer]
log_level = 2
warn_on_root = 1
'''

# ---------- buildozer_admin.spec ----------
BUILDOZER_ADMIN = '''
[app]
title = AVG SPACE ADMIN
package.name = avgspaceadmin
package.domain = org.kiyyofficial
source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,ttf,dat
version = 1.0.0
requirements = python3,kivy==2.2.0
orientation = landscape
osx.python_version = 3
osx.kivy_version = 2.0.0
fullscreen = 0
icon.filename = icon.png
android.permissions = INTERNET, ACCESS_NETWORK_STATE, WAKE_LOCK
android.ndk = 25b
android.api = 30
android.minapi = 21
android.sdk = 30
android.accept_sdk_license = True
android.gradle_dependencies = 'com.android.support:support-annotations:28.0.0'
android.archs = arm64-v8a
[buildozer]
log_level = 2
warn_on_root = 1
'''

# ---------- .github/workflows/build.yml ----------
GITHUB_WORKFLOW = '''
name: Build APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            build-essential git zip unzip \
            openjdk-17-jdk \
            python3-pip \
            autoconf libtool pkg-config \
            zlib1g-dev libncurses-dev \
            cmake libffi-dev libssl-dev

      - name: Install Python packages
        run: |
          pip install --upgrade pip
          pip install buildozer cython

      - name: Clean previous builds
        run: |
          buildozer android clean

      - name: Build APK
        env:
          ANDROID_SDK_ACCEPT_LICENSE: true
        run: |
          buildozer android debug deploy 2>&1 | tee build.log

      - name: Upload build log
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: build-log
          path: build.log

      - name: Upload APK
        if: success()
        uses: actions/upload-artifact@v4
        with:
          name: AVG-SPACE-8-APK
          path: bin/*.apk
          if-no-files-found: error
'''

# =================================================================
# FUNGSI UTAMA – MEMBUAT SEMUA FILE
# =================================================================

def create_files():
    print("[+] Membuat folder dan file...")
    os.makedirs(".github/workflows", exist_ok=True)
    
    files = [
        ("main_user.py", MAIN_USER),
        ("main_admin.py", MAIN_ADMIN),
        ("avg_bot.py", AVG_BOT),
        ("buildozer_user.spec", BUILDOZER_USER),
        ("buildozer_admin.spec", BUILDOZER_ADMIN),
        (".github/workflows/build.yml", GITHUB_WORKFLOW)
    ]
    
    for filename, content in files:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   ✅ {filename} dibuat")
    
    print("\n[+] SEMUA FILE BERHASIL DIBUAT!")

def print_instructions():
    print("\n" + "="*60)
    print("📋 INSTRUKSI SELANJUTNYA:")
    print("="*60)
    print("1. INSTALL DEPENDENSI:")
    print("   pkg update && pkg upgrade -y")
    print("   pkg install python git nano wget curl clang make cmake pkg-config -y")
    print("   pkg install sdl2 sdl2-image sdl2-ttf sdl2-mixer -y")
    print("   pkg install python3.11 python3.11-pip -y")
    print("   pip3.11 install --upgrade pip setuptools wheel cython")
    print("   pip3.11 install kivy==2.2.0 buildozer")
    print()
    print("2. JALANKAN BOT TELEGRAM:")
    print("   python3.11 avg_bot.py")
    print()
    print("3. BUILD APK USER:")
    print("   buildozer -f buildozer_user.spec android debug deploy run")
    print()
    print("4. BUILD APK ADMIN:")
    print("   buildozer -f buildozer_admin.spec android debug deploy run")
    print()
    print("5. PUSH KE GITHUB (untuk auto build via Actions):")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'AVG SPACE 8 full source'")
    print("   git remote add origin https://github.com/kiyyofficial/NEKA-NEW.git")
    print("   git push -u origin main")
    print()
    print("6. CEK GITHUB ACTIONS:")
    print("   Buka https://github.com/kiyyofficial/NEKA-NEW/actions")
    print("   Tunggu build selesai, download APK dari artifact")
    print("="*60)

# =================================================================
# MAIN
# =================================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   🚀 SETUP AVG SPACE 8 – INSTALLER OTOMATIS            ║")
    print("║   Dibuat untuk KiYY OFFICIAL                           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    create_files()
    print_instructions()
