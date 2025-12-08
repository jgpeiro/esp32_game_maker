# app_runner.py - Ejecuta aplicaciones generadas

import config
import lib.logging as logging
from ui.screen import Screen, Button
import time
import sys

logger = logging.getLogger("app_runner")

class AppRunner(Screen):
    def __init__(self, app, app_filename):
        super().__init__(app)
        self.app_filename = app_filename
        self.app_instance = None
        self.paused = False
        self.error = None
        self.frame = 0
        
        # Botón pausa/menú ajustado para pantalla vertical (320x480)
        self.menu_btn = Button(260, 5, 50, 30, "X", config.COLOR_WHITE, config.COLOR_ACCENT)
        logger.debug(f"AppRunner initialized for: {app_filename}")
    
    def enter(self):
        """Carga y ejecuta la app"""
        logger.info(f"Loading and executing app: {self.app_filename}")
        try:
            # Carga el código
            logger.debug("Loading app code from storage...")
            code = self.app.storage.load_app(self.app_filename)
            if not code:
                self.error = "No se pudo cargar la app"
                logger.error(f"Failed to load app code: {self.app_filename}")
                return
            
            logger.debug(f"App code loaded: {len(code)} bytes")
            
            # Incrementa contador
            self.app.storage.increment_app_used(self.app_filename)
            logger.debug("Use counter incremented")
            
            # Crea namespace para exec
            namespace = {
                'renderer': self.renderer,
                'touch': self.app.touch
            }
            
            # Ejecuta el código
            logger.debug("Executing app code...")
            exec(code, namespace)
            
            # Guarda las funciones si existen
            self.update_func = namespace.get('update', None)
            self.draw_func = namespace.get('draw', None)
            self.on_touch_func = namespace.get('on_touch', None)
            
            # También intenta con la clase App si existe
            if 'App' in namespace:
                logger.debug("Found App class, instantiating...")
                AppClass = namespace['App']
                self.app_instance = AppClass()
            elif 'app' in namespace:
                logger.debug("Found app instance...")
                self.app_instance = namespace['app']
            
            logger.info(f"App '{self.app_filename}' loaded successfully")
            
        except Exception as e:
            self.error = f"Error: {str(e)}"
            logger.error(f"App execution error: {e}")
            if config.DEBUG:
                sys.print_exception(e)
    
    def update(self):
        if self.error or self.paused:
            return
        
        self.frame += 1
        
        try:
            # Actualiza la app
            if self.app_instance and hasattr(self.app_instance, 'update'):
                self.app_instance.update(self.frame)
            elif self.update_func:
                self.update_func(self.frame)
        except Exception as e:
            self.error = f"Error en update: {str(e)}"
            logger.error(f"App update error: {e}")
            if config.DEBUG:
                sys.print_exception(e)
    
    def draw(self):
        r = self.renderer
        
        if self.error:
            # Muestra error
            logger.debug("Drawing error screen")
            r.fill(config.COLOR_BACKGROUND)
            r.text_centered(200, "ERROR", config.COLOR_ACCENT, scale=3)
            r.text_centered(250, self.error[:40], config.COLOR_TEXT_SECONDARY, scale=1)
            
            btn = Button(90, 320, 140, 35, "Volver", config.COLOR_WHITE, config.COLOR_PRIMARY)
            btn.draw(r)
            r.flush()
            
        elif self.paused:
            # Overlay de pausa
            logger.debug("Drawing pause overlay")
            for i in range(0, 480, 4):
                r.line(0, i, 320, i, 0x2945)
            
            r.text_centered(200, "MENU", config.COLOR_PRIMARY, scale=3)
            
            resume_btn = Button(50, 280, 100, 35, "Reanudar", config.COLOR_WHITE, config.COLOR_SUCCESS)
            exit_btn = Button(170, 280, 100, 35, "Salir", config.COLOR_WHITE, config.COLOR_ACCENT)
            
            resume_btn.draw(r)
            exit_btn.draw(r)
            r.flush()
            
        else:
            try:
                # Dibuja la app
                if self.app_instance and hasattr(self.app_instance, 'draw'):
                    self.app_instance.draw(r, self.frame)
                elif self.draw_func:
                    self.draw_func(r, self.frame)
                else:
                    # Si no hay función draw, muestra mensaje
                    r.fill(config.COLOR_BACKGROUND)
                    r.text_centered(240, "App sin interfaz", config.COLOR_TEXT_SECONDARY, scale=1)
                
                # Dibuja botón menú encima
                self.menu_btn.draw(r)
                r.flush()
                
            except Exception as e:
                self.error = f"Error en draw: {str(e)}"
                logger.error(f"App draw error: {e}")
                if config.DEBUG:
                    sys.print_exception(e)
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce():
            return
        
        logger.debug(f"AppRunner touch at ({x}, {y})")
        
        if self.error:
            # Volver al explorador
            logger.info("Returning to AppsScreen after error")
            from ui.apps_screen import AppsScreen
            self.app.change_screen(AppsScreen(self.app))
            return
        
        if self.paused:
            # Botones de pausa
            if 50 <= x <= 150 and 280 <= y <= 315:
                # Reanudar
                logger.info("App resumed")
                self.paused = False
            elif 170 <= x <= 270 and 280 <= y <= 315:
                # Salir
                logger.info("Exiting app, returning to AppsScreen")
                from ui.apps_screen import AppsScreen
                self.app.change_screen(AppsScreen(self.app))
            return
        
        # Botón menú
        if self.menu_btn.is_touched(x, y):
            logger.info("App menu opened")
            self.paused = True
            return
        
        # Pasa el toque a la app
        try:
            if self.app_instance and hasattr(self.app_instance, 'on_touch'):
                self.app_instance.on_touch(x, y)
            elif self.on_touch_func:
                self.on_touch_func(x, y)
        except Exception as e:
            logger.error(f"App touch error: {e}")
