# menu_screen.py - Menú principal

import config
import lib.logging as logging
from ui.screen import Screen, Button
from ui.generator_screen import GeneratorScreen
from ui.games_screen import GamesScreen
from ui.app_generator_screen import AppGeneratorScreen
from ui.apps_screen import AppsScreen
from ui.settings_screen import SettingsScreen
from ui.about_screen import AboutScreen
    
logger = logging.getLogger("menu_screen")

class MenuScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        logger.debug("Initializing MenuScreen...")
        
        # Botones del menú (6 botones para pantalla 320x480)
        self.buttons = [
            Button(70, 80, 180, 45, "CREAR JUEGO", config.COLOR_WHITE, config.COLOR_PRIMARY),
            Button(70, 130, 180, 45, "MIS JUEGOS", config.COLOR_PRIMARY, config.COLOR_BUTTON_BG),
            Button(70, 185, 180, 45, "CREAR APP", config.COLOR_WHITE, config.COLOR_SUCCESS),
            Button(70, 235, 180, 45, "MIS APPS", config.COLOR_SUCCESS, config.COLOR_BUTTON_BG),
            Button(70, 290, 180, 45, "AJUSTES", config.COLOR_TEXT_SECONDARY, config.COLOR_BUTTON_BG),
            Button(70, 340, 180, 45, "ACERCA DE", config.COLOR_TEXT_SECONDARY, config.COLOR_BUTTON_BG)
        ]
        
        self.game_count = 0
        self.app_count = 0
        logger.debug("MenuScreen initialized with 6 buttons")
    
    def enter(self):
        logger.info("Entering MenuScreen")
        # Cuenta juegos y apps disponibles
        self.game_count = len(self.app.storage.list_games())
        self.app_count = len(self.app.storage.list_apps())
        logger.debug(f"Found {self.game_count} saved games and {self.app_count} saved apps")
    
    def draw(self):
        r = self.renderer
        
        # Fondo
        r.fill(config.COLOR_BACKGROUND)
        
        # Header (ajustado para 320 de ancho)
        r.rect(0, 0, 320, 45, config.COLOR_BLACK, fill=True)
        
        # Icono play
        r.circle(25, 22, 12, config.COLOR_PRIMARY, fill=True)
        r.line(22, 17, 22, 27, config.COLOR_WHITE)
        r.line(22, 17, 28, 22, config.COLOR_WHITE)
        r.line(22, 27, 28, 22, config.COLOR_WHITE)
        
        r.text(45, 14, "MENU", config.COLOR_WHITE, scale=2)
        r.text(45, 32, "PRINCIPAL", config.COLOR_TEXT_SECONDARY, scale=1)
        
        # Botones
        for btn in self.buttons:
            btn.draw(r)
        
        # Badge con contador de juegos
        if self.game_count > 0:
            badge_x, badge_y = 238, 155
            r.circle(badge_x, badge_y, 10, config.COLOR_ACCENT, fill=True)
            count_str = str(self.game_count)
            text_x = badge_x - len(count_str) * 4
            r.text(text_x, badge_y - 4, count_str, config.COLOR_WHITE)
        
        # Badge con contador de apps
        if self.app_count > 0:
            badge_x, badge_y = 238, 260
            r.circle(badge_x, badge_y, 10, config.COLOR_ACCENT, fill=True)
            count_str = str(self.app_count)
            text_x = badge_x - len(count_str) * 4
            r.text(text_x, badge_y - 4, count_str, config.COLOR_WHITE)
        
        # Iconos en los botones
        # Icono + en CREAR JUEGO
        r.circle(88, 102, 10, config.COLOR_WHITE, fill=True)
        r.text(84, 98, "+", config.COLOR_PRIMARY, scale=1)
        
        # Icono carpeta en MIS JUEGOS
        r.rect(88, 145, 15, 18, config.COLOR_PRIMARY, fill=False)
        r.line(88, 152, 103, 152, config.COLOR_PRIMARY)
        
        # Icono + en CREAR APP
        r.circle(88, 207, 10, config.COLOR_WHITE, fill=True)
        r.text(84, 203, "+", config.COLOR_SUCCESS, scale=1)
        
        # Icono carpeta en MIS APPS
        r.rect(88, 250, 15, 18, config.COLOR_SUCCESS, fill=False)
        r.line(88, 257, 103, 257, config.COLOR_SUCCESS)
        
        # Icono engranaje en AJUSTES
        r.circle(95, 312, 8, config.COLOR_TEXT_SECONDARY, fill=False)
        
        # Icono info en ACERCA DE
        r.circle(95, 362, 8, config.COLOR_TEXT_SECONDARY, fill=False)
        r.text(92, 358, "i", config.COLOR_TEXT_SECONDARY)
        
        r.flush()
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce():
            return
        
        logger.debug(f"MenuScreen touch at ({x}, {y})")
        
        # Crear juego
        if self.buttons[0].is_touched(x, y):
            logger.info("Button 'CREAR JUEGO' pressed - navigating to GeneratorScreen")
            self.app.change_screen(GeneratorScreen(self.app))
        
        # Mis juegos
        elif self.buttons[1].is_touched(x, y):
            logger.info("Button 'MIS JUEGOS' pressed - navigating to GamesScreen")
            self.app.change_screen(GamesScreen(self.app))
        
        # Crear app
        elif self.buttons[2].is_touched(x, y):
            logger.info("Button 'CREAR APP' pressed - navigating to AppGeneratorScreen")
            self.app.change_screen(AppGeneratorScreen(self.app))
        
        # Mis apps
        elif self.buttons[3].is_touched(x, y):
            logger.info("Button 'MIS APPS' pressed - navigating to AppsScreen")
            self.app.change_screen(AppsScreen(self.app))
        
        # Ajustes
        elif self.buttons[4].is_touched(x, y):
            logger.info("Button 'AJUSTES' pressed - navigating to SettingsScreen")
            self.app.change_screen(SettingsScreen(self.app))
        
        # Acerca de
        elif self.buttons[5].is_touched(x, y):
            logger.info("Button 'ACERCA DE' pressed - navigating to AboutScreen")
            self.app.change_screen(AboutScreen(self.app))

