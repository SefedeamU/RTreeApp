import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from rtree import index
import copy

class RTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("R-Tree Visualizer")
        self.index = index.Index()
        self.history = [copy.deepcopy(self.index)]  # Historial para skip back/skip
        self.current_state = 0  # Puntero al estado actual
        self.root.resizable(False, False)

        # Dimensiones del canvas y escala
        self.canvas_width = 800
        self.canvas_height = 600
        self.coord_scale = 10  # Unidades de escala inicial
        self.offset_x = 0  # Desplazamiento en X
        self.offset_y = 0  # Desplazamiento en Y
        self.zoom_factor = 1.0  # Factor de zoom inicial

        # Variables de arrastre
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Estilo de la ventana
        discord_gray = "#2f3136"
        discord_dark = "#202225"
        discord_text = "#ffffff"

        self.root.configure(bg=discord_gray)
        self.log_text = tk.StringVar(value="")

        # Crear el canvas para dibujar
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg=discord_dark, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=5)

        # Vincular eventos de zoom y arrastre
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

        # Botones de operación
        ttk.Button(self.root, text="Insertar", command=self.insert_rect).grid(row=1, column=0)
        ttk.Button(self.root, text="Eliminar", command=self.delete_rect).grid(row=1, column=1)
        ttk.Button(self.root, text="Buscar", command=self.search_rect).grid(row=1, column=2)
        ttk.Button(self.root, text="Limpiar", command=self.clear_all).grid(row=1, column=3)

        # Registro de operaciones
        self.log_label = ttk.Label(self.root, text="Registro de Operaciones:", background=discord_gray, foreground=discord_text)
        self.log_label.grid(row=2, column=0, columnspan=5, sticky="w")
        self.log_box = tk.Text(self.root, height=10, width=95, state="disabled", wrap="word", bg=discord_dark, fg=discord_text)
        self.log_box.grid(row=3, column=0, columnspan=5)

        # Colores para niveles
        self.colors = ["cyan", "yellow", "orange", "lime", "magenta", "red", "blue", "purple"]

        # Dibujar los ejes iniciales
        self.draw_axes()

    def draw_axes(self):
        """Dibuja un sistema de coordenadas en el canvas."""
        self.canvas.delete("all")
        scaled_scale = self.coord_scale * self.zoom_factor

        # Eje X
        self.canvas.create_line(
            50 + self.offset_x, self.canvas_height - 50 - self.offset_y,
            self.canvas_width - 50 + self.offset_x, self.canvas_height - 50 - self.offset_y,
            fill="white", width=2
        )
        # Eje Y
        self.canvas.create_line(
            50 + self.offset_x, self.canvas_height - 50 - self.offset_y,
            50 + self.offset_x, 50 - self.offset_y,
            fill="white", width=2
        )

        # Marcas y etiquetas en X
        for i in range(0, int((self.canvas_width // scaled_scale))):
            x = 50 + i * scaled_scale + self.offset_x
            if x < self.canvas_width - 50:
                self.canvas.create_line(x, self.canvas_height - 45 - self.offset_y, x, self.canvas_height - 55 - self.offset_y, fill="white")
                self.canvas.create_text(x, self.canvas_height - 30 - self.offset_y, text=str(i), fill="white", font=("Arial", 8))

        # Marcas y etiquetas en Y
        for i in range(0, int((self.canvas_height // scaled_scale))):
            y = self.canvas_height - 50 - i * scaled_scale - self.offset_y
            if y > 50:
                self.canvas.create_line(45 + self.offset_x, y, 55 + self.offset_x, y, fill="white")
                self.canvas.create_text(30 + self.offset_x, y, text=str(i), fill="white", font=("Arial", 8))

    def zoom(self, event):
        """Maneja el evento de zoom con Ctrl + scroll del ratón."""
        if event.state & 0x4:  # Verificar si Ctrl está presionado
            if event.delta > 0:  # Zoom In
                self.zoom_factor *= 1.1
            elif event.delta < 0:  # Zoom Out
                self.zoom_factor /= 1.1

            # Limitar el zoom para evitar problemas
            self.zoom_factor = max(0.1, min(self.zoom_factor, 10))
            self.draw_mbr()

    def start_drag(self, event):
        """Inicia el arrastre del sistema de coordenadas."""
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def drag(self, event):
        """Realiza el arrastre del sistema de coordenadas."""
        if self.dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y

            # Actualizar los offsets
            self.offset_x += dx
            self.offset_y += dy

            # Limitar el movimiento al primer cuadrante
            self.offset_x = max(-50, self.offset_x)
            self.offset_y = max(-50, self.offset_y)

            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.draw_mbr()

    def stop_drag(self, event):
        """Termina el arrastre del sistema de coordenadas."""
        self.dragging = False

    def log_operation(self, message):
        """Registra una operación en la caja de texto."""
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, f"{message}\n")
        self.log_box.configure(state="disabled")
        self.log_box.see(tk.END)

    def draw_rectangle(self, rect, rect_id, color="blue"):
        """Dibuja un rectángulo con su ID en el canvas."""
        scaled_scale = self.coord_scale * self.zoom_factor

        # Escalar coordenadas al sistema de coordenadas visual
        scaled_rect = (
            50 + self.offset_x + rect[0] * scaled_scale,
            self.canvas_height - 50 - self.offset_y - rect[1] * scaled_scale,
            50 + self.offset_x + rect[2] * scaled_scale,
            self.canvas_height - 50 - self.offset_y - rect[3] * scaled_scale,
        )
        rect_canvas_id = self.canvas.create_rectangle(scaled_rect, outline=color, width=3)
        
        text_canvas_id = None
        # Solo dibujar el texto si el rect_id no es "B"
        if rect_id != "B":
            text_canvas_id = self.canvas.create_text(
                (scaled_rect[0] + scaled_rect[2]) / 2, (scaled_rect[1] + scaled_rect[3]) / 2,
                text=str(rect_id), fill="white", font=("Arial", 10, "bold")
            )
        return rect_canvas_id, text_canvas_id



    def draw_mbr(self):
        """Dibuja los MBRs actuales del R-Tree con colores diferenciados por niveles."""
        self.canvas.delete("all")
        self.draw_axes()
        for obj in self.index.intersection((0, 0, 100, 100), objects=True):
            level = self.get_level(obj.id)
            color = self.colors[level % len(self.colors)]
            self.draw_rectangle(obj.bbox, obj.id, color)

    def save_state(self):
        """Guarda el estado actual en el historial."""
        self.history = self.history[:self.current_state + 1]
        self.history.append(copy.deepcopy(self.index))
        self.current_state += 1

    def get_level(self, rect_id):
        """Calcula el nivel del rectángulo en el R-Tree."""
        return rect_id % len(self.colors)

    def insert_rect(self):
        """Permite insertar un rectángulo con datos personalizados como cadena."""
        try:
            rect_input = simpledialog.askstring("Insertar", "Ingresa las coordenadas: x1, y1, x2, y2")
            if not rect_input:
                return

            coords = list(map(int, rect_input.split(",")))
            if len(coords) != 4:
                messagebox.showerror("Error", "Debes ingresar exactamente 4 valores separados por comas.")
                return

            x1, y1, x2, y2 = coords
            if x1 >= x2 or y1 >= y2:
                messagebox.showerror("Error", "Las coordenadas deben formar un rectángulo válido (x1 < x2, y1 < y2).")
                return

            rect = (x1, y1, x2, y2)
            rect_id = len(self.index)
            self.index.insert(rect_id, rect)
            self.save_state()
            self.draw_mbr()
            self.log_operation(f"Insertado rectángulo {rect} con ID {rect_id}")
        except ValueError:
            messagebox.showerror("Error", "El formato debe ser: x1, y1, x2, y2 con valores numéricos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al insertar rectángulo: {e}")

    def delete_rect(self):
        """Elimina un rectángulo dado su ID."""
        try:
            id_to_delete = simpledialog.askinteger("Eliminar", "ID del rectángulo a eliminar:")
            if id_to_delete is None:
                return

            for obj in self.index.intersection((0, 0, 100, 100), objects=True):
                if obj.id == id_to_delete:
                    rect = obj.bbox
                    self.index.delete(id_to_delete, rect)
                    self.save_state()
                    self.draw_mbr()
                    self.log_operation(f"Eliminado rectángulo {rect} con ID {id_to_delete}")
                    return

            messagebox.showerror("Error", "ID no encontrado.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar rectángulo: {e}")

    def search_rect(self):
        """Busca rectángulos que intersectan un área definida."""
        try:
            rect_input = simpledialog.askstring("Buscar", "Ingresa las coordenadas del área: x1, y1, x2, y2")
            if not rect_input:
                return

            coords = list(map(int, rect_input.split(",")))
            if len(coords) != 4:
                messagebox.showerror("Error", "Debes ingresar exactamente 4 valores separados por comas.")
                return

            x1, y1, x2, y2 = coords
            search_area = (x1, y1, x2, y2)
            search_rect_id, search_text_id = self.draw_rectangle(search_area, "B", color="red")

            results = [obj.id for obj in self.index.intersection(search_area, objects=True)]
            self.log_operation(f"Área buscada: {search_area}. Rectángulos encontrados: {results}")
            messagebox.showinfo("Búsqueda", f"Área buscada: {search_area}\nIDs encontrados: {results}")

            # Eliminar el rectángulo de búsqueda y su texto después de mostrar el mensaje
            self.canvas.delete(search_rect_id)
            if search_text_id:
                self.canvas.delete(search_text_id)
        except ValueError:
            messagebox.showerror("Error", "El formato debe ser: x1, y1, x2, y2 con valores numéricos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar rectángulos: {e}")
            
    def clear_all(self):
        """Elimina todos los rectángulos del R-Tree."""
        self.index = index.Index()
        self.history = [copy.deepcopy(self.index)]
        self.current_state = 0
        self.draw_mbr()
        self.log_operation("Todos los rectángulos han sido eliminados.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RTreeApp(root)
    root.mainloop()