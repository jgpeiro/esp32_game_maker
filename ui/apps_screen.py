# apps_screen.py - Explorador de aplicaciones guardadas

import config
import lib.logging as logging
from ui.screen import Screen, Button
from core.app_runner import AppRunner

logger = logging.getLogger("apps_screen")

class AppsScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        logger.debug("Initializing AppsScreen...")
        self.apps = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible = 5
        
        # Botones de acción
        self.run_btn = Button(20, 420, 80, 35, "ABRIR", config.COLOR_WHITE, config.COLOR_SUCCESS)
        self.delete_btn = Button(120, 420, 80, 35, "Borrar", config.COLOR_ACCENT, config.COLOR_BUTTON_BG)
        self.back_btn = Button(220, 420, 80, 35, "Atras", config.COLOR_WHITE, config.COLOR_BUTTON_BG)
        logger.debug("AppsScreen initialized")
    
    def enter(self):
        logger.info("Entering AppsScreen")
        self._load_apps()
    
    def _load_apps(self):
        """Carga la lista de apps"""
        logger.debug("Loading apps list...")
        self.apps = self.app.storage.list_apps()
        logger.info(f"Loaded {len(self.apps)} apps")
        if not self.apps:
            self.selected_index = -1
            logger.debug("No apps found, selected_index set to -1")
        else:
            self.selected_index = 0
            for i, app_item in enumerate(self.apps):
                logger.debug(f"  App {i}: {app_item['name']} (used: {app_item['used']}x)")
    
    def draw(self):
        r = self.renderer
        
        # Fondo
        r.fill(config.COLOR_BACKGROUND)
        
        # Header
        r.rect(0, 0, 320, 50, config.COLOR_BLACK, fill=True)
        
        # Icono app
        r.rect(15, 18, 18, 22, config.COLOR_SECONDARY, fill=False)
        r.circle(24, 29, 5, config.COLOR_SECONDARY, fill=True)
        
        r.text(40, 15, "MIS APPS", config.COLOR_WHITE, scale=2)
        
        # Contador
        count_text = f"{len(self.apps)} apps"
        r.text_right(310, 35, count_text, config.COLOR_SECONDARY)
        
        if not self.apps:
            # Sin apps
            r.text_centered(180, "No hay apps", config.COLOR_TEXT_SECONDARY, scale=2)
            r.text_centered(210, "Crea tu primera app!", config.COLOR_TEXT_SECONDARY, scale=1)
            
            # Solo botón atrás
            self.back_btn.draw(r)
        else:
            # Lista de apps
            y_start = 60
            item_height = 60
            
            for i in range(self.max_visible):
                app_index = i + self.scroll_offset
                if app_index >= len(self.apps):
                    break
                
                app_item = self.apps[app_index]
                y = y_start + i * item_height
                
                # Fondo del item
                if app_index == self.selected_index:
                    r.rounded_rect(15, y, 290, 52, 6, config.COLOR_BUTTON_BG, fill=True)
                    r.rounded_rect(15, y, 290, 52, 6, config.COLOR_PRIMARY, fill=False)
                    text_color = config.COLOR_WHITE
                else:
                    r.rounded_rect(15, y, 290, 52, 6, config.COLOR_BLACK, fill=True)
                    r.rounded_rect(15, y, 290, 52, 6, 0x4A69, fill=False)
                    text_color = config.COLOR_TEXT_SECONDARY
                
                # Icono app
                cx, cy = 35, y + 26
                if app_index == self.selected_index:
                    r.circle(cx, cy, 12, config.COLOR_PRIMARY, fill=True)
                    icon_color = config.COLOR_WHITE
                else:
                    r.circle(cx, cy, 12, config.COLOR_BUTTON_BG, fill=True)
                    icon_color = config.COLOR_TEXT_SECONDARY
                
                # Cuadrado con punto (icono de app)
                r.rect(cx - 6, cy - 6, 12, 12, icon_color, fill=False)
                r.circle(cx, cy, 3, icon_color, fill=True)
                
                # Nombre de la app
                name = app_item["name"][:25]
                r.text(55, y + 10, name, text_color, scale=1)
                
                # Fecha
                date_text = self._format_date(app_item["created"])
                r.text(55, y + 30, date_text, 0x8410, scale=1)
                
                # Flecha
                if app_index == self.selected_index:
                    r.circle(285, y + 26, 10, config.COLOR_SECONDARY, fill=True)
                    r.text(282, y + 22, ">", config.COLOR_WHITE)
            
            # Indicadores de scroll
            if self.scroll_offset > 0:
                r.text_centered(55, "^", config.COLOR_PRIMARY)
            if self.scroll_offset + self.max_visible < len(self.apps):
                r.text_centered(375, "v", config.COLOR_PRIMARY)
            
            # Botones de acción
            self.run_btn.draw(r)
            self.delete_btn.draw(r)
            self.back_btn.draw(r)
        
        r.flush()
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce():
            return
        
        logger.debug(f"AppsScreen touch at ({x}, {y})")
        
        if not self.apps:
            # Solo botón atrás disponible
            if self.back_btn.is_touched(x, y):
                logger.info("Returning to MenuScreen (no apps available)")
                from ui.menu_screen import MenuScreen
                self.app.change_screen(MenuScreen(self.app))
            return
        
        # Selección de apps
        if 15 <= x <= 305 and 60 <= y <= 360:
            item_index = (y - 60) // 60
            app_index = item_index + self.scroll_offset
            if app_index < len(self.apps):
                self.selected_index = int(app_index)
                logger.debug(f"App selected: index={self.selected_index}, name='{self.apps[self.selected_index]['name']}'")
            return
        
        # Botón abrir
        if self.run_btn.is_touched(x, y):
            if 0 <= self.selected_index < len(self.apps):
                app_item = self.apps[self.selected_index]
                logger.info(f"Running app: '{app_item['name']}' (filename: {app_item['filename']})")
                self.app.change_screen(AppRunner(self.app, app_item["filename"]))
            return
        
        # Botón borrar
        if self.delete_btn.is_touched(x, y):
            if 0 <= self.selected_index < len(self.apps):
                app_item = self.apps[self.selected_index]
                logger.warning(f"Deleting app: '{app_item['name']}' (filename: {app_item['filename']})")
                self.app.storage.delete_app(app_item["filename"])
                self._load_apps()
            return
        
        # Botón atrás
        if self.back_btn.is_touched(x, y):
            logger.info("Returning to MenuScreen")
            from ui.menu_screen import MenuScreen
            self.app.change_screen(MenuScreen(self.app))
            return
    
    def _format_date(self, timestamp):
        """Formatea timestamp a string legible"""
        import time
        t = time.localtime(int(timestamp))
        return f"{t[2]:02d}/{t[1]:02d}/{t[0]} {t[3]:02d}:{t[4]:02d}"
