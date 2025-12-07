# renderer.py - Sistema de renderizado con framebuffer

import framebuf
import micropython
import lib.logging as logging

logger = logging.getLogger("renderer")

class Renderer:
    def __init__(self, display):
        logger.debug("Initializing Renderer...")
        self.display = display
        self.width = display.WIDTH
        self.height = display.HEIGHT
        
        # Framebuffer RGB565
        buffer_size = self.width * self.height * 2
        logger.debug(f"Allocating framebuffer: {buffer_size} bytes ({self.width}x{self.height})")
        self.buffer = bytearray(buffer_size)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
        
        # Fuente básica (8x8 por defecto en framebuf)
        self.font_width = 8
        self.font_height = 8
        logger.info(f"Renderer initialized: {self.width}x{self.height}, buffer={buffer_size} bytes")
    
    def fill(self, color):
        """Rellena toda la pantalla con un color"""
        self.fb.fill(color)
    
    def pixel(self, x, y, color):
        """Dibuja un pixel"""
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            self.fb.pixel(x, y, color)
    
    def line(self, x0, y0, x1, y1, color):
        """Dibuja una línea"""
        x0, y0 = int(x0), int(y0)
        x1, y1 = int(x1), int(y1)
        self.fb.line(x0, y0, x1, y1, color)
    
    def rect(self, x, y, w, h, color, fill=False):
        """Dibuja un rectángulo"""
        x, y = int(x), int(y)
        w, h = int(w), int(h)
        if fill:
            self.fb.fill_rect(x, y, w, h, color)
        else:
            self.fb.rect(x, y, w, h, color)
    
    def circle(self, cx, cy, r, color, fill=False):
        """Dibuja un círculo usando framebuf.ellipse"""
        cx, cy = int(cx), int(cy)
        r = int(r)
        self.fb.ellipse(cx, cy, r, r, color, fill)
    
    def text(self, x, y, txt, color, scale=1):
        """Dibuja texto con escala opcional"""
        x, y = int(x), int(y)
        if scale == 1:
            self.fb.text(txt, x, y, color)
        else:
            # Calcula dimensiones del texto
            text_w = len(txt) * self.font_width
            text_h = self.font_height
            scaled_w = text_w * scale
            scaled_h = text_h * scale
            
            # Buffer temporal para texto original
            temp_buf = bytearray(text_w * text_h * 2)
            temp_fb = framebuf.FrameBuffer(temp_buf, text_w, text_h, framebuf.RGB565)
            temp_fb.fill(0)
            temp_fb.text(txt, 0, 0, color)
            
            # Buffer temporal para texto escalado
            scaled_buf = bytearray(scaled_w * scaled_h * 2)
            scaled_fb = framebuf.FrameBuffer(scaled_buf, scaled_w, scaled_h, framebuf.RGB565)
            
            # Escalar usando función optimizada
            self._scale_buffer(temp_buf, scaled_buf, text_w, text_h, scale)
            
            # Blit del texto escalado al framebuffer principal
            self.fb.blit(scaled_fb, x, y, 0)
    
    @micropython.viper
    def _scale_buffer(self, src, dst, w: int, h: int, scale: int):
        """Escala un buffer usando viper para máxima velocidad"""
        src_buf = ptr16(src)
        dst_buf = ptr16(dst)
        scaled_w = w * scale
        
        for sy in range(h):
            for sx in range(w):
                pixel = src_buf[sy * w + sx]
                if pixel != 0:  # Solo copiar pixels no negros
                    # Escalar el pixel
                    for dy in range(scale):
                        for dx in range(scale):
                            dst_y = sy * scale + dy
                            dst_x = sx * scale + dx
                            dst_buf[dst_y * scaled_w + dst_x] = pixel
    
    def text_centered(self, y, txt, color, scale=1):
        """Dibuja texto centrado horizontalmente"""
        y = int(y)
        text_width = len(txt) * self.font_width * scale
        x = (self.width - text_width) // 2
        self.text(x, y, txt, color, scale)
    
    def text_right(self, x, y, txt, color, scale=1):
        """Dibuja texto alineado a la derecha"""
        x, y = int(x), int(y)
        text_width = len(txt) * self.font_width * scale
        self.text(x - text_width, y, txt, color, scale)
    
    def rounded_rect(self, x, y, w, h, r, color, fill=False):
        """Dibuja un rectángulo con esquinas redondeadas"""
        x, y = int(x), int(y)
        w, h = int(w), int(h)
        r = int(r)
        if fill:
            self.fb.fill_rect(x + r, y, w - 2 * r, h, color)
            self.fb.fill_rect(x, y + r, w, h - 2 * r, color)
            self._fill_corner(x + r, y + r, r, color, 1)  # Top-left (Q2)
            self._fill_corner(x + w - r - 1, y + r, r, color, 0)  # Top-right (Q1)
            self._fill_corner(x + r, y + h - r - 1, r, color, 2)  # Bottom-left (Q3)
            self._fill_corner(x + w - r - 1, y + h - r - 1, r, color, 3)  # Bottom-right (Q4)
        else:
            self.fb.hline(x + r, y, w - 2 * r, color)
            self.fb.hline(x + r, y + h - 1, w - 2 * r, color)
            self.fb.vline(x, y + r, h - 2 * r, color)
            self.fb.vline(x + w - 1, y + r, h - 2 * r, color)
            self._draw_corner(x + r, y + r, r, color, 1)  # Top-left (Q2)
            self._draw_corner(x + w - r - 1, y + r, r, color, 0)  # Top-right (Q1)
            self._draw_corner(x + r, y + h - r - 1, r, color, 2)  # Bottom-left (Q3)
            self._draw_corner(x + w - r - 1, y + h - r - 1, r, color, 3)  # Bottom-right (Q4)
    
    def _draw_corner(self, cx, cy, r, color, quadrant):
        """Dibuja un cuarto de círculo usando ellipse"""
        cx, cy = int(cx), int(cy)
        r = int(r)
        # Usar ellipse con máscara de cuadrante
        mask = 1 << quadrant
        self.fb.ellipse(cx, cy, r, r, color, False, mask)
    
    def _fill_corner(self, cx, cy, r, color, quadrant):
        """Rellena un cuarto de círculo usando ellipse"""
        cx, cy = int(cx), int(cy)
        r = int(r)
        # Usar ellipse con máscara de cuadrante
        mask = 1 << quadrant
        self.fb.ellipse(cx, cy, r, r, color, True, mask)
    
    def progress_bar(self, x, y, w, h, progress, bg_color, fg_color):
        """Dibuja una barra de progreso (0.0 - 1.0)"""
        x, y = int(x), int(y)
        w, h = int(w), int(h)
        # Fondo
        self.rounded_rect(x, y, w, h, h // 2, bg_color, fill=True)
        # Progreso
        if progress > 0:
            prog_w = int(w * min(progress, 1.0))
            if prog_w > 0:
                self.rounded_rect(x, y, prog_w, h, h // 2, fg_color, fill=True)
    
    def flush(self):
        """Envía el framebuffer al display"""
        self.display.draw(0, 0, self.width, self.height, self.buffer)