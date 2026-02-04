#!/usr/bin/env python3
"""
Basic Evaluation Example

This example demonstrates how to use basic template evaluators
for common evaluation tasks like exact matching, fuzzy matching,
and JSON validation.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluators.basic import (
    MatchEvaluator, 
    IncludesEvaluator, 
    FuzzyMatchEvaluator, 
    JSONMatchEvaluator,
    RegexEvaluator
)
from evaluators.base import EvaluationSuite
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def demo_match_evaluator():
    """Demonstrate exact match evaluation."""
    console.print("\n[bold blue]1. Exact Match Evaluator[/bold blue]")
    
    evaluator = MatchEvaluator(case_sensitive=False)
    
    test_cases = [
        ("The capital of France is Paris", "the capital of france is paris"),
        ("42", "42"),
        ("Hello World", "Hello Universe"),
    ]
    
    table = Table(title="Match Evaluator Results")
    table.add_column("Completion", style="cyan")
    table.add_column("Expected", style="green")
    table.add_column("Score", style="yellow")
    table.add_column("Passed", style="red")
    
    for completion, expected in test_cases:
        result = evaluator.evaluate(completion, expected)
        table.add_row(
            completion[:30] + "..." if len(completion) > 30 else completion,
            expected[:30] + "..." if len(expected) > 30 else expected,
            f"{result.score:.1f}",
            "✓" if result.passed else "✗"
        )
    
    console.print(table)


def demo_includes_evaluator():
    """Demonstrate substring inclusion evaluation."""
    console.print("\n[bold blue]2. Includes Evaluator[/bold blue]")
    
    evaluator = IncludesEvaluator(case_sensitive=False)
    
    test_cases = [
        ("The quick brown fox jumps over the lazy dog", ["fox", "dog"]),
        ("Python is a great programming language", ["python", "java"]),
        ("AI evaluation frameworks are essential", ["evaluation", "framework", "testing"]),
    ]
    
    table = Table(title="Includes Evaluator Results")
    table.add_column("Completion", style="cyan")
    table.add_column("Required Items", style="green")
    table.add_column("Score", style="yellow")
    table.add_column("Found", style="magenta")
    
    for completion, required in test_cases:
        result = evaluator.evaluate(completion, required)
        found_items = result.metadata.get("found_items", [])
        table.add_row(
            completion[:40] + "..." if len(completion) > 40 else completion,
            str(required),
            f"{result.score:.1f}",
            str(found_items)
        )
    
    console.print(table)


def demo_fuzzy_evaluator():
    """Demonstrate fuzzy string matching."""
    console.print("\n[bold blue]3. Fuzzy Match Evaluator[/bold blue]")
    
    evaluator = FuzzyMatchEvaluator(threshold=75.0)
    
    test_cases = [
        ("The cat sat on the mat", "The cat sits on the mat"),
        ("Machine learning is awesome", "Machine Learning is awesome!"),
        ("Hello world", "Goodbye universe"),
    ]
    
    table = Table(title="Fuzzy Match Results")
    table.add_column("Completion", style="cyan")
    table.add_column("Expected", style="green")
    table.add_column("Similarity", style="yellow")
    table.add_column("Passed", style="red")
    
    for completion, expected in test_cases:
        result = evaluator.evaluate(completion, expected)
        similarity = result.metadata.get("similarity_score", 0)
        table.add_row(
            completion,
            expected,
            f"{similarity}%",
            "✓" if result.passed else "✗"
        )
    
    console.print(table)


def demo_json_evaluator():
    """Demonstrate JSON structure validation."""
    console.print("\n[bold blue]4. JSON Match Evaluator[/bold blue]")
    
    evaluator = JSONMatchEvaluator(exact_match=False, required_keys=["name", "age"])
    
    test_cases = [
        ('{"name": "John", "age": 30, "city": "NYC"}', {"name": "John", "age": 30}),
        ('{"name": "Alice"}', {"name": "Alice", "age": 25}),
        ('{"invalid": "json"', {"name": "Bob", "age": 35}),
        ('{"name": "Charlie", "age": 40}', {"name": "Charlie", "age": 40}),
    ]
    
    table = Table(title="JSON Evaluator Results")
    table.add_column("Completion", style="cyan")
    table.add_column("Expected", style="green")
    table.add_column("Score", style="yellow")
    table.add_column("Issues", style="red")
    
    for completion, expected in test_cases:
        result = evaluator.evaluate(completion, expected)
        issues = result.metadata.get("missing_required_keys", [])
        if "error" in result.metadata:
            issues.append("Parse error")
        
        table.add_row(
            completion[:30] + "..." if len(completion) > 30 else completion,
            str(expected),
            f"{result.score:.2f}",
            str(issues) if issues else "None"
        )
    
    console.print(table)


def demo_regex_evaluator():
    """Demonstrate regex pattern matching."""
    console.print("\n[bold blue]5. Regex Evaluator[/bold blue]")
    
    # Email pattern evaluator
    email_evaluator = RegexEvaluator(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    test_cases = [
        "Contact me at john.doe@example.com for more info",
        "My email is invalid-email-format",
        "Send reports to admin@company.org and backup@company.org",
        "No email addresses in this text",
    ]
    
    table = Table(title="Email Pattern Detection")
    table.add_column("Text", style="cyan")
    table.add_column("Email Found", style="yellow")
    table.add_column("Matched Text", style="green")
    
    for text in test_cases:
        result = email_evaluator.evaluate(text)
        matched_text = result.metadata.get("matched_text", "None")
        table.add_row(
            text[:50] + "..." if len(text) > 50 else text,
            "✓" if result.passed else "✗",
            matched_text
        )
    
    console.print(table)


def demo_evaluation_suite():
    """Demonstrate using multiple evaluators together."""
    console.print("\n[bold blue]6. Evaluation Suite Demo[/bold blue]")
    
    # Create a suite for evaluating a Q&A response
    suite = EvaluationSuite(
        name="QA Response Evaluation",
        description="Comprehensive evaluation of question-answering responses"
    )
    
    # Add evaluators
    suite.add_evaluator(IncludesEvaluator())
    suite.add_evaluator(FuzzyMatchEvaluator(threshold=70))
    suite.add_evaluator(RegexEvaluator(r'\d+'))  # Should contain numbers
    
    # Test case
    completion = "The population of Tokyo is approximately 14 million people as of 2023."
    test_case = {
        "includes": ["Tokyo", "population", "million"],
        "fuzzy_match": "Tokyo has about 14 million residents in 2023",
        "regex": True  # Should find numbers
    }
    
    # Run suite
    results = suite.run_suite(completion, test_case)
    aggregate = suite.aggregate_results(results)
    
    # Display results
    table = Table(title="Suite Evaluation Results")
    table.add_column("Evaluator", style="cyan")
    table.add_column("Score", style="yellow")
    table.add_column("Passed", style="green")
    table.add_column("Reasoning", style="white")
    
    for name, result in results.items():
        table.add_row(
            name,
            f"{result.score:.2f}",
            "✓" if result.passed else "✗",
            result.reasoning[:50] + "..." if len(result.reasoning) > 50 else result.reasoning
        )
    
    # Add aggregate row
    table.add_row(
        "[bold]AGGREGATE[/bold]",
        f"[bold]{aggregate.score:.2f}[/bold]",
        f"[bold]{'✓' if aggregate.passed else '✗'}[/bold]",
        f"[bold]{aggregate.reasoning}[/bold]"
    )
    
    console.print(table)


def main():
    """Run all evaluation demos."""
    console.print(Panel.fit(
        "[bold green]AI Evaluation Toolkit - Basic Evaluators Demo[/bold green]",
        border_style="green"
    ))
    
    demo_match_evaluator()
    demo_includes_evaluator()
    demo_fuzzy_evaluator()
    demo_json_evaluator()
    demo_regex_evaluator()
    demo_evaluation_suite()
    
    console.print("\n[bold green]Demo completed! Try modifying the test cases to see how evaluators respond.[/bold green]")


if __name__ == "__main__":
    main()