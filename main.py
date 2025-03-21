import sys
import time
import requests
import tkinter as tk
from tkinter import ttk
import threading
import pystray
from PIL import Image, ImageDraw, ImageFont

class CryptoTaskbarMonitor:
    def __init__(self):
        self.crypto = "bitcoin"
        self.price = "0.00"
        self.previous_price = "0.00"
        self.update_interval = 240  
        self.running = True
        self.icon = None
        self.last_update_time = None
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Crypto Taskbar Monitor")
        self.root.geometry("300x180")
        self.root.resizable(False, False)
        
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Selecciona la criptomoneda:").pack(pady=5)
        
        self.crypto_var = tk.StringVar(value=self.crypto)
        crypto_combo = ttk.Combobox(main_frame, textvariable=self.crypto_var)
        crypto_combo['values'] = ("bitcoin", "ethereum", 'bnb', 'solana', 'polkadot')
        crypto_combo.pack(pady=5, fill=tk.X)
        
        ttk.Label(main_frame, text="Intervalo de actualización (segundos):").pack(pady=5)
        
        self.interval_var = tk.IntVar(value=self.update_interval)
        interval_entry = ttk.Spinbox(main_frame, from_=10, to=600, increment=10, textvariable=self.interval_var)
        interval_entry.pack(pady=5, fill=tk.X)
        
        start_button = tk.Button(main_frame, text="Iniciar Monitoreo", command=self.start_monitoring)
        start_button.pack(pady=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def get_arrow_symbol(self):
        try:
            current = float(self.price.replace(',', ''))
            previous = float(self.previous_price.replace(',', ''))
            
            if current > previous:
                return "↑"  
            elif current < previous:
                return "↓" 
            else:
                return "="
        except:
            return "" 

    def fetch_price(self):
        try:
            url = f"https://apicrypto.ggomez.tech/api/price/{self.crypto}"
            response = requests.get(url)
            
            if response.status_code == 200:
                price = response.json()
                price = price['price'].strip()
                try:
                    price_float = float(price)
                    price = f"{price_float:,.2f}"
                except:
                    pass
                
                self.previous_price = self.price
                self.price = price
                print(f"{self.crypto} actualizado: {self.price}")
            else:
                print(f"Error al obtener datos: {response.status_code}")
        except Exception as e:
            print(f"Error al obtener el precio: {e}")
            self.price = "Error"
        
        self.last_update_time = time.time()
        
        if self.icon:
            self.icon.title = f"{self.crypto}: {self.price}"
            
    def update_price_loop(self):
        while self.running:
            self.fetch_price()
            
            interval = self.interval_var.get()
            for remaining in range(interval, 0, -1):
                if not self.running:
                    break
                time.sleep(1)
            
    def start_monitoring(self):
        self.crypto = self.crypto_var.get()
        self.update_interval = self.interval_var.get()
        
        self.root.withdraw()
        
        self.fetch_price()
        
        menu = pystray.Menu(
            pystray.MenuItem("Actualizar ahora", self.force_update),
            pystray.MenuItem("Salir", self.exit_app)
        )
        
        icon_image = self.create_simple_price_icon()
        
        self.icon = pystray.Icon("crypto_monitor", icon_image, f"{self.crypto}: {self.price}", menu)
        
        update_thread = threading.Thread(target=self.update_price_loop)
        update_thread.daemon = True
        update_thread.start()
        
        self.icon.run()

    def create_simple_price_icon(self):
        icon_size = 256 
        img = Image.new('RGBA', (icon_size, icon_size), color=(0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        price_text = self.price.replace('.', '').replace(',', '').replace("$", "")[:2]

        font_size = 200
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        text_bbox = d.textbbox((0, 0), price_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        position = ((icon_size - text_width) // 2, (icon_size - text_height) // 2)
        d.text(position, price_text, fill='white', font=font)

        return img

    def force_update(self):
        threading.Thread(target=self.fetch_price).start()
        
    def exit_app(self):
        self.running = False
        if self.icon:
            self.icon.stop()
        self.root.destroy()
        sys.exit()
        
    def on_close(self):
        self.root.withdraw()

if __name__ == "__main__":
    app = CryptoTaskbarMonitor()