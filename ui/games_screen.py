# games_screen.py - Explorador de juegos guardados

import config
import lib.logging as logging
from ui.screen import Screen, Button
# from ui.menu_screen import MenuScreen # Made local to prevent recursive imports
from core.game_runner import GameRunner

logger = logging.getLogger("games_screen")

class GamesScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        logger.debug("Initializing GamesScreen...")
        self.games = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible = 5  # Más items visibles en pantalla vertical
        
        # Botones de acción (ajustados para pantalla vertical 320x480)
        self.play_btn = Button(20, 420, 80, 35, "JUGAR", config.COLOR_WHITE, config.COLOR_SUCCESS)
        self.delete_btn = Button(120, 420, 80, 35, "Borrar", config.COLOR_ACCENT, config.COLOR_BUTTON_BG)
        self.back_btn = Button(220, 420, 80, 35, "Atras", config.COLOR_WHITE, config.COLOR_BUTTON_BG)
        logger.debug("GamesScreen initialized")
    
    def enter(self):
        logger.info("Entering GamesScreen")
        self._load_games()
    
    def _load_games(self):
        """Carga la lista de juegos"""
        logger.debug("Loading games list...")
        self.games = self.app.storage.list_games()
        logger.info(f"Loaded {len(self.games)} games")
        if not self.games:
            self.selected_index = -1
            logger.debug("No games found, selected_index set to -1")
        else:
            self.selected_index = 0
            for i, game in enumerate(self.games):
                logger.debug(f"  Game {i}: {game['name']} (played: {game['played']}x)")
    
    def draw(self):
        r = self.renderer
        
        # Fondo
        r.fill(config.COLOR_BACKGROUND)
        
        # Header (ajustado para 320 de ancho)
        r.rect(0, 0, 320, 50, config.COLOR_BLACK, fill=True)
        
        # Icono carpeta
        r.rect(15, 18, 18, 22, config.COLOR_SECONDARY, fill=False)
        r.line(15, 25, 33, 25, config.COLOR_SECONDARY)
        
        r.text(40, 15, "MIS JUEGOS", config.COLOR_WHITE, scale=2)
        
        # Contador
        count_text = f"{len(self.games)} juegos"
        r.text_right(310, 35, count_text, config.COLOR_SECONDARY)
        
        if not self.games:
            # Sin juegos
            r.text_centered(180, "No hay juegos", config.COLOR_TEXT_SECONDARY, scale=2)
            r.text_centered(210, "Crea tu primer juego!", config.COLOR_TEXT_SECONDARY, scale=1)
            
            # Solo botón atrás
            self.back_btn.draw(r)
        else:
            # Lista de juegos (ajustada para pantalla vertical)
            y_start = 60
            item_height = 60
            
            for i in range(self.max_visible):
                game_index = i + self.scroll_offset
                if game_index >= len(self.games):
                    break
                
                game = self.games[game_index]
                y = y_start + i * item_height
                
                # Fondo del item (ajustado para 320 de ancho)
                if game_index == self.selected_index:
                    r.rounded_rect(15, y, 290, 52, 6, config.COLOR_BUTTON_BG, fill=True)
                    r.rounded_rect(15, y, 290, 52, 6, config.COLOR_PRIMARY, fill=False)
                    text_color = config.COLOR_WHITE
                else:
                    r.rounded_rect(15, y, 290, 52, 6, config.COLOR_BLACK, fill=True)
                    r.rounded_rect(15, y, 290, 52, 6, 0x4A69, fill=False)
                    text_color = config.COLOR_TEXT_SECONDARY
                
                # Icono play
                cx, cy = 35, y + 26
                if game_index == self.selected_index:
                    r.circle(cx, cy, 12, config.COLOR_PRIMARY, fill=True)
                    icon_color = config.COLOR_WHITE
                else:
                    r.circle(cx, cy, 12, config.COLOR_BUTTON_BG, fill=True)
                    icon_color = config.COLOR_TEXT_SECONDARY
                
                # Triángulo play
                r.line(cx - 3, cy - 6, cx - 3, cy + 6, icon_color)
                r.line(cx - 3, cy - 6, cx + 5, cy, icon_color)
                r.line(cx - 3, cy + 6, cx + 5, cy, icon_color)
                
                # Nombre del juego (ajustado para ancho menor)
                name = game["name"][:25]  # Trunca si es muy largo
                r.text(55, y + 10, name, text_color, scale=1)
                
                # Fecha
                date_text = self._format_date(game["created"])
                r.text(55, y + 30, date_text, 0x8410, scale=1)
                
                # Botón play pequeño
                if game_index == self.selected_index:
                    r.circle(285, y + 26, 10, config.COLOR_SECONDARY, fill=True)
                    r.text(282, y + 22, ">", config.COLOR_WHITE)
            
            # Indicadores de scroll
            if self.scroll_offset > 0:
                r.text_centered(55, "^", config.COLOR_PRIMARY)
            if self.scroll_offset + self.max_visible < len(self.games):
                r.text_centered(375, "v", config.COLOR_PRIMARY)
            
            # Botones de acción
            self.play_btn.draw(r)
            self.delete_btn.draw(r)
            self.back_btn.draw(r)
        
        r.flush()
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce():
            return
        
        logger.debug(f"GamesScreen touch at ({x}, {y})")
        
        if not self.games:
            # Solo botón atrás disponible
            if self.back_btn.is_touched(x, y):
                logger.info("Returning to MenuScreen (no games available)")
                from ui.menu_screen import MenuScreen
                self.app.change_screen(MenuScreen(self.app))
            return
        
        # Selección de juegos (ajustado para pantalla vertical)
        if 15 <= x <= 305 and 60 <= y <= 360:
            item_index = (y - 60) // 60
            game_index = item_index + self.scroll_offset
            if game_index < len(self.games):
                self.selected_index = int(game_index)
                logger.debug(f"Game selected: index={self.selected_index}, name='{self.games[self.selected_index]['name']}'")
            return
        
        # Botón jugar
        if self.play_btn.is_touched(x, y):
            if 0 <= self.selected_index < len(self.games):
                game = self.games[self.selected_index]
                logger.info(f"Playing game: '{game['name']}' (filename: {game['filename']})")
                self.app.change_screen(GameRunner(self.app, game["filename"]))
            return
        
        # Botón borrar
        if self.delete_btn.is_touched(x, y):
            if 0 <= self.selected_index < len(self.games):
                game = self.games[self.selected_index]
                logger.warning(f"Deleting game: '{game['name']}' (filename: {game['filename']})")
                self.app.storage.delete_game(game["filename"])
                self._load_games()
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


