# modules/interfaz.py

## @file interfaz.py
#  @brief Módulo que define la interfaz gráfica del conversor de audio a texto con encriptación.
#  @details Este módulo contiene la clase AppGUI, responsable de la interfaz,
#           interacción con el usuario, carga de archivos, conversión a texto,
#           encriptación, desencriptación y almacenamiento de registros.
#  @author Eddy
#  @date 2025
#  @version 1.0

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import os
import logging
import base64  # Necesario para almacenar código máquina

from .encriptacion import EncriptadorFernet
from .audio_converter import AudioConverter
from .storage import StorageManager
from config import (
    FORMATOS_PERMITIDOS,
    TAMANO_MAX_MB,
    AUDIOS_DIR,
    MENSAJES,
    ANCHO_VENTANA,
    ALTO_VENTANA,
    COLOR_FONDO,
    COLOR_TEXTO,
    FUENTE_NORMAL,
    FUENTE_BOTON
)

logger = logging.getLogger(__name__)

## @class AppGUI
#  @brief Clase principal de la interfaz gráfica.
#  @details Crea la ventana, los componentes gráficos y gestiona
#           todas las acciones del usuario relacionadas con:
#           - Selección de audio  
#           - Conversión a texto  
#           - Encriptación y desencriptación  
#           - Visualización de RAW  
#           - Guardado de registros
class AppGUI:

    ## @brief Constructor de la interfaz.
    #  @param title Título de la ventana principal.
    def __init__(self, title="App"):
        # --- Ventana principal ---
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}")
        self.root.configure(bg=COLOR_FONDO)

        # --- Estilos visuales ---
        style = ttk.Style()
        style.theme_use("clam")

        PRIMARIO = "#2b3e50"
        SECUNDARIO = "#1c252c"
        BOTON = "#4c9aff"
        BOTON_HOVER = "#2f7de1"
        TEXTO = "#ffffff"

        self.root.configure(bg=SECUNDARIO)

        style.configure(
            "TButton",
            background=BOTON,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=8
        )

        style.map(
            "TButton",
            background=[("active", BOTON_HOVER)],
            foreground=[("active", "white")]
        )

        style.configure("TLabel", background=SECUNDARIO, foreground=TEXTO, font=("Segoe UI", 10))
        style.configure("TFrame", background=SECUNDARIO)

        # --- Instancias de lógica del negocio ---
        self.audio_converter = AudioConverter()
        self.encriptador = EncriptadorFernet()
        self.storage = StorageManager()

        # --- Estado de la interfaz ---
        self.ruta_audio = None
        self.texto_extraido = ""
        self.texto_encriptado = None
        self.bytes_audio = None

        # Construcción de elementos gráficos
        self._construir_ui()

    ## @brief Construye todos los elementos de la interfaz gráfica.
    #  @details Separa la UI en botones, panel de información,
    #           texto extraído, texto encriptado y código RAW.
    def _construir_ui(self):
        frm_top = ttk.Frame(self.root, padding=10)
        frm_top.pack(fill='x')

        # Botones principales
        btn_select = ttk.Button(frm_top, text="Seleccionar audio...", command=self.seleccionar_archivo)
        btn_select.grid(row=0, column=0, padx=5, pady=5)

        self.lbl_archivo = ttk.Label(frm_top, text="Ningún archivo seleccionado", font=FUENTE_NORMAL)
        self.lbl_archivo.grid(row=0, column=1, sticky='w', padx=5)

        btn_convert = ttk.Button(frm_top, text="Convertir a Texto", command=self._thread(self.convertir_a_texto))
        btn_convert.grid(row=1, column=0, padx=5, pady=5)

        btn_encrypt = ttk.Button(frm_top, text="Encriptar Texto", command=self._thread(self.encriptar_texto))
        btn_encrypt.grid(row=1, column=1, padx=5, pady=5)

        btn_decrypt = ttk.Button(frm_top, text="Desencriptar Texto", command=self._thread(self.desencriptar_texto))
        btn_decrypt.grid(row=1, column=2, padx=5, pady=5)

        btn_guardar = ttk.Button(frm_top, text="Guardar conversión", command=self._thread(self.guardar_registro))
        btn_guardar.grid(row=1, column=3, padx=5, pady=5)

        # --- Información del archivo ---
        lbl_info_audio = ttk.Label(self.root, text="Información del archivo:", font=FUENTE_NORMAL)
        lbl_info_audio.pack(anchor='w', padx=10, pady=(10, 0))

        self.txt_info_audio = ScrolledText(self.root, height=6, font=("Consolas", 10), wrap=tk.WORD)
        self.txt_info_audio.pack(fill='x', padx=10, pady=5)
        self.txt_info_audio.configure(bg="#0e141a", fg="#b0e0ff", insertbackground="white")

        # --- Texto extraído ---
        lbl_res = ttk.Label(self.root, text="Texto extraído:", font=FUENTE_NORMAL)
        lbl_res.pack(anchor='w', padx=10, pady=(10,0))

        self.txt_res = ScrolledText(self.root, height=10, font=FUENTE_NORMAL, wrap=tk.WORD)
        self.txt_res.pack(fill='both', expand=False, padx=10, pady=5)
        self.txt_res.configure(bg="#0e141a", fg="white", insertbackground="white")

        # --- Texto encriptado ---
        lbl_enc = ttk.Label(self.root, text="Texto encriptado (Fernet Base64):", font=FUENTE_NORMAL)
        lbl_enc.pack(anchor='w', padx=10, pady=(10,0))

        self.txt_hex = ScrolledText(self.root, height=4, font=("Consolas", 10), wrap=tk.WORD)
        self.txt_hex.pack(fill='x', padx=10, pady=5)
        self.txt_hex.configure(bg="#0e141a", fg="cyan", insertbackground="white")

        # --- Código RAW ---
        lbl_raw = ttk.Label(self.root, text="Código RAW (código máquina):", font=FUENTE_NORMAL)
        lbl_raw.pack(anchor='w', padx=10, pady=(10,0))

        self.txt_raw = ScrolledText(self.root, height=20, font=("Consolas", 10), wrap=tk.CHAR)
        self.txt_raw.pack(fill='both', expand=True, padx=10, pady=5)
        self.txt_raw.configure(bg="#0e141a", fg="#b0e0ff", insertbackground="white")

    ## @brief Ejecuta una función en un hilo separado.
    #  @param func Función a ejecutar.
    def _thread(self, func):
        def wrapper():
            t = threading.Thread(target=func, daemon=True)
            t.start()
        return wrapper

    ## @brief Permite seleccionar un archivo de audio desde el explorador.
    #  @details Extrae la información técnica, bytes del archivo y muestra el RAW.
    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=[("Audio files", "*.mp3 *.wav *.ogg *.flac *.m4a *.wma *.aac"), ("All files", "*.*")]
        )

        if ruta:
            self.ruta_audio = ruta
            self.lbl_archivo.config(text=os.path.basename(ruta))

            try:
                info = self.audio_converter.obtener_info_audio(ruta)
                self.bytes_audio = self.audio_converter.obtener_bytes_audio(ruta, max_bytes=None)

                # Resumen del archivo
                resumen = (
                    f"Nombre: {info.get('nombre_archivo')}\n"
                    f"Formato: {info.get('formato')}\n"
                    f"Tamaño (KB): {info.get('tamano_kb')}\n"
                    f"Duración (s): {info.get('duracion_segundos')}\n"
                    f"Canales: {info.get('canales')}\n"
                    f"Frecuencia: {info.get('frecuencia_muestreo')} Hz\n"
                    f"Bits por muestra: {info.get('bits_por_muestra')}\n"
                )

                self.txt_info_audio.delete('1.0', tk.END)
                self.txt_info_audio.insert(tk.END, resumen)

                # RAW → código máquina decodificado en Latin-1
                raw_text = self.bytes_audio.decode("latin-1", errors="replace")
                self.txt_raw.delete('1.0', tk.END)
                self.txt_raw.insert(tk.END, raw_text)

            except Exception as e:
                logger.exception("Error mostrando info de audio")
                messagebox.showerror("Error", f"No se pudo leer info del audio: {e}")

    ## @brief Convierte el archivo de audio a texto mediante Speech Recognition.
    def convertir_a_texto(self):
        if not self.ruta_audio:
            messagebox.showwarning("Atención", "Seleccione un archivo primero")
            return
        try:
            self._set_status(MENSAJES['cargando'])
            texto, duracion = self.audio_converter.extraer_texto_de_audio(self.ruta_audio)
            self.texto_extraido = texto

            self.txt_res.delete('1.0', tk.END)
            self.txt_res.insert(tk.END, texto)

            messagebox.showinfo("Éxito", MENSAJES['exito_conversion'])

        except Exception as e:
            logger.exception("Error al convertir a texto")
            messagebox.showerror("Error", str(e))

    ## @brief Encripta el texto extraído usando Fernet.
    def encriptar_texto(self):
        if not self.texto_extraido.strip():
            messagebox.showwarning("Atención", "No hay texto para encriptar.")
            return
        try:
            self.texto_encriptado = self.encriptador.encriptar_texto(self.texto_extraido)
            self.txt_hex.delete('1.0', tk.END)
            self.txt_hex.insert(tk.END, self.texto_encriptado.decode('utf-8'))
            messagebox.showinfo("Éxito", MENSAJES['exito_encriptacion'])
        except Exception as e:
            logger.exception("Error encriptando")
            messagebox.showerror("Error", str(e))

    ## @brief Desencripta el texto encriptado y lo muestra.
    def desencriptar_texto(self):
        if not self.texto_encriptado:
            messagebox.showwarning("Atención", "No hay texto encriptado.")
            return
        try:
            texto = self.encriptador.desencriptar_texto(self.texto_encriptado)
            self.txt_res.delete('1.0', tk.END)
            self.txt_res.insert(tk.END, texto)
            messagebox.showinfo("Éxito", MENSAJES['exito_desencriptacion'])
        except Exception as e:
            logger.exception("Error desencriptando")
            messagebox.showerror("Error", str(e))

    ## @brief Guarda la conversión en formato JSON dentro del sistema de almacenamiento.
    #  @details Incluye texto, encriptado, info del audio y código máquina en Base64.
    def guardar_registro(self):
        if not self.ruta_audio:
            messagebox.showwarning("Atención", "Seleccione un archivo primero")
            return
        try:
            info_audio = self.audio_converter.obtener_info_audio(self.ruta_audio)

            registro = {
                "archivo_origen": os.path.basename(self.ruta_audio),
                "ruta": self.ruta_audio,
                "texto": self.texto_extraido,
                "texto_encriptado": self.texto_encriptado,
                "codigo_maquina": base64.b64encode(self.bytes_audio).decode('utf-8') if self.bytes_audio else None,
                "duracion_segundos": info_audio.get("duracion_segundos"),
                "info_audio": info_audio
            }

            self.storage.agregar_conversion(registro)
            messagebox.showinfo("Guardado", MENSAJES['exito_guardado'])

        except Exception as e:
            logger.exception("Error guardando registro")
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    ## @brief Cambia el texto del título de la ventana.
    def _set_status(self, texto):
        self.root.title(f"{texto}")

    ## @brief Inicia el loop principal de Tkinter.
    def run(self):
        self.root.mainloop()