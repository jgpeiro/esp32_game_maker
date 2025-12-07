# generator_screen.py - Pantalla de generación de ideas

import config
import lib.logging as logging
from ui.screen import Screen, Button
# from ui.menu_screen import MenuScreen # Made local to prevent recursive imports
from ui.loading_screen import LoadingScreen

logger = logging.getLogger("generator_screen")

class GeneratorScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        logger.debug("Initializing GeneratorScreen...")
        self.step = 0  # 0, 1, 2 (3 pasos)
        self.max_steps = 3
        self.prompt_parts = []
        self.suggestions = []
        self.selected_index = -1
        self.loading_suggestions = False
        
        # Botones de navegación (ajustados para 320x480)
        self.back_btn = Button(20, 430, 70, 25, "Atras", config.COLOR_TEXT_SECONDARY, config.COLOR_BUTTON_BG)
        self.next_btn = Button(230, 430, 70, 25, "Siguiente", config.COLOR_WHITE, config.COLOR_SUCCESS)
        self.generate_btn = Button(90, 430, 140, 25, "GENERAR", config.COLOR_WHITE, config.COLOR_SUCCESS)
        
        # Grid de sugerencias (2 columnas, 5 filas) - ajustado para pantalla vertical
        self.suggestion_buttons = []
        for row in range(5):
            for col in range(2):
                x = 20 + col * 145
                y = 170 + row * 45
                btn = Button(x, y, 130, 35, "", config.COLOR_SECONDARY, config.COLOR_BUTTON_BG)
                self.suggestion_buttons.append(btn)
        logger.debug(f"GeneratorScreen initialized with {len(self.suggestion_buttons)} suggestion buttons")
    
    def enter(self):
        logger.info("Entering GeneratorScreen")
        self.step = 0
        self.prompt_parts = []
        self.selected_index = -1
        self._load_suggestions()
    
    def _load_suggestions(self):
        """Carga sugerencias desde la API"""
        logger.info(f"Loading suggestions for step {self.step + 1}/{self.max_steps}")
        self.loading_suggestions = True
        
        # Construye el contexto
        context = "Quiero hacer un juego de"
        if self.prompt_parts:
            context += " " + " ".join(self.prompt_parts)
        logger.debug(f"Context for suggestions: '{context}'")
        
        # Llamada a la API (esto puede tardar)
        logger.debug("Calling API for suggestions...")
        self.suggestions = self.app.api.generate_suggestions(context)
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
        
        # Header (ajustado para 320 de ancho)
        r.rect(0, 0, 320, 40, config.COLOR_BLACK, fill=True)
        step_text = f"Paso {self.step + 1} de {self.max_steps}"
        r.text_centered(15, step_text, config.COLOR_SECONDARY, scale=1)
        
        # Barra de progreso (ajustada para ancho 320)
        progress = (self.step + 1) / self.max_steps
        r.progress_bar(40, 30, 240, 6, progress, config.COLOR_BUTTON_BG, config.COLOR_PRIMARY)
        
        # Prompt del usuario
        r.text(20, 55, "Quiero hacer un juego de...", config.COLOR_WHITE, scale=1)
        
        # Cuadro con texto seleccionado (ajustado para 320 de ancho)
        r.rounded_rect(20, 75, 280, 40, 6, config.COLOR_BUTTON_BG, fill=True)
        r.rounded_rect(20, 75, 280, 40, 6, config.COLOR_PRIMARY, fill=False)
        
        # Texto construido hasta ahora
        full_text = " ".join(self.prompt_parts) if self.prompt_parts else "(selecciona)"
        r.text(30, 90, full_text[:35], config.COLOR_PRIMARY, scale=1)
        
        # Dropdown indicator
        r.text(285, 90, "v", config.COLOR_SECONDARY)
        
        # Título de sugerencias
        r.text(20, 135, "Selecciona una opcion:", config.COLOR_TEXT_SECONDARY, scale=1)
        
        # Dibuja sugerencias o loading
        if self.loading_suggestions:
            r.text_centered(280, "Cargando...", config.COLOR_PRIMARY, scale=2)
        else:
            for i, btn in enumerate(self.suggestion_buttons):
                if btn.enabled:
                    # Resalta si está seleccionado
                    if i == self.selected_index:
                        btn.bg_color = config.COLOR_PRIMARY
                        btn.color = config.COLOR_WHITE
                    else:
                        btn.bg_color = config.COLOR_BUTTON_BG
                        btn.color = config.COLOR_SECONDARY
                    btn.draw(r)
        
        # Botones de navegación
        self.back_btn.draw(r)
        
        if self.step < self.max_steps - 1:
            self.next_btn.enabled = self.selected_index >= 0
            self.next_btn.draw(r)
        else:
            # Último paso: muestra botón generar
            self.generate_btn.enabled = self.selected_index >= 0
            self.generate_btn.draw(r)
        
        r.flush()
    
    def handle_touch(self, x, y):
        if not self.check_touch_debounce() or self.loading_suggestions:
            return
        
        logger.debug(f"GeneratorScreen touch at ({x}, {y})")
        
        # Verifica sugerencias
        for i, btn in enumerate(self.suggestion_buttons):
            if btn.is_touched(x, y):
                self.selected_index = i
                logger.debug(f"Suggestion selected: index={i}, text='{self.suggestions[i]}'")
                return
        
        # Botón atrás
        if self.back_btn.is_touched(x, y):
            if self.step > 0:
                logger.info(f"Going back from step {self.step + 1} to step {self.step}")
                self.step -= 1
                if self.prompt_parts:
                    removed = self.prompt_parts.pop()
                    logger.debug(f"Removed prompt part: '{removed}'")
                self.selected_index = -1
                self._load_suggestions()
            else:
                # Volver al menú
                logger.info("Returning to MenuScreen from GeneratorScreen")
                from ui.menu_screen import MenuScreen
                self.app.change_screen(MenuScreen(self.app))
            return
        
        # Botón siguiente
        if self.step < self.max_steps - 1 and self.next_btn.is_touched(x, y):
            if self.selected_index >= 0:
                # Añade la palabra seleccionada
                selected_word = self.suggestions[self.selected_index]
                self.prompt_parts.append(selected_word)
                logger.info(f"Step {self.step + 1} complete. Added '{selected_word}'. Moving to step {self.step + 2}")
                logger.debug(f"Current prompt parts: {self.prompt_parts}")
                self.step += 1
                self.selected_index = -1
                self._load_suggestions()
            return
        
        # Botón generar
        if self.step == self.max_steps - 1 and self.generate_btn.is_touched(x, y):
            if self.selected_index >= 0:
                # Añade última palabra
                selected_word = self.suggestions[self.selected_index]
                self.prompt_parts.append(selected_word)
                logger.info(f"Final selection: '{selected_word}'")
                
                # Construye descripción completa
                description = "Quiero hacer un juego de " + " ".join(self.prompt_parts)
                logger.info(f"Starting game generation with description: '{description}'")
                
                # Va a pantalla de carga
                self.app.change_screen(LoadingScreen(self.app, description))

