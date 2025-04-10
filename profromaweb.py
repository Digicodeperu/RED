import tkinter as tk
from tkinter import ttk, messagebox
import requests
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime
import locale
import webbrowser

locale.setlocale(locale.LC_ALL, '')

# --- CONFIGURACIÓN GITHUB PRIVADO ---
GITHUB_USER = "digicodeperu"
REPO = "raw"
RAMA = "main"
TOKEN = "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"

COLUMNAS = ["FILTRO", "M-COD", "PRODUCTO", "DETALLES", "STOCK", "DISTRIB", "FOTO"]

class ProformaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proforma Digital - ServiComp")
        self.root.geometry("1200x720")
        self.root.configure(bg="white")
        self.dataframe = None
        self.crear_interfaz()

    def crear_interfaz(self):
        tk.Label(self.root, text="PROFORMA DIGITAL - ServiComp",
                 font=("Segoe UI", 20, "bold"), bg="white", fg="#1e3d59").pack(pady=10)

        frame_top = tk.Frame(self.root, bg="white")
        frame_top.pack(pady=5)

        tk.Label(frame_top, text="Código de Proforma:", font=("Segoe UI", 12), bg="white").pack(side=tk.LEFT, padx=5)
        self.codigo_var = tk.StringVar()
        tk.Entry(frame_top, textvariable=self.codigo_var, font=("Segoe UI", 12), width=10).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_top, text="Cargar", font=("Segoe UI", 12), bg="#005f73", fg="white",
                  command=self.cargar_proforma).pack(side=tk.LEFT, padx=10)

        tk.Button(frame_top, text="Guardar como PDF", font=("Segoe UI", 12),
                  command=self.guardar_pdf).pack(side=tk.LEFT, padx=10)

        tk.Button(frame_top, text="Salir", font=("Segoe UI", 12), command=self.root.quit).pack(side=tk.LEFT, padx=10)

        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 10))
        style.map("Treeview", foreground=[("selected", "#1a73e8")])

        self.tree = ttk.Treeview(self.root, columns=COLUMNAS, show="headings", height=20)
        for col in COLUMNAS:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=130)
        self.tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.tree.bind("<Button-1>", self.abrir_link_foto)

        self.total_label = tk.Label(self.root, text="", font=("Segoe UI", 12), bg="white", fg="#333")
        self.total_label.pack(pady=5)

        self.pie_label = tk.Label(self.root, text="", font=("Segoe UI", 10, "italic"), bg="white", fg="#666")
        self.pie_label.pack(pady=5)

    def cargar_proforma(self):
        codigo = ''.join(self.codigo_var.get().strip().split())
        if not codigo.isdigit() or len(codigo) != 4:
            messagebox.showerror("Error", "Por favor ingresa un código válido de 4 dígitos.")
            return

        archivo = f"{codigo}.xlsx"
        url_api = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{archivo}?ref={RAMA}"
        headers = {
            "Authorization": f"token {TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            r = requests.get(url_api, headers=headers)
            r.raise_for_status()

            content_b64 = r.json().get("content", "")
            if not content_b64:
                raise ValueError("Contenido vacío.")

            binario = base64.b64decode(content_b64)
            df = pd.read_excel(BytesIO(binario))
            self.dataframe = df
            self.actualizar_tabla(df)

        except requests.exceptions.HTTPError:
            messagebox.showerror("Aviso", "No se encontró la proforma solicitada.")
        except Exception:
            messagebox.showerror("Aviso", "No se pudo mostrar la proforma. Intenta nuevamente.")

    def actualizar_tabla(self, df):
        self.tree.delete(*self.tree.get_children())
        total = 0

        for _, row in df.iterrows():
            valores = [row.get(col, "") for col in COLUMNAS]
            link = valores[6]
            valores[6] = "🔗 Ver Foto"
            self.tree.insert("", "end", values=valores, tags=(link,))

            distrib = str(row.get("DISTRIB", "")).replace("S/.", "").replace(",", "").strip()
            try:
                total += int(distrib)
            except:
                pass

        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.total_label.config(text=f"Total general: S/. {total:,}  |  Ítems: {len(df)}")
        self.pie_label.config(text=f"Fecha de emisión: {fecha} - Gracias por su preferencia.")

    def abrir_link_foto(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)

        if not row_id or COLUMNAS[int(col_id[1:]) - 1] != "FOTO":
            return

        link = self.tree.item(row_id, "tags")[0]
        if link.startswith("http"):
            webbrowser.open(link)

    def guardar_pdf(self):
        messagebox.showinfo("PDF", "Esta función estará disponible pronto.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ProformaApp(root)
    root.mainloop()
