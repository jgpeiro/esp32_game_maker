# splash_screen.py - Pantalla de inicio/splash

import time
import config
import lib.logging as logging
from ui.screen import Screen
from ui.menu_screen import MenuScreen

logger = logging.getLogger("splash_screen")

class SplashScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.start_time = 0
        self.duration = config.SPLASH_DURATION
        self.progress = 0.0
        self.angle = 0
        logger.debug(f"SplashScreen initialized with duration: {self.duration}ms")
    
    def enter(self):
        logger.info("Entering SplashScreen")
        self.start_time = time.ticks_ms()
        self.progress = 0.0
    
    def update(self):
        elapsed = time.ticks_diff(time.ticks_ms(), self.start_time)
        self.progress = min(elapsed / self.duration, 1.0)
        self.angle = (self.angle + 5) % 360
        
        if elapsed >= self.duration:
            logger.info(f"Splash duration complete ({elapsed}ms), transitioning to MenuScreen")
            self.app.change_screen(MenuScreen(self.app))
    
    def draw(self):
        r = self.renderer
        
        # Fondo
        r.fill(config.COLOR_BACKGROUND)
        
        # Círculos concéntricos animados (centrado en pantalla vertical 320x480)
        cx, cy = 160, 140
        
        # Círculo exterior
        r.circle(cx, cy, 50, config.COLOR_PRIMARY, fill=False)
        
        # Círculo medio
        r.circle(cx, cy, 40, config.COLOR_SECONDARY, fill=False)
        
        # Círculo interior
        r.circle(cx, cy, 30, config.COLOR_ACCENT, fill=False)
        
        # Texto principal
        r.text_centered(195, "GAME", config.COLOR_PRIMARY, scale=3)
        r.text_centered(230, "MAKER", config.COLOR_SECONDARY, scale=2)
        
        # Estrellas decorativas (posiciones ajustadas para vertical)
        stars = [(50, 80), (260, 100), (70, 290)]
        for sx, sy in stars:
            self._draw_star(sx, sy, 6, config.COLOR_WARNING)
        
        # Barra de progreso
        bar_x, bar_y = 60, 330
        bar_w, bar_h = 200, 12
        r.progress_bar(bar_x, bar_y, bar_w, bar_h, self.progress, 
                      config.COLOR_BUTTON_BG, config.COLOR_PRIMARY)
        
        # Texto inferior
        r.text_centered(370, "Powered by Claude AI", config.COLOR_TEXT_SECONDARY)
        r.text_centered(390, "v1.0 - ESP32", config.COLOR_TEXT_SECONDARY)
        
        r.flush()
    
    def _draw_star(self, cx, cy, size, color):
        """Dibuja una estrella de 5 puntas"""
        # Versión simplificada con líneas
        points = []
        for i in range(5):
            angle = i * 72 - 90  # -90 para empezar arriba
            x = cx + int(size * self._cos(angle))
            y = cy + int(size * self._sin(angle))
            points.append((x, y))
            
            angle2 = angle + 36
            x2 = cx + int(size * 0.4 * self._cos(angle2))
            y2 = cy + int(size * 0.4 * self._sin(angle2))
            points.append((x2, y2))
        
        # Dibuja líneas conectando los puntos
        for i in range(10):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % 10]
            self.renderer.line(x1, y1, x2, y2, color)
    
    def _cos(self, degrees):
        """Coseno aproximado"""
        import math
        return math.cos(math.radians(degrees))
    
    def _sin(self, degrees):
        """Seno aproximado"""
        import math
        return math.sin(math.radians(degrees))
