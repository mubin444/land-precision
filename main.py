import math
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.core.text import Label as CoreLabel

HAS_PIL = True
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    HAS_PIL = False


class CenteredTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.input_filter = 'float'
        self.font_size = '15sp'
        self.bold = True
        self.size_hint_y = None
        self.height = 42
        self.background_normal = ''
        self.background_color = (0.95, 0.97, 1.0, 1)
        self.foreground_color = (0.1, 0.1, 0.3, 1)
        self.cursor_color = (0.1, 0.5, 0.9, 1)
        self.padding = [10, 10, 10, 0]
        self.bind(size=self._update_padding, line_height=self._update_padding)

    def _update_padding(self, *args):
        lh = self.line_height if self.line_height > 0 else 20
        pad_top = max(0, (self.height - lh) / 2)
        self.padding = [10, pad_top, 10, 0]


class TriangleVisualizer(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.a, self.b, self.c = 0.0, 0.0, 0.0
        self.cut_ratio1, self.cut_ratio2 = 0.0, 0.0
        self.from_vertex = "Vertex A (Top)"

    def draw_triangle(self, a, b, c, r1, r2, from_vertex):
        self.a, self.b, self.c = a, b, c
        self.cut_ratio1 = r1
        self.cut_ratio2 = r2
        self.from_vertex = from_vertex
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        cw, ch = self.width, self.height
        if cw <= 0 or ch <= 0 or self.a <= 0 or self.b <= 0 or self.c <= 0:
            return

        s = (self.a + self.b + self.c) / 2.0
        if s <= self.a or s <= self.b or s <= self.c:
            return
        area = math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))

        hc = (2 * area) / self.c
        x_proj = (self.b**2 + self.c**2 - self.a**2) / (2 * self.c)

        max_dim = max(self.c, hc)
        scale = (min(cw, ch) * 0.65) / max_dim

        cx, cy = self.x + cw / 2, self.y + ch / 2 - (hc * scale) / 3

        p_bl = (cx - (self.c * scale) / 2, cy)
        p_br = (cx + (self.c * scale) / 2, cy)
        p_top = (p_bl[0] + x_proj * scale, cy + hc * scale)

        with self.canvas:
            Color(0.12, 0.16, 0.28, 1)
            Rectangle(pos=self.pos, size=self.size)

            Color(0.2, 0.8, 1, 1)
            Line(points=[p_top[0], p_top[1], p_bl[0], p_bl[1], p_br[0], p_br[1], p_top[0], p_top[1]], width=2.5)

            self._draw_text("A", (p_top[0], p_top[1] + 10), (0.2, 1, 0.2, 1))
            self._draw_text("B", (p_bl[0] - 12, p_bl[1] - 8), (0.2, 1, 0.2, 1))
            self._draw_text("C", (p_br[0] + 12, p_br[1] - 8), (0.2, 1, 0.2, 1))

            self._draw_text(f"b: {self.b:.1f}", ((p_top[0]+p_bl[0])/2 - 12, (p_top[1]+p_bl[1])/2), (1, 0.8, 0.2, 1))
            self._draw_text(f"a: {self.a:.1f}", ((p_top[0]+p_br[0])/2 + 12, (p_top[1]+p_br[1])/2), (1, 0.8, 0.2, 1))
            self._draw_text(f"c: {self.c:.1f}", (cx, cy - 12), (1, 0.8, 0.2, 1))

            if self.cut_ratio1 > 0 or self.cut_ratio2 > 0:
                Color(1, 0.3, 0.3, 1)
                r1 = min(max(self.cut_ratio1, 0.0), 1.0)
                r2 = min(max(self.cut_ratio2, 0.0), 1.0)

                if "Vertex A" in self.from_vertex:
                    cp1 = (p_top[0] + (p_bl[0] - p_top[0]) * r1, p_top[1] + (p_bl[1] - p_top[1]) * r1)
                    cp2 = (p_top[0] + (p_br[0] - p_top[0]) * r2, p_top[1] + (p_br[1] - p_top[1]) * r2)
                elif "Vertex B" in self.from_vertex:
                    cp1 = (p_bl[0] + (p_top[0] - p_bl[0]) * r1, p_bl[1] + (p_top[1] - p_bl[1]) * r1)
                    cp2 = (p_bl[0] + (p_br[0] - p_bl[0]) * r2, p_bl[1] + (p_br[1] - p_bl[1]) * r2)
                else:
                    cp1 = (p_br[0] + (p_top[0] - p_br[0]) * r1, p_br[1] + (p_top[1] - p_br[1]) * r1)
                    cp2 = (p_br[0] + (p_bl[0] - p_br[0]) * r2, p_br[1] + (p_bl[1] - p_br[1]) * r2)

                Line(points=[cp1[0], cp1[1], cp2[0], cp2[1]], width=3)

    def _draw_text(self, text, pos, color=(1, 1, 1, 1)):
        core_lbl = CoreLabel(text=text, font_size=11, bold=True)
        core_lbl.refresh()
        tex = core_lbl.texture
        Color(*color)
        Rectangle(texture=tex, pos=(pos[0] - tex.width / 2, pos[1] - tex.height / 2), size=tex.size)


