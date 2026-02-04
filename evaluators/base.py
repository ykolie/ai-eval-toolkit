"""Base evaluation classes and interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class EvalResult(BaseModel):
    """Standard evaluation result format."""
    
    score: Union[float, int, bool] = Field(description="Primary evaluation score")
    reasoning: Optional[str] = Field(default=None, description="Explanation of the score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional evaluation data")
    passed: bool = Field(description="Whether the evaluation passed")
    
    @property
    def normalized_score(self) -> float:
        """Return score normalized to 0-1 range."""
        if isinstance(self.score, bool):
            return 1.0 if self.score else 0.0
        if isinstance(self.score, (int, float)):
            return max(0.0, min(1.0, float(self.score)))
        return 0.0


class EvalType(str, Enum):
    """Types of evaluations supported."""
    MATCH = "match"
    INCLUDES = "includes"
    FUZZY_MATCH = "fuzzy_match"
    JSON_MATCH = "json_match"
    MODEL_GRADED = "model_graded"
    CUSTOM = "custom"


class BaseEvaluator(ABC):
    """Abstract base class for all evaluators."""
    
    def __init__(self, name: str, eval_type: EvalType):
        self.name = name
        self.eval_type = eval_type
    
    @abstractmethod
    def evaluate(self, completion: str, expected: Any, **kwargs) -> EvalResult:
        """Evaluate a completion against expected result."""
        pass
    
    def batch_evaluate(self, 
                      completions: List[str], 
                      expected: List[Any], 
                      **kwargs) -> List[EvalResult]:
        """Evaluate multiple completions."""
        if len(completions) != len(expected):
            raise ValueError("Completions and expected must have same length")
        
        return [
            self.evaluate(completion, exp, **kwargs) 
            for completion, exp in zip(completions, expected)
        ]


class EvaluationSuite(BaseModel):
    """A collection of evaluators for comprehensive testing."""
    
    name: str
    description: str
    evaluators: List[BaseEvaluator] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_evaluator(self, evaluator: BaseEvaluator):
        """Add an evaluator to the suite."""
        self.evaluators.append(evaluator)
    
    def run_suite(self, 
                  completion: str, 
                  test_case: Dict[str, Any]) -> Dict[str, EvalResult]:
        """Run all evaluators in the suite."""
        results = {}
        
        for evaluator in self.evaluators:
            try:
                expected = test_case.get(evaluator.name)
                if expected is not None:
                    result = evaluator.evaluate(completion, expected)
                    results[evaluator.name] = result
            except Exception as e:
                results[evaluator.name] = EvalResult(
                    score=0.0,
                    reasoning=f"Evaluation failed: {str(e)}",
                    passed=False,
                    metadata={"error": str(e)}
                )
        
        return results
    
    def aggregate_results(self, results: Dict[str, EvalResult]) -> EvalResult:
        """Aggregate results from multiple evaluators."""
        if not results:
            return EvalResult(score=0.0, passed=False, reasoning="No results to aggregate")
        
        scores = [r.normalized_score for r in results.values()]
        passed_count = sum(1 for r in results.values() if r.passed)
        
        avg_score = sum(scores) / len(scores)
        pass_rate = passed_count / len(results)
        
        return EvalResult(
            score=avg_score,
            passed=pass_rate >= 0.5,  # Majority must pass
            reasoning=f"Average score: {avg_score:.3f}, Pass rate: {pass_rate:.1%}",
            metadata={
                "individual_results": results,
                "pass_rate": pass_rate,
                "total_evaluators": len(results)
            }
        )