# menu_screen.py - Menú principal

import config
import lib.logging as logging
from ui.screen import Screen, Button
from ui.generator_screen import GeneratorScreen
from ui.games_screen import GamesScreen
from ui.settings_screen import SettingsScreen
from ui.about_screen import AboutScreen
    
logger = logging.getLogger("menu_screen")

class MenuScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        logger.debug("Initializing MenuScreen...")
        
        # Botones del menú (centrados para pantalla 320x480)
        self.buttons = [
            Button(70, 100, 180, 50, "CREAR JUEGO", config.COLOR_WHITE, config.COLOR_PRIMARY),
            Button(70, 160, 180, 50, "MIS JUEGOS", config.COLOR_PRIMARY, config.COLOR_BUTTON_BG),
            Button(70, 220, 180, 50, "AJUSTES", config.COLOR_TEXT_SECONDARY, config.COLOR_BUTTON_BG),
            Button(70, 280, 180, 50, "ACERCA DE", config.COLOR_TEXT_SECONDARY, config.COLOR_BUTTON_BG)
        ]
        
        self.game_count = 0
        logger.debug("MenuScreen initialized with 4 buttons")
    
    def enter(self):
        logger.info("Entering MenuScreen")
        # Cuenta juegos disponibles
        self.game_count = len(self.app.storage.list_games())
        logger.debug(f"Found {self.game_count} saved games")
    
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
        
        # Badge con contador de juegos (ajustado para nueva posición de botón)
        if self.game_count > 0:
            badge_x, badge_y = 238, 185
            r.circle(badge_x, badge_y, 10, config.COLOR_ACCENT, fill=True)
            count_str = str(self.game_count)
            text_x = badge_x - len(count_str) * 4
            r.text(text_x, badge_y - 4, count_str, config.COLOR_WHITE)
        
        # Iconos en los botones (posiciones ajustadas)
        # Icono + en CREAR JUEGO
        r.circle(88, 125, 10, config.COLOR_WHITE, fill=True)
        r.text(84, 121, "+", config.COLOR_PRIMARY, scale=1)
        
        # Icono carpeta en MIS JUEGOS
        r.rect(88, 178, 15, 18, config.COLOR_PRIMARY, fill=False)
        r.line(88, 185, 103, 185, config.COLOR_PRIMARY)
        
        # Icono engranaje en AJUSTES
        r.circle(95, 245, 8, config.COLOR_TEXT_SECONDARY, fill=False)
        
        # Icono info en ACERCA DE
        r.circle(95, 305, 8, config.COLOR_TEXT_SECONDARY, fill=False)
        r.text(92, 301, "i", config.COLOR_TEXT_SECONDARY)
        
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
        
        # Ajustes
        elif self.buttons[2].is_touched(x, y):
            logger.info("Button 'AJUSTES' pressed - navigating to SettingsScreen")
            self.app.change_screen(SettingsScreen(self.app))
        
        # Acerca de
        elif self.buttons[3].is_touched(x, y):
            logger.info("Button 'ACERCA DE' pressed - navigating to AboutScreen")
            self.app.change_screen(AboutScreen(self.app))

