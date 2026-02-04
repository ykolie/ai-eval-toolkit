"""Basic template evaluators for common matching patterns."""

import json
import re
from typing import Any, List, Union
from fuzzywuzzy import fuzz
from .base import BaseEvaluator, EvalResult, EvalType


class MatchEvaluator(BaseEvaluator):
    """Exact string matching evaluator."""
    
    def __init__(self, case_sensitive: bool = False):
        super().__init__("match", EvalType.MATCH)
        self.case_sensitive = case_sensitive
    
    def evaluate(self, completion: str, expected: str, **kwargs) -> EvalResult:
        """Evaluate exact string match."""
        if not self.case_sensitive:
            completion = completion.lower().strip()
            expected = expected.lower().strip()
        else:
            completion = completion.strip()
            expected = expected.strip()
        
        passed = completion == expected
        
        return EvalResult(
            score=1.0 if passed else 0.0,
            passed=passed,
            reasoning=f"Expected '{expected}', got '{completion}'" if not passed else "Exact match",
            metadata={
                "case_sensitive": self.case_sensitive,
                "expected_length": len(expected),
                "completion_length": len(completion)
            }
        )


class IncludesEvaluator(BaseEvaluator):
    """Substring matching evaluator."""
    
    def __init__(self, case_sensitive: bool = False):
        super().__init__("includes", EvalType.INCLUDES)
        self.case_sensitive = case_sensitive
    
    def evaluate(self, completion: str, expected: Union[str, List[str]], **kwargs) -> EvalResult:
        """Evaluate substring inclusion."""
        if isinstance(expected, str):
            expected = [expected]
        
        completion_text = completion if self.case_sensitive else completion.lower()
        found_items = []
        
        for item in expected:
            search_item = item if self.case_sensitive else item.lower()
            if search_item in completion_text:
                found_items.append(item)
        
        score = len(found_items) / len(expected)
        passed = score == 1.0
        
        return EvalResult(
            score=score,
            passed=passed,
            reasoning=f"Found {len(found_items)}/{len(expected)} required items: {found_items}",
            metadata={
                "expected_items": expected,
                "found_items": found_items,
                "missing_items": [item for item in expected if item not in found_items]
            }
        )


class FuzzyMatchEvaluator(BaseEvaluator):
    """Fuzzy string matching evaluator using Levenshtein distance."""
    
    def __init__(self, threshold: float = 80.0):
        super().__init__("fuzzy_match", EvalType.FUZZY_MATCH)
        self.threshold = threshold
    
    def evaluate(self, completion: str, expected: str, **kwargs) -> EvalResult:
        """Evaluate fuzzy string similarity."""
        similarity = fuzz.ratio(completion.strip(), expected.strip())
        passed = similarity >= self.threshold
        
        return EvalResult(
            score=similarity / 100.0,
            passed=passed,
            reasoning=f"Similarity: {similarity}% (threshold: {self.threshold}%)",
            metadata={
                "similarity_score": similarity,
                "threshold": self.threshold,
                "partial_ratio": fuzz.partial_ratio(completion, expected),
                "token_sort_ratio": fuzz.token_sort_ratio(completion, expected)
            }
        )


class JSONMatchEvaluator(BaseEvaluator):
    """JSON structure and value matching evaluator."""
    
    def __init__(self, exact_match: bool = False, required_keys: List[str] = None):
        super().__init__("json_match", EvalType.JSON_MATCH)
        self.exact_match = exact_match
        self.required_keys = required_keys or []
    
    def evaluate(self, completion: str, expected: Union[str, dict], **kwargs) -> EvalResult:
        """Evaluate JSON structure and content."""
        try:
            # Parse completion JSON
            completion_data = json.loads(completion)
        except json.JSONDecodeError as e:
            return EvalResult(
                score=0.0,
                passed=False,
                reasoning=f"Invalid JSON in completion: {str(e)}",
                metadata={"parse_error": str(e)}
            )
        
        try:
            # Parse expected JSON if it's a string
            if isinstance(expected, str):
                expected_data = json.loads(expected)
            else:
                expected_data = expected
        except json.JSONDecodeError as e:
            return EvalResult(
                score=0.0,
                passed=False,
                reasoning=f"Invalid JSON in expected: {str(e)}",
                metadata={"expected_parse_error": str(e)}
            )
        
        # Check required keys
        missing_keys = []
        for key in self.required_keys:
            if key not in completion_data:
                missing_keys.append(key)
        
        if self.exact_match:
            # Exact match comparison
            passed = completion_data == expected_data and len(missing_keys) == 0
            score = 1.0 if passed else 0.0
            reasoning = "Exact JSON match" if passed else "JSON structures differ"
        else:
            # Partial match scoring
            total_keys = len(expected_data) + len(self.required_keys)
            if total_keys == 0:
                score = 1.0
            else:
                matching_keys = 0
                for key, value in expected_data.items():
                    if key in completion_data and completion_data[key] == value:
                        matching_keys += 1
                
                required_keys_present = len(self.required_keys) - len(missing_keys)
                score = (matching_keys + required_keys_present) / total_keys
            
            passed = score >= 0.8 and len(missing_keys) == 0
            reasoning = f"JSON similarity: {score:.1%}, Missing keys: {missing_keys}"
        
        return EvalResult(
            score=score,
            passed=passed,
            reasoning=reasoning,
            metadata={
                "completion_keys": list(completion_data.keys()),
                "expected_keys": list(expected_data.keys()),
                "missing_required_keys": missing_keys,
                "exact_match": self.exact_match
            }
        )


class RegexEvaluator(BaseEvaluator):
    """Regular expression pattern matching evaluator."""
    
    def __init__(self, pattern: str, flags: int = 0):
        super().__init__("regex", EvalType.CUSTOM)
        self.pattern = pattern
        self.regex = re.compile(pattern, flags)
    
    def evaluate(self, completion: str, expected: Any = None, **kwargs) -> EvalResult:
        """Evaluate regex pattern match."""
        match = self.regex.search(completion)
        passed = match is not None
        
        reasoning = f"Pattern '{self.pattern}' {'found' if passed else 'not found'}"
        metadata = {"pattern": self.pattern}
        
        if match:
            metadata.update({
                "match_start": match.start(),
                "match_end": match.end(),
                "matched_text": match.group(),
                "groups": match.groups()
            })
        
        return EvalResult(
            score=1.0 if passed else 0.0,
            passed=passed,
            reasoning=reasoning,
            metadata=metadata
        )