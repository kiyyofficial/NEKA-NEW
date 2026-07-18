cat > main.py << 'EOF'
"""
VGX SPACE 8 - XAZEX EDITION
Aplikasi Game Space dengan fitur: Splash, Side Menu, Floating Monitor, Performance, Fan, RGB, Stats, Game Launcher
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
from kivy.graphics import Color, Rectangle, Line
from kivy.animation import Animation
from kivy.core.window import Window
import random

VGX_RED = [1, 0.1, 0.1, 1]
VGX_DARK = [0.04, 0.04, 0.04, 1]
VGX_GRAY = [0.12, 0.12, 0.12, 1]
WHITE = [1, 1, 1, 1]

GAME_LIST = [
    "Cyberpunk 2077",
    "Call of Duty: Warzone",
    "Genshin Impact",
    "PUBG Mobile",
    "Mobile Legends",
    "Apex Legends",
    "Valorant",
    "Dota 2",
    "CS:GO",
    "Fortnite"
]

class SplashScreen(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = Window.size
        self.pos = (0, 0)
        with self.canvas.before:
            Color(*VGX_DARK)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.logo_text = Label(
            text="[b]VGX[/b]",
            markup=True,
            font_size='60sp',
            color=VGX_RED,
            pos_hint={'center_x': 0.5, 'center_y': 0.55},
            size_hint=(None, None),
            size=(200, 60)
        )
        self.add_widget(self.logo_text)
        self.sub_text = Label(
            text="SPACE 8",
            font_size='18sp',
            color=[0.7, 0.7, 0.7, 1],
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            size_hint=(None, None),
            size=(300, 40)
        )
        self.add_widget(self.sub_text)
        self.opacity = 0
        self.logo_text.opacity = 0
        self.sub_text.opacity = 0
        Clock.schedule_once(self.fade_in, 0.3)

    def fade_in(self, dt):
        anim = Animation(opacity=1, duration=1.0, t='out_quad')
        anim.start(self.logo_text)
        anim.start(self.sub_text)
        Clock.schedule_once(self.finish_splash, 2.5)

    def finish_splash(self, dt):
        anim = Animation(opacity=0, duration=0.6, t='in_quad')
        anim.bind(on_complete=self.remove_splash)
        anim.start(self.logo_text)
        anim.start(self.sub_text)
        anim.start(self)

    def remove_splash(self, instance, value):
        app = App.get_running_app()
        if app and hasattr(app, 'root_widget'):
            app.root_widget.remove_widget(self)
            app.root_widget.show_main()

class FloatingMonitor(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (180, 170)
        self.pos = (Window.width - 200, Window.height - 220)
        self.fps = 0
        self.cpu = 0
        self.gpu = 0
        self.temp = 0
        self.rpm = 0
        self.is_dragging = False
        self.drag_start = (0, 0)
        with self.canvas.before:
            Color(*VGX_GRAY)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(*VGX_RED)
            self.border = Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]), width=2)
        content = BoxLayout(orientation='vertical', padding=5, spacing=2)
        title = Label(text="[b]VGX MONITOR[/b]", markup=True, color=VGX_RED, font_size='12sp', size_hint_y=None, height=22)
        content.add_widget(title)
        self.fps_label = Label(text="FPS: 0", color=WHITE, font_size='10sp', size_hint_y=None, height=18)
        content.add_widget(self.fps_label)
        self.cpu_label = Label(text="CPU: 0%", color=WHITE, font_size='10sp', size_hint_y=None, height=18)
        content.add_widget(self.cpu_label)
        self.gpu_label = Label(text="GPU: 0%", color=WHITE, font_size='10sp', size_hint_y=None, height=18)
        content.add_widget(self.gpu_label)
        self.temp_label = Label(text="Temp: 0°C", color=WHITE, font_size='10sp', size_hint_y=None, height=18)
        content.add_widget(self.temp_label)
        self.rpm_label = Label(text="RPM: 0", color=WHITE, font_size='10sp', size_hint_y=None, height=18)
        content.add_widget(self.rpm_label)
        self.add_widget(content)
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*VGX_GRAY)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(*VGX_RED)
            self.border = Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]), width=2)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.is_dragging = True
            self.drag_start = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_dragging:
            dx = touch.pos[0] - self.drag_start[0]
            dy = touch.pos[1] - self.drag_start[1]
            new_x = self.pos[0] + dx
            new_y = self.pos[1] + dy
            if new_x < 0: new_x = 0
            if new_y < 0: new_y = 0
            if new_x + self.size[0] > Window.width: new_x = Window.width - self.size[0]
            if new_y + self.size[1] > Window.height: new_y = Window.height - self.size[1]
            self.pos = (new_x, new_y)
            self.drag_start = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.is_dragging = False
        return super().on_touch_up(touch)

    def update_values(self, fps, cpu, gpu, temp, rpm):
        self.fps = fps
        self.cpu = cpu
        self.gpu = gpu
        self.temp = temp
        self.rpm = rpm
        self.fps_label.text = f"FPS: {fps}"
        self.cpu_label.text = f"CPU: {cpu}%"
        self.gpu_label.text = f"GPU: {gpu}%"
        self.temp_label.text = f"Temp: {temp}°C"
        self.rpm_label.text = f"RPM: {rpm}"

class SideMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_x = 0.3
        self.pos_hint = {'x': -0.3}
        with self.canvas.before:
            Color(*VGX_GRAY)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        header = BoxLayout(size_hint_y=0.1, padding=10)
        header.add_widget(Label(text="VGX", color=VGX_RED, font_size='22sp', bold=True))
        header.add_widget(Label(text="SPACE 8", color=WHITE, font_size='14sp'))
        self.add_widget(header)
        menu_items = [
            ("Dashboard", "dashboard"),
            ("Performance", "performance"),
            ("Fan Control", "fan"),
            ("RGB Lighting", "rgb"),
            ("Statistics", "stats"),
            ("Game Launcher", "games"),
            ("Floating Monitor", "floating")
        ]
        for text, screen in menu_items:
            btn = Button(text=text, background_normal='', background_color=VGX_DARK,
                         color=WHITE, size_hint_y=None, height=45, font_size='14sp')
            btn.screen_name = screen
            btn.bind(on_press=self._on_menu_press)
            self.add_widget(btn)
        self.add_widget(Label(text="", size_hint_y=0.5))

    def _on_menu_press(self, instance):
        app = App.get_running_app()
        if app and hasattr(app, 'root_widget'):
            app.root_widget.current_screen = instance.screen_name
            app.root_widget.toggle_menu()

    def _update_rect(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*VGX_GRAY)
            self.rect = Rectangle(pos=self.pos, size=self.size)

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
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.status_label = Label(text="VGX SPACE 8", color=VGX_RED, font_size='20sp')
        layout.add_widget(self.status_label)
        self.mode_label = Label(text="Mode: Balanced", color=WHITE, font_size='16sp')
        layout.add_widget(self.mode_label)
        self.game_label = Label(text="Game: None", color=WHITE, font_size='16sp')
        layout.add_widget(self.game_label)
        self.add_widget(layout)

    def update_status(self, mode, game):
        self.mode_label.text = f"Mode: {mode}"
        self.game_label.text = f"Game: {game if game else 'None'}"

class PerformanceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="Performance Mode", color=VGX_RED, font_size='18sp'))
        mode_layout = BoxLayout(spacing=10, size_hint_y=0.2)
        for m in ["Balanced", "Performance", "X-Mode"]:
            btn = Button(text=m, background_normal='', background_color=VGX_GRAY,
                         color=WHITE, font_size='14sp')
            btn.bind(on_press=self.change_mode)
            mode_layout.add_widget(btn)
        layout.add_widget(mode_layout)
        self.current_mode = Label(text="Current: Balanced", color=WHITE, font_size='14sp')
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
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="Fan Control", color=VGX_RED, font_size='18sp'))
        self.fan_slider = Slider(min=0, max=100, value=50, value_track_color=VGX_RED)
        self.fan_slider.bind(value=self.on_fan_change)
        layout.add_widget(self.fan_slider)
        self.fan_label = Label(text="RPM: 0", color=WHITE, font_size='14sp')
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
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="RGB Lighting", color=VGX_RED, font_size='18sp'))
        self.rgb_btn = Button(text="MATIKAN RGB", background_normal='', background_color=VGX_GRAY,
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
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="System Statistics", color=VGX_RED, font_size='18sp'))
        self.stat_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        self.stat_grid.bind(minimum_height=self.stat_grid.setter('height'))
        self.stat_labels = {}
        stats = ["CPU Usage", "GPU Usage", "CPU Temp", "GPU Temp", "FPS", "RPM Fan"]
        for s in stats:
            lbl = Label(text=f"{s}: 0", color=WHITE, font_size='14sp')
            self.stat_grid.add_widget(lbl)
            self.stat_labels[s] = lbl
        layout.add_widget(self.stat_grid)
        self.add_widget(layout)

    def update_stats(self, cpu, gpu, temp_cpu, temp_gpu, fps, rpm):
        self.stat_labels["CPU Usage"].text = f"CPU Usage: {cpu}%"
        self.stat_labels["GPU Usage"].text = f"GPU Usage: {gpu}%"
        self.stat_labels["CPU Temp"].text = f"CPU Temp: {temp_cpu}°C"
        self.stat_labels["GPU Temp"].text = f"GPU Temp: {temp_gpu}°C"
        self.stat_labels["FPS"].text = f"FPS: {fps}"
        self.stat_labels["RPM Fan"].text = f"RPM Fan: {rpm}"

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="Game Launcher", color=VGX_RED, font_size='18sp'))
        self.game_list = RecycleView(
            data=[{'text': g} for g in GAME_LIST],
            viewclass='Label',
            size_hint_y=None,
            height=300
        )
        self.game_list.bind(on_touch_down=self.on_game_select)
        layout.add_widget(self.game_list)
        self.launch_btn = Button(text="LAUNCH GAME", background_normal='', background_color=VGX_RED,
                                 color=WHITE, font_size='16sp', size_hint_y=0.1)
        self.launch_btn.bind(on_press=self.launch_game)
        layout.add_widget(self.launch_btn)
        self.current_game_label = Label(text="Selected: None", color=WHITE, font_size='14sp')
        layout.add_widget(self.current_game_label)
        self.add_widget(layout)
        self.selected_game = None

    def on_game_select(self, instance, touch):
        if instance.collide_point(*touch.pos):
            for child in instance.children:
                if child.collide_point(*touch.pos):
                    self.selected_game = child.text
                    self.current_game_label.text = f"Selected: {self.selected_game}"
                    return True

    def launch_game(self, instance):
        if self.selected_game:
            popup = Popup(title='Game Launcher',
                          content=Label(text=f"Launching {self.selected_game}..."),
                          size_hint=(0.8, 0.3))
            popup.open()
            Clock.schedule_once(lambda dt: popup.dismiss(), 2)
            app = App.get_running_app()
            if app and hasattr(app, 'root_widget'):
                app.root_widget.set_current_game(self.selected_game)
        else:
            popup = Popup(title='Pilih Game', content=Label(text="Silakan pilih game."), size_hint=(0.8, 0.3))
            popup.open()

class FloatingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text="Floating Monitor", color=VGX_RED, font_size='18sp'))
        self.toggle_btn = Button(text="TAMPILKAN MONITOR", background_normal='', background_color=VGX_RED,
                                 color=WHITE, size_hint_y=0.2)
        self.toggle_btn.bind(on_press=self.toggle_floating)
        layout.add_widget(self.toggle_btn)
        self.status_label = Label(text="Status: Sembunyi", color=WHITE, font_size='14sp')
        layout.add_widget(self.status_label)
        self.add_widget(layout)

    def toggle_floating(self, instance):
        app = App.get_running_app()
        if app and hasattr(app, 'root_widget'):
            visible = app.root_widget.toggle_floating()
            self.status_label.text = f"Status: {'Tampil' if visible else 'Sembunyi'}"
            self.toggle_btn.text = "SEMBUNYIKAN MONITOR" if visible else "TAMPILKAN MONITOR"

class VGXSpaceRoot(FloatLayout):
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
        self.sm.add_widget(FloatingScreen(name='floating'))
        self.current_screen = 'dashboard'
        self.sm.current = 'dashboard'
        self.sm.opacity = 0
        self.add_widget(self.sm)
        self.floating_monitor = FloatingMonitor()
        self.floating_monitor.opacity = 0
        self.add_widget(self.floating_monitor)
        self.menu_btn = Button(text='☰', size_hint=(None, None), size=(50, 50),
                               background_normal='', background_color=VGX_RED,
                               pos_hint={'x': 0.02, 'top': 0.95}, opacity=0)
        self.menu_btn.bind(on_press=self.toggle_menu)
        self.add_widget(self.menu_btn)
        self.mode = "Balanced"
        self.fan_rpm = 0
        self.rgb_on = True
        self.rgb_color = [0, 1, 0, 1]
        self.current_game = None
        self.is_floating_visible = False
        self.splash = SplashScreen()
        self.add_widget(self.splash)
        Clock.schedule_interval(self.update_stats, 0.5)

    def show_main(self):
        anim = Animation(opacity=1, duration=0.8, t='out_quad')
        anim.start(self.sm)
        anim.start(self.menu_btn)
        self.main_visible = True

    def toggle_menu(self, *args):
        self.side_menu.toggle()

    def set_mode(self, mode):
        self.mode = mode
        dash = self.sm.get_screen('dashboard')
        if dash:
            dash.update_status(self.mode, self.current_game)

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
        dash = self.sm.get_screen('dashboard')
        if dash:
            dash.update_status(self.mode, self.current_game)

    def toggle_floating(self):
        self.is_floating_visible = not self.is_floating_visible
        self.floating_monitor.opacity = 1 if self.is_floating_visible else 0
        return self.is_floating_visible

    def update_stats(self, dt):
        cpu = random.randint(5, 95)
        gpu = random.randint(5, 95)
        temp_cpu = random.randint(35, 80)
        temp_gpu = random.randint(40, 85)
        if self.mode == "Balanced":
            fps = random.randint(30, 60)
        elif self.mode == "Performance":
            fps = random.randint(45, 90)
        else:
            fps = random.randint(60, 144)
        stats_screen = self.sm.get_screen('stats')
        if stats_screen:
            stats_screen.update_stats(cpu, gpu, temp_cpu, temp_gpu, fps, self.fan_rpm)
        if self.is_floating_visible:
            self.floating_monitor.update_values(fps, cpu, gpu, temp_cpu, self.fan_rpm)

class VGXSpaceApp(App):
    def build(self):
        self.title = "VGX SPACE 8"
        self.icon = 'icon.png'
        self.root_widget = VGXSpaceRoot()
        return self.root_widget

if __name__ == '__main__':
    VGXSpaceApp().run()
EOF