class ScaleneTrianglePartitionView(BoxLayout):
    def __init__(self, popup_ref=None, **kwargs):
        super().__init__(**kwargs)
        self.popup_ref = popup_ref
        self.orientation = 'vertical'
        self.padding = 12
        self.spacing = 10
        self.updating_internally = False

        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=[0, 0, 0, 20])
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(Label(text="[color=00e5ff][b]Scalene Triangle Calculator & Partition[/b][/color]", 
                                 markup=True, font_size="17sp", size_hint_y=None, height=35))

        grid = GridLayout(cols=2, spacing=10, row_default_height=42, size_hint_y=None, height=260)
        
        grid.add_widget(Label(text="Side A (ft):", bold=True, font_size="14sp"))
        self.side_a = CenteredTextInput(text="100")
        grid.add_widget(self.side_a)

        grid.add_widget(Label(text="Side B (ft):", bold=True, font_size="14sp"))
        self.side_b = CenteredTextInput(text="120")
        grid.add_widget(self.side_b)

        grid.add_widget(Label(text="Side C (ft):", bold=True, font_size="14sp"))
        self.side_c = CenteredTextInput(text="140")
        grid.add_widget(self.side_c)

        grid.add_widget(Label(text="Target Land (Shotok):", bold=True, font_size="14sp"))
        self.target_shotok = CenteredTextInput(text="1.5")
        grid.add_widget(self.target_shotok)

        grid.add_widget(Label(text="Cut From Vertex:", bold=True, font_size="14sp"))
        self.vertex_spinner = Spinner(
            text="Vertex A (Top)",
            values=("Vertex A (Top)", "Vertex B (Left)", "Vertex C (Right)"),
            size_hint_y=None, height=42, font_size="13sp",
            background_normal='', background_color=(0.2, 0.5, 0.8, 1)
        )
        self.vertex_spinner.bind(text=self.on_vertex_change)
        grid.add_widget(self.vertex_spinner)

        content.add_widget(grid)

        calc_btn = Button(text="Calculate & Partition", size_hint_y=None, height=45,
                          bold=True, font_size="15sp", background_normal='', background_color=(0.1, 0.7, 0.4, 1))
        calc_btn.bind(on_press=self.calculate)
        content.add_widget(calc_btn)

        content.add_widget(Label(text="[color=ffb703][b]Adjust Cut Segment Lengths:[/b][/color]", markup=True, font_size="15sp", size_hint_y=None, height=25))
        
        adjust_grid = GridLayout(cols=2, spacing=10, row_default_height=42, size_hint_y=None, height=95)
        
        self.cut1_label = Label(text="Cut Side B (ft):", font_size="14sp", bold=True, color=(0.9, 0.9, 0.9, 1))
        adjust_grid.add_widget(self.cut1_label)
        self.cut1_in = CenteredTextInput(text="")
        self.cut1_in.bind(text=self.on_cut1_change)
        adjust_grid.add_widget(self.cut1_in)

        self.cut2_label = Label(text="Cut Side A (ft):", font_size="14sp", bold=True, color=(0.9, 0.9, 0.9, 1))
        adjust_grid.add_widget(self.cut2_label)
        self.cut2_in = CenteredTextInput(text="")
        adjust_grid.add_widget(self.cut2_in)

        content.add_widget(adjust_grid)

        self.visualizer = TriangleVisualizer(size_hint_y=None, height=200)
        content.add_widget(self.visualizer)

        btn_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=42)

        export_btn = Button(text="Export Scaled JPG", bold=True, font_size="11sp",
                            background_normal='', background_color=(0.9, 0.5, 0.1, 1))
        export_btn.bind(on_press=self.export_triangle_jpg)
        btn_box.add_widget(export_btn)

        back_btn = Button(text="Back / Close", bold=True, font_size="11sp",
                          background_normal='', background_color=(0.8, 0.2, 0.2, 1))
        back_btn.bind(on_press=self.close_popup)
        btn_box.add_widget(back_btn)

        content.add_widget(btn_box)

        self.result_lbl = Label(text="Enter values and click calculate...", markup=True, font_size="14sp",
                                size_hint_y=None, halign="left", valign="top")
        self.result_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)),
                             texture_size=lambda inst, val: setattr(inst, 'height', val[1] + 15))
        content.add_widget(self.result_lbl)

        scroll.add_widget(content)
        self.add_widget(scroll)

    def close_popup(self, instance):
        if self.popup_ref:
            self.popup_ref.dismiss()

    def on_vertex_change(self, spinner, text):
        if self.side_a.text and self.side_b.text and self.side_c.text:
            self.calculate()

    def calculate(self, *args):
        try:
            a = float(self.side_a.text)
            b = float(self.side_b.text)
            c = float(self.side_c.text)
            target = float(self.target_shotok.text)
            vertex = self.vertex_spinner.text

            s = (a + b + c) / 2.0
            if s <= a or s <= b or s <= c:
                self.result_lbl.text = "[color=ff4d4d]Invalid sides! Impossible to form a triangle.[/color]"
                return

            total_sqft = math.sqrt(s * (s - a) * (s - b) * (s - c))
            target_sqft = target * 435.6

            if target_sqft > total_sqft:
                self.result_lbl.text = "[color=ff4d4d]Error: Target land exceeds total land area![/color]"
                return

            ratio = math.sqrt(target_sqft / total_sqft)

            if "Vertex A" in vertex:
                self.cut1_label.text = "Cut Side B (ft):"
                self.cut2_label.text = "Cut Side A (ft):"
                c1_init = b * ratio
            elif "Vertex B" in vertex:
                self.cut1_label.text = "Cut Side B (ft):"
                self.cut2_label.text = "Cut Side C (ft):"
                c1_init = b * ratio
            else:
                self.cut1_label.text = "Cut Side A (ft):"
                self.cut2_label.text = "Cut Side C (ft):"
                c1_init = a * ratio

            ang = self._get_vertex_angle(vertex, a, b, c)
            c2_exact = (target_sqft * 2) / (c1_init * math.sin(ang)) if c1_init > 0 else 0

            self.updating_internally = True
            self.cut1_in.text = f"{c1_init:.2f}"
            self.cut2_in.text = f"{c2_exact:.2f}"
            self.updating_internally = False

            self.update_results(c1_init, c2_exact)

        except ValueError:
            self.result_lbl.text = "[color=ff4d4d]Please enter valid numeric values.[/color]"

    def _get_vertex_angle(self, vertex, a, b, c):
        if "Vertex A" in vertex:
            cos_val = (b**2 + a**2 - c**2) / (2 * b * a)
        elif "Vertex B" in vertex:
            cos_val = (b**2 + c**2 - a**2) / (2 * b * c)
        else:
            cos_val = (a**2 + c**2 - b**2) / (2 * a * c)
        return math.acos(max(-1.0, min(1.0, cos_val)))

    def on_cut1_change(self, instance, value):
        if self.updating_internally or not value:
            return
        try:
            c1 = float(value)
            a = float(self.side_a.text)
            b = float(self.side_b.text)
            c = float(self.side_c.text)
            target_sqft = float(self.target_shotok.text) * 435.6
            vertex = self.vertex_spinner.text

            max_len = b if "Vertex A" in vertex or "Vertex B" in vertex else a
            ang_rad = self._get_vertex_angle(vertex, a, b, c)

            limit_c2 = a if "Vertex A" in vertex else (c if "Vertex B" in vertex or "Vertex C" in vertex else b)
            min_c1_required = (target_sqft * 2.0) / (limit_c2 * math.sin(ang_rad))

            if c1 > max_len or c1 < min_c1_required:
                self.updating_internally = True
                self.cut2_in.text = "Invalid"
                self.updating_internally = False

                err_msg = f"[color=ff4d4d][b]Error: Invalid Cut Length![/b]\n"
                err_msg += f"• Allowed Range: [color=00ff66]{min_c1_required:.2f} ft[/color] to [color=00ff66]{max_len:.2f} ft[/color]\n"
                err_msg += f"Entered: [color=ffaa00]{c1:.2f} ft[/color][/color]"
                self.result_lbl.text = err_msg
                return

            c2 = (target_sqft * 2.0) / (c1 * math.sin(ang_rad))

            self.updating_internally = True
            self.cut2_in.text = f"{c2:.2f}"
            self.updating_internally = False

            self.update_results(c1, c2)
        except (ValueError, ZeroDivisionError):
            pass

    def update_results(self, c1, c2):
        try:
            a = float(self.side_a.text)
            b = float(self.side_b.text)
            c = float(self.side_c.text)
            vertex = self.vertex_spinner.text

            s = (a + b + c) / 2.0
            total_sqft = math.sqrt(s * (s - a) * (s - b) * (s - c))
            total_shotok = total_sqft / 435.6

            ang_rad = self._get_vertex_angle(vertex, a, b, c)
            actual_target_sqft = 0.5 * c1 * c2 * math.sin(ang_rad)
            actual_target_shotok = actual_target_sqft / 435.6

            div_line = math.sqrt(c1**2 + c2**2 - 2 * c1 * c2 * math.cos(ang_rad))

            if "Vertex A" in vertex:
                l1_name, l2_name = "Side B Cut", "Side A Cut"
                r1, r2 = c1 / b, c2 / a
            elif "Vertex B" in vertex:
                l1_name, l2_name = "Side B Cut", "Side C Cut"
                r1, r2 = c1 / b, c2 / c
            else:
                l1_name, l2_name = "Side A Cut", "Side C Cut"
                r1, r2 = c1 / a, c2 / c

            rem_sqft = total_sqft - actual_target_sqft
            rem_shotok = rem_sqft / 435.6

            res = f"[color=00e5ff][b]=== Scalene Triangle Report ===[/b][/color]\n"
            res += f"Total Area: {total_sqft:.2f} Sq.Ft ([color=00ffff]{total_shotok:.3f} Shotok[/color])\n"
            res += f"Target Area: [color=00ff66]{actual_target_shotok:.3f} Shotok ({actual_target_sqft:.2f} Sq.Ft)[/color]\n\n"
            res += f"[color=ffb703][b]Cut Measures ({vertex}):[/b][/color]\n"
            res += f"• {l1_name}: {c1:.2f} ft, {l2_name}: {c2:.2f} ft\n"
            res += f"• Divider Line: [color=ff5555]{div_line:.2f} ft[/color]\n\n"
            res += f"[color=00e5ff][b]Remaining Land:[/b][/color] {rem_shotok:.3f} Shotok ({rem_sqft:.2f} Sq.Ft)"

            self.result_lbl.text = res
            self.visualizer.draw_triangle(a, b, c, r1, r2, vertex)
        except Exception:
            pass

    def export_triangle_jpg(self, instance):
        if not HAS_PIL:
            self.result_lbl.text = "[color=ff4d4d]Pillow library is missing! Install: pip install pillow[/color]"
            return

        try:
            a = float(self.side_a.text)
            b = float(self.side_b.text)
            c = float(self.side_c.text)
            target_shotok = float(self.target_shotok.text)
            vertex = self.vertex_spinner.text
            c1 = float(self.cut1_in.text)
            c2 = float(self.cut2_in.text)

            cw, ch = 1200, 700
            img = Image.new("RGB", (cw, ch), (245, 247, 250))
            draw = ImageDraw.Draw(img)

            scale = 96.0 / 165.0 

            s = (a + b + c) / 2.0
            area = math.sqrt(s * (s - a) * (s - b) * (s - c))
            hc = (2 * area) / c
            x_proj = (b**2 + c**2 - a**2) / (2 * c)

            cx, cy = 400, ch / 2 + (hc * scale) / 3

            p_bl = (cx - (c * scale) / 2, cy)
            p_br = (cx + (c * scale) / 2, cy)
            p_top = (p_bl[0] + x_proj * scale, cy - hc * scale)

            draw.polygon([p_top, p_bl, p_br], outline=(0, 102, 204), width=4)

            ang_rad = self._get_vertex_angle(vertex, a, b, c)
            r1 = c1 / (b if "Vertex A" in vertex or "Vertex B" in vertex else a)
            r2 = c2 / (a if "Vertex A" in vertex else c)

            if "Vertex A" in vertex:
                cp1 = (p_top[0] + (p_bl[0] - p_top[0]) * r1, p_top[1] + (p_bl[1] - p_top[1]) * r1)
                cp2 = (p_top[0] + (p_br[0] - p_top[0]) * r2, p_top[1] + (p_br[1] - p_top[1]) * r2)
            elif "Vertex B" in vertex:
                cp1 = (p_bl[0] + (p_top[0] - p_bl[0]) * r1, p_bl[1] + (p_top[1] - p_bl[1]) * r1)
                cp2 = (p_bl[0] + (p_br[0] - p_bl[0]) * r2, p_bl[1] + (p_br[1] - p_bl[1]) * r2)
            else:
                cp1 = (p_br[0] + (p_top[0] - p_br[0]) * r1, p_br[1] + (p_top[1] - p_br[1]) * r1)
                cp2 = (p_br[0] + (p_bl[0] - p_br[0]) * r2, p_br[1] + (p_bl[1] - p_br[1]) * r2)

            draw.line([cp1, cp2], fill=(220, 38, 38), width=4)

            try:
                font_title = ImageFont.truetype("arial.ttf", 20)
                font_header = ImageFont.truetype("arial.ttf", 15)
                font_label = ImageFont.truetype("arial.ttf", 13)
            except:
                font_title = font_header = font_label = ImageFont.load_default()

            draw.text((30, 20), "TRIANGLE LAND PARTITION MAP (Scale: 32\" = 1 Mile)", fill=(15, 23, 42), font=font_title)

            draw.text((p_top[0] - 5, p_top[1] - 18), "A", fill=(0, 150, 0), font=font_label)
            draw.text((p_bl[0] - 15, p_bl[1] + 2), "B", fill=(0, 150, 0), font=font_label)
            draw.text((p_br[0] + 5, p_br[1] + 2), "C", fill=(0, 150, 0), font=font_label)

            draw.text(((p_top[0] + p_bl[0]) / 2 - 45, (p_top[1] + p_bl[1]) / 2), f"b: {b:.1f}'", fill=(10, 30, 90), font=font_label)
            draw.text(((p_top[0] + p_br[0]) / 2 + 5, (p_top[1] + p_br[1]) / 2), f"a: {a:.1f}'", fill=(10, 30, 90), font=font_label)
            draw.text((cx - 20, cy + 5), f"c: {c:.1f}'", fill=(10, 30, 90), font=font_label)

            div_line = math.sqrt(c1**2 + c2**2 - 2 * c1 * c2 * math.cos(ang_rad))
            draw.text(((cp1[0] + cp2[0]) / 2 + 5, (cp1[1] + cp2[1]) / 2 - 10), f"Div: {div_line:.2f}'", fill=(220, 38, 38), font=font_label)

            box_x1, box_y1 = 820, 100
            box_x2, box_y2 = 1150, 550
            draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=(255, 255, 255), outline=(30, 58, 138), width=2)
            draw.rectangle([box_x1, box_y1, box_x2, box_y1 + 38], fill=(30, 58, 138))
            draw.text((box_x1 + 30, box_y1 + 10), "TRIANGLE REPORT", fill=(255, 255, 255), font=font_header)

            total_shotok = area / 435.6

            report_lines = [
                ("Total Area:", (30, 58, 138)),
                (f" {total_shotok:.3f} Shotok ({area:.1f} sqft)", (15, 23, 42)),
                ("Sides:", (30, 58, 138)),
                (f" A:{a:.1f}' | B:{b:.1f}' | C:{c:.1f}'", (15, 23, 42)),
                (f"Cut From: {vertex}", (30, 58, 138)),
                (f" Target: {target_shotok:.3f} Shotok", (220, 38, 38)),
                (f" Cut 1: {c1:.2f} ft | Cut 2: {c2:.2f} ft", (15, 23, 42)),
                (f" Divider Line: {div_line:.2f} ft", (180, 0, 0)),
                ("Remaining Land:", (30, 58, 138)),
                (f" {total_shotok - target_shotok:.3f} Shotok", (0, 102, 204))
            ]

            curr_y = box_y1 + 50
            for text, color in report_lines:
                draw.text((box_x1 + 15, curr_y), text, fill=color, font=font_label)
                curr_y += 24

            file_name = "triangle_scaled_map.jpg"
            img.save(file_name, "JPEG", quality=95)

            msg = f"Scaled Triangle Map Saved!\nPath: {os.path.abspath(file_name)}"
            self.result_lbl.text = f"[color=00ff66]{msg}[/color]"

        except Exception as err:
            self.result_lbl.text = f"[color=ff4d4d]Export Error: {str(err)}[/color]"


