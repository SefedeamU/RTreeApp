import tkinter as tk
from tkinter import ttk
from rtree import index
import copy

class RTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("R-Tree Visualizer")
        self.index = index.Index()

        # Estilo de la ventana
        discord_gray = "#2f3136"
        discord_dark = "#202225"
        discord_text = "#ffffff"

        self.root.configure(bg=discord_gray)
        self.root.minsize(800, 600)  # Establecer tamaño mínimo de la ventana

        # Configuración de grid para adaptabilidad
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Canvas
        self.canvas = tk.Canvas(self.root, bg=discord_dark, highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=5, sticky="nsew")

        # Frame para botones y entradas
        self.button_frame = tk.Frame(self.root, bg=discord_gray)
        self.button_frame.grid(row=1, column=0, columnspan=5, sticky="ew")
        self.button_frame.columnconfigure([0, 1, 2, 3], weight=1)

        # Insertar
        self.insert_frame = tk.Frame(self.button_frame, bg=discord_gray, bd=2, relief="groove", highlightbackground="cyan", highlightcolor="cyan", highlightthickness=2)
        self.insert_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.insert_frame.columnconfigure([0, 1], weight=1)
        tk.Label(self.insert_frame, text="Insertar (x1, y1, x2, y2):", bg=discord_gray, fg=discord_text).grid(row=0, column=0, sticky="e")
        self.insert_entry = tk.Entry(self.insert_frame, bg=discord_dark, fg=discord_text, insertbackground=discord_text)
        self.insert_entry.grid(row=0, column=1, sticky="ew")
        insert_button = tk.Button(self.insert_frame, text="Insertar", command=self.insert_rect, bg="cyan", fg=discord_dark, relief="flat", bd=0)
        insert_button.grid(row=1, column=0, columnspan=2, pady=5)
        insert_button.configure(highlightbackground="cyan", highlightthickness=2, borderwidth=2, relief="solid", highlightcolor="cyan", padx=10, pady=5)
        insert_button.config(borderwidth=2, relief="solid", highlightthickness=2, highlightbackground="cyan", highlightcolor="cyan", padx=10, pady=5)

        # Eliminar
        self.delete_frame = tk.Frame(self.button_frame, bg=discord_gray, bd=2, relief="groove", highlightbackground="red", highlightcolor="red", highlightthickness=2)
        self.delete_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.delete_frame.columnconfigure([0, 1], weight=1)
        tk.Label(self.delete_frame, text="Eliminar ID:", bg=discord_gray, fg=discord_text).grid(row=0, column=0, sticky="e")
        self.delete_entry = tk.Entry(self.delete_frame, bg=discord_dark, fg=discord_text, insertbackground=discord_text)
        self.delete_entry.grid(row=0, column=1, sticky="ew")
        delete_button = tk.Button(self.delete_frame, text="Eliminar", command=self.delete_rect, bg="red", fg=discord_dark, relief="flat", bd=0)
        delete_button.grid(row=1, column=0, columnspan=2, pady=5)
        delete_button.configure(highlightbackground="red", highlightthickness=2, borderwidth=2, relief="solid", highlightcolor="red", padx=10, pady=5)
        delete_button.config(borderwidth=2, relief="solid", highlightthickness=2, highlightbackground="red", highlightcolor="red", padx=10, pady=5)

        # Buscar
        self.search_frame = tk.Frame(self.button_frame, bg=discord_gray, bd=2, relief="groove", highlightbackground="lime", highlightcolor="lime", highlightthickness=2)
        self.search_frame.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.search_frame.columnconfigure([0, 1], weight=1)
        tk.Label(self.search_frame, text="Buscar (x1, y1, x2, y2):", bg=discord_gray, fg=discord_text).grid(row=0, column=0, sticky="e")
        self.search_entry = tk.Entry(self.search_frame, bg=discord_dark, fg=discord_text, insertbackground=discord_text)
        self.search_entry.grid(row=0, column=1, sticky="ew")
        search_button = tk.Button(self.search_frame, text="Buscar", command=self.search_rect, bg="lime", fg=discord_dark, relief="flat", bd=0)
        search_button.grid(row=1, column=0, columnspan=2, pady=5)
        search_button.configure(highlightbackground="lime", highlightthickness=2, borderwidth=2, relief="solid", highlightcolor="lime", padx=10, pady=5)
        search_button.config(borderwidth=2, relief="solid", highlightthickness=2, highlightbackground="lime", highlightcolor="lime", padx=10, pady=5)

        # Limpiar
        self.clear_frame = tk.Frame(self.button_frame, bg=discord_gray, bd=2, relief="groove", highlightbackground="yellow", highlightcolor="yellow", highlightthickness=2)
        self.clear_frame.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.clear_frame.columnconfigure(0, weight=1)
        clear_button = tk.Button(self.clear_frame, text="Limpiar", command=self.clear_canvas, bg="yellow", fg=discord_dark, relief="flat", bd=0)
        clear_button.grid(row=0, column=0, pady=5)
        clear_button.configure(highlightbackground="yellow", highlightthickness=2, borderwidth=2, relief="solid", highlightcolor="yellow", padx=10, pady=5)
        clear_button.config(borderwidth=2, relief="solid", highlightthickness=2, highlightbackground="yellow", highlightcolor="yellow", padx=10, pady=5)

        # Registro de operaciones
        self.log_box = tk.Text(self.root, height=10, state="normal", wrap="word", bg=discord_dark, fg=discord_text)
        self.log_box.grid(row=2, column=0, columnspan=5, sticky="nsew")
        self.root.rowconfigure(2, weight=1)

        # Colores para niveles
        self.colors = ["cyan", "yellow", "orange", "lime", "magenta", "red", "blue", "purple"]

    def log_operation(self, message, error=False):
        """Registra una operación en la caja de texto."""
        self.log_box.configure(state="normal")
        color = "red" if error else "white"
        self.log_box.insert(tk.END, f"{message}\n", color)
        self.log_box.tag_configure("red", foreground="red")
        self.log_box.tag_configure("white", foreground="white")
        self.log_box.configure(state="disabled")
        self.log_box.see(tk.END)

    def draw_rectangle(self, rect, rect_id, color="blue"):
        """Dibuja un rectángulo con su ID en el canvas."""
        self.canvas.create_rectangle(rect[0], rect[1], rect[2], rect[3], outline=color, width=3)
        self.canvas.create_text(
            (rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2,
            text=str(rect_id), fill="white", font=("Arial", 12, "bold")
        )

    def draw_mbr(self):
        """Dibuja los MBRs actuales del R-Tree con colores diferenciados por niveles."""
        self.canvas.delete("all")
        for obj in self.index.intersection((0, 0, 800, 600), objects=True):
            rect = obj.bbox
            level = self.get_level(obj.id)
            color = self.colors[level % len(self.colors)]
            self.draw_rectangle(rect, obj.id, color)

    def clear_canvas(self):
        """Limpia el canvas y el R-Tree."""
        self.canvas.delete("all")
        self.index = index.Index()
        self.log_operation("Canvas y R-Tree limpiados.")

    def get_level(self, rect_id):
        """Calcula el nivel del rectángulo en el R-Tree."""
        return rect_id % len(self.colors)

    def insert_rect(self):
        """Inserta un rectángulo en el R-Tree."""
        coords = self.insert_entry.get()
        try:
            x1, y1, x2, y2 = map(int, coords.split(","))
            if x1 >= x2 or y1 >= y2:
                raise ValueError("Coordenadas inválidas.")
            rect_id = len(self.index)
            self.index.insert(rect_id, (x1, y1, x2, y2))
            self.draw_mbr()
            self.log_operation(f"Insertado rectángulo {coords} con ID {rect_id}.")
        except Exception as e:
            self.log_operation(f"Error al insertar: {e}", error=True)

    def delete_rect(self):
        """Elimina un rectángulo por su ID."""
        rect_id = self.delete_entry.get()
        try:
            rect_id = int(rect_id)
            for obj in self.index.intersection((0, 0, 800, 600), objects=True):
                if obj.id == rect_id:
                    self.index.delete(rect_id, obj.bbox)
                    self.draw_mbr()
                    self.log_operation(f"Eliminado rectángulo con ID {rect_id}.")
                    return
            self.log_operation("ID no encontrado.", error=True)
        except Exception as e:
            self.log_operation(f"Error al eliminar: {e}", error=True)

    def search_rect(self):
        """Busca rectángulos que intersecten un área."""
        coords = self.search_entry.get()
        try:
            x1, y1, x2, y2 = map(int, coords.split(","))
            results = [obj.id for obj in self.index.intersection((x1, y1, x2, y2), objects=True)]
            self.log_operation(f"Área buscada: {coords}. IDs encontrados: {results}")
        except Exception as e:
            self.log_operation(f"Error al buscar: {e}", error=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = RTreeApp(root)
    root.mainloop()