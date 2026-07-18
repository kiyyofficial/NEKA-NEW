["""
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
        self]
