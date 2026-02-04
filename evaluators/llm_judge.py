"""LLM-as-a-Judge evaluators using LLMs to assess LLM outputs."""

import os
from typing import Any, Dict, List, Optional
from openai import OpenAI
from anthropic import Anthropic
import json
from .base import BaseEvaluator, EvalResult, EvalType


class ModelGradedEvaluator(BaseEvaluator):
    """Base class for model-graded evaluations."""
    
    def __init__(self, model: str = "gpt-4", provider: str = "openai"):
        super().__init__("model_graded", EvalType.MODEL_GRADED)
        self.model = model
        self.provider = provider
        
        if provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif provider == "anthropic":
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _call_model(self, prompt: str) -> str:
        """Call the appropriate model based on provider."""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
    
    def evaluate(self, completion: str, expected: Any, **kwargs) -> EvalResult:
        """Override in subclasses."""
        raise NotImplementedError


class CriteriaEvaluator(ModelGradedEvaluator):
    """Evaluate based on multiple criteria with detailed scoring."""
    
    def __init__(self, criteria: Dict[str, str], model: str = "gpt-4", provider: str = "openai"):
        super().__init__(model, provider)
        self.criteria = criteria
    
    def evaluate(self, completion: str, expected: Any = None, **kwargs) -> EvalResult:
        """Evaluate completion against multiple criteria."""
        
        criteria_list = "\n".join([f"- {name}: {description}" for name, description in self.criteria.items()])
        
        prompt = f"""You are evaluating an AI model's response against specific criteria.

RESPONSE TO EVALUATE:
{completion}

EVALUATION CRITERIA:
{criteria_list}

For each criterion, provide a score from 1-5 where:
1 = Poor (criterion not met)
2 = Below average (partially meets criterion)
3 = Average (adequately meets criterion)
4 = Good (exceeds criterion)
5 = Excellent (far exceeds criterion)

Respond with a JSON object containing:
- "scores": {{criterion_name: score, ...}}
- "overall_score": average of all scores
- "reasoning": detailed explanation for each score
- "summary": brief overall assessment

Example:
{{
  "scores": {{"accuracy": 4, "clarity": 3}},
  "overall_score": 3.5,
  "reasoning": "Accuracy: Well-researched facts. Clarity: Could be more concise.",
  "summary": "Good response with minor clarity issues."
}}"""

        try:
            response = self._call_model(prompt)
            result_data = json.loads(response)
            
            overall_score = result_data.get("overall_score", 0) / 5.0  # Normalize to 0-1
            passed = overall_score >= 0.6  # 3/5 or better
            
            return EvalResult(
                score=overall_score,
                passed=passed,
                reasoning=result_data.get("summary", "No summary provided"),
                metadata={
                    "detailed_scores": result_data.get("scores", {}),
                    "detailed_reasoning": result_data.get("reasoning", ""),
                    "criteria": self.criteria,
                    "model_used": f"{self.provider}:{self.model}"
                }
            )
            
        except Exception as e:
            return EvalResult(
                score=0.0,
                passed=False,
                reasoning=f"Model evaluation failed: {str(e)}",
                metadata={"error": str(e)}
            )


class FactualConsistencyEvaluator(ModelGradedEvaluator):
    """Evaluate factual accuracy and consistency."""
    
    def evaluate(self, completion: str, reference: str, **kwargs) -> EvalResult:
        """Evaluate factual consistency against reference."""
        
        prompt = f"""You are evaluating whether a response is factually consistent with a reference text.

REFERENCE TEXT:
{reference}

RESPONSE TO EVALUATE:
{completion}

Evaluate the response for:
1. Factual accuracy (no contradictions with reference)
2. Completeness (covers key points from reference)
3. No hallucinations (no facts not in reference)

Respond with JSON:
{{
  "accuracy_score": 1-5,
  "completeness_score": 1-5,
  "hallucination_score": 1-5,
  "overall_score": 1-5,
  "issues": ["list", "of", "specific", "issues"],
  "reasoning": "detailed explanation"
}}

Score meanings:
1 = Major issues, 2 = Some issues, 3 = Adequate, 4 = Good, 5 = Excellent"""

        try:
            response = self._call_model(prompt)
            result_data = json.loads(response)
            
            overall_score = result_data.get("overall_score", 0) / 5.0
            passed = overall_score >= 0.6 and len(result_data.get("issues", [])) <= 1
            
            return EvalResult(
                score=overall_score,
                passed=passed,
                reasoning=result_data.get("reasoning", "No reasoning provided"),
                metadata={
                    "accuracy_score": result_data.get("accuracy_score"),
                    "completeness_score": result_data.get("completeness_score"),
                    "hallucination_score": result_data.get("hallucination_score"),
                    "identified_issues": result_data.get("issues", []),
                    "reference_text": reference
                }
            )
            
        except Exception as e:
            return EvalResult(
                score=0.0,
                passed=False,
                reasoning=f"Factual consistency evaluation failed: {str(e)}",
                metadata={"error": str(e)}
            )


