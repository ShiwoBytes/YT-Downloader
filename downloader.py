import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import webbrowser
import time
from PIL import Image, ImageTk
import yt_dlp
import signal

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de YouTube")
        self.root.geometry("700x550")
        self.root.minsize(600, 500)
        self.root.configure(bg="#f0f0f0")
        
        # Configurar grid para responsive
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables para control de descarga
        self.downloading = False
        self.ydl_process = None
        self.download_thread = None
        
        # Crear interfaz
        self.create_widgets()
        self.create_footer()
        
    def create_widgets(self):
        # Marco principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Descargador de YouTube", 
                               font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Entrada de URL
        url_label = ttk.Label(main_frame, text="URL del video:")
        url_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botón de pegar URL
        paste_btn = ttk.Button(main_frame, text="Pegar URL", command=self.paste_url)
        paste_btn.grid(row=2, column=1, padx=(10, 0), pady=(0, 10))
        
        # Marco para formatos y calidades
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)
        
        # Selector de formato
        format_label = ttk.Label(options_frame, text="Formato:")
        format_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, 
                                   values=["mp4", "mp3"], 
                                   state="readonly", width=20)
        format_combo.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Selector de calidad
        quality_label = ttk.Label(options_frame, text="Calidad:")
        quality_label.grid(row=0, column=1, sticky=tk.W, pady=(0, 5))
        
        self.quality_var = tk.StringVar(value="mejor")
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality_var, 
                                    values=["mejor", "720p", "480p", "360p"], 
                                    state="readonly", width=20)
        quality_combo.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # Selector de carpeta destino
        folder_label = ttk.Label(main_frame, text="Carpeta destino:")
        folder_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        self.folder_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        folder_entry = ttk.Entry(main_frame, textvariable=self.folder_var)
        folder_entry.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        folder_btn = ttk.Button(main_frame, text="Examinar", command=self.select_folder)
        folder_btn.grid(row=5, column=1, padx=(10, 0), pady=(0, 10))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 10))
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        
        self.download_btn = ttk.Button(button_frame, text="Descargar", command=self.start_download)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancelar", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT)
        
        # Área de log
        log_label = ttk.Label(main_frame, text="Estado:")
        log_label.grid(row=8, column=0, sticky=tk.W, pady=(20, 5))
        
        # Marco para el área de texto con scrollbar
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        # Configurar expansión de columnas
        main_frame.columnconfigure(0, weight=1)
        
    def create_footer(self):
        # Footer con redes sociales
        footer_frame = ttk.Frame(self.root, style='Footer.TFrame')
        footer_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        footer_frame.columnconfigure(0, weight=1)
        footer_frame.columnconfigure(1, weight=1)
        
        # Configurar estilo para el footer
        self.style.configure('Footer.TFrame', background='#e1e1e1')
        
        # Copyright
        copyright_label = ttk.Label(footer_frame, text="© 2023 ShiwoBytes", 
                                   background='#e1e1e1', font=("Helvetica", 8))
        copyright_label.grid(row=0, column=0, sticky=tk.W)
        
        # Marco para redes sociales
        social_frame = ttk.Frame(footer_frame, style='Footer.TFrame')
        social_frame.grid(row=0, column=1, sticky=tk.E)
        
        # GitHub
        github_btn = ttk.Button(social_frame, text="GitHub", 
                               command=lambda: webbrowser.open("https://github.com/ShiwoBytes"),
                               style='Social.TButton')
        github_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Instagram
        instagram_btn = ttk.Button(social_frame, text="Instagram", 
                                  command=lambda: webbrowser.open("https://www.instagram.com/pamphilx/"),
                                  style='Social.TButton')
        instagram_btn.pack(side=tk.LEFT)
        
        # Configurar estilo para botones sociales
        self.style.configure('Social.TButton', font=("Helvetica", 8), padding=(5, 2))
        
    def paste_url(self):
        try:
            clipboard = self.root.clipboard_get()
            self.url_var.set(clipboard)
            self.log("URL pegada desde portapapeles")
        except:
            self.log("No se pudo pegar desde el portapapeles")
    
    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)
    
    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor, ingresa una URL válida de YouTube")
            return
        
        if not os.path.isdir(self.folder_var.get()):
            messagebox.showerror("Error", "La carpeta destino no existe")
            return
        
        # Deshabilitar controles durante la descarga
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.downloading = True
        
        # Iniciar barra de progreso
        self.progress.start(10)
        
        # Iniciar descarga en un hilo separado
        self.download_thread = threading.Thread(target=self.download_video, args=(url,))
        self.download_thread.daemon = True
        self.download_thread.start()
        
        # Iniciar monitor para verificar cancelación
        self.monitor_download()
    
    def monitor_download(self):
        """Monitoriza el estado de la descarga y actualiza la interfaz"""
        if self.downloading and self.download_thread.is_alive():
            # Revisar cada 100ms si la descarga sigue activa
            self.root.after(100, self.monitor_download)
        elif not self.downloading:
            # La descarga fue cancelada
            self.download_finished()
    
    def download_video(self, url):
        try:
            format_type = self.format_var.get()
            quality = self.quality_var.get()
            
            # Configurar opciones de yt-dlp con interruptor de cancelación
            ydl_opts = {
                'outtmpl': os.path.join(self.folder_var.get(), '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'noprogress': False,
            }
            
            # Configurar formato según selección
            if format_type == 'mp3':
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                if quality == 'mejor':
                    ydl_opts['format'] = 'best'
                elif quality == '720p':
                    ydl_opts['format'] = 'best[height<=720]'
                elif quality == '480p':
                    ydl_opts['format'] = 'best[height<=480]'
                elif quality == '360p':
                    ydl_opts['format'] = 'best[height<=360]'
            
            self.log("Iniciando descarga...")
            self.log(f"URL: {url}")
            self.log(f"Formato: {format_type}, Calidad: {quality}")
            
            # Crear instancia de yt-dlp con manejo de cancelación
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Guardar referencia para posible cancelación
                self.ydl_process = ydl
                
                # Verificar periódicamente si se solicitó cancelación
                def should_continue():
                    return self.downloading
                
                # Sobrescribir el método de verificación de continuación
                ydl._should_continue = should_continue
                
                # Realizar la descarga
                ydl.download([url])
            
            if self.downloading:  # Solo si no fue cancelada
                self.log("Descarga completada exitosamente")
                self.root.after(0, lambda: messagebox.showinfo("Éxito", "Descarga completada exitosamente"))
            
        except Exception as e:
            if self.downloading:  # Solo mostrar error si no fue cancelación intencional
                self.log(f"Error durante la descarga: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error: {str(e)}"))
        
        finally:
            # Limpiar referencia
            self.ydl_process = None
            # Restaurar interfaz
            self.root.after(0, self.download_finished)
    
    def progress_hook(self, d):
        if not self.downloading:
            # Lanzar excepción para detener la descarga si fue cancelada
            raise yt_dlp.DownloadError("Descarga cancelada por el usuario")
            
        if d['status'] == 'downloading':
            if '_percent_str' in d:
                percent = d['_percent_str']
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                self.log(f"Progreso: {percent} | Velocidad: {speed} | Tiempo restante: {eta}")
        elif d['status'] == 'finished':
            self.log("Procesamiento finalizado, convirtiendo si es necesario...")
    
    def cancel_download(self):
        """Cancelar la descarga actual"""
        if self.downloading:
            self.downloading = False
            self.log("Cancelando descarga...")
            
            # Intentar detener el proceso de yt-dlp
            if self.ydl_process:
                try:
                    # Forzar la interrupción del proceso
                    self.ydl_process._download_retcode = -1
                    self.ydl_process._screen_file = None
                except:
                    pass
            
            # Actualizar interfaz inmediatamente
            self.download_finished()
            self.log("Descarga cancelada exitosamente")
    
    def download_finished(self):
        """Restaurar la interfaz después de la descarga"""
        self.progress.stop()
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.downloading = False
        self.ydl_process = None
    
    def log(self, message):
        def update_log():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        self.root.after(0, update_log)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()