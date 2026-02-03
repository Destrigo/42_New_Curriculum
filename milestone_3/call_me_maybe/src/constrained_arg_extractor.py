"""
Constrained Argument Extractor - Select from candidates

Pick from candidates (prompt).
1. extract form prompt the values
2. Tokenize the candidates
3. LLM chooses with constrained decoding
"""

from typing import Dict, List, Any, Tuple
import math
import re


class ConstrainedArgumentExtractor:
    """
    Extracts arguments using constrained decoding from a set of candidates.
    1. Extracts CANDIDATES from the prompt
    2. Uses CONSTRAINED DECODING to select among candidates
       (same principle as function selection)
    """

    def __init__(self, model: Any, tokenizer: Any, vocabulary: Dict[str, int]):
        self.model = model
        self.tokenizer = tokenizer
        self.vocabulary = vocabulary
        self.inv_vocabulary = {v: k for k, v in vocabulary.items()}

    def extract_arguments(
        self,
        prompt: str,
        fn_name: str,
        arg_names: List[str],
        arg_types: Dict[str, str]
    ) -> Dict[str, Any]:
        """Extracts arguments from a prompt using constrained decoding."""
        if not arg_names:
            return {}

        result: Dict[Any, Any] = {}
        used_candidates: List[str] = []

        for arg_name in arg_names:
            arg_type = arg_types.get(arg_name, "string").lower()

            # Extracts candidates
            candidates = self._extract_candidates(prompt, fn_name, arg_name,
                                                  arg_type, used_candidates)

            if not candidates:
                if "int" in arg_type:
                    result[arg_name] = 0
                elif "float" in arg_type:
                    result[arg_name] = 0.0
                elif "bool" in arg_type:
                    result[arg_name] = False
                else:
                    result[arg_name] = ""
                continue

            if len(candidates) == 1:
                value = candidates[0]
            else:
                # picks
                value = self._select_candidate(prompt, fn_name,
                                               arg_name, arg_type, candidates)

            used_candidates.append(value)
            result[arg_name] = self._convert_type(value, arg_type)

        return result

    def _extract_candidates(
        self,
        prompt: str,
        fn_name: str,
        arg_name: str,
        arg_type: str,
        used_candidates: List[str]
    ) -> List[str]:
        """Extracts candidates for an argument."""
        candidates = []
        prompt = prompt.lower()

        if "int" in arg_type or "float" in arg_type or "number" in arg_type:
            numbers = re.findall(r'-?\d+\.?\d*', prompt)
            candidates.extend([n for n in numbers if n not in used_candidates])

        elif "bool" in arg_type:
            candidates = ["true", "false"]

        else:  # string
            if fn_name == "fn_substitute_string_with_regex":
                candidates = self._extract_sub_candidates(prompt,
                                                          arg_name,
                                                          used_candidates)

            elif fn_name == "fn_reverse_string":
                match = re.search(r"['\"]([^'\"]+)['\"]", prompt)
                if match:
                    candidates.append(match.group(1))
            elif fn_name == "fn_greet":
                match = re.search(r"greet\s+(\w+)", prompt, re.IGNORECASE)
                if match:
                    candidates.append(match.group(1))
            else:
                all_quoted = re.findall(r"['\"]([^'\"]+)['\"]", prompt)
                candidates.extend([q for q in all_quoted
                                   if q not in used_candidates])

        # Remove duplicates
        seen = set()
        unique = []
        for c in candidates:
            if c not in seen and c not in used_candidates:
                seen.add(c)
                unique.append(c)
        return unique

    def _extract_sub_candidates(
        self,
        prompt: str,
        arg_name: str,
        used_candidates: List[str]
    ) -> List[str]:
        """Estrae candidati per fn_substitute_string_with_regex."""
        candidates = []
        prompt_lower = prompt.lower()

        if arg_name == "source_string":
            # Case 1: "in 'X' with Y" or "in the string 'X' with Y"
            with_match = re.search(r"'\s+with\s+", prompt_lower)
            in_match = re.search(r"in\s+(?:the\s+)?(?:string\s+)?'",
                                 prompt_lower)

            if (in_match and with_match
               and in_match.end() <= with_match.start()):
                start_pos = in_match.end()
                end_pos = with_match.start()
                source_string = prompt[start_pos:end_pos]
                if source_string:
                    candidates.append(source_string)

            # Case 2: "with 'Y' in 'X'" - source_string until end of prompt
            if not candidates:
                mtc = re.search(r"with\s+'[^']+'\s+in\s+'(.+)'(?:\s*$|\s+\w)",
                                prompt, re.IGNORECASE)
                if mtc:
                    candidates.append(mtc.group(1))

            # Case 3: fallback - string after "in '" to the end
            if not candidates:
                match = re.search(r"in\s+'([^']+)'(?:\s*$)",
                                  prompt, re.IGNORECASE)
                if match:
                    candidates.append(match.group(1))

        elif arg_name == "regex":
            # Pattern semantici
            if "digit" in prompt_lower:
                candidates.append(r"\d+")
            if "vowel" in prompt_lower:
                candidates.append("[aeiouAEIOU]")
            if "consonant" in prompt_lower:
                candidates.append("[bcdfghjklmnpqrstvwxyz"
                                  "BCDFGHJKLMNPQRSTVWXYZ]")
            if "space" in prompt_lower or "whitespace" in prompt_lower:
                candidates.append(r"\s+")

            # "word 'X'"
            word_match = re.search(r"(?:the\s+)?word\s+['\"]?(\w+)['\"]?",
                                   prompt, re.IGNORECASE)
            if word_match:
                candidates.append(word_match.group(1))

        elif arg_name == "replacement":
            # Case 1: "with 'X' in" (replacement before source_string)
            match = re.search(r"with\s+'([^']+)'\s+in\s+",
                              prompt, re.IGNORECASE)
            if match:
                candidates.append(match.group(1))

            # Case 2: "with 'X'" to end of prompt
            if not candidates:
                match = re.search(r"with\s+'([^']+)'\s*$",
                                  prompt, re.IGNORECASE)
                if match:
                    candidates.append(match.group(1))

            # Case 3: "with X" (semantic words)
            if not candidates:
                match = re.search(r"with\s+(\w+)\s*$",
                                  prompt, re.IGNORECASE)
                if match:
                    word = match.group(1).lower()
                    semantic_map = {
                        "asterisks": "*",
                        "asterisk": "*",
                        "stars": "*",
                        "star": "*",
                        "underscores": "_",
                        "underscore": "_",
                        "nothing": "",
                        "empty": "",
                        "blank": "",
                        "hyphens": "-",
                        "hyphen": "-",
                    }
                    if word in semantic_map:
                        candidates.append(semantic_map[word])
                    else:
                        candidates.append(match.group(1))
        return [c for c in candidates if c not in used_candidates]

    def _select_candidate(
        self,
        prompt: str,
        fn_name: str,
        arg_name: str,
        arg_type: str,
        candidates: List[str]
    ) -> str:
        """
        constrained decoding to select a candidate.
        """
        if not candidates:
            return ""
        if len(candidates) == 1:
            return candidates[0]

        # Prompt
        selection_prompt = self._build_selection_prompt(prompt, fn_name,
                                                        arg_name,
                                                        arg_type, candidates)
        input_ids = self.tokenizer.encode(selection_prompt,
                                          add_special_tokens=False)

        # Token per candidate
        candidate_matrix = []
        for candidate in candidates:
            tokens = self.tokenizer.encode(str(candidate),
                                           add_special_tokens=False)
            candidate_matrix.append(tokens)

        # Generate with constrained decoding
        generated_ids: List[int] = []
        max_tokens = max(len(t) for t in candidate_matrix) + 5
        for _ in range(max_tokens):
            logits = self.model.get_logits_from_input_ids(input_ids)
            # Allowed tokens
            allowed_ids = self._get_allowed_tokens(generated_ids,
                                                   candidate_matrix)
            if not allowed_ids:
                break
            # Mask not valid digits
            masked_logits = [-math.inf] * len(logits)
            for token_id in allowed_ids:
                if token_id < len(logits):
                    masked_logits[token_id] = float(logits[token_id])
            max_logit = max(masked_logits)
            if max_logit == -math.inf:
                break
            next_token_id = masked_logits.index(max_logit)
            generated_ids.append(next_token_id)
            input_ids.append(next_token_id)
            # match
            is_unique, matched = self._check_unique_match(generated_ids,
                                                          candidate_matrix,
                                                          candidates)
            if is_unique:
                return matched
        return self._find_best_match(generated_ids,
                                     candidate_matrix,
                                     candidates)

    def _build_selection_prompt(
        self,
        user_prompt: str,
        fn_name: str,
        arg_name: str,
        arg_type: str,
        candidates: List[str]
    ) -> str:
        """Prompt for selection."""
        cands = ", ".join(f'"{c}"' for c in candidates[:5])
        return f"""Select "{arg_name}" from: {cands}
                Request: "{user_prompt}"
                Function: {fn_name}
                Answer: """

    def _get_allowed_tokens(
        self,
        generated_ids: List[int],
        candidate_matrix: List[List[int]]
    ) -> List[int]:
        """Token that continue at least one candidate."""
        allowed = set()
        prefix_len = len(generated_ids)
        for tokens in candidate_matrix:
            if len(tokens) > prefix_len:
                if tokens[:prefix_len] == generated_ids:
                    allowed.add(tokens[prefix_len])
        return list(allowed)

    def _check_unique_match(
        self,
        generated_ids: List[int],
        candidate_matrix: List[List[int]],
        candidates: List[str]
    ) -> Tuple[bool, str]:
        """Check for unique match."""
        matches = []

        for i, tokens in enumerate(candidate_matrix):
            if tokens == generated_ids:
                return True, candidates[i]
            if len(tokens) >= len(generated_ids):
                if tokens[:len(generated_ids)] == generated_ids:
                    matches.append(i)
        if len(matches) == 1:
            return True, candidates[matches[0]]
        return False, ""

    def _find_best_match(
        self,
        generated_ids: List[int],
        candidate_matrix: List[List[int]],
        candidates: List[str]
    ) -> str:
        """Find the most similar candidate."""
        best_len = -1
        best = candidates[0] if candidates else ""

        for i, tokens in enumerate(candidate_matrix):
            match_len = 0
            for j, t in enumerate(tokens):
                if j < len(generated_ids) and generated_ids[j] == t:
                    match_len += 1
                else:
                    break
            if match_len > best_len:
                best_len = match_len
                best = candidates[i]
        return best

    def _convert_type(self, value: str, arg_type: str) -> Any:
        """Convert value to the specified type."""
        arg_type = arg_type.lower()
        if "int" in arg_type:
            try:
                return int(float(value))
            except Exception:
                return 0
        elif "float" in arg_type:
            try:
                return float(value)
            except Exception:
                return 0.0
        elif "bool" in arg_type:
            return str(value).lower() == "true"
        return str(value)