class ChainOfThoughtEvaluator(ModelGradedEvaluator):
    """Evaluate reasoning quality and chain-of-thought."""
    
    def evaluate(self, completion: str, expected: Any = None, **kwargs) -> EvalResult:
        """Evaluate reasoning quality in the response."""
        
        prompt = f"""You are evaluating the quality of reasoning in an AI response.

RESPONSE TO EVALUATE:
{completion}

Evaluate the reasoning for:
1. Logic (steps follow logically)
2. Clarity (reasoning is clear and understandable)
3. Completeness (all necessary steps included)
4. Accuracy (reasoning leads to correct conclusion)

Respond with JSON:
{{
  "logic_score": 1-5,
  "clarity_score": 1-5,
  "completeness_score": 1-5,
  "accuracy_score": 1-5,
  "overall_score": 1-5,
  "strengths": ["list", "of", "strengths"],
  "weaknesses": ["list", "of", "weaknesses"],
  "reasoning": "detailed analysis"
}}"""

        try:
            response = self._call_model(prompt)
            result_data = json.loads(response)
            
            overall_score = result_data.get("overall_score", 0) / 5.0
            passed = overall_score >= 0.6
            
            return EvalResult(
                score=overall_score,
                passed=passed,
                reasoning=result_data.get("reasoning", "No reasoning provided"),
                metadata={
                    "logic_score": result_data.get("logic_score"),
                    "clarity_score": result_data.get("clarity_score"),
                    "completeness_score": result_data.get("completeness_score"),
                    "accuracy_score": result_data.get("accuracy_score"),
                    "strengths": result_data.get("strengths", []),
                    "weaknesses": result_data.get("weaknesses", [])
                }
            )
            
        except Exception as e:
            return EvalResult(
                score=0.0,
                passed=False,
                reasoning=f"Chain-of-thought evaluation failed: {str(e)}",
                metadata={"error": str(e)}
            )


class HeadToHeadEvaluator(ModelGradedEvaluator):
    """Compare two responses head-to-head."""
    
    def evaluate(self, completion: str, alternative: str, **kwargs) -> EvalResult:
        """Compare two responses and determine which is better."""
        
        criteria = kwargs.get("criteria", "overall quality")
        
        prompt = f"""You are comparing two AI responses to determine which is better.

RESPONSE A:
{completion}

RESPONSE B:
{alternative}

Compare based on: {criteria}

Respond with JSON:
{{
  "winner": "A" or "B" or "Tie",
  "confidence": 1-5,
  "reasoning": "detailed explanation of why one is better",
  "response_a_score": 1-5,
  "response_b_score": 1-5
}}"""

        try:
            response = self._call_model(prompt)
            result_data = json.loads(response)
            
            winner = result_data.get("winner", "Tie")
            a_score = result_data.get("response_a_score", 3)
            confidence = result_data.get("confidence", 1) / 5.0
            
            if winner == "A":
                score = 1.0
                passed = True
            elif winner == "B":
                score = 0.0
                passed = False
            else:  # Tie
                score = 0.5
                passed = abs(a_score - result_data.get("response_b_score", 3)) <= 1
            
            return EvalResult(
                score=score,
                passed=passed,
                reasoning=result_data.get("reasoning", "No reasoning provided"),
                metadata={
                    "winner": winner,
                    "confidence": confidence,
                    "response_a_score": a_score,
                    "response_b_score": result_data.get("response_b_score"),
                    "alternative_response": alternative,
                    "comparison_criteria": criteria
                }
            )
            
        except Exception as e:
            return EvalResult(
                score=0.0,
                passed=False,
                reasoning=f"Head-to-head evaluation failed: {str(e)}",
                metadata={"error": str(e)}
            )