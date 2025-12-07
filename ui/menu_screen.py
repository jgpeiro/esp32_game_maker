# menu_screen.py - Menú principal

import config
import lib.logging as logging
from ui.screen import Screen, Button
from ui.generator_screen import GeneratorScreen
from ui.games_screen import GamesScreen
    
logger = logging.getLogger("menu_screen")

class MenuScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        logger.debug("Initializing MenuScreen...")
        
        # Botones del menú
        self.buttons = [
            Button(150, 80, 180, 50, "CREAR JUEGO", config.COLOR_WHITE, config.COLOR_PRIMARY),
            Button(150, 140, 180, 50, "MIS JUEGOS", config.COLOR_PRIMARY, config.COLOR_BUTTON_BG),
            Button(150, 200, 180, 50, "AJUSTES", config.COLOR_TEXT_SECONDARY, config.COLOR_BUTTON_BG),
            Button(150, 260, 180, 50, "ACERCA DE", config.COLOR_TEXT_SECONDARY, config.COLOR_BUTTON_BG)
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
        
        # Header
        r.rect(0, 0, 480, 45, config.COLOR_BLACK, fill=True)
        
        # Icono play
        r.circle(30, 22, 12, config.COLOR_PRIMARY, fill=True)
        r.line(27, 17, 27, 27, config.COLOR_WHITE)
        r.line(27, 17, 33, 22, config.COLOR_WHITE)
        r.line(27, 27, 33, 22, config.COLOR_WHITE)
        
        r.text(50, 17, "MENU PRINCIPAL", config.COLOR_WHITE, scale=2)
        
        # Botones
        for btn in self.buttons:
            btn.draw(r)
        
        # Badge con contador de juegos
        if self.game_count > 0:
            badge_x, badge_y = 318, 165
            r.circle(badge_x, badge_y, 10, config.COLOR_ACCENT, fill=True)
            count_str = str(self.game_count)
            text_x = badge_x - len(count_str) * 4
            r.text(text_x, badge_y - 4, count_str, config.COLOR_WHITE)
        
        # Iconos en los botones
        # Icono + en CREAR JUEGO
        r.circle(168, 105, 10, config.COLOR_WHITE, fill=True)
        r.text(164, 101, "+", config.COLOR_PRIMARY, scale=1)
        
        # Icono carpeta en MIS JUEGOS
        r.rect(168, 158, 15, 18, config.COLOR_PRIMARY, fill=False)
        r.line(168, 165, 183, 165, config.COLOR_PRIMARY)
        
        # Icono engranaje en AJUSTES
        r.circle(175, 225, 8, config.COLOR_TEXT_SECONDARY, fill=False)
        
        # Icono info en ACERCA DE
        r.circle(175, 285, 8, config.COLOR_TEXT_SECONDARY, fill=False)
        r.text(172, 281, "i", config.COLOR_TEXT_SECONDARY)
        
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
            logger.info("Button 'AJUSTES' pressed (not implemented)")
            # TODO: Implementar pantalla de ajustes
            pass
        
        # Acerca de
        elif self.buttons[3].is_touched(x, y):
            logger.info("Button 'ACERCA DE' pressed (not implemented)")
            # TODO: Implementar pantalla acerca de
            pass
