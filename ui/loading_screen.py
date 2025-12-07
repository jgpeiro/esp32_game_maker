# loading_screen.py - Pantalla de carga mientras genera el juego

import time
import config
import lib.logging as logging
from ui.screen import Screen, Button

logger = logging.getLogger("loading_screen")

class LoadingScreen(Screen):
    def __init__(self, app, description):
        super().__init__(app)
        self.description = description
        self.progress = 0.0
        self.angle = 0
        self.game_code = None
        self.error = False
        self.generating = False
        
        self.cancel_btn = Button(180, 285, 120, 25, "Cancelar", config.COLOR_ACCENT, config.COLOR_BUTTON_BG)
        logger.debug(f"LoadingScreen initialized with description: '{description[:50]}...'")
    
    def enter(self):
        logger.info("Entering LoadingScreen")
        self.progress = 0.0
        self.generating = True
        self.error = False
        # Inicia generación en background
        self._start_generation()
    
    def _start_generation(self):
        """Inicia la generación del juego"""
        logger.info("Starting game generation...")
        logger.debug(f"Full description: '{self.description}'")
        try:
            # Genera el código
            logger.debug("Calling Claude API to generate game code...")
            self.game_code = self.app.api.generate_game(self.description)
            
            if self.game_code:
                logger.info(f"Game code generated successfully: {len(self.game_code)} bytes")
                logger.debug(f"First 200 chars: {self.game_code[:200]}...")
                
                # Extrae el nombre del juego
                game_name = self._extract_game_name()
                logger.debug(f"Extracted game name: '{game_name}'")
                
                # Guarda el juego
                logger.debug("Saving game to storage...")
                success = self.app.storage.save_game(game_name, self.game_code, self.description)
                
                if success:
                    logger.info(f"Game saved successfully as '{game_name}'")
                    # Ejecuta el juego
                    from game_runner import GameRunner
                    self.app.change_screen(GameRunner(self.app, game_name))
                else:
                    logger.error("Failed to save game to storage")
                    self.error = True
            else:
                logger.error("API returned empty game code")
                self.error = True
        except Exception as e:
            logger.error(f"Generation error: {e}")
            if config.DEBUG:
                import sys
                sys.print_exception(e)
            self.error = True
        finally:
            self.generating = False
            logger.debug(f"Generation complete. Error: {self.error}")
    
    def _extract_game_name(self):
        """Extrae un nombre del juego de la descripción"""
        # Usa las primeras palabras de la descripción
        words = self.description.split()
        if len(words) > 5:
            return " ".join(words[5:8])  # Salta "Quiero hacer un juego de"
        return "Mi Juego"
    
    def update(self):
        # Anima el spinner
        self.angle = (self.angle + 10) % 360
        
        # Simula progreso mientras genera
        if self.generating:
            self.progress = min(self.progress + 0.01, 0.95)
        else:
            self.progress = 1.0
    
    def draw(self):
        r = self.renderer
        
        # Fondo
        r.fill(config.COLOR_BACKGROUND)
        
        # Header
        r.rect(0, 0, 480, 40, config.COLOR_BLACK, fill=True)
        status = "Generando..." if self.generating else ("Error!" if self.error else "Listo!")
        r.text_centered(15, status, config.COLOR_SECONDARY if self.generating else 
                       (config.COLOR_ACCENT if self.error else config.COLOR_SUCCESS), scale=1)
        
        # Barra progreso completa
        r.progress_bar(90, 28, 300, 6, 1.0, config.COLOR_BUTTON_BG, config.COLOR_SUCCESS)
        
        # Cuadro con descripción
        r.rounded_rect(30, 60, 420, 80, 8, config.COLOR_BLACK, fill=True)
        r.rounded_rect(30, 60, 420, 80, 8, config.COLOR_SECONDARY, fill=False)
        
        r.text(40, 70, "Tu juego:", config.COLOR_SECONDARY, scale=1)
        
        # Divide descripción en líneas
        words = self.description.split()
        line1 = " ".join(words[:8])
        line2 = " ".join(words[8:16]) if len(words) > 8 else ""
        line3 = " ".join(words[16:24]) if len(words) > 16 else ""
        
        r.text(40, 90, line1, config.COLOR_WHITE, scale=1)
        if line2:
            r.text(40, 105, line2, config.COLOR_WHITE, scale=1)
        if line3:
            r.text(40, 120, line3, config.COLOR_WHITE, scale=1)
        
        if self.generating:
            # Spinner animado
            cx, cy = 240, 200
            
            # Círculo exterior
            r.circle(cx, cy, 35, config.COLOR_BUTTON_BG, fill=False)
            
            # Arcos animados (simulados con líneas)
            for i in range(0, 360, 30):
                angle = (i + self.angle) % 360
                if angle < 180:  # Solo dibuja mitad
                    x1 = cx + int(35 * self._cos(angle))
                    y1 = cy + int(35 * self._sin(angle))
                    x2 = cx + int(30 * self._cos(angle))
                    y2 = cy + int(30 * self._sin(angle))
                    r.line(x1, y1, x2, y2, config.COLOR_PRIMARY)
            
            # Círculo medio
            for i in range(0, 360, 40):
                angle = (i - self.angle) % 360
                if angle < 200:
                    x1 = cx + int(25 * self._cos(angle))
                    y1 = cy + int(25 * self._sin(angle))
                    x2 = cx + int(20 * self._cos(angle))
                    y2 = cy + int(20 * self._sin(angle))
                    r.line(x1, y1, x2, y2, config.COLOR_SECONDARY)
            
            # Texto
            r.text_centered(250, "Claude esta pensando...", config.COLOR_SECONDARY, scale=1)
            
            # Barra de progreso
            r.progress_bar(140, 270, 200, 8, self.progress, config.COLOR_BUTTON_BG, config.COLOR_PRIMARY)
            
            # Puntos animados
            dots = "." * ((self.angle // 60) % 4)
            r.text_centered(285, dots, config.COLOR_TEXT_SECONDARY, scale=2)
            
            # Botón cancelar
            self.cancel_btn.draw(r)
            
        elif self.error:
            # Mensaje de error
            r.text_centered(200, "Error al generar", config.COLOR_ACCENT, scale=2)
            r.text_centered(225, "Verifica tu conexion", config.COLOR_TEXT_SECONDARY, scale=1)
            
            # Botón volver
            btn = Button(170, 260, 140, 30, "Volver", config.COLOR_WHITE, config.COLOR_PRIMARY)
            btn.draw(r)
        
        r.flush()
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce():
            return
        
        logger.debug(f"LoadingScreen touch at ({x}, {y})")
        
        if self.generating and self.cancel_btn.is_touched(x, y):
            # Cancela y vuelve al generador
            logger.warning("Generation cancelled by user")
            from generator_screen import GeneratorScreen
            self.app.change_screen(GeneratorScreen(self.app))
        
        elif self.error:
            # Vuelve al generador
            logger.info("Returning to GeneratorScreen after error")
            from generator_screen import GeneratorScreen
            self.app.change_screen(GeneratorScreen(self.app))
    
    def _cos(self, degrees):
        import math
        return math.cos(math.radians(degrees))
    
    def _sin(self, degrees):
        import math
        return math.sin(math.radians(degrees))