class Interactive3DLandVisualizer(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.n, self.s, self.e, self.w = 0.0, 0.0, 0.0, 0.0
        self.cut_frac = [0.0, 0.0]
        self.direction = "From North"
        self.diag_choice = "Diagonal 1 (NE to SW)"
        self.angles = {}
        self.part_diag_pts = None
        self.part_diag_len = 0.0
        self.rot_angle = 0.0
        self.last_touch_x = 0

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.last_touch_x = touch.x
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            dx = touch.x - self.last_touch_x
            self.rot_angle += dx * 0.5
            self.update_canvas()
            return True
        return super().on_touch_move(touch)

    def reset_rotation(self):
        self.rot_angle = 0.0
        self.update_canvas()

    def _rotate_pt(self, pt, center, angle_deg):
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        cx, cy = center
        px, py = pt[0] - cx, pt[1] - cy
        rx = px * cos_a - py * sin_a
        ry = px * sin_a + py * cos_a
        return (rx + cx, ry + cy)

    def draw_land(self, n, s, e, w, cut_frac, direction, diag_choice, angles, quad_pts=None, part_diag_pts=None, part_diag_len=0.0):
        self.n, self.s, self.e, self.w = n, s, e, w
        self.cut_frac = cut_frac
        self.direction = direction
        self.diag_choice = diag_choice
        self.angles = angles
        self.quad_pts = quad_pts
        self.part_diag_pts = part_diag_pts
        self.part_diag_len = part_diag_len
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        cw, ch = self.width, self.height
        if cw <= 0 or ch <= 0:
            return

        with self.canvas:
            Color(0.12, 0.16, 0.28, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

            if not hasattr(self, 'quad_pts') or not self.quad_pts:
                return

            nw_q, ne_q, se_q, sw_q = self.quad_pts

            all_x = [nw_q[0], ne_q[0], se_q[0], sw_q[0]]
            all_y = [nw_q[1], ne_q[1], se_q[1], sw_q[1]]
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            width_geo = max_x - min_x if max_x != min_x else 1.0
            height_geo = max_y - min_y if max_y != min_y else 1.0

            scale = min(cw * 0.65 / width_geo, ch * 0.65 / height_geo)
            cx_canvas, cy_canvas = self.x + cw / 2, self.y + ch / 2
            center = (cx_canvas, cy_canvas)

            mid_x_geo = (min_x + max_x) / 2
            mid_y_geo = (min_y + max_y) / 2

            def to_canvas(p):
                return (cx_canvas + (p[0] - mid_x_geo) * scale, cy_canvas + (p[1] - mid_y_geo) * scale)

            raw_nw = to_canvas(nw_q)
            raw_ne = to_canvas(ne_q)
            raw_se = to_canvas(se_q)
            raw_sw = to_canvas(sw_q)

            nw = self._rotate_pt(raw_nw, center, self.rot_angle)
            ne = self._rotate_pt(raw_ne, center, self.rot_angle)
            se = self._rotate_pt(raw_se, center, self.rot_angle)
            sw = self._rotate_pt(raw_sw, center, self.rot_angle)

            Color(0.2, 0.8, 1, 1)
            Line(points=[nw[0], nw[1], ne[0], ne[1], se[0], se[1], sw[0], sw[1], nw[0], nw[1]], width=2.5)

            Color(1, 0.84, 0, 0.8)
            if "NE" in self.diag_choice:
                Line(points=[ne[0], ne[1], sw[0], sw[1]], width=2, dash_length=6, dash_offset=2)
            else:
                Line(points=[nw[0], nw[1], se[0], se[1]], width=2, dash_length=6, dash_offset=2)

            self._render_angle_labels(nw, ne, se, sw)

            Color(1, 0.3, 0.3, 1)
            f1, f2 = self.cut_frac[0], self.cut_frac[1]

            if self.direction == "From North":
                raw_p1 = (raw_nw[0] + (raw_sw[0] - raw_nw[0]) * f1, raw_nw[1] + (raw_sw[1] - raw_nw[1]) * f1)
                raw_p2 = (raw_ne[0] + (raw_se[0] - raw_ne[0]) * f2, raw_ne[1] + (raw_se[1] - raw_ne[1]) * f2)
            elif self.direction == "From South":
                raw_p1 = (raw_sw[0] + (raw_nw[0] - raw_sw[0]) * f1, raw_sw[1] + (raw_nw[1] - raw_sw[1]) * f1)
                raw_p2 = (raw_se[0] + (raw_ne[0] - raw_se[0]) * f2, raw_se[1] + (raw_ne[1] - raw_se[1]) * f2)
            elif self.direction == "From East":
                raw_p1 = (raw_ne[0] + (raw_nw[0] - raw_ne[0]) * f1, raw_ne[1] + (raw_nw[1] - raw_ne[1]) * f1)
                raw_p2 = (raw_se[0] + (raw_sw[0] - raw_se[0]) * f2, raw_se[1] + (raw_sw[1] - raw_se[1]) * f2)
            elif self.direction == "From West":
                raw_p1 = (raw_nw[0] + (raw_ne[0] - raw_nw[0]) * f1, raw_nw[1] + (raw_ne[1] - raw_nw[1]) * f1)
                raw_p2 = (raw_sw[0] + (raw_se[0] - raw_sw[0]) * f2, raw_sw[1] + (raw_se[1] - raw_sw[1]) * f2)

            p1 = self._rotate_pt(raw_p1, center, self.rot_angle)
            p2 = self._rotate_pt(raw_p2, center, self.rot_angle)

            Line(points=[p1[0], p1[1], p2[0], p2[1]], width=3)

            if self.part_diag_pts and self.part_diag_len > 0:
                raw_dp1 = to_canvas(self.part_diag_pts[0])
                raw_dp2 = to_canvas(self.part_diag_pts[1])
                dp1 = self._rotate_pt(raw_dp1, center, self.rot_angle)
                dp2 = self._rotate_pt(raw_dp2, center, self.rot_angle)

                Color(1, 0.55, 0, 0.9)
                Line(points=[dp1[0], dp1[1], dp2[0], dp2[1]], width=2, dash_length=4, dash_offset=2)

            core_lbl = CoreLabel(text="[Touch & Drag to Rotate Diagram]", font_size=11, bold=True)
            core_lbl.refresh()
            tex = core_lbl.texture
            Color(0.1, 0.9, 0.9, 0.8)
            Rectangle(texture=tex, pos=(self.x + 10, self.y + 10), size=tex.size)

    def _render_angle_labels(self, nw, ne, se, sw):
        if not self.angles:
            return

        pts = {"NW": nw, "NE": ne, "SE": se, "SW": sw}
        for corner, pos in pts.items():
            ang_val = self.angles.get(corner, 0.0)
            txt = f"{corner}: {ang_val:.1f}°"
            core_lbl = CoreLabel(text=txt, font_size=11, bold=True)
            core_lbl.refresh()
            tex = core_lbl.texture

            offset_x = -25 if "W" in corner else 2
            offset_y = 2 if "N" in corner else -15

            Color(0.1, 0.1, 0.1, 0.8)
            Rectangle(pos=(pos[0] + offset_x - 2, pos[1] + offset_y - 2), size=(tex.width + 4, tex.height + 4))
            Color(0.2, 1.0, 0.2, 1)
            Rectangle(texture=tex, pos=(pos[0] + offset_x, pos[1] + offset_y), size=tex.size)


class AdvancedLandCalculatorApp(App):
    def build(self):
        self.updating_internally = False
        self.has_calculated = False
        self.title = "Precision Land Calculator & Automatic Partition System"
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=10)

        with main_layout.canvas.before:
            Color(0.08, 0.1, 0.18, 1)
            self.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True)
        content = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, padding=[0, 0, 0, 30])
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(Label(text="[color=00e5ff][b]Advanced Precision Land Calculator[/b][/color]", markup=True, font_size="20sp", size_hint_y=None, height=40))

        grid = GridLayout(cols=2, spacing=10, row_default_height=42, size_hint_y=None, height=310)

        grid.add_widget(Label(text="North Side (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.north_in = CenteredTextInput(text="165")
        grid.add_widget(self.north_in)

        grid.add_widget(Label(text="South Side (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.south_in = CenteredTextInput(text="122")
        grid.add_widget(self.south_in)

        grid.add_widget(Label(text="East Side (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.east_in = CenteredTextInput(text="97")
        grid.add_widget(self.east_in)

        grid.add_widget(Label(text="West Side (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.west_in = CenteredTextInput(text="96")
        grid.add_widget(self.west_in)

        grid.add_widget(Label(text="Diagonal (Karna) (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.diag_in = CenteredTextInput(text="172.9")
        grid.add_widget(self.diag_in)

        grid.add_widget(Label(text="Select Diagonal:", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))

        self.diag_spinner = Spinner(
            text="Diagonal 2 (NW to SE)", 
            values=("Diagonal 1 (NE to SW)", "Diagonal 2 (NW to SE)"), 
            font_size="14sp", 
            size_hint_y=None, 
            height=42,
            background_normal='',
            background_color=(0.4, 0.2, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        self.diag_spinner.bind(text=self.on_dropdown_change)
        grid.add_widget(self.diag_spinner)

        content.add_widget(grid)

        part_grid = GridLayout(cols=2, spacing=10, row_default_height=42, size_hint_y=None, height=150)

        part_grid.add_widget(Label(text="Target Land (Shotok):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.target_shotok_in = CenteredTextInput(text="6")
        part_grid.add_widget(self.target_shotok_in)

        part_grid.add_widget(Label(text="Cut Direction:", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.direction_spinner = Spinner(
            text="From East", 
            values=("From North", "From South", "From East", "From West"), 
            font_size="15sp", 
            size_hint_y=None, 
            height=42,
            background_normal='',
            background_color=(0.1, 0.6, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        self.direction_spinner.bind(text=self.on_dropdown_change)
        part_grid.add_widget(self.direction_spinner)

        part_grid.add_widget(Label(text="Target Part Diagonal:", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1)))
        self.part_diag_spinner = Spinner(
            text="Diagonal A", 
            values=("Diagonal A", "Diagonal B"), 
            font_size="14sp", 
            size_hint_y=None, 
            height=42,
            background_normal='',
            background_color=(0.8, 0.4, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        self.part_diag_spinner.bind(text=self.on_dropdown_change)
        part_grid.add_widget(self.part_diag_spinner)

        content.add_widget(part_grid)

        btn_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)

        calc_btn = Button(
            text="Calculate & Partition", 
            font_size="16sp", 
            bold=True, 
            size_hint_x=0.7,
            background_normal='',
            background_color=(0.1, 0.7, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        calc_btn.bind(on_press=self.on_calc_click)
        btn_box.add_widget(calc_btn)

        reset_btn = Button(
            text="Reset", 
            font_size="16sp", 
            bold=True, 
            size_hint_x=0.3,
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        reset_btn.bind(on_press=self.reset_inputs)
        btn_box.add_widget(reset_btn)

        content.add_widget(btn_box)

        content.add_widget(Label(text="[color=ffb703][b]Adjust Cut Segment Lengths:[/b][/color]", markup=True, font_size="16sp", size_hint_y=None, height=25))

        adjust_grid = GridLayout(cols=2, spacing=10, row_default_height=42, size_hint_y=None, height=95)

        self.cut1_label = Label(text="Cut Side 1 (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1))
        adjust_grid.add_widget(self.cut1_label)
        self.cut1_in = CenteredTextInput(text="")
        self.cut1_in.bind(text=self.on_cut1_change)
        adjust_grid.add_widget(self.cut1_in)

        self.cut2_label = Label(text="Cut Side 2 (ft):", font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1))
        adjust_grid.add_widget(self.cut2_label)
        self.cut2_in = CenteredTextInput(text="")
        adjust_grid.add_widget(self.cut2_in)

        content.add_widget(adjust_grid)

        diagram_box = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=600)
        self.visualizer = Interactive3DLandVisualizer(size_hint=(1, 1))
        diagram_box.add_widget(self.visualizer)

        diag_btn_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)

        reset_rot_btn = Button(
            text="Reset View Angle",
            font_size="13sp",
            bold=True,
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.2, 0.5, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        reset_rot_btn.bind(on_press=lambda x: self.visualizer.reset_rotation())
        diag_btn_box.add_widget(reset_rot_btn)

        export_btn = Button(
            text="Export Scaled JPG",
            font_size="13sp",
            bold=True,
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.9, 0.5, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        export_btn.bind(on_press=self.export_scaled_jpg)
        diag_btn_box.add_widget(export_btn)

        diagram_box.add_widget(diag_btn_box)

        content.add_widget(diagram_box)

        self.result_label = Label(text="Enter values and click Calculate...", markup=True, font_size="15sp", size_hint_y=None, halign="left", valign="top")
        self.result_label.bind(size=self._update_text_size, texture_size=self._update_label_height)
        content.add_widget(self.result_label)

        triangle_btn = Button(
            text="Scalene Triangle Calculator & Partition", 
            font_size="15sp", 
            bold=True, 
            size_hint_y=None, 
            height=45, 
            background_normal='',
            background_color=(0.1, 0.5, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        triangle_btn.bind(on_press=self.open_triangle_popup)
        content.add_widget(triangle_btn)

        formula_btn = Button(
            text="Formulas & Working Principles", 
            font_size="15sp", 
            bold=True, 
            size_hint_y=None, 
            height=45, 
            background_normal='',
            background_color=(0.85, 0.45, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        formula_btn.bind(on_press=self.show_formula_popup)
        content.add_widget(formula_btn)

        developer_info = (
            "[color=00e5ff][b]Developed by[/b][/color]\n"
            "[color=ffffff]Md: Zual Badsha[/color]\n"
            "[color=00ff66]Mobile no: 01744431272[/color]\n"
            "[color=ff0000]Word no: 07, union no: 09, post office: Radhanagor\n"
            "Thana: Badargonj, zilla+division: Rangpur[/color]"
        )
        self.dev_label = Label(
            text=developer_info,
            markup=True,
            font_size="15sp",
            halign="center",
            valign="middle",
            size_hint_y=None
        )
        self.dev_label.bind(size=self._update_dev_text_size, texture_size=self._update_dev_label_height)
        content.add_widget(self.dev_label)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)

        return main_layout

    def open_triangle_popup(self, instance):
        popup = Popup(
            title="Scalene Triangle Calculator & Auto Partition",
            size_hint=(0.95, 0.9)
        )
        popup_content = ScaleneTrianglePartitionView(popup_ref=popup)
        popup.content = popup_content
        popup.open()

    def export_scaled_jpg(self, instance):
        if not HAS_PIL:
            self._show_info_popup("Missing Library", "Pillow library is missing!\nPlease run: pip install pillow")
            return

        if not self.has_calculated:
            self._show_info_popup("Warning", "Please calculate the land area first!")
            return

        try:
            n = float(self.north_in.text)
            s = float(self.south_in.text)
            e = float(self.east_in.text)
            w = float(self.west_in.text)
            d = float(self.diag_in.text)
            target_shotok = float(self.target_shotok_in.text)
            diag_choice = self.diag_spinner.text
            direction = self.direction_spinner.text

            c1 = float(self.cut1_in.text) if self.cut1_in.text and self.cut1_in.text != "Invalid" else 0.0
            c2 = float(self.cut2_in.text) if self.cut2_in.text and self.cut2_in.text != "Invalid" else 0.0

            cw, ch = 1300, 750
            cx, cy = 450, ch / 2

            nw_coord, ne_coord, se_coord, sw_coord, angles = self.get_quad_points_and_angles(n, s, e, w, d, diag_choice)

            all_x = [nw_coord[0], ne_coord[0], se_coord[0], sw_coord[0]]
            all_y = [nw_coord[1], ne_coord[1], se_coord[1], sw_coord[1]]
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            width_geo = max_x - min_x if max_x != min_x else 1.0
            height_geo = max_y - min_y if max_y != min_y else 1.0

            scale = min(500.0 / width_geo, 450.0 / height_geo)
            mid_x_geo = (min_x + max_x) / 2
            mid_y_geo = (min_y + max_y) / 2

            def to_img(p):
                return (cx + (p[0] - mid_x_geo) * scale, cy - (p[1] - mid_y_geo) * scale)

            img_nw = to_img(nw_coord)
            img_ne = to_img(ne_coord)
            img_se = to_img(se_coord)
            img_sw = to_img(sw_coord)

            img = Image.new("RGB", (cw, ch), (245, 247, 250))
            draw = ImageDraw.Draw(img)

            try:
                font_title = ImageFont.truetype("arial.ttf", 20)
                font_header = ImageFont.truetype("arial.ttf", 15)
                font_label = ImageFont.truetype("arial.ttf", 13)
                font_compass = ImageFont.truetype("arial.ttf", 16)
            except:
                font_title = font_header = font_label = font_compass = ImageFont.load_default()

            draw.polygon([img_nw, img_ne, img_se, img_sw], outline=(0, 102, 204), width=4)

            if "NE" in diag_choice:
                draw.line([img_ne, img_sw], fill=(212, 160, 23), width=3)
            else:
                draw.line([img_nw, img_se], fill=(212, 160, 23), width=3)

            if direction in ["From North", "From South"]:
                f1 = min(c1 / w, 1.0) if w > 0 else 0
                f2 = min(c2 / e, 1.0) if e > 0 else 0
            else:
                f1 = min(c1 / n, 1.0) if n > 0 else 0
                f2 = min(c2 / s, 1.0) if s > 0 else 0

            if direction == "From North":
                cp1_g = (nw_coord[0] + (sw_coord[0]-nw_coord[0])*f1, nw_coord[1] + (sw_coord[1]-nw_coord[1])*f1)
                cp2_g = (ne_coord[0] + (se_coord[0]-ne_coord[0])*f2, ne_coord[1] + (se_coord[1]-ne_coord[1])*f2)
            elif direction == "From South":
                cp1_g = (sw_coord[0] + (nw_coord[0]-sw_coord[0])*f1, sw_coord[1] + (nw_coord[1]-sw_coord[1])*f1)
                cp2_g = (se_coord[0] + (ne_coord[0]-se_coord[0])*f2, se_coord[1] + (ne_coord[1]-se_coord[1])*f2)
            elif direction == "From East":
                cp1_g = (ne_coord[0] + (nw_coord[0]-ne_coord[0])*f1, ne_coord[1] + (nw_coord[1]-ne_coord[1])*f1)
                cp2_g = (se_coord[0] + (sw_coord[0]-se_coord[0])*f2, se_coord[1] + (sw_coord[1]-se_coord[1])*f2)
            elif direction == "From West":
                cp1_g = (nw_coord[0] + (ne_coord[0]-nw_coord[0])*f1, nw_coord[1] + (ne_coord[1]-nw_coord[1])*f1)
                cp2_g = (sw_coord[0] + (se_coord[0]-sw_coord[0])*f2, sw_coord[1] + (se_coord[1]-sw_coord[1])*f2)

            img_p1 = to_img(cp1_g)
            img_p2 = to_img(cp2_g)

            draw.line([img_p1, img_p2], fill=(220, 38, 38), width=4)

            draw.text(((img_nw[0] + img_ne[0]) / 2 - 20, (img_nw[1] + img_ne[1]) / 2 - 14), f"N: {n:.1f}ft", fill=(10, 30, 90), font=font_label)
            draw.text(((img_sw[0] + img_se[0]) / 2 - 20, (img_sw[1] + img_se[1]) / 2 + 2), f"S: {s:.1f}ft", fill=(10, 30, 90), font=font_label)
            draw.text(((img_nw[0] + img_sw[0]) / 2 - 48, (img_nw[1] + img_sw[1]) / 2 - 6), f"W: {w:.1f}ft", fill=(10, 30, 90), font=font_label)
            draw.text(((img_ne[0] + img_se[0]) / 2 + 3, (img_ne[1] + img_se[1]) / 2 - 6), f"E: {e:.1f}ft", fill=(10, 30, 90), font=font_label)

            div_exact_len = math.sqrt((cp1_g[0]-cp2_g[0])**2 + (cp1_g[1]-cp2_g[1])**2)
            draw.text(((img_p1[0] + img_p2[0]) / 2 + 3, (img_p1[1] + img_p2[1]) / 2 - 6), f"Div: {div_exact_len:.2f}ft", fill=(180, 0, 0), font=font_label)

            draw.text((img_nw[0] - 35, img_nw[1] - 12), f"NW:{angles.get('NW', 0):.1f}°", fill=(0, 100, 0), font=font_label)
            draw.text((img_ne[0] + 3, img_ne[1] - 12), f"NE:{angles.get('NE', 0):.1f}°", fill=(0, 100, 0), font=font_label)
            draw.text((img_se[0] + 3, img_se[1] + 2), f"SE:{angles.get('SE', 0):.1f}°", fill=(0, 100, 0), font=font_label)
            draw.text((img_sw[0] - 35, img_sw[1] + 2), f"SW:{angles.get('SW', 0):.1f}°", fill=(0, 100, 0), font=font_label)

            cx_comp, cy_comp = 70, 80
            draw.polygon([(cx_comp, cy_comp - 25), (cx_comp - 8, cy_comp), (cx_comp + 8, cy_comp)], fill=(220, 38, 38))
            draw.polygon([(cx_comp, cy_comp + 25), (cx_comp - 8, cy_comp), (cx_comp + 8, cy_comp)], fill=(30, 41, 59))
            draw.text((cx_comp - 5, cy_comp - 45), "N", fill=(220, 38, 38), font=font_compass)

            draw.text((30, 20), "LAND SURVEY & PARTITION MAP (Scale: 32\" = 1 Mile)", fill=(15, 23, 42), font=font_title)

            box_x1, box_y1 = 920, 120
            box_x2, box_y2 = 1250, 600

            draw.rectangle([box_x1 + 4, box_y1 + 4, box_x2 + 4, box_y2 + 4], fill=(210, 215, 225))
            draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=(255, 255, 255), outline=(30, 58, 138), width=2)

            draw.rectangle([box_x1, box_y1, box_x2, box_y1 + 38], fill=(30, 58, 138))
            draw.text((box_x1 + 35, box_y1 + 10), "SUMMARY REPORT", fill=(255, 255, 255), font=font_header)

            if "NE" in diag_choice:
                area1 = self.heron_area(n, e, d)
                area2 = self.heron_area(s, w, d)
            else:
                area1 = self.heron_area(n, w, d)
                area2 = self.heron_area(s, e, d)

            total_sqft = area1 + area2
            total_shotok = total_sqft / 435.6

            sep_shotok = target_shotok
            sep_sqft = sep_shotok * 435.6

            rem_sqft = max(total_sqft - sep_sqft, 0)
            rem_shotok = rem_sqft / 435.6

            curr_y = box_y1 + 50
            line_spacing = 24

            report_lines = [
                ("Total Area:", (30, 58, 138), True),
                (f" {total_shotok:.3f} Shotok ({total_sqft:.1f} sqft)", (15, 23, 42), False),
                ("Main Boundaries:", (30, 58, 138), True),
                (f" N:{n:.1f}' | S:{s:.1f}'", (15, 23, 42), False),
                (f" E:{e:.1f}' | W:{w:.1f}' | Diag:{d:.1f}'", (15, 23, 42), False),
                ("Partition Details:", (30, 58, 138), True),
                (f" Direction: {direction}", (15, 23, 42), False),
                (f" Target: {sep_shotok:.3f} Shotok", (220, 38, 38), False),
                (f" Cut 1: {c1:.2f} ft | Cut 2: {c2:.2f} ft", (15, 23, 42), False),
                (f" Divider Line: {div_exact_len:.2f} ft", (180, 0, 0), False),
                ("Remaining Area:", (30, 58, 138), True),
                (f" {rem_shotok:.3f} Shotok ({rem_sqft:.1f} sqft)", (0, 102, 204), False),
            ]

            for text, color, is_header in report_lines:
                if is_header:
                    draw.text((box_x1 + 15, curr_y), text, fill=color, font=font_header)
                    curr_y += 22
                else:
                    draw.text((box_x1 + 15, curr_y), text, fill=color, font=font_label)
                    curr_y += line_spacing

            file_name = "scaled_land_map.jpg"
            img.save(file_name, "JPEG", quality=95)

            msg = f"Scaled Map Saved Successfully!\n\nSaved Path:\n{os.path.abspath(file_name)}"
            self._show_info_popup("SUCCESS", msg)

        except Exception as err:
            self._show_info_popup("Export Error", str(err))

    def _show_info_popup(self, title_text, body_text):
        popup_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)

        lbl = Label(text=body_text, font_size="14sp", halign="center", color=(1, 1, 1, 1))
        lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        popup_layout.add_widget(lbl)

        ok_btn = Button(
            text="OK", 
            size_hint_y=None, 
            height=42, 
            bold=True, 
            font_size="16sp",
            background_normal='',
            background_color=(0.1, 0.7, 0.4, 1)
        )
        popup_layout.add_widget(ok_btn)

        popup = Popup(
            title=title_text, 
            content=popup_layout, 
            size_hint=(0.85, 0.45),
            auto_dismiss=False
        )
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()

    def on_calc_click(self, instance):
        self.has_calculated = True
        self.calculate()

    def on_dropdown_change(self, spinner, text):
        if self.has_calculated:
            self.calculate()

    def reset_inputs(self, instance=None):
        self.updating_internally = True
        self.has_calculated = False

        self.north_in.text = ""
        self.south_in.text = ""
        self.east_in.text = ""
        self.west_in.text = ""
        self.diag_in.text = ""
        self.target_shotok_in.text = ""
        self.diag_spinner.text = "Diagonal 1 (NE to SW)"
        self.direction_spinner.text = "From North"
        self.part_diag_spinner.text = "Diagonal A"
        self.cut1_in.text = ""
        self.cut2_in.text = ""

        self.result_label.text = "Enter values and click Calculate..."
        self.visualizer.reset_rotation()
        self.visualizer.draw_land(0, 0, 0, 0, [0, 0], "From North", "Diagonal 1 (NE to SW)", {})
        self.updating_internally = False

    def show_formula_popup(self, instance):
        info_text = (
            "[color=00e5ff][b]1. Heron's Formula (Triangulation Area):[/b][/color]\n"
            "Calculates non-parallel quadrilateral & scalene triangle areas accurately by splitting via selected Diagonal (NE-SW or NW-SE):\n"
            "• [color=ffb703]Semi-perimeter (s) = (a + b + c) / 2[/color]\n"
            "• [color=ffb703]Area = sqrt(s * (s - a) * (s - b) * (s - c))[/color]\n\n"

            "[color=00e5ff][b]2. Law of Cosines & Trigonometry (Corner Angles & Cuts):[/b][/color]\n"
            "Determines exact corner angles (NW, NE, SE, SW) for 2D/3D plotting and computes triangular cuts:\n"
            "• [color=ffb703]cos(C) = (a^2 + b^2 - c^2) / (2 * a * b)[/color]\n"
            "• [color=ffb703]Triangle Partition Area = 0.5 * a * b * sin(C)[/color]\n\n"

            "[color=00e5ff][b]3. Binary Search Algorithm (Exact Partitioning):[/b][/color]\n"
            "Determines precise cut lengths (Side 1 & Side 2) for target land division across angled boundaries:\n"
            "• Performs [color=00ff66]50 High-Precision Iterations[/color] of Binary Search.\n"
            "• Ensures accuracy up to [color=00ff66]0.0001 ft[/color].\n\n"

            "[color=00e5ff][b]4. Coordinate Geometry & Sub-Diagonals:[/b][/color]\n"
            "Calculates exact lengths of Divider Line and Sub-Partition Diagonals (Diagonal A & B):\n"
            "• [color=ffb703]Euclidean Distance (d) = sqrt((x2 - x1)^2 + (y2 - y1)^2)[/color]\n\n"

            "[color=00e5ff][b]Precision & Accuracy Standard:[/b][/color]\n"
            "Unlike traditional average methods (which cause significant error), this application uses true [color=00ff66]Triangulation Architecture[/color] to ensure 100% mathematical accuracy.")
        popup_layout = BoxLayout(orientation='vertical', padding=12, spacing=10)
        popup_scroll = ScrollView(size_hint=(1, 1))
        popup_label = Label(text=info_text, markup=True, font_size="14sp", size_hint_y=None, halign="left", valign="top")
        popup_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        popup_label.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1] + 10))

        popup_scroll.add_widget(popup_label)
        popup_layout.add_widget(popup_scroll)

        close_btn = Button(text="Close", size_hint_y=None, height=42, background_normal='', background_color=(0.8, 0.2, 0.2, 1), bold=True, font_size="15sp")
        popup_layout.add_widget(close_btn)

        popup = Popup(title="Formulas & Calculation Principles", content=popup_layout, size_hint=(0.92, 0.82))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

        popup_layout = BoxLayout(orientation='vertical', padding=12, spacing=10)
        popup_scroll = ScrollView(size_hint=(1, 1))
        popup_label = Label(text=info_text, markup=True, font_size="14sp", size_hint_y=None, halign="left", valign="top")
        popup_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        popup_label.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1] + 10))

        popup_scroll.add_widget(popup_label)
        popup_layout.add_widget(popup_scroll)

        popup = Popup(title="Formulas & Calculation Principles", content=popup_layout, size_hint=(0.92, 0.82))
        
    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _update_text_size(self, instance, value):
        instance.text_size = (value[0], None)

    def _update_label_height(self, instance, value):
        instance.height = value[1] + 20

    def _update_dev_text_size(self, instance, value):
        instance.text_size = (value[0], None)

    def _update_dev_label_height(self, instance, value):
        instance.height = value[1] + 10

    def heron_area(self, a, b, c):
        s = (a + b + c) / 2
        if s <= a or s <= b or s <= c:
            return 0.0
        return math.sqrt(s * (s - a) * (s - b) * (s - c))

    def triangle_angle(self, a, b, c):
        if a <= 0 or b <= 0:
            return 0.0
        cos_val = (a**2 + b**2 - c**2) / (2 * a * b)
        cos_val = max(-1.0, min(1.0, cos_val))
        return math.degrees(math.acos(cos_val))

    def quad_area(self, p1, p2, p3, p4):
        return 0.5 * abs(p1[0]*(p2[1]-p4[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p4[1]-p2[1]) + p4[0]*(p1[1]-p3[1]))

    def get_quad_points_and_angles(self, n, s, e, w, d, diag_choice):
        angles = {}
        if "NE" in diag_choice:
            # Triangle 1: NE-SW diagonal dividing into (N, E, D) and (S, W, D)
            ang_NE1 = self.triangle_angle(n, e, d)
            ang_NW = self.triangle_angle(n, w, d)
            ang_SE = self.triangle_angle(s, e, d)
            ang_SW1 = self.triangle_angle(s, w, d)

            # SW at (0,0)
            sw = (0.0, 0.0)
            # SE along X-axis
            se = (s, 0.0)
            
            # NE position using Triangle (S, W, D) -> SW, SE, NE
            ang_SW_diag = self.triangle_angle(s, d, w)
            rad_SW_diag = math.radians(ang_SW_diag)
            ne = (d * math.cos(rad_SW_diag), d * math.sin(rad_SW_diag))

            # NW position relative to SW and NE
            ang_SW_W = self.triangle_angle(w, d, n)
            rad_NW_tot = math.radians(ang_SW_diag + ang_SW_W)
            nw = (w * math.cos(rad_NW_tot), w * math.sin(rad_NW_tot))

            angles['NW'] = ang_NW
            angles['NE'] = ang_NE1
            angles['SE'] = ang_SE
            angles['SW'] = ang_SW1
        else:
            # Triangle 2: NW-SE diagonal dividing into (N, W, D) and (S, E, D)
            ang_NW1 = self.triangle_angle(n, w, d)
            ang_NE = self.triangle_angle(n, e, d)
            ang_SE1 = self.triangle_angle(s, e, d)
            ang_SW = self.triangle_angle(s, w, d)

            sw = (0.0, 0.0)
            se = (s, 0.0)

            # NW from SW along W
            ang_SW_corner = self.triangle_angle(s, w, d)
            rad_SW_corner = math.radians(ang_SW_corner)
            nw = (w * math.cos(rad_SW_corner), w * math.sin(rad_SW_corner))

            # SE is at (s, 0), NE from SE along E
            ang_SE_corner = self.triangle_angle(s, e, d)
            rad_SE_corner = math.radians(180 - ang_SE_corner)
            ne = (s + e * math.cos(rad_SE_corner), e * math.sin(rad_SE_corner))

            angles['NW'] = ang_NW1
            angles['NE'] = ang_NE
            angles['SE'] = ang_SE1
            angles['SW'] = ang_SW

        return nw, ne, se, sw, angles

    def compute_exact_c2(self, c1, target_sqft):
        try:
            n = float(self.north_in.text)
            s = float(self.south_in.text)
            e = float(self.east_in.text)
            w = float(self.west_in.text)
            d = float(self.diag_in.text)
            direction = self.direction_spinner.text
            diag_choice = self.diag_spinner.text
        except ValueError:
            return None

        nw, ne, se, sw, _ = self.get_quad_points_and_angles(n, s, e, w, d, diag_choice)

        limit_c1 = w if direction in ["From North", "From South"] else n
        limit_c2 = e if direction in ["From North", "From South"] else s

        f1 = min(max(c1 / limit_c1, 0.0), 1.0) if limit_c1 > 0 else 0.0

        low, high = 0.0, limit_c2
        best_c2 = 0.0

        for _ in range(50):
            mid = (low + high) / 2
            f2 = min(max(mid / limit_c2, 0.0), 1.0) if limit_c2 > 0 else 0.0

            if direction == "From North":
                p1 = (nw[0] + (sw[0]-nw[0])*f1, nw[1] + (sw[1]-nw[1])*f1)
                p2 = (ne[0] + (se[0]-ne[0])*f2, ne[1] + (se[1]-ne[1])*f2)
                curr_area = self.quad_area(nw, ne, p2, p1)
            elif direction == "From South":
                p1 = (sw[0] + (nw[0]-sw[0])*f1, sw[1] + (nw[1]-sw[1])*f1)
                p2 = (se[0] + (ne[0]-se[0])*f2, se[1] + (ne[1]-se[1])*f2)
                curr_area = self.quad_area(sw, se, p2, p1)
            elif direction == "From East":
                p1 = (ne[0] + (nw[0]-ne[0])*f1, ne[1] + (nw[1]-ne[1])*f1)
                p2 = (se[0] + (sw[0]-se[0])*f2, se[1] + (sw[1]-se[1])*f2)
                curr_area = self.quad_area(ne, se, p2, p1)
            elif direction == "From West":
                p1 = (nw[0] + (ne[0]-nw[0])*f1, nw[1] + (ne[1]-nw[1])*f1)
                p2 = (sw[0] + (se[0]-sw[0])*f2, sw[1] + (se[1]-sw[1])*f2)
                curr_area = self.quad_area(nw, sw, p2, p1)

            if curr_area < target_sqft:
                low = mid
            else:
                high = mid
            best_c2 = mid

        return best_c2

    def _get_max_c1_for_target(self, target_sqft):
        try:
            n = float(self.north_in.text)
            s = float(self.south_in.text)
            e = float(self.east_in.text)
            w = float(self.west_in.text)
            d = float(self.diag_in.text)
            direction = self.direction_spinner.text
            diag_choice = self.diag_spinner.text
        except ValueError:
            return 0.0

        nw, ne, se, sw, _ = self.get_quad_points_and_angles(n, s, e, w, d, diag_choice)

        limit_c1 = w if direction in ["From North", "From South"] else n
        limit_c2 = e if direction in ["From North", "From South"] else s

        f2 = 1.0
        low, high = 0.0, limit_c1
        min_c1 = 0.0

        for _ in range(50):
            mid = (low + high) / 2
            f1 = min(max(mid / limit_c1, 0.0), 1.0) if limit_c1 > 0 else 0.0

            if direction == "From North":
                p1 = (nw[0] + (sw[0]-nw[0])*f1, nw[1] + (sw[1]-nw[1])*f1)
                p2 = (ne[0] + (se[0]-ne[0])*f2, ne[1] + (se[1]-ne[1])*f2)
                curr_area = self.quad_area(nw, ne, p2, p1)
            elif direction == "From South":
                p1 = (sw[0] + (nw[0]-sw[0])*f1, sw[1] + (nw[1]-sw[1])*f1)
                p2 = (se[0] + (ne[0]-se[0])*f2, se[1] + (ne[1]-se[1])*f2)
                curr_area = self.quad_area(sw, se, p2, p1)
            elif direction == "From East":
                p1 = (ne[0] + (nw[0]-ne[0])*f1, ne[1] + (nw[1]-ne[1])*f1)
                p2 = (se[0] + (sw[0]-se[0])*f2, se[1] + (sw[1]-se[1])*f2)
                curr_area = self.quad_area(ne, se, p2, p1)
            elif direction == "From West":
                p1 = (nw[0] + (ne[0]-nw[0])*f1, nw[1] + (ne[1]-nw[1])*f1)
                p2 = (sw[0] + (se[0]-sw[0])*f2, sw[1] + (se[1]-sw[1])*f2)
                curr_area = self.quad_area(nw, sw, p2, p1)

            if curr_area < target_sqft:
                low = mid
            else:
                high = mid
            min_c1 = mid

        return min_c1

    def compute_exact_c2_limit_for_zero(self, target_sqft):
        try:
            n = float(self.north_in.text)
            s = float(self.south_in.text)
            e = float(self.east_in.text)
            w = float(self.west_in.text)
            d = float(self.diag_in.text)
            direction = self.direction_spinner.text
            diag_choice = self.diag_spinner.text
        except ValueError:
            return 0.0

        nw, ne, se, sw, _ = self.get_quad_points_and_angles(n, s, e, w, d, diag_choice)

        limit_c1 = w if direction in ["From North", "From South"] else n
        f2 = 0.0

        low, high = 0.0, limit_c1
        max_c1 = limit_c1

        for _ in range(50):
            mid = (low + high) / 2
            f1 = min(max(mid / limit_c1, 0.0), 1.0) if limit_c1 > 0 else 0.0

            if direction == "From North":
                p1 = (nw[0] + (sw[0]-nw[0])*f1, nw[1] + (sw[1]-nw[1])*f1)
                p2 = (ne[0] + (se[0]-ne[0])*f2, ne[1] + (se[1]-ne[1])*f2)
                curr_area = self.quad_area(nw, ne, p2, p1)
            elif direction == "From South":
                p1 = (sw[0] + (nw[0]-sw[0])*f1, sw[1] + (nw[1]-sw[1])*f1)
                p2 = (se[0] + (ne[0]-se[0])*f2, se[1] + (ne[1]-se[1])*f2)
                curr_area = self.quad_area(sw, se, p2, p1)
            elif direction == "From East":
                p1 = (ne[0] + (nw[0]-ne[0])*f1, ne[1] + (nw[1]-ne[1])*f1)
                p2 = (se[0] + (sw[0]-se[0])*f2, se[1] + (sw[1]-se[1])*f2)
                curr_area = self.quad_area(ne, se, p2, p1)
            elif direction == "From West":
                p1 = (nw[0] + (ne[0]-nw[0])*f1, nw[1] + (ne[1]-nw[1])*f1)
                p2 = (sw[0] + (se[0]-sw[0])*f2, sw[1] + (se[1]-sw[1])*f2)
                curr_area = self.quad_area(nw, sw, p2, p1)

            if curr_area < target_sqft:
                low = mid
            else:
                high = mid
            max_c1 = mid

        return max_c1

    def calculate(self, *args):
        if self.updating_internally:
            return

        try:
            n = float(self.north_in.text)
            s = float(self.south_in.text)
            e = float(self.east_in.text)
            w = float(self.west_in.text)
            d = float(self.diag_in.text)
            target_shotok = float(self.target_shotok_in.text)
            direction = self.direction_spinner.text
            diag_choice = self.diag_spinner.text

            if "NE" in diag_choice:
                min_d = max(abs(n - e), abs(s - w))
                max_d = min(n + e, s + w)
            else:
                min_d = max(abs(n - w), abs(s - e))
                max_d = min(n + w, s + e)

            if d <= min_d or d >= max_d:
                err_msg = f"[color=ff4d4d][b]Error: Invalid side lengths or diagonal![/b]\n"
                err_msg += f"Selected Diagonal Range:\n"
                err_msg += f"• Min: [color=00ff66]{min_d + 0.01:.2f} ft[/color]\n"
                err_msg += f"• Max: [color=00ff66]{max_d - 0.01:.2f} ft[/color][/color]"
                self.result_label.text = err_msg
                return

            if "NE" in diag_choice:
                area1 = self.heron_area(n, e, d)
                area2 = self.heron_area(s, w, d)
            else:
                area1 = self.heron_area(n, w, d)
                area2 = self.heron_area(s, e, d)

            total_sqft = area1 + area2

            if total_sqft == 0:
                self.result_label.text = "[color=ff4d4d]Error: Invalid side lengths or diagonal![/color]"
                return

            target_sqft = target_shotok * 435.6
            if target_sqft > total_sqft:
                self.result_label.text = "[color=ff4d4d]Error: Target land is larger than total land![/color]"
                return

            area_ratio = target_sqft / total_sqft

            if direction in ["From North", "From South"]:
                self.cut1_label.text = "Cut West Side (ft):"
                self.cut2_label.text = "Cut East Side (ft):"
                c1_init = w * area_ratio
            else:
                self.cut1_label.text = "Cut North Side (ft):"
                self.cut2_label.text = "Cut South Side (ft):"
                c1_init = n * area_ratio

            c2_exact = self.compute_exact_c2(c1_init, target_sqft)

            if c2_exact is None:
                c2_exact = 0.0

            self.updating_internally = True
            self.cut1_in.text = f"{c1_init:.2f}"
            self.cut2_in.text = f"{c2_exact:.2f}"
            self.updating_internally = False

            self.update_results(c1_init, c2_exact)

        except ValueError:
            pass

    def on_cut1_change(self, instance, value):
        if self.updating_internally or not self.has_calculated:
            return

        if not value:
            self.updating_internally = True
            self.cut2_in.text = ""
            self.updating_internally = False
            return

        try:
            c1 = float(value)
            direction = self.direction_spinner.text

            n = float(self.north_in.text)
            w = float(self.west_in.text)

            max_allowed = w if direction in ["From North", "From South"] else n
            side_name = "West Side Boundary" if direction in ["From North", "From South"] else "North Side Boundary"

            target_sqft = float(self.target_shotok_in.text) * 435.6

            min_c1_required = self._get_max_c1_for_target(target_sqft)
            max_c1_limit = self.compute_exact_c2_limit_for_zero(target_sqft)

            if c1 > max_allowed or c1 < min_c1_required or c1 > max_c1_limit:
                self.updating_internally = True
                self.cut2_in.text = "Invalid"
                self.updating_internally = False

                err_msg = f"[color=ff4d4d][b]Error: Invalid Cut Side 1 Length![/b]\n"
                err_msg += f"• Entered Value: [color=ffaa00]{c1:.2f} ft[/color]\n"
                err_msg += f"• Referenced {side_name}: [color=00ff66]{max_allowed:.2f} ft[/color]\n"
                err_msg += f"• Valid Reference Range: [color=00ff66]{min_c1_required:.2f} ft[/color] to [color=00ff66]{max_c1_limit:.2f} ft[/color]\n"
                err_msg += f"Please enter a value within the reference scale.[/color]"
                self.result_label.text = err_msg
                return

            c2 = self.compute_exact_c2(c1, target_sqft)

            if c2 is None:
                self.updating_internally = True
                self.cut2_in.text = "Error"
                self.updating_internally = False
                return

            self.updating_internally = True
            self.cut2_in.text = f"{c2:.2f}"
            self.updating_internally = False

            self.update_results(c1, c2)
        except ValueError:
            pass

    def update_results(self, c1, c2):
        try:
            n = float(self.north_in.text)
            s = float(self.south_in.text)
            e = float(self.east_in.text)
            w = float(self.west_in.text)
            d = float(self.diag_in.text)
            direction = self.direction_spinner.text
            diag_choice = self.diag_spinner.text
            part_diag_choice = self.part_diag_spinner.text

            if "NE" in diag_choice:
                area1 = self.heron_area(n, e, d)
                area2 = self.heron_area(s, w, d)
            else:
                area1 = self.heron_area(n, w, d)
                area2 = self.heron_area(s, e, d)

            total_sqft = area1 + area2
            total_shotok = total_sqft / 435.6

            nw, ne, se, sw, angles = self.get_quad_points_and_angles(n, s, e, w, d, diag_choice)

            if direction in ["From North", "From South"]:
                f1 = min(c1 / w, 1.0) if w > 0 else 0
                f2 = min(c2 / e, 1.0) if e > 0 else 0
            else:
                f1 = min(c1 / n, 1.0) if n > 0 else 0
                f2 = min(c2 / s, 1.0) if s > 0 else 0

            cut_frac = [f1, f2]
            base_len = 0
            part_diag_pts = None
            diag_dir_name = ""

            if direction == "From North":
                p1 = (nw[0] + (sw[0]-nw[0])*f1, nw[1] + (sw[1]-nw[1])*f1)
                p2 = (ne[0] + (se[0]-ne[0])*f2, ne[1] + (se[1]-ne[1])*f2)
                sep_sqft = self.quad_area(nw, ne, p2, p1)
                base_len = n
                if part_diag_choice == "Diagonal A":
                    part_diag_pts = (nw, p2)
                    diag_dir_name = "North-West Corner to East Cut-Point"
                else:
                    part_diag_pts = (ne, p1)
                    diag_dir_name = "North-East Corner to West Cut-Point"

            elif direction == "From South":
                p1 = (sw[0] + (nw[0]-sw[0])*f1, sw[1] + (nw[1]-sw[1])*f1)
                p2 = (se[0] + (ne[0]-se[0])*f2, se[1] + (ne[1]-se[1])*f2)
                sep_sqft = self.quad_area(sw, se, p2, p1)
                base_len = s
                if part_diag_choice == "Diagonal A":
                    part_diag_pts = (sw, p2)
                    diag_dir_name = "South-West Corner to East Cut-Point"
                else:
                    part_diag_pts = (se, p1)
                    diag_dir_name = "South-East Corner to West Cut-Point"

            elif direction == "From East":
                p1 = (ne[0] + (nw[0]-ne[0])*f1, ne[1] + (nw[1]-ne[1])*f1)
                p2 = (se[0] + (sw[0]-se[0])*f2, se[1] + (sw[1]-se[1])*f2)
                sep_sqft = self.quad_area(ne, se, p2, p1)
                base_len = e
                if part_diag_choice == "Diagonal A":
                    part_diag_pts = (ne, p2)
                    diag_dir_name = "North-East Corner to South Cut-Point"
                else:
                    part_diag_pts = (se, p1)
                    diag_dir_name = "South-East Corner to North Cut-Point"

            elif direction == "From West":
                p1 = (nw[0] + (ne[0]-nw[0])*f1, nw[1] + (ne[1]-nw[1])*f1)
                p2 = (sw[0] + (se[0]-sw[0])*f2, sw[1] + (se[1]-sw[1])*f2)
                sep_sqft = self.quad_area(nw, sw, p2, p1)
                base_len = w
                if part_diag_choice == "Diagonal A":
                    part_diag_pts = (nw, p2)
                    diag_dir_name = "North-West Corner to South Cut-Point"
                else:
                    part_diag_pts = (sw, p1)
                    diag_dir_name = "South-West Corner to North Cut-Point"

            new_line = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
            part_diag_len = math.sqrt((part_diag_pts[0][0] - part_diag_pts[1][0])**2 + (part_diag_pts[0][1] - part_diag_pts[1][1])**2)

            sep_shotok = sep_sqft / 435.6
            rem_sqft = max(total_sqft - sep_sqft, 0)
            rem_shotok = rem_sqft / 435.6

            res = f"[color=00e5ff][b]=== Precision Land Report ===[/b][/color]\n"
            res += f"Total Area: {total_sqft:.2f} Sq.Ft ([color=00ffff]{total_shotok:.3f} Shotok[/color])\n"
            res += f"Calculated Angles: NW: {angles.get('NW',0):.1f}°, NE: {angles.get('NE',0):.1f}°, SE: {angles.get('SE',0):.1f}°, SW: {angles.get('SW',0):.1f}°\n"
            res += f"Separated Target Area: [color=00ff66]{sep_shotok:.3f} Shotok ({sep_sqft:.2f} Sq.Ft)[/color]\n\n"
            res += f"[color=ffb703][b]Partition Boundary Measures ({direction}):[/b][/color]\n"
            res += f"• Main Base Line: {base_len:.2f} ft\n"
            res += f"• Adjusted Cut Side 1: {c1:.2f} ft\n"
            res += f"• Adjusted Cut Side 2: {c2:.2f} ft\n"
            res += f"• Exact Divider Line: [color=ff5555]{new_line:.2f} ft[/color]\n"
            res += f"• Sub-Partition Diagonal ([color=ffaa00]{part_diag_choice}[/color]): [color=ffaa00]{part_diag_len:.2f} ft[/color]\n"
            res += f"  ({diag_dir_name})\n\n"
            res += f"[color=00e5ff][b]Remaining Main Land:[/b][/color] {rem_shotok:.3f} Shotok ({rem_sqft:.2f} Sq.Ft)"

            self.visualizer.draw_land(n, s, e, w, cut_frac, direction, diag_choice, angles, quad_pts=(nw, ne, se, sw), part_diag_pts=part_diag_pts, part_diag_len=part_diag_len)
            self.result_label.text = res

        except Exception:
            pass


if __name__ == "__main__":
    AdvancedLandCalculatorApp().run()
