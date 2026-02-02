"""
Constrained Argument Extractor

Estrae gli argomenti delle funzioni usando constrained decoding.
Sostituisce l'approccio basato su regex.
"""

from typing import Dict, List, Any, Set
import math


class ConstrainedArgumentExtractor:
    """
    Estrae argomenti usando constrained decoding.
    
    Invece di regex, guida l'LLM token-per-token:
    1. FORZA i token strutturali ({"arg":)
    2. PERMETTE solo token validi per il tipo
    3. L'LLM "sceglie" i valori basandosi sul contesto
    """
    
    def __init__(self, model: Any, tokenizer: Any, vocabulary: Dict[str, int]):
        self.model = model
        self.tokenizer = tokenizer
        self.vocabulary = vocabulary
        self.inv_vocabulary = {v: k for k, v in vocabulary.items()}
        self._precompute_token_sets()
    
    def _normalize_token(self, token: str) -> str:
        """Normalizza token (gestisce caratteri speciali GPT-style)."""
        return token.replace('Ġ', ' ').replace('Ċ', '\n').replace('ĉ', '\t')
    
    def _precompute_token_sets(self) -> None:
        """Pre-calcola i token permessi per ogni tipo."""
        self.number_tokens: Set[int] = set()
        self.string_tokens: Set[int] = set()
        self.terminator_tokens: Set[int] = set()
        
        for token_str, token_id in self.vocabulary.items():
            normalized = self._normalize_token(token_str)
            
            # Token per NUMERI
            if normalized and all(c in '0123456789.-+eE' for c in normalized):
                self.number_tokens.add(token_id)
            
            # Token per STRINGHE (no quote, no newline)
            if normalized and '"' not in normalized and '\n' not in normalized:
                self.string_tokens.add(token_id)
            
            # Token terminatori
            if normalized in [',', '}', '"', ',"']:
                self.terminator_tokens.add(token_id)
    
    def extract_arguments(
        self,
        prompt: str,
        fn_name: str,
        arg_names: List[str],
        arg_types: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Estrae gli argomenti dal prompt.
        
        Args:
            prompt: Prompt dell'utente
            fn_name: Nome della funzione
            arg_names: Lista nomi argomenti
            arg_types: Dict nome -> tipo
        
        Returns:
            Dict con argomenti estratti
        """
        if not arg_names:
            return {}
        
        # Costruisci prompt per estrazione
        extraction_prompt = self._build_prompt(prompt, fn_name, arg_names, arg_types)
        input_ids = self.tokenizer.encode(extraction_prompt, add_special_tokens=False)
        
        result = {}
        
        # Forza "{"
        self._force_tokens(input_ids, "{")
        
        for i, arg_name in enumerate(arg_names):
            arg_type = arg_types.get(arg_name, "string").lower()
            
            # Forza la chiave JSON
            if i == 0:
                self._force_tokens(input_ids, f'"{arg_name}":')
            else:
                self._force_tokens(input_ids, f',"{arg_name}":')
            
            # Genera il valore con constrained decoding
            if "str" in arg_type or "string" in arg_type:
                self._force_tokens(input_ids, '"')
                value = self._generate_string_value(input_ids)
                self._force_tokens(input_ids, '"')
                result[arg_name] = value
            
            elif any(t in arg_type for t in ["int", "float", "number"]):
                value_str = self._generate_number_value(input_ids)
                try:
                    if "int" in arg_type:
                        result[arg_name] = int(float(value_str))
                    else:
                        result[arg_name] = float(value_str)
                except ValueError:
                    result[arg_name] = 0
            
            elif "bool" in arg_type:
                result[arg_name] = self._generate_boolean_value(input_ids)
            
            else:
                # Default: stringa
                self._force_tokens(input_ids, '"')
                value = self._generate_string_value(input_ids)
                self._force_tokens(input_ids, '"')
                result[arg_name] = value
        
        return result
    
    def _build_prompt(
        self,
        user_prompt: str,
        fn_name: str,
        arg_names: List[str],
        arg_types: Dict[str, str]
    ) -> str:
        """Costruisce il prompt per l'estrazione."""
        schema_parts = []
        for name in arg_names:
            t = arg_types.get(name, "string")
            schema_parts.append(f'"{name}": <{t}>')
        schema = "{" + ", ".join(schema_parts) + "}"
        
        return f"""Extract argument values from the user request.
Function: {fn_name}
User request: "{user_prompt}"
Output format: {schema}
JSON: """
    
    def _force_tokens(self, input_ids: List[int], text: str) -> None:
        """Forza una sequenza di token."""
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        input_ids.extend(tokens)
    
    def _generate_number_value(self, input_ids: List[int], max_tokens: int = 15) -> str:
        """Genera un numero con constrained decoding."""
        value_str = ""
        
        for _ in range(max_tokens):
            logits = self.model.get_logits_from_input_ids(input_ids)
            masked_logits = [-math.inf] * len(logits)
            
            # Permetti solo token numerici validi
            for token_id in self.number_tokens:
                if token_id < len(logits):
                    token_str = self.inv_vocabulary.get(token_id, "")
                    normalized = self._normalize_token(token_str)
                    if self._is_valid_number_partial(value_str + normalized):
                        masked_logits[token_id] = float(logits[token_id])
            
            # Permetti terminatori
            for token_id in self.terminator_tokens:
                if token_id < len(logits):
                    masked_logits[token_id] = float(logits[token_id])
            
            max_logit = max(masked_logits)
            if max_logit == -math.inf:
                break
            
            next_token_id = masked_logits.index(max_logit)
            next_token = self._normalize_token(self.inv_vocabulary.get(next_token_id, ""))
            
            # Se è terminatore, fermati
            if next_token in [',', '}', ',"']:
                break
            
            value_str += next_token
            input_ids.append(next_token_id)
            
            # Check se numero completo
            if self._is_complete_number(value_str):
                peek_logits = self.model.get_logits_from_input_ids(input_ids)
                if hasattr(peek_logits, 'argmax'):
                    top_id = int(peek_logits.argmax())
                else:
                    top_id = peek_logits.index(max(peek_logits))
                top_token = self._normalize_token(self.inv_vocabulary.get(top_id, ""))
                if top_token in [',', '}']:
                    break
        
        return value_str.strip() if value_str.strip() else "0"
    
    def _generate_string_value(self, input_ids: List[int], max_tokens: int = 100) -> str:
        """Genera una stringa con constrained decoding."""
        value_str = ""
        
        for _ in range(max_tokens):
            logits = self.model.get_logits_from_input_ids(input_ids)
            masked_logits = [-math.inf] * len(logits)
            
            # Permetti token stringa + virgoletta chiusura
            for token_id in self.string_tokens:
                if token_id < len(logits):
                    masked_logits[token_id] = float(logits[token_id])
            
            # Permetti virgoletta di chiusura
            for token_str, token_id in self.vocabulary.items():
                if self._normalize_token(token_str) == '"' and token_id < len(logits):
                    masked_logits[token_id] = float(logits[token_id])
            
            max_logit = max(masked_logits)
            if max_logit == -math.inf:
                break
            
            next_token_id = masked_logits.index(max_logit)
            next_token = self._normalize_token(self.inv_vocabulary.get(next_token_id, ""))
            
            # Se è virgoletta chiusura, fermati
            if next_token == '"':
                break
            
            value_str += next_token
            input_ids.append(next_token_id)
        
        return value_str
    
    def _generate_boolean_value(self, input_ids: List[int]) -> bool:
        """Genera un booleano."""
        logits = self.model.get_logits_from_input_ids(input_ids)
        
        true_tokens = self.tokenizer.encode("true", add_special_tokens=False)
        false_tokens = self.tokenizer.encode("false", add_special_tokens=False)
        
        true_logit = float(logits[true_tokens[0]]) if true_tokens and true_tokens[0] < len(logits) else -math.inf
        false_logit = float(logits[false_tokens[0]]) if false_tokens and false_tokens[0] < len(logits) else -math.inf
        
        result = true_logit > false_logit
        
        if result:
            input_ids.extend(true_tokens)
        else:
            input_ids.extend(false_tokens)
        
        return result
    
    def _is_valid_number_partial(self, s: str) -> bool:
        """Verifica se è un numero parziale valido."""
        s = s.strip()
        if not s:
            return True
        if s in ['-', '+', '.', '-.', '+.']:
            return True
        if s.endswith('e') or s.endswith('E') or s.endswith('e-') or s.endswith('E-'):
            return True
        try:
            float(s)
            return True
        except ValueError:
            if s.endswith('.'):
                try:
                    float(s + '0')
                    return True
                except ValueError:
                    pass
            return False
    
    def _is_complete_number(self, s: str) -> bool:
        """Verifica se è un numero completo."""
        s = s.strip()
        if not s:
            return False
        try:
            float(s)
            return not (s.endswith('.') or s.endswith('e') or s.endswith('E'))
        except ValueError:
            return False