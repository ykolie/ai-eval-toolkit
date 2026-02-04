#!/usr/bin/env python3
"""
LLM-as-a-Judge Evaluation Example

This example demonstrates how to use LLMs to evaluate other LLM outputs
across different dimensions like factual accuracy, reasoning quality,
and comparative assessment.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluators.llm_judge import (
    CriteriaEvaluator,
    FactualConsistencyEvaluator,
    ChainOfThoughtEvaluator,
    HeadToHeadEvaluator
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSON

console = Console()


def demo_criteria_evaluator():
    """Demonstrate multi-criteria evaluation."""
    console.print("\n[bold blue]1. Criteria-Based Evaluation[/bold blue]")
    
    # Define evaluation criteria
    criteria = {
        "accuracy": "Information provided is factually correct",
        "clarity": "Response is clear and easy to understand",
        "completeness": "Response fully addresses the question",
        "helpfulness": "Response is practical and useful"
    }
    
    evaluator = CriteriaEvaluator(criteria=criteria, model="gpt-4")
    
    # Test responses
    responses = [
        "The capital of France is Paris. It's located in northern France and has been the country's capital since 1790. Paris is known for landmarks like the Eiffel Tower and Louvre Museum.",
        
        "Paris is the capital. Big city with tower.",
        
        "The capital of France is London, which is famous for its beautiful architecture and rich history dating back centuries."
    ]
    
    console.print(Panel("Evaluating responses about France's capital", style="cyan"))
    
    for i, response in enumerate(responses, 1):
        console.print(f"\n[bold yellow]Response {i}:[/bold yellow] {response}")
        
        try:
            result = evaluator.evaluate(response)
            
            table = Table(title=f"Evaluation Results - Response {i}")
            table.add_column("Criterion", style="cyan")
            table.add_column("Score", style="yellow")
            
            for criterion, score in result.metadata["detailed_scores"].items():
                table.add_row(criterion.title(), f"{score}/5")
            
            table.add_row("[bold]Overall[/bold]", f"[bold]{result.score:.2f}[/bold]")
            
            console.print(table)
            console.print(f"[green]Reasoning:[/green] {result.reasoning}")
            console.print(f"[red]Passed:[/red] {'✓' if result.passed else '✗'}")
            
        except Exception as e:
            console.print(f"[red]Error evaluating response {i}: {e}[/red]")
            console.print("[yellow]Make sure you have OPENAI_API_KEY set in your environment[/yellow]")


def demo_factual_consistency():
    """Demonstrate factual consistency evaluation."""
    console.print("\n[bold blue]2. Factual Consistency Evaluation[/bold blue]")
    
    evaluator = FactualConsistencyEvaluator(model="gpt-4")
    
    # Reference text
    reference = """
    Python is a high-level programming language created by Guido van Rossum 
    and first released in 1991. It emphasizes code readability and uses 
    significant whitespace. Python supports multiple programming paradigms 
    including procedural, object-oriented, and functional programming.
    """
    
    # Test responses for consistency
    test_responses = [
        "Python was created by Guido van Rossum in 1991. It's known for readable code and supports object-oriented programming.",
        
        "Python is a programming language from 1995 invented by John Smith. It uses brackets for code structure.",
        
        "Python emphasizes readability and was first released in 1991. It supports functional and object-oriented paradigms."
    ]
    
    console.print(Panel("Reference Text", style="green"))
    console.print(reference.strip())
    
    for i, response in enumerate(test_responses, 1):
        console.print(f"\n[bold yellow]Response {i}:[/bold yellow] {response}")
        
        try:
            result = evaluator.evaluate(response, reference)
            
            table = Table(title=f"Factual Consistency - Response {i}")
            table.add_column("Metric", style="cyan")
            table.add_column("Score", style="yellow")
            
            table.add_row("Accuracy", f"{result.metadata.get('accuracy_score', 'N/A')}/5")
            table.add_row("Completeness", f"{result.metadata.get('completeness_score', 'N/A')}/5")
            table.add_row("No Hallucinations", f"{result.metadata.get('hallucination_score', 'N/A')}/5")
            table.add_row("[bold]Overall[/bold]", f"[bold]{result.score:.2f}[/bold]")
            
            console.print(table)
            
            issues = result.metadata.get("identified_issues", [])
            if issues:
                console.print(f"[red]Issues identified:[/red] {', '.join(issues)}")
            
            console.print(f"[green]Reasoning:[/green] {result.reasoning}")
            console.print(f"[red]Passed:[/red] {'✓' if result.passed else '✗'}")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def demo_chain_of_thought():
    """Demonstrate reasoning quality evaluation."""
    console.print("\n[bold blue]3. Chain-of-Thought Evaluation[/bold blue]")
    
    evaluator = ChainOfThoughtEvaluator(model="gpt-4")
    
    # Test reasoning responses
    reasoning_responses = [
        """To solve 2x + 5 = 11:
        Step 1: Subtract 5 from both sides: 2x = 6
        Step 2: Divide both sides by 2: x = 3
        Step 3: Check: 2(3) + 5 = 6 + 5 = 11 ✓
        Therefore, x = 3.""",
        
        "x = 3 because that's the answer.",
        
        """Let me work through this equation:
        2x + 5 = 11
        First, I'll isolate the term with x by subtracting 5:
        2x = 11 - 5 = 6
        Then divide by the coefficient of x:
        x = 6 ÷ 2 = 3"""
    ]
    
    for i, response in enumerate(reasoning_responses, 1):
        console.print(f"\n[bold yellow]Reasoning Response {i}:[/bold yellow]")
        console.print(Panel(response, style="white"))
        
        try:
            result = evaluator.evaluate(response)
            
            table = Table(title=f"Reasoning Quality - Response {i}")
            table.add_column("Aspect", style="cyan")
            table.add_column("Score", style="yellow")
            
            table.add_row("Logic", f"{result.metadata.get('logic_score', 'N/A')}/5")
            table.add_row("Clarity", f"{result.metadata.get('clarity_score', 'N/A')}/5")
            table.add_row("Completeness", f"{result.metadata.get('completeness_score', 'N/A')}/5")
            table.add_row("Accuracy", f"{result.metadata.get('accuracy_score', 'N/A')}/5")
            table.add_row("[bold]Overall[/bold]", f"[bold]{result.score:.2f}[/bold]")
            
            console.print(table)
            
            strengths = result.metadata.get("strengths", [])
            weaknesses = result.metadata.get("weaknesses", [])
            
            if strengths:
                console.print(f"[green]Strengths:[/green] {', '.join(strengths)}")
            if weaknesses:
                console.print(f"[red]Weaknesses:[/red] {', '.join(weaknesses)}")
            
            console.print(f"[blue]Overall Assessment:[/blue] {result.reasoning}")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def demo_head_to_head():
    """Demonstrate head-to-head comparison."""
    console.print("\n[bold blue]4. Head-to-Head Comparison[/bold blue]")
    
    evaluator = HeadToHeadEvaluator(model="gpt-4")
    
    # Compare two responses
    response_a = """Climate change is caused by increased greenhouse gas emissions, 
    primarily from burning fossil fuels. This leads to global warming, rising sea levels, 
    and extreme weather events. Solutions include renewable energy, energy efficiency, 
    and carbon capture technologies."""
    
    response_b = """Climate change happens because of gases in the air. It makes the 
    Earth hot and causes bad weather. We can fix it by using solar panels and wind."""
    
    console.print(Panel("Response A", style="cyan"))
    console.print(response_a)
    
    console.print(Panel("Response B", style="magenta"))
    console.print(response_b)
    
    try:
        result = evaluator.evaluate(
            response_a, 
            response_b, 
            criteria="scientific accuracy and comprehensiveness"
        )
        
        table = Table(title="Head-to-Head Comparison Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Winner", result.metadata.get("winner", "Unknown"))
        table.add_row("Confidence", f"{result.metadata.get('confidence', 0):.1f}/5")
        table.add_row("Response A Score", f"{result.metadata.get('response_a_score', 'N/A')}/5")
        table.add_row("Response B Score", f"{result.metadata.get('response_b_score', 'N/A')}/5")
        table.add_row("Overall Score", f"{result.score:.2f}")
        
        console.print(table)
        console.print(f"[green]Reasoning:[/green] {result.reasoning}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def main():
    """Run all LLM-as-a-judge evaluation demos."""
    console.print(Panel.fit(
        "[bold green]AI Evaluation Toolkit - LLM-as-a-Judge Evaluators Demo[/bold green]",
        border_style="green"
    ))
    
    # Check for API keys
    if not os.getenv("your_key_here"):
        console.print(Panel(
            "[red]Warning: OPENAI_API_KEY not found in environment variables.\n"
            "Set your API key to run model-graded evaluations:\n"
            "export OPENAI_API_KEY='your-key-here'[/red]",
            style="red"
        ))
        return
    
    console.print("[green]Running LLM-as-a-judge evaluation demos...[/green]")
    
    demo_criteria_evaluator()
    demo_factual_consistency()
    demo_chain_of_thought()
    demo_head_to_head()
    
    console.print("\n[bold green]LLM-as-a-judge evaluation demo completed![/bold green]")
    console.print("[yellow]Note: These evaluations use GPT-4 and require API credits.[/yellow]")


if __name__ == "__main__":
    main()