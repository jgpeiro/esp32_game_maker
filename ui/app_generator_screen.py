# app_generator_screen.py - Pantalla de generación de ideas para aplicaciones

import config
import lib.logging as logging
from ui.screen import Screen, Button
from ui.app_loading_screen import AppLoadingScreen

logger = logging.getLogger("app_generator_screen")

class AppGeneratorScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        logger.debug("Initializing AppGeneratorScreen...")
        self.step = 0  # 0 = tipo de app, 1+ = características
        self.max_steps = 5  # Reducido a 5 pasos máximo
        self.description_parts = []  # Lista de frases seleccionadas (tipo + características)
        self.suggestions = []  # Sugerencias actuales mostradas
        self.rotation_index = 0  # Índice para rotar fallbacks
        self.loading_suggestions = False
        
        # Botones de navegación
        self.back_btn = Button(10, 430, 70, 30, "Atras", config.COLOR_TEXT_SECONDARY, config.COLOR_BUTTON_BG)
        self.regenerate_btn = Button(85, 430, 75, 30, "Otras", config.COLOR_SECONDARY, config.COLOR_BUTTON_BG)
        self.generate_btn = Button(165, 430, 145, 30, "GENERAR APP", config.COLOR_WHITE, config.COLOR_SUCCESS)
        
        # Botones de sugerencias (5 botones)
        self.suggestion_buttons = []
        for i in range(5):
            y = 165 + i * 50
            btn = Button(15, y, 290, 45, "", config.COLOR_SECONDARY, config.COLOR_BUTTON_BG)
            self.suggestion_buttons.append(btn)
        
        logger.debug(f"AppGeneratorScreen initialized with {len(self.suggestion_buttons)} suggestion buttons")
    
    def enter(self):
        logger.info("Entering AppGeneratorScreen")
        self.step = 0
        self.description_parts = []
        self.rotation_index = 0  # Reiniciar índice de rotación
        self._load_suggestions()
    
    def _get_current_description(self):
        """Construye la descripción actual para mostrar en pantalla"""
        if not self.description_parts:
            return "Elige el tipo de aplicacion:"
        # Construye la descripción a partir del tipo de app y las características
        app_type = self.description_parts[0]
        if len(self.description_parts) == 1:
            return f"App: {app_type}"
        features = ", ".join(self.description_parts[1:])
        return f"App: {app_type} - {features}"
    
    def _get_full_description_for_api(self):
        """Construye la descripción completa para enviar a la API de generación"""
        if not self.description_parts:
            return "Una aplicacion simple"
        app_type = self.description_parts[0]
        if len(self.description_parts) == 1:
            return f"Una aplicacion de tipo: {app_type}"
        features = ", ".join(self.description_parts[1:])
        return f"Una aplicacion de tipo {app_type} con las siguientes caracteristicas: {features}"
    
    def _load_suggestions(self):
        """Carga sugerencias desde la API"""
        logger.info(f"Loading suggestions for step {self.step}/{self.max_steps}")
        self.loading_suggestions = True
        
        # Llamada a la API según el paso
        if self.step == 0:
            # Paso inicial: pedir tipos de aplicaciones
            logger.debug(f"Calling API for app TYPE suggestions (rotation={self.rotation_index})...")
            self.suggestions = self.app.api.generate_app_type_suggestions(
                rotation_index=self.rotation_index,
                temperature=0.95
            )
        else:
            # Pasos siguientes: pedir características
            context = self._get_full_description_for_api()
            app_type = self.description_parts[0] if self.description_parts else ""
            logger.debug(f"Context for suggestions: '{context}'")
            logger.debug("Calling API for app FEATURE suggestions...")
            self.suggestions = self.app.api.generate_app_feature_suggestions(
                context, 
                app_type=app_type,
                temperature=0.9
            )
        
        logger.info(f"Received {len(self.suggestions)} suggestions")
        logger.debug(f"Suggestions: {self.suggestions}")
        
        # Actualiza los botones
        for i, btn in enumerate(self.suggestion_buttons):
            if i < len(self.suggestions):
                btn.text = self.suggestions[i]
                btn.enabled = True
            else:
                btn.text = ""
                btn.enabled = False
        
        self.loading_suggestions = False
        logger.debug("Suggestions loaded and buttons updated")
    
    def draw(self):
        r = self.renderer
        
        # Fondo
        r.fill(config.COLOR_BACKGROUND)
        
        # Header
        r.rect(0, 0, 320, 40, config.COLOR_BLACK, fill=True)
        if self.step == 0:
            header_text = "Elige tipo de app"
        else:
            header_text = f"Paso {self.step}/{self.max_steps-1} - Caracteristicas"
        r.text_centered(15, header_text, config.COLOR_SECONDARY, scale=1)
        
        # Barra de progreso
        progress = self.step / max(1, self.max_steps - 1)
        r.progress_bar(40, 30, 240, 6, progress, config.COLOR_BUTTON_BG, config.COLOR_PRIMARY)
        
        # Título
        r.text(15, 50, "Tu aplicacion:", config.COLOR_WHITE, scale=1)
        
        # Cuadro con descripción actual
        r.rounded_rect(15, 70, 290, 80, 6, config.COLOR_BUTTON_BG, fill=True)
        r.rounded_rect(15, 70, 290, 80, 6, config.COLOR_PRIMARY, fill=False)
        
        # Texto de la descripción (múltiples líneas)
        full_text = self._get_current_description()
        lines = self._wrap_text(full_text, 32)
        for i, line in enumerate(lines[:4]):  # Máximo 4 líneas
            r.text(25, 80 + i * 15, line, config.COLOR_PRIMARY, scale=1)
        
        # Título de sugerencias
        if self.step == 0:
            sug_title = "Selecciona el tipo:"
        else:
            sug_title = "Añade caracteristica:"
        r.text(15, 155, sug_title, config.COLOR_TEXT_SECONDARY, scale=1)
        
        # Dibuja sugerencias o loading
        if self.loading_suggestions:
            r.text_centered(280, "Cargando...", config.COLOR_PRIMARY, scale=2)
        else:
            for i, btn in enumerate(self.suggestion_buttons):
                if btn.enabled:
                    btn.bg_color = config.COLOR_BUTTON_BG
                    btn.color = config.COLOR_SECONDARY
                    
                    # Dibuja el botón
                    r.rounded_rect(btn.x, btn.y, btn.w, btn.h, 6, btn.bg_color, fill=True)
                    r.rounded_rect(btn.x, btn.y, btn.w, btn.h, 6, btn.color, fill=False)
                    
                    # Texto en dos líneas si es necesario
                    text_lines = self._wrap_text(btn.text, 34)
                    for j, line in enumerate(text_lines[:2]):
                        text_y = btn.y + 10 + j * 15
                        r.text(btn.x + 10, text_y, line, btn.color, scale=1)
        
        # Botones de navegación
        self.back_btn.draw(r)
        self.regenerate_btn.draw(r)
        
        # Botón generar solo si hay al menos el tipo de app seleccionado
        if len(self.description_parts) >= 1:
            self.generate_btn.draw(r)
        
        r.flush()
    
    def _wrap_text(self, text, max_chars):
        """Divide texto en líneas"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce() or self.loading_suggestions:
            return
        
        logger.debug(f"AppGeneratorScreen touch at ({x}, {y})")
        
        # Verifica sugerencias - un solo toque añade y avanza
        for i, btn in enumerate(self.suggestion_buttons):
            if btn.enabled and btn.is_touched(x, y):
                selected_phrase = self.suggestions[i]
                self.description_parts.append(selected_phrase)
                logger.info(f"Selected: '{selected_phrase}'")
                logger.debug(f"Current description: {self.description_parts}")
                
                # Avanzar al siguiente paso si no hemos llegado al máximo
                if self.step < self.max_steps - 1:
                    self.step += 1
                    self.rotation_index = 0  # Reiniciar rotación para nuevo paso
                    self._load_suggestions()
                return
        
        # Botón atrás
        if self.back_btn.is_touched(x, y):
            if len(self.description_parts) > 0:
                # Quitar última selección
                removed = self.description_parts.pop()
                logger.info(f"Removed: '{removed}'")
                if self.step > 0:
                    self.step -= 1
                self.rotation_index = 0
                self._load_suggestions()
            else:
                # Volver al menú
                logger.info("Returning to MenuScreen from AppGeneratorScreen")
                from ui.menu_screen import MenuScreen
                self.app.change_screen(MenuScreen(self.app))
            return
        
        # Botón "Otras" - rota los fallbacks
        if self.regenerate_btn.is_touched(x, y):
            self.rotation_index += 1
            logger.info(f"Rotating suggestions (index={self.rotation_index})")
            self._load_suggestions()
            return
        
        # Botón generar
        if self.generate_btn.is_touched(x, y):
            if len(self.description_parts) >= 1:
                # Construye descripción completa para la API
                description = self._get_full_description_for_api()
                logger.info(f"Starting app generation with description: '{description}'")
                
                # Va a pantalla de carga
                self.app.change_screen(AppLoadingScreen(self.app, description))
            return
