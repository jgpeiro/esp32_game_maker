# game_runner.py - Ejecuta juegos generados

import config
import lib.logging as logging
from ui.screen import Screen, Button
import time
import sys

logger = logging.getLogger("game_runner")

class GameRunner(Screen):
    def __init__(self, app, game_filename):
        super().__init__(app)
        self.game_filename = game_filename
        self.game_instance = None
        self.paused = False
        self.error = None
        
        self.pause_btn = Button(420, 5, 50, 30, "||", config.COLOR_WHITE, config.COLOR_ACCENT)
        logger.debug(f"GameRunner initialized for: {game_filename}")
    
    def enter(self):
        """Carga y ejecuta el juego"""
        logger.info(f"Loading and executing game: {self.game_filename}")
        try:
            # Carga el código
            logger.debug("Loading game code from storage...")
            code = self.app.storage.load_game(self.game_filename)
            if not code:
                self.error = "No se pudo cargar el juego"
                logger.error(f"Failed to load game code: {self.game_filename}")
                return
            
            logger.debug(f"Game code loaded: {len(code)} bytes")
            
            # Incrementa contador
            self.app.storage.increment_played(self.game_filename)
            logger.debug("Play counter incremented")
            
            # Crea namespace para exec
            namespace = {
                'renderer': self.renderer,
                'touch': self.app.touch
            }
            
            # Ejecuta el código
            logger.debug("Executing game code...")
            exec(code, namespace)
            
            # Obtiene la clase Game
            if 'Game' not in namespace:
                self.error = "El juego no tiene clase Game"
                logger.error("Game code does not contain 'Game' class")
                return
            
            # Instancia el juego
            logger.debug("Instantiating Game class...")
            GameClass = namespace['Game']
            self.game_instance = GameClass(self.renderer, self.app.touch)
            logger.info(f"Game '{self.game_filename}' loaded and running successfully")
            
        except Exception as e:
            self.error = f"Error: {str(e)}"
            logger.error(f"Game execution error: {e}")
            if config.DEBUG:
                sys.print_exception(e)
    
    def update(self):
        if self.error or self.paused or not self.game_instance:
            return
        
        try:
            # Actualiza el juego
            self.game_instance.update()
        except Exception as e:
            self.error = f"Error en update: {str(e)}"
            logger.error(f"Game update error: {e}")
            if config.DEBUG:
                sys.print_exception(e)
    
    def draw(self):
        r = self.renderer
        
        if self.error:
            # Muestra error
            logger.debug("Drawing error screen")
            r.fill(config.COLOR_BACKGROUND)
            r.text_centered(140, "ERROR", config.COLOR_ACCENT, scale=3)
            r.text_centered(180, self.error[:50], config.COLOR_TEXT_SECONDARY, scale=1)
            
            btn = Button(170, 230, 140, 35, "Volver", config.COLOR_WHITE, config.COLOR_PRIMARY)
            btn.draw(r)
            r.flush()
            
        elif self.paused:
            # Overlay de pausa
            logger.debug("Drawing pause overlay")
            # Oscurece pantalla (dibuja rectángulos semi-transparentes simulados)
            for i in range(0, 320, 4):
                r.line(0, i, 480, i, 0x2945)
            
            r.text_centered(140, "PAUSA", config.COLOR_PRIMARY, scale=3)
            
            resume_btn = Button(120, 180, 110, 35, "Reanudar", config.COLOR_WHITE, config.COLOR_SUCCESS)
            exit_btn = Button(250, 180, 110, 35, "Salir", config.COLOR_WHITE, config.COLOR_ACCENT)
            
            resume_btn.draw(r)
            exit_btn.draw(r)
            r.flush()
            
        elif self.game_instance:
            try:
                # Dibuja el juego
                self.game_instance.draw()
                
                # Dibuja botón pausa encima
                self.pause_btn.draw(r)
                r.flush()
                
            except Exception as e:
                self.error = f"Error en draw: {str(e)}"
                logger.error(f"Game draw error: {e}")
                if config.DEBUG:
                    sys.print_exception(e)
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce():
            return
        
        logger.debug(f"GameRunner touch at ({x}, {y})")
        
        if self.error:
            # Volver al explorador
            logger.info("Returning to GamesScreen after error")
            from games_screen import GamesScreen
            self.app.change_screen(GamesScreen(self.app))
            return
        
        if self.paused:
            # Botones de pausa
            if 120 <= x <= 230 and 180 <= y <= 215:
                # Reanudar
                logger.info("Game resumed")
                self.paused = False
            elif 250 <= x <= 360 and 180 <= y <= 215:
                # Salir
                logger.info("Exiting game, returning to GamesScreen")
                from games_screen import GamesScreen
                self.app.change_screen(GamesScreen(self.app))
            return
        
        # Botón pausa
        if self.pause_btn.is_touched(x, y):
            logger.info("Game paused")
            self.paused = True
            return
        
        # Pasa el toque al juego
        if self.game_instance:
            try:
                self.game_instance.handle_touch(x, y)
            except Exception as e:
                logger.error(f"Game touch error: {e}")
