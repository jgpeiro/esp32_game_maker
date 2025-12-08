# about_screen.py - Pantalla "Acerca de"

import config
import lib.logging as logging
from ui.screen import Screen, Button

logger = logging.getLogger("about_screen")

class AboutScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        logger.debug("Initializing AboutScreen...")
        
        self.back_btn = Button(120, 420, 80, 35, "Atras", config.COLOR_WHITE, config.COLOR_BUTTON_BG)
        
        # Info de la aplicación
        self.app_name = "Game Maker Console"
        self.app_version = "1.0.0"
        self.app_year = "2025"
        
        logger.debug("AboutScreen initialized")
    
    def enter(self):
        logger.info("Entering AboutScreen")
    
    def draw(self):
        r = self.renderer
        
        # Fondo
        r.fill(config.COLOR_BACKGROUND)
        
        # Header
        r.rect(0, 0, 320, 50, config.COLOR_BLACK, fill=True)
        
        # Icono info
        r.circle(25, 25, 12, config.COLOR_SECONDARY, fill=False)
        r.text(21, 18, "i", config.COLOR_SECONDARY, scale=2)
        
        r.text(45, 10, "ACERCA DE", config.COLOR_WHITE, scale=2)
        
        # Logo / Icono grande
        cx, cy = 160, 110
        r.circle(cx, cy, 35, config.COLOR_PRIMARY, fill=True)
        r.circle(cx, cy, 35, config.COLOR_SECONDARY, fill=False)
        
        # Triángulo play en el logo
        r.line(cx - 12, cy - 18, cx - 12, cy + 18, config.COLOR_WHITE)
        r.line(cx - 12, cy - 18, cx + 15, cy, config.COLOR_WHITE)
        r.line(cx - 12, cy + 18, cx + 15, cy, config.COLOR_WHITE)
        
        # Nombre de la app
        r.text_centered(165, self.app_name, config.COLOR_WHITE, scale=2)
        
        # Versión
        version_text = f"Version {self.app_version}"
        r.text_centered(195, version_text, config.COLOR_SECONDARY, scale=1)
        
        # Línea separadora
        r.line(40, 220, 280, 220, config.COLOR_BUTTON_BG)
        
        # Descripción
        desc_lines = [
            "Crea juegos con IA",
            "usando Claude de Anthropic",
            "",
            "Plataforma: ESP32",
            "Display: ST7796S 320x480",
            "Touch: FT6x36"
        ]
        
        y = 235
        for line in desc_lines:
            if line:
                r.text_centered(y, line, config.COLOR_TEXT_SECONDARY, scale=1)
            y += 18
        
        # Línea separadora
        r.line(40, 345, 280, 345, config.COLOR_BUTTON_BG)
        
        # Créditos
        r.text_centered(365, "Desarrollado con", config.COLOR_TEXT_SECONDARY, scale=1)
        
        # Corazón
        heart_x = 160
        heart_y = 390
        r.circle(heart_x - 5, heart_y - 2, 5, config.COLOR_ACCENT, fill=True)
        r.circle(heart_x + 5, heart_y - 2, 5, config.COLOR_ACCENT, fill=True)
        r.line(heart_x - 10, heart_y, heart_x, heart_y + 10, config.COLOR_ACCENT)
        r.line(heart_x + 10, heart_y, heart_x, heart_y + 10, config.COLOR_ACCENT)
        
        # Año
        r.text_centered(405, f"(c) {self.app_year}", config.COLOR_TEXT_SECONDARY, scale=1)
        
        # Botón atrás
        self.back_btn.draw(r)
        
        r.flush()
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce():
            return
        
        logger.debug(f"AboutScreen touch at ({x}, {y})")
        
        if self.back_btn.is_touched(x, y):
            logger.info("Returning to MenuScreen")
            from ui.menu_screen import MenuScreen
            self.app.change_screen(MenuScreen(self.app))
