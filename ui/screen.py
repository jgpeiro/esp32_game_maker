# screen.py - Clase base para todas las pantallas

import time
import lib.logging as logging

logger = logging.getLogger("screen")

class Screen:
    def __init__(self, app):
        self.app = app
        self.renderer = app.renderer
        self.last_touch_time = 0
        self.touch_debounce = 20  # ms
        logger.debug(f"Screen base initialized: {type(self).__name__}")
    
    def enter(self):
        """Llamado cuando se entra a esta pantalla"""
        logger.debug(f"{type(self).__name__}.enter()")
        pass
    
    def exit(self):
        """Llamado cuando se sale de esta pantalla"""
        logger.debug(f"{type(self).__name__}.exit()")
        pass
    
    def update(self):
        """Actualiza la lógica de la pantalla - llamado cada frame"""
        pass
    
    def draw(self):
        """Dibuja la pantalla - debe ser implementado por subclases"""
        raise NotImplementedError("Subclass must implement draw()")
    
    def handle_touch(self, x, y):
        """Maneja eventos de toque - implementado por subclases"""
        pass
    
    def check_touch_debounce(self):
        """Verifica si ha pasado suficiente tiempo desde el último toque"""
        current = time.ticks_ms()
        if time.ticks_diff(current, self.last_touch_time) > self.touch_debounce:
            self.last_touch_time = current
            logger.debug(f"{type(self).__name__}: touch debounce passed")
            return True
        return False

class Button:
    def __init__(self, x, y, w, h, text, color, bg_color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.enabled = True
    
    def draw(self, renderer):
        """Dibuja el botón"""
        if self.enabled:
            renderer.rounded_rect(self.x, self.y, self.w, self.h, 8, self.bg_color, fill=True)
            renderer.rounded_rect(self.x, self.y, self.w, self.h, 8, self.color, fill=False)
        else:
            renderer.rounded_rect(self.x, self.y, self.w, self.h, 8, 0x2945, fill=True)
            renderer.rounded_rect(self.x, self.y, self.w, self.h, 8, 0x4A69, fill=False)
        
        # Texto centrado
        text_w = len(self.text) * 8
        text_x = self.x + (self.w - text_w) // 2
        text_y = self.y + (self.h - 8) // 2
        
        color = self.color if self.enabled else 0x8410
        renderer.text(text_x, text_y, self.text, color)
    
    def is_touched(self, x, y):
        """Verifica si el toque está dentro del botón"""
        return (self.enabled and 
                self.x <= x <= self.x + self.w and 
                self.y <= y <= self.y + self.h)
