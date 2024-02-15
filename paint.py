import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import cv2

class AplicacionDibujo:
    def __init__(self, ventana_raiz):
        self.ventana_raiz = ventana_raiz
        self.ancho_canvas = 1000
        self.alto_canvas = 800
        self.configurar_canvas()
        self.configurar_herramientas()
        self.configurar_eventos()
        self.configurar_valores_predeterminados()

    def configurar_canvas(self):
        self.imagen = np.ones((self.alto_canvas, self.ancho_canvas, 3), dtype=np.uint8) * 255
        self.imagen_dibujada = self.obtener_imagen_tk(self.imagen)
        self.canvas = tk.Canvas(self.ventana_raiz, width=self.ancho_canvas, height=self.alto_canvas)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.imagen_dibujada, anchor="nw")

    def configurar_herramientas(self):
        self.herramienta_seleccionada = tk.StringVar(value="pluma")
        self.color_seleccionado = tk.StringVar(value="Negro")
        self.colores = ["Negro", "Azul", "Rojo", "Amarillo", "Naranja", "Verde"]
        self.tamaño_pincel = 4
        self.mapa_colores = {
            "Negro": (0, 0, 0),
            "Azul": (255, 100, 0),
            "Rojo": (0, 0, 255),
            "Amarillo": (0, 255, 255),
            "Naranja": (0, 165, 255),
            "Verde": (0, 128, 0)
        }

        self.marco_herramienta = ttk.LabelFrame(self.ventana_raiz, text="")
        self.marco_herramienta.pack(side=tk.RIGHT, padx=8, pady=8, fill=tk.Y)

        self.botones_herramienta = []
        nombres_herramientas = ["Borrador", "Mano alzada", "Rectángulo", "Círculo", "Línea"]
        comandos_herramientas = [self.seleccionar_herramienta_borrador, self.seleccionar_herramienta_pluma, self.seleccionar_herramienta_rectángulo, self.seleccionar_herramienta_círculo, self.seleccionar_herramienta_línea]

        self.etiqueta_color = ttk.Label(self.marco_herramienta, text="Selecciona un color:")
        self.etiqueta_color.pack(side=tk.TOP, padx=8, pady=8)  
        self.combo_color = ttk.Combobox(self.marco_herramienta, values=self.colores, textvariable=self.color_seleccionado, state="readonly")
        self.combo_color.pack(side=tk.TOP, padx=18, pady=8)
        self.combo_color.bind("<<ComboboxSelected>>", lambda event: self.seleccionar_color())
        
        for nombre, comando in zip(nombres_herramientas, comandos_herramientas):
            boton = ttk.Button(self.marco_herramienta, text=nombre, command=comando)
            boton.pack(side=tk.TOP, padx=8, pady=8)
            self.botones_herramienta.append(boton)

        self.boton_limpiar = ttk.Button(self.marco_herramienta, text="Borrar todo", command=self.limpiar_canvas)
        self.boton_limpiar.pack(side=tk.TOP, padx=8, pady=8)      


    def configurar_eventos(self):
        self.canvas.bind("<Button-1>", self.iniciar_dibujo)
        self.canvas.bind("<B1-Motion>", self.dibujar)
        self.canvas.bind("<ButtonRelease-1>", self.finalizar_dibujo)

    def configurar_valores_predeterminados(self):
        self.prev_x = None
        self.prev_y = None
        self.imagen_temporal = None

    def seleccionar_herramienta_pluma(self):
        self.herramienta_seleccionada.set("pluma")

    def seleccionar_herramienta_borrador(self):
        self.herramienta_seleccionada.set("borrador")

    def seleccionar_herramienta_línea(self):
        self.herramienta_seleccionada.set("línea")

    def seleccionar_herramienta_rectángulo(self):
        self.herramienta_seleccionada.set("rectángulo")

    def seleccionar_herramienta_círculo(self):
        self.herramienta_seleccionada.set("círculo")

    def seleccionar_color(self):
        self.color_seleccionado.get()

    def iniciar_dibujo(self, evento):
        self.prev_x = evento.x
        self.prev_y = evento.y
        self.imagen_temporal = self.imagen.copy()

    def dibujar(self, evento):
        color = self.obtener_color()
        if self.herramienta_seleccionada.get() == "pluma":
            cv2.line(self.imagen, (self.prev_x, self.prev_y), (evento.x, evento.y), color, self.tamaño_pincel)
            self.prev_x = evento.x
            self.prev_y = evento.y
            self.redibujar()
        elif self.herramienta_seleccionada.get() == "borrador":
            cv2.line(self.imagen, (self.prev_x, self.prev_y), (evento.x, evento.y), (255, 255, 255), self.tamaño_pincel)
            self.prev_x = evento.x
            self.prev_y = evento.y
            self.redibujar()
        elif self.herramienta_seleccionada.get() in ["línea", "rectángulo", "círculo"]:
            self.imagen_temporal = self.imagen.copy()
            if self.herramienta_seleccionada.get() == "línea":
                cv2.line(self.imagen_temporal, (self.prev_x, self.prev_y), (evento.x, evento.y), color, self.tamaño_pincel)
            elif self.herramienta_seleccionada.get() == "rectángulo":
                cv2.rectangle(self.imagen_temporal, (self.prev_x, self.prev_y), (evento.x, evento.y), color, self.tamaño_pincel)
            elif self.herramienta_seleccionada.get() == "círculo":
                centro = ((self.prev_x + evento.x) // 2, (self.prev_y + evento.y) // 2)
                radio = int(np.sqrt((evento.x - self.prev_x) ** 2 + (evento.y - self.prev_y) ** 2) / 2)
                cv2.circle(self.imagen_temporal, centro, radio, color, self.tamaño_pincel)
            self.redibujar(imagen_temporal=True)

    def finalizar_dibujo(self, evento):
        if self.herramienta_seleccionada.get() in ["línea", "rectángulo", "círculo"]:
            self.imagen = self.imagen_temporal.copy()
        self.prev_x = None
        self.prev_y = None
        self.redibujar()

    def redibujar(self, imagen_temporal=False):
        if imagen_temporal:
            imagen = self.imagen_temporal
        else:
            imagen = self.imagen
        self.imagen_dibujada = self.obtener_imagen_tk(imagen)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.imagen_dibujada, anchor="nw")

    def limpiar_canvas(self):
        self.imagen = np.ones((self.alto_canvas, self.ancho_canvas, 3), dtype=np.uint8) * 255
        self.redibujar()

    def obtener_color(self):    
        return self.mapa_colores[self.color_seleccionado.get()]

    def obtener_imagen_tk(self, imagen):
        return ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)))


if __name__ == "__main__":
    ventana_raiz = tk.Tk()
    ventana_raiz.title("Paint")
    app = AplicacionDibujo(ventana_raiz)
    ventana_raiz.mainloop()
