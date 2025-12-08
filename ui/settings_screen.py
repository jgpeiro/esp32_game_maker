# settings_screen.py - Pantalla de ajustes con WiFi y API Key

import config
import network
import lib.logging as logging
from ui.screen import Screen, Button
from core.settings import Settings

logger = logging.getLogger("settings_screen")

class SettingsScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        logger.debug("Initializing SettingsScreen...")
        self.settings = Settings()
        self.wlan = network.WLAN(network.STA_IF)
        
        # Estados
        self.mode = "menu"  # menu, wifi_list, keyboard
        self.keyboard_target = None  # "wifi_password" o "api_key"
        self.keyboard_text = ""
        self.networks = []
        self.selected_network = -1
        self.scanning = False
        self.scroll_offset = 0
        self.max_visible_networks = 5
        
        # Botones del menú principal
        self.wifi_toggle_btn = Button(20, 70, 280, 40, "", config.COLOR_WHITE, config.COLOR_BUTTON_BG)
        self.wifi_scan_btn = Button(20, 120, 280, 40, "Escanear redes", config.COLOR_SECONDARY, config.COLOR_BUTTON_BG)
        self.wifi_ssid_btn = Button(20, 170, 280, 40, "", config.COLOR_SECONDARY, config.COLOR_BUTTON_BG)
        self.wifi_pass_btn = Button(20, 220, 280, 40, "Cambiar password", config.COLOR_SECONDARY, config.COLOR_BUTTON_BG)
        self.api_key_btn = Button(20, 300, 280, 40, "Configurar API Key", config.COLOR_SECONDARY, config.COLOR_BUTTON_BG)
        self.back_btn = Button(20, 430, 80, 35, "Atras", config.COLOR_WHITE, config.COLOR_BUTTON_BG)
        self.save_btn = Button(220, 430, 80, 35, "Guardar", config.COLOR_WHITE, config.COLOR_SUCCESS)
        
        # Teclado QWERTY
        self.keyboard_rows = [
            "1234567890",
            "qwertyuiop",
            "asdfghjkl",
            "zxcvbnm_-."
        ]
        self.keyboard_caps = False
        self.keyboard_keys = []
        self._init_keyboard()
        
        logger.debug("SettingsScreen initialized")
    
    def _init_keyboard(self):
        """Inicializa las posiciones de las teclas"""
        self.keyboard_keys = []
        key_w = 28
        key_h = 35
        start_y = 280
        
        for row_idx, row in enumerate(self.keyboard_rows):
            row_x = (320 - len(row) * key_w) // 2
            for col_idx, char in enumerate(row):
                x = row_x + col_idx * key_w
                y = start_y + row_idx * (key_h + 5)
                self.keyboard_keys.append((x, y, key_w - 2, key_h, char))
        
        # Teclas especiales
        self.caps_btn = Button(10, start_y + 2 * (key_h + 5), 35, key_h, "CAP", config.COLOR_SECONDARY, config.COLOR_BUTTON_BG)
        self.backspace_btn = Button(275, start_y + 2 * (key_h + 5), 35, key_h, "<-", config.COLOR_ACCENT, config.COLOR_BUTTON_BG)
        self.space_btn = Button(60, start_y + 4 * (key_h + 5), 200, key_h, "ESPACIO", config.COLOR_SECONDARY, config.COLOR_BUTTON_BG)
        self.ok_btn = Button(230, 430, 70, 35, "OK", config.COLOR_WHITE, config.COLOR_SUCCESS)
        self.cancel_btn = Button(20, 430, 70, 35, "Cancelar", config.COLOR_ACCENT, config.COLOR_BUTTON_BG)
    
    def enter(self):
        logger.info("Entering SettingsScreen")
        self.mode = "menu"
        self._update_wifi_status()
    
    def _update_wifi_status(self):
        """Actualiza el estado del botón WiFi"""
        if self.settings.wifi_enabled:
            self.wifi_toggle_btn.text = "WiFi: ENCENDIDO"
            self.wifi_toggle_btn.bg_color = config.COLOR_SUCCESS
        else:
            self.wifi_toggle_btn.text = "WiFi: APAGADO"
            self.wifi_toggle_btn.bg_color = config.COLOR_BUTTON_BG
        
        ssid = self.settings.wifi_ssid
        if ssid:
            self.wifi_ssid_btn.text = f"Red: {ssid[:20]}"
        else:
            self.wifi_ssid_btn.text = "Red: (ninguna)"
    
    def _scan_networks(self):
        """Escanea redes WiFi disponibles"""
        logger.info("Scanning WiFi networks...")
        self.scanning = True
        self.networks = []
        
        try:
            was_active = self.wlan.active()
            if not was_active:
                self.wlan.active(True)
            
            scan_results = self.wlan.scan()
            for net in scan_results:
                ssid = net[0].decode('utf-8') if isinstance(net[0], bytes) else net[0]
                rssi = net[3] if len(net) > 3 else -100
                if ssid:  # Solo añadir redes con SSID
                    self.networks.append({"ssid": ssid, "rssi": rssi})
            
            # Ordenar por señal
            self.networks.sort(key=lambda x: x["rssi"], reverse=True)
            logger.info(f"Found {len(self.networks)} networks")
            
        except Exception as e:
            logger.error(f"Error scanning networks: {e}")
        
        self.scanning = False
    
    def draw(self):
        r = self.renderer
        r.fill(config.COLOR_BACKGROUND)
        
        # Header
        r.rect(0, 0, 320, 50, config.COLOR_BLACK, fill=True)
        
        # Icono engranaje
        r.circle(25, 25, 12, config.COLOR_SECONDARY, fill=False)
        r.circle(25, 25, 4, config.COLOR_SECONDARY, fill=True)
        
        r.text(45, 10, "AJUSTES", config.COLOR_WHITE, scale=2)
        
        if self.mode == "menu":
            self._draw_menu(r)
        elif self.mode == "wifi_list":
            self._draw_wifi_list(r)
        elif self.mode == "keyboard":
            self._draw_keyboard(r)
        
        r.flush()
    
    def _draw_menu(self, r):
        """Dibuja el menú principal de ajustes"""
        # Sección WiFi
        r.text(20, 55, "WiFi", config.COLOR_PRIMARY, scale=1)
        self.wifi_toggle_btn.draw(r)
        self.wifi_scan_btn.draw(r)
        self.wifi_ssid_btn.draw(r)
        self.wifi_pass_btn.draw(r)
        
        # Indicador de conexión
        if self.wlan.isconnected():
            ip = self.wlan.ifconfig()[0]
            r.text(20, 265, f"Conectado: {ip}", config.COLOR_SUCCESS, scale=1)
        elif self.settings.wifi_enabled:
            r.text(20, 265, "Desconectado", config.COLOR_ACCENT, scale=1)
        
        # Sección API
        r.text(20, 285, "Claude API", config.COLOR_PRIMARY, scale=1)
        
        # Mostrar estado del API key
        if self.settings.api_key:
            key_preview = self.settings.api_key[:10] + "..." if len(self.settings.api_key) > 10 else self.settings.api_key
            self.api_key_btn.text = f"API Key: {key_preview}"
        else:
            self.api_key_btn.text = "API Key: (no configurada)"
        self.api_key_btn.draw(r)
        
        self.back_btn.draw(r)
    
    def _draw_wifi_list(self, r):
        """Dibuja la lista de redes WiFi"""
        r.text(20, 55, "Selecciona una red:", config.COLOR_PRIMARY, scale=1)
        
        if self.scanning:
            r.text_centered(200, "Escaneando...", config.COLOR_SECONDARY, scale=2)
        elif not self.networks:
            r.text_centered(200, "No se encontraron redes", config.COLOR_TEXT_SECONDARY, scale=1)
        else:
            # Lista de redes
            y_start = 80
            item_height = 50
            
            for i in range(self.max_visible_networks):
                net_idx = i + self.scroll_offset
                if net_idx >= len(self.networks):
                    break
                
                net = self.networks[net_idx]
                y = y_start + i * item_height
                
                # Fondo del item
                if net_idx == self.selected_network:
                    r.rounded_rect(20, y, 280, 45, 6, config.COLOR_BUTTON_BG, fill=True)
                    r.rounded_rect(20, y, 280, 45, 6, config.COLOR_PRIMARY, fill=False)
                    text_color = config.COLOR_WHITE
                else:
                    r.rounded_rect(20, y, 280, 45, 6, config.COLOR_BLACK, fill=True)
                    text_color = config.COLOR_TEXT_SECONDARY
                
                # SSID
                ssid = net["ssid"][:25]
                r.text(30, y + 10, ssid, text_color, scale=1)
                
                # Señal
                rssi = net["rssi"]
                if rssi > -50:
                    signal = "Excelente"
                    sig_color = config.COLOR_SUCCESS
                elif rssi > -70:
                    signal = "Buena"
                    sig_color = config.COLOR_PRIMARY
                else:
                    signal = "Debil"
                    sig_color = config.COLOR_ACCENT
                r.text(30, y + 28, signal, sig_color, scale=1)
                
                # Icono de señal
                bars = 3 if rssi > -50 else (2 if rssi > -70 else 1)
                for b in range(bars):
                    r.rect(270 + b * 8, y + 30 - b * 5, 5, 5 + b * 5, sig_color, fill=True)
            
            # Indicadores de scroll
            if self.scroll_offset > 0:
                r.text_centered(70, "^", config.COLOR_PRIMARY)
            if self.scroll_offset + self.max_visible_networks < len(self.networks):
                r.text_centered(340, "v", config.COLOR_PRIMARY)
        
        self.cancel_btn.draw(r)
        if self.selected_network >= 0:
            self.ok_btn.draw(r)
    
    def _draw_keyboard(self, r):
        """Dibuja el teclado virtual"""
        # Campo de texto
        target_text = "Password WiFi" if self.keyboard_target == "wifi_password" else "API Key"
        r.text(20, 55, target_text, config.COLOR_PRIMARY, scale=1)
        
        # Cuadro de texto
        r.rounded_rect(20, 75, 280, 40, 6, config.COLOR_BUTTON_BG, fill=True)
        r.rounded_rect(20, 75, 280, 40, 6, config.COLOR_PRIMARY, fill=False)
        
        # Texto introducido (mostrar asteriscos para password)
        if self.keyboard_target == "wifi_password":
            display_text = "*" * len(self.keyboard_text) if self.keyboard_text else "(escribe aqui)"
        else:
            display_text = self.keyboard_text if self.keyboard_text else "(escribe aqui)"
        
        # Limitar texto mostrado
        if len(display_text) > 30:
            display_text = "..." + display_text[-27:]
        
        text_color = config.COLOR_WHITE if self.keyboard_text else config.COLOR_TEXT_SECONDARY
        r.text(30, 90, display_text, text_color, scale=1)
        
        # Cursor parpadeante
        import time
        if time.ticks_ms() % 1000 < 500:
            cursor_x = 30 + len(display_text) * 8
            if cursor_x < 290:
                r.line(cursor_x, 80, cursor_x, 110, config.COLOR_PRIMARY)
        
        # Longitud
        r.text(20, 120, f"Caracteres: {len(self.keyboard_text)}", config.COLOR_TEXT_SECONDARY, scale=1)
        
        # Teclas
        for x, y, w, h, char in self.keyboard_keys:
            display_char = char.upper() if self.keyboard_caps else char
            r.rounded_rect(x, y, w, h, 4, config.COLOR_BUTTON_BG, fill=True)
            r.rounded_rect(x, y, w, h, 4, config.COLOR_SECONDARY, fill=False)
            char_x = x + (w - 8) // 2
            char_y = y + (h - 8) // 2
            r.text(char_x, char_y, display_char, config.COLOR_WHITE, scale=1)
        
        # Teclas especiales
        self.caps_btn.bg_color = config.COLOR_PRIMARY if self.keyboard_caps else config.COLOR_BUTTON_BG
        self.caps_btn.draw(r)
        self.backspace_btn.draw(r)
        self.space_btn.draw(r)
        
        self.cancel_btn.draw(r)
        self.ok_btn.draw(r)
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce():
            return
        
        logger.debug(f"SettingsScreen touch at ({x}, {y}), mode={self.mode}")
        
        if self.mode == "menu":
            self._handle_menu_touch(x, y)
        elif self.mode == "wifi_list":
            self._handle_wifi_list_touch(x, y)
        elif self.mode == "keyboard":
            self._handle_keyboard_touch(x, y)
    
    def _handle_menu_touch(self, x, y):
        """Maneja toques en el menú principal"""
        # Toggle WiFi
        if self.wifi_toggle_btn.is_touched(x, y):
            self.settings.wifi_enabled = not self.settings.wifi_enabled
            logger.info(f"WiFi toggled: {self.settings.wifi_enabled}")
            
            if self.settings.wifi_enabled:
                self.wlan.active(True)
                # Intentar conectar si hay credenciales
                if self.settings.wifi_ssid and self.settings.wifi_password:
                    try:
                        self.wlan.connect(self.settings.wifi_ssid, self.settings.wifi_password)
                    except Exception as e:
                        logger.error(f"Error connecting: {e}")
            else:
                self.wlan.active(False)
            
            self._update_wifi_status()
            return
        
        # Escanear redes
        if self.wifi_scan_btn.is_touched(x, y):
            logger.info("Opening WiFi scanner")
            self._scan_networks()
            self.mode = "wifi_list"
            self.selected_network = -1
            self.scroll_offset = 0
            return
        
        # Cambiar password
        if self.wifi_pass_btn.is_touched(x, y):
            logger.info("Opening password keyboard")
            self.mode = "keyboard"
            self.keyboard_target = "wifi_password"
            self.keyboard_text = self.settings.wifi_password
            return
        
        # API Key
        if self.api_key_btn.is_touched(x, y):
            logger.info("Opening API Key keyboard")
            self.mode = "keyboard"
            self.keyboard_target = "api_key"
            self.keyboard_text = self.settings.api_key
            return
        
        # Atrás
        if self.back_btn.is_touched(x, y):
            logger.info("Returning to MenuScreen")
            from ui.menu_screen import MenuScreen
            self.app.change_screen(MenuScreen(self.app))
            return
    
    def _handle_wifi_list_touch(self, x, y):
        """Maneja toques en la lista de WiFi"""
        # Cancelar
        if self.cancel_btn.is_touched(x, y):
            self.mode = "menu"
            return
        
        # OK - seleccionar red
        if self.selected_network >= 0 and self.ok_btn.is_touched(x, y):
            net = self.networks[self.selected_network]
            self.settings.wifi_ssid = net["ssid"]
            self.settings.save()
            logger.info(f"Selected network: {net['ssid']}")
            self._update_wifi_status()
            
            # Abrir teclado para password
            self.mode = "keyboard"
            self.keyboard_target = "wifi_password"
            self.keyboard_text = ""
            return
        
        # Selección de red
        if 20 <= x <= 300 and 80 <= y <= 330:
            item_height = 50
            item_index = (y - 80) // item_height
            net_index = item_index + self.scroll_offset
            
            if net_index < len(self.networks):
                self.selected_network = net_index
                logger.debug(f"Selected network index: {net_index}")
            return
        
        # Scroll arriba
        if y < 80 and self.scroll_offset > 0:
            self.scroll_offset -= 1
            return
        
        # Scroll abajo
        if y > 340 and self.scroll_offset + self.max_visible_networks < len(self.networks):
            self.scroll_offset += 1
            return
    
    def _handle_keyboard_touch(self, x, y):
        """Maneja toques en el teclado"""
        # Cancelar
        if self.cancel_btn.is_touched(x, y):
            self.mode = "menu"
            return
        
        # OK - guardar
        if self.ok_btn.is_touched(x, y):
            if self.keyboard_target == "wifi_password":
                self.settings.wifi_password = self.keyboard_text
                logger.info("WiFi password saved")
                
                # Intentar conectar si WiFi está habilitado
                if self.settings.wifi_enabled and self.settings.wifi_ssid:
                    try:
                        self.wlan.disconnect()
                        self.wlan.connect(self.settings.wifi_ssid, self.settings.wifi_password)
                    except Exception as e:
                        logger.error(f"Error connecting: {e}")
            else:
                self.settings.api_key = self.keyboard_text
                logger.info("API Key saved")
            
            self.settings.save()
            self._update_wifi_status()
            self.mode = "menu"
            return
        
        # Caps
        if self.caps_btn.is_touched(x, y):
            self.keyboard_caps = not self.keyboard_caps
            return
        
        # Backspace
        if self.backspace_btn.is_touched(x, y):
            if self.keyboard_text:
                self.keyboard_text = self.keyboard_text[:-1]
            return
        
        # Espacio
        if self.space_btn.is_touched(x, y):
            self.keyboard_text += " "
            return
        
        # Teclas normales
        for kx, ky, kw, kh, char in self.keyboard_keys:
            if kx <= x <= kx + kw and ky <= y <= ky + kh:
                if self.keyboard_caps:
                    self.keyboard_text += char.upper()
                else:
                    self.keyboard_text += char
                return
