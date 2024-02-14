import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import cv2

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.canvas_width = 1000
        self.canvas_height = 800
        self.setup_canvas()
        self.setup_tools()
        self.setup_events()
        self.setup_defaults()

    def setup_canvas(self):
        self.image = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
        self.drawn_image = self.get_image_tk(self.image)
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.drawn_image, anchor="nw")

    def setup_tools(self):
        self.selected_tool = tk.StringVar(value="pen")
        self.selected_color = tk.StringVar(value="Negro")
        self.colors = ["Negro", "Azul", "Rojo", "Amarillo", "Naranja", "Verde"]
        self.brush_size = 4
        self.color_map = {
            "Negro": (0, 0, 0),
            "Azul": (255, 100, 0),
            "Rojo": (0, 0, 255),
            "Amarillo": (0, 255, 255),
            "Naranja": (0, 165, 255),
            "Verde": (0, 128, 0)
        }

        self.tool_frame = ttk.LabelFrame(self.root, text="")
        self.tool_frame.pack(side=tk.RIGHT, padx=8, pady=8, fill=tk.Y)

        self.tool_buttons = []
        tool_names = ["Borrador", "Mano alzada", "Rectángulo", "Círculo", "Linea"]
        tool_commands = [self.select_eraser_tool, self.select_pen_tool, self.select_rectangle_tool, self.select_circle_tool, self.select_line_tool]

        self.color_label = ttk.Label(self.tool_frame, text="Selecciona un color:")
        self.color_label.pack(side=tk.TOP, padx=8, pady=8)  
        self.color_combobox = ttk.Combobox(self.tool_frame, values=self.colors, textvariable=self.selected_color, state="readonly")
        self.color_combobox.pack(side=tk.TOP, padx=18, pady=8)
        self.color_combobox.bind("<<ComboboxSelected>>", lambda event: self.select_color())
        
        for name, command in zip(tool_names, tool_commands):
            button = ttk.Button(self.tool_frame, text=name, command=command)
            button.pack(side=tk.TOP, padx=8, pady=8)
            self.tool_buttons.append(button)

        self.clear_button = ttk.Button(self.tool_frame, text="Borrar todo", command=self.clear_canvas)
        self.clear_button.pack(side=tk.TOP, padx=8, pady=8)      


    def setup_events(self):
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.finalize_draw)

    def setup_defaults(self):
        self.prev_x = None
        self.prev_y = None
        self.temp_image = None

    def select_pen_tool(self):
        self.selected_tool.set("pen")

    def select_eraser_tool(self):
        self.selected_tool.set("eraser")

    def select_line_tool(self):
        self.selected_tool.set("line")

    def select_rectangle_tool(self):
        self.selected_tool.set("rectangle")

    def select_circle_tool(self):
        self.selected_tool.set("circle")

    def select_color(self):
        self.selected_color.get()

    def start_draw(self, event):
        self.prev_x = event.x
        self.prev_y = event.y
        self.temp_image = self.image.copy()

    def draw(self, event):
        color = self.get_color()
        if self.selected_tool.get() == "pen":
            cv2.line(self.image, (self.prev_x, self.prev_y), (event.x, event.y), color, self.brush_size)
            self.prev_x = event.x
            self.prev_y = event.y
            self.redraw()
        elif self.selected_tool.get() == "eraser":
            cv2.line(self.image, (self.prev_x, self.prev_y), (event.x, event.y), (255, 255, 255), self.brush_size)
            self.prev_x = event.x
            self.prev_y = event.y
            self.redraw()
        elif self.selected_tool.get() in ["line", "rectangle", "circle"]:
            self.temp_image = self.image.copy()
            if self.selected_tool.get() == "line":
                cv2.line(self.temp_image, (self.prev_x, self.prev_y), (event.x, event.y), color, self.brush_size)
            elif self.selected_tool.get() == "rectangle":
                cv2.rectangle(self.temp_image, (self.prev_x, self.prev_y), (event.x, event.y), color, self.brush_size)
            elif self.selected_tool.get() == "circle":
                center = ((self.prev_x + event.x) // 2, (self.prev_y + event.y) // 2)
                radius = int(np.sqrt((event.x - self.prev_x) ** 2 + (event.y - self.prev_y) ** 2) / 2)
                cv2.circle(self.temp_image, center, radius, color, self.brush_size)
            self.redraw(temp_image=True)

    def finalize_draw(self, event):
        if self.selected_tool.get() in ["line", "rectangle", "circle"]:
            self.image = self.temp_image.copy()
        self.prev_x = None
        self.prev_y = None
        self.redraw()

    def redraw(self, temp_image=False):
        if temp_image:
            image = self.temp_image
        else:
            image = self.image
        self.drawn_image = self.get_image_tk(image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.drawn_image, anchor="nw")

    def clear_canvas(self):
        self.image = np.ones((self.canvas_height, self.canvas_width, 3), dtype=np.uint8) * 255
        self.redraw()

    def get_color(self):    
        return self.color_map[self.selected_color.get()]

    def get_image_tk(self, image):
        return ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Paint")
    app = PaintApp(root)
    root.mainloop()
