# claude_api.py - Cliente para la API de Claude

import urequests as requests
import ujson as json
import config
import lib.logging as logging
from core.settings import Settings

logger = logging.getLogger("claude_api")

class ClaudeAPI:
    def __init__(self):
        self.settings = Settings()
        # Usar API key de settings si está disponible, sino usar config.py
        self.api_key = self.settings.api_key if self.settings.api_key else config.CLAUDE_API_KEY
        self.model = config.CLAUDE_MODEL
        self.max_tokens = config.CLAUDE_MAX_TOKENS
        self.endpoint = "https://api.anthropic.com/v1/messages"
        logger.debug(f"ClaudeAPI initialized with model: {self.model}")
    
    def refresh_api_key(self):
        """Actualiza el API key desde settings"""
        self.api_key = self.settings.api_key if self.settings.api_key else config.CLAUDE_API_KEY
        logger.debug("API key refreshed from settings")
    
    def _make_request(self, prompt, max_tokens=None, temperature=1.0):
        """Realiza una petición a la API de Claude
        
        Args:
            prompt: El prompt a enviar
            max_tokens: Número máximo de tokens en la respuesta
            temperature: Controla la aleatoriedad (0.0-1.0). Más alto = más variado
        """
        # Refrescar API key por si cambió
        self.refresh_api_key()
        
        logger.debug(f"Making API request with max_tokens={max_tokens or self.max_tokens}, temperature={temperature}")
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        body = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            # Serializa y valida JSON
            json_str = json.dumps(body)
            
            logger.debug(f"Request body size: {len(json_str)} bytes")
            logger.debug(f"Prompt length: {len(prompt)} chars")
            
            logger.info(f"Sending POST request to {self.endpoint}...")
            response = requests.post(
                self.endpoint,
                headers=headers,
                data=json_str
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "content" in data and len(data["content"]) > 0:
                    content = data["content"][0]["text"]
                    logger.debug(f"Response content length: {len(content)} chars")
                    return content
                logger.warning("Response has no content")
                return None
            else:
                logger.error(f"API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    logger.error(f"Error details: {error_data}")
                except:
                    logger.error(f"Response text: {response.text[:200]}")
                return None
                
        except Exception as e:
            logger.error(f"Request exception: {e}")
            return None
        finally:
            try:
                response.close()
            except:
                pass
    
    def generate_suggestions(self, context, temperature=0.9):
        """
        Genera 10 sugerencias de palabras dado un contexto
        
        Args:
            context: El texto actual (ej: "Quiero hacer un juego de")
            temperature: Controla la variabilidad de las respuestas (0.0-1.0)
        
        Returns:
            Lista de 10 palabras o None si falla
        """
        logger.info(f"Generating suggestions for context: '{context}'")
        prompt = config.SUGGESTION_PROMPT.format(context=context)
        response = self._make_request(prompt, max_tokens=100, temperature=temperature)
        
        if response:
            # Procesa la respuesta: espera "palabra1,palabra2,..."
            logger.debug(f"Raw response: '{response}'")
            words = [w.strip() for w in response.split(",")]
            # Limita a 10 y filtra vacíos
            words = [w for w in words if w][:10]
            logger.debug(f"Parsed {len(words)} words: {words}")
            
            # Si no hay suficientes, añade defaults
            if len(words) < 10:
                logger.debug("Adding fallback words to reach 10")
                for fallback in config.FALLBACK_GAME_SUGGESTIONS:
                    if fallback not in words:
                        words.append(fallback)
                    if len(words) >= 10:
                        break
            
            logger.info(f"Returning {len(words)} suggestions")
            return words[:10]
        
        # Fallback si falla la API
        logger.warning("API failed, returning fallback suggestions")
        return config.FALLBACK_GAME_SUGGESTIONS[:]
    
    def generate_app_type_suggestions(self, rotation_index=0, temperature=0.95):
        """
        Genera 5 sugerencias de TIPOS de aplicaciones (paso inicial)
        
        Args:
            rotation_index: Índice para rotar entre grupos de fallbacks
            temperature: Controla la variabilidad (0.0-1.0). Alto para más creatividad.
        
        Returns:
            Lista de 5 tipos de apps o fallback si falla
        """
        logger.info(f"Generating app type suggestions with temperature={temperature}, rotation={rotation_index}")
        prompt = config.APP_TYPE_SUGGESTION_PROMPT
        response = self._make_request(prompt, max_tokens=200, temperature=temperature)
        
        if response:
            logger.debug(f"Raw response: '{response}'")
            # Procesa la respuesta: espera "tipo1|tipo2|..."
            types = [t.strip() for t in response.split("|")]
            # Limita a 5 y filtra vacíos
            types = [t for t in types if t][:5]
            logger.debug(f"Parsed {len(types)} types: {types}")
            
            # Si no hay suficientes, añade defaults
            if len(types) < 5:
                logger.debug("Adding fallback types to reach 5")
                for fallback in config.FALLBACK_APP_TYPES:
                    if fallback not in types:
                        types.append(fallback)
                    if len(types) >= 5:
                        break
            
            logger.info(f"Returning {len(types)} app type suggestions")
            return types[:5]
        
        # Fallback si falla la API - usa rotación para variedad
        logger.warning("API failed, returning fallback app types")
        pool = config.FALLBACK_APP_TYPES_POOL
        group_index = rotation_index % len(pool)
        logger.debug(f"Using fallback group {group_index}")
        return pool[group_index][:]
    
    def generate_app_feature_suggestions(self, context, app_type="", temperature=0.9):
        """
        Genera 5 sugerencias de CARACTERÍSTICAS para una app (pasos siguientes)
        
        Args:
            context: La descripción actual de la app
            app_type: El tipo de app para fallbacks inteligentes
            temperature: Controla la variabilidad (0.0-1.0)
        
        Returns:
            Lista de 5 características o fallback si falla
        """
        logger.info(f"Generating app feature suggestions for context: '{context}'")
        prompt = config.APP_FEATURE_SUGGESTION_PROMPT.format(context=context)
        response = self._make_request(prompt, max_tokens=300, temperature=temperature)
        
        if response:
            logger.debug(f"Raw response: '{response}'")
            # Procesa la respuesta: espera "feature1|feature2|..."
            features = [f.strip() for f in response.split("|")]
            # Limita a 5 y filtra vacíos
            features = [f for f in features if f][:5]
            logger.debug(f"Parsed {len(features)} features: {features}")
            
            # Si no hay suficientes, añade defaults
            if len(features) < 5:
                logger.debug("Adding fallback features to reach 5")
                for fallback in config.FALLBACK_APP_FEATURES:
                    if fallback not in features:
                        features.append(fallback)
                    if len(features) >= 5:
                        break
            
            logger.info(f"Returning {len(features)} app feature suggestions")
            return features[:5]
        
        # Fallback si falla la API - usa características específicas por tipo
        logger.warning("API failed, returning fallback app features")
        # Buscar fallbacks específicos para este tipo de app
        features_dict = config.FALLBACK_FEATURES_BY_TYPE
        fallback_features = features_dict.get(app_type, features_dict.get("default", config.FALLBACK_APP_FEATURES))
        logger.debug(f"Using fallback features for type '{app_type}': {fallback_features}")
        return fallback_features[:]
    
    def generate_game(self, description):
        """
        Genera el código de un juego completo
        
        Args:
            description: Descripción del juego (ej: "aventura espacial con aliens")
        
        Returns:
            Código Python del juego o None si falla
        """
        logger.info(f"Generating game code for: '{description}'")
        prompt = config.GAME_TEMPLATE.format(description=description)
        
        # Solicita más tokens para el código completo
        logger.debug("Requesting 16000 tokens for game generation...")
        response = self._make_request(prompt, max_tokens=16000)
        
        if response:
            # Extrae el código entre ```python y ```
            logger.debug("Extracting Python code from response...")
            code = self._extract_code(response)
            logger.info(f"Extracted code: {len(code)} chars")
            return code
        
        logger.error("Failed to generate game code")
        return None
    
    def generate_app(self, description):
        """
        Genera el código de una aplicación completa
        
        Args:
            description: Descripción de la app
        
        Returns:
            Código Python de la app o None si falla
        """
        logger.info(f"Generating app code for: '{description}'")
        prompt = config.APP_TEMPLATE.format(description=description)
        
        logger.debug("Requesting 16000 tokens for app generation...")
        response = self._make_request(prompt, max_tokens=16000)
        
        if response:
            logger.debug("Extracting Python code from response...")
            code = self._extract_code(response)
            logger.info(f"Extracted code: {len(code)} chars")
            return code
        
        logger.error("Failed to generate app code")
        return None
    
    def _extract_code(self, text):
        """Extrae bloques de código Python de la respuesta"""
        logger.debug("Parsing code blocks from response...")
        # Busca entre ```python y ```
        start_markers = ["```python\n", "```Python\n", "```py\n"]
        end_marker = "\n```"
        
        code_blocks = []
        
        for marker in start_markers:
            parts = text.split(marker)
            for i in range(1, len(parts)):
                if end_marker in parts[i]:
                    code = parts[i].split(end_marker)[0]
                    code_blocks.append(code)
        
        logger.debug(f"Found {len(code_blocks)} code block(s)")
        
        # Si no hay bloques de código, intenta retornar todo
        if not code_blocks:
            logger.warning("No code blocks found, returning raw text")
            return text.strip()
        
        # Concatena todos los bloques encontrados
        return "\n\n".join(code_blocks)