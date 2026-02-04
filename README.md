# AI Evaluation Toolkit
A practical toolkit for building and running custom AI evaluations - from basic template matching to model-graded assessments.

# Overview
This toolkit provides battle-tested evaluation methods for measuring LLM performance across different tasks. Whether you're building domain-specific benchmarks or need rigorous model comparisons, these tools help you create reproducible, meaningful evaluations.

# Quick Start
# Install dependencies
pip install -r requirements.txt

# Run a basic evaluation
python examples/basic_eval.py

# Run LLM-as-a-judge evaluation
python examples/llm_judge_eval.py

# Generate evaluation report
python tools/generate_report.py results/

# Evaluation Types

1. Basic Template Evals
* Match: Exact string matching
* Includes: Substring matching
* FuzzyMatch: Approximate string matching
* JSONMatch: Structured data validation

2. LLM-as-a-Judge Evals
* Criteria-based: Multi-dimensional scoring
* Head-to-head: Comparative evaluation
* Chain-of-thought: Reasoning transparency
* Factual consistency: Truth verification

3. Custom Domain Evals
* Security compliance: Policy adherence
* Code quality: Static analysis integration
* Reasoning: Multi-step problem solving
* Safety: Harmful content detection

📚 Key Concepts
LLM-as-a-Judge
Uses one LLM to evaluate the outputs of another LLM. This approach scales beyond human evaluation while maintaining quality assessment. The judge LLM receives the original prompt, the response to evaluate, and scoring criteria, then provides structured feedback and numerical scores.

📊 Example Results
Security Compliance Evaluation Results:
┌─────────────────┬─────────┬──────────┬─────────┐
│ Model           │ Accuracy│ Precision│ Recall  │
├─────────────────┼─────────┼──────────┼─────────┤
│ gpt-4           │   94.2% │    92.1% │   96.3% │
│ claude-3-sonnet │   91.8% │    89.7% │   94.1% │
│ gpt-3.5-turbo   │   87.3% │    85.2% │   89.4% │
└─────────────────┴─────────┴──────────┴─────────┘

