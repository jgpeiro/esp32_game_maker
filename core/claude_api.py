# claude_api.py - Cliente para la API de Claude

import urequests as requests
import ujson as json
import config
import lib.logging as logging

logger = logging.getLogger("claude_api")

class ClaudeAPI:
    def __init__(self):
        self.api_key = config.CLAUDE_API_KEY
        self.model = config.CLAUDE_MODEL
        self.max_tokens = config.CLAUDE_MAX_TOKENS
        self.endpoint = "https://api.anthropic.com/v1/messages"
        logger.debug(f"ClaudeAPI initialized with model: {self.model}")
    
    def _make_request(self, prompt, max_tokens=None):
        """Realiza una petición a la API de Claude"""
        logger.debug(f"Making API request with max_tokens={max_tokens or self.max_tokens}")
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        body = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
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
    
    def generate_suggestions(self, context):
        """
        Genera 10 sugerencias de palabras dado un contexto
        
        Args:
            context: El texto actual (ej: "Quiero hacer un juego de")
        
        Returns:
            Lista de 10 palabras o None si falla
        """
        logger.info(f"Generating suggestions for context: '{context}'")
        prompt = config.SUGGESTION_PROMPT.format(context=context)
        response = self._make_request(prompt, max_tokens=100)
        
        if response:
            # Procesa la respuesta: espera "palabra1,palabra2,..."
            logger.debug(f"Raw response: '{response}'")
            words = [w.strip() for w in response.split(",")]
            # Limita a 10 y filtra vacíos
            words = [w for w in words if w][:10]
            logger.debug(f"Parsed {len(words)} words: {words}")
            
            # Si no hay suficientes, añade defaults
            while len(words) < 10:
                logger.debug("Adding fallback words to reach 10")
                words.extend(["aventura", "puzzle", "arcade", "plataforma", "carreras"])
                words = words[:10]
            
            logger.info(f"Returning {len(words)} suggestions")
            return words
        
        # Fallback si falla la API
        logger.warning("API failed, returning fallback suggestions")
        return [
            "aventura", "plataforma", "carreras", "puzzle", "arcade",
            "shooter", "estrategia", "deportes", "simulador", "retro"
        ]
    
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
        logger.debug("Requesting 8000 tokens for game generation...")
        response = self._make_request(prompt, max_tokens=8000)
        
        if response:
            # Extrae el código entre ```python y ```
            logger.debug("Extracting Python code from response...")
            code = self._extract_code(response)
            logger.info(f"Extracted code: {len(code)} chars")
            return code
        
        logger.error("Failed to generate game code")
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