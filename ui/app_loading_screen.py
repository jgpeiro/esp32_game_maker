# app_loading_screen.py - Pantalla de carga mientras genera la aplicación

import time
import math
import config
import lib.logging as logging
from ui.screen import Screen, Button

logger = logging.getLogger("app_loading_screen")

class AppLoadingScreen(Screen):
    def __init__(self, app, description):
        super().__init__(app)
        self.description = description
        self.progress = 0.0
        self.angle = 0
        self.app_code = None
        self.error = False
        self.generating = False
        
        self.cancel_btn = Button(100, 420, 120, 25, "Cancelar", config.COLOR_ACCENT, config.COLOR_BUTTON_BG)
        logger.debug(f"AppLoadingScreen initialized with description: '{description[:50]}...'")
    
    def enter(self):
        logger.info("Entering AppLoadingScreen")
        self.progress = 0.0
        self.generating = True
        self.error = False
        # Inicia generación
        self._start_generation()
    
    def _start_generation(self):
        """Inicia la generación de la app"""
        logger.info("Starting app generation...")
        logger.debug(f"Full description: '{self.description}'")
        try:
            # Genera el código
            logger.debug("Calling Claude API to generate app code...")
            self.app_code = self.app.api.generate_app(self.description)
            
            if self.app_code:
                logger.info(f"App code generated successfully: {len(self.app_code)} bytes")
                logger.debug(f"First 200 chars: {self.app_code[:200]}...")
                
                # Extrae el nombre de la app
                app_name = self._extract_app_name()
                logger.debug(f"Extracted app name: '{app_name}'")
                
                # Guarda la app
                logger.debug("Saving app to storage...")
                success = self.app.storage.save_app(app_name, self.app_code, self.description)
                
                if success:
                    logger.info(f"App saved successfully as '{app_name}'")
                    # Ejecuta la app
                    from core.app_runner import AppRunner
                    self.app.change_screen(AppRunner(self.app, app_name))
                else:
                    logger.error("Failed to save app to storage")
                    self.error = True
            else:
                logger.error("API returned empty app code")
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
    
    def _extract_app_name(self):
        """Extrae un nombre de la app de la descripción"""
        # Usa las primeras palabras relevantes de la descripción
        words = self.description.split()
        # Salta "Una aplicacion que"
        if len(words) > 4:
            return " ".join(words[3:6])
        return "Mi App"
    
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
        r.rect(0, 0, 320, 40, config.COLOR_BLACK, fill=True)
        status = "Generando..." if self.generating else ("Error!" if self.error else "Listo!")
        r.text_centered(15, status, config.COLOR_SECONDARY if self.generating else 
                       (config.COLOR_ACCENT if self.error else config.COLOR_SUCCESS), scale=1)
        
        # Barra progreso completa
        r.progress_bar(40, 30, 240, 6, 1.0, config.COLOR_BUTTON_BG, config.COLOR_SUCCESS)
        
        # Cuadro con descripción
        r.rounded_rect(20, 60, 280, 100, 8, config.COLOR_BLACK, fill=True)
        r.rounded_rect(20, 60, 280, 100, 8, config.COLOR_SECONDARY, fill=False)
        
        r.text(30, 70, "Tu aplicacion:", config.COLOR_SECONDARY, scale=1)
        
        # Divide descripción en líneas
        words = self.description.split()
        line1 = " ".join(words[:6])
        line2 = " ".join(words[6:12]) if len(words) > 6 else ""
        line3 = " ".join(words[12:18]) if len(words) > 12 else ""
        line4 = " ".join(words[18:24]) if len(words) > 18 else ""
        
        r.text(30, 90, line1, config.COLOR_WHITE, scale=1)
        if line2:
            r.text(30, 105, line2, config.COLOR_WHITE, scale=1)
        if line3:
            r.text(30, 120, line3, config.COLOR_WHITE, scale=1)
        if line4:
            r.text(30, 135, line4, config.COLOR_WHITE, scale=1)
        
        if self.generating:
            # Spinner animado
            cx, cy = 160, 250
            
            # Círculo exterior
            r.circle(cx, cy, 35, config.COLOR_BUTTON_BG, fill=False)
            
            # Arcos animados
            for i in range(0, 360, 30):
                angle = (i + self.angle) % 360
                if angle < 180:
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
            r.text_centered(320, "Claude esta pensando...", config.COLOR_SECONDARY, scale=1)
            
            # Barra de progreso
            r.progress_bar(60, 350, 200, 8, self.progress, config.COLOR_BUTTON_BG, config.COLOR_PRIMARY)
            
            # Puntos animados
            dots = "." * ((self.angle // 60) % 4)
            r.text_centered(380, dots, config.COLOR_TEXT_SECONDARY, scale=2)
            
            # Botón cancelar
            self.cancel_btn.draw(r)
            
        elif self.error:
            # Mensaje de error
            r.text_centered(250, "Error al generar", config.COLOR_ACCENT, scale=2)
            r.text_centered(280, "Verifica tu conexion", config.COLOR_TEXT_SECONDARY, scale=1)
            
            # Botón volver
            btn = Button(90, 350, 140, 30, "Volver", config.COLOR_WHITE, config.COLOR_PRIMARY)
            btn.draw(r)
        
        r.flush()
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce():
            return
        
        logger.debug(f"AppLoadingScreen touch at ({x}, {y})")
        
        if self.generating and self.cancel_btn.is_touched(x, y):
            # Cancela y vuelve al generador
            logger.warning("Generation cancelled by user")
            from ui.app_generator_screen import AppGeneratorScreen
            self.app.change_screen(AppGeneratorScreen(self.app))
        
        elif self.error:
            # Vuelve al generador
            logger.info("Returning to AppGeneratorScreen after error")
            from ui.app_generator_screen import AppGeneratorScreen
            self.app.change_screen(AppGeneratorScreen(self.app))
    
    def _cos(self, degrees):
        return math.cos(math.radians(degrees))
    
    def _sin(self, degrees):
        return math.sin(math.radians(degrees))
