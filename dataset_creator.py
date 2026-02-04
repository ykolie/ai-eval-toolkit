#!/usr/bin/env python3
"""
Dataset Creator Tool

Create evaluation datasets from various sources including:
- Manual entry with templates
- CSV/JSON import
- AI-generated test cases
- Domain-specific generators
"""

import json
import csv
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
import typer

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

console = Console()
app = typer.Typer(help="Create and manage evaluation datasets")


class DatasetCreator:
    """Create and manage evaluation datasets."""
    
    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = Path(datasets_dir)
        self.datasets_dir.mkdir(exist_ok=True)
    
    def create_empty_dataset(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create an empty dataset structure."""
        return {
            "name": name,
            "description": description,
            "version": "1.0",
            "created_by": "AI Evaluation Toolkit",
            "eval_type": "custom",
            "test_cases": [],
            "metadata": {
                "total_cases": 0,
                "categories": [],
                "difficulty_levels": []
            }
        }
    
    def add_test_case(self, 
                     dataset: Dict[str, Any], 
                     input_text: str,
                     expected: Any,
                     category: str = "general",
                     difficulty: str = "medium",
                     metadata: Dict[str, Any] = None) -> None:
        """Add a test case to the dataset."""
        
        test_case = {
            "id": len(dataset["test_cases"]) + 1,
            "input": input_text,
            "expected": expected,
            "category": category,
            "difficulty": difficulty,
            "metadata": metadata or {}
        }
        
        dataset["test_cases"].append(test_case)
        dataset["metadata"]["total_cases"] = len(dataset["test_cases"])
        
        # Update categories and difficulty levels
        if category not in dataset["metadata"]["categories"]:
            dataset["metadata"]["categories"].append(category)
        
        if difficulty not in dataset["metadata"]["difficulty_levels"]:
            dataset["metadata"]["difficulty_levels"].append(difficulty)
    
    def save_dataset(self, dataset: Dict[str, Any], filename: str = None) -> Path:
        """Save dataset to file."""
        if filename is None:
            filename = f"{dataset['name'].lower().replace(' ', '_')}.json"
        
        filepath = self.datasets_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        return filepath
    
    def load_dataset(self, filepath: str) -> Dict[str, Any]:
        """Load dataset from file."""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def import_from_csv(self, csv_file: str, input_col: str, expected_col: str) -> Dict[str, Any]:
        """Import dataset from CSV file."""
        dataset = self.create_empty_dataset(
            name=f"Imported from {Path(csv_file).stem}",
            description=f"Dataset imported from {csv_file}"
        )
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.add_test_case(
                    dataset,
                    input_text=row[input_col],
                    expected=row[expected_col],
                    category=row.get('category', 'imported'),
                    difficulty=row.get('difficulty', 'medium')
                )
        
        return dataset


def create_security_dataset():
    """Create a sample security compliance dataset."""
    creator = DatasetCreator()
    
    dataset = creator.create_empty_dataset(
        name="Security Compliance Evaluation",
        description="Test cases for evaluating security policy compliance analysis"
    )
    
    # Sample security test cases
    test_cases = [
        {
            "input": "Our application stores user passwords in plaintext in the database for easier debugging.",
            "expected": {
                "compliant": False,
                "violations": ["password_storage", "sensitive_data_protection"],
                "severity": "critical",
                "recommendation": "Hash passwords using bcrypt or similar"
            },
            "category": "password_security",
            "difficulty": "easy"
        },
        {
            "input": "We implement HTTPS for all external APIs but use HTTP for internal microservice communication within our VPC.",
            "expected": {
                "compliant": False,
                "violations": ["encryption_in_transit"],
                "severity": "medium",
                "recommendation": "Use TLS for all communication, including internal services"
            },
            "category": "encryption",
            "difficulty": "medium"
        },
        {
            "input": "Our access control system requires multi-factor authentication for all administrative accounts and uses role-based permissions.",
            "expected": {
                "compliant": True,
                "violations": [],
                "severity": "none",
                "recommendation": "Continue current practices"
            },
            "category": "access_control",
            "difficulty": "easy"
        },
        {
            "input": "Database backups are encrypted at rest and stored in a separate geographic region. Access logs are maintained for all backup operations.",
            "expected": {
                "compliant": True,
                "violations": [],
                "severity": "none",
                "recommendation": "Excellent backup security practices"
            },
            "category": "data_protection",
            "difficulty": "medium"
        }
    ]
    
    for case in test_cases:
        creator.add_test_case(
            dataset,
            input_text=case["input"],
            expected=case["expected"],
            category=case["category"],
            difficulty=case["difficulty"]
        )
    
    filepath = creator.save_dataset(dataset, "security_compliance.json")
    console.print(f"[green]Created security compliance dataset: {filepath}[/green]")
    
    return filepath


def create_reasoning_dataset():
    """Create a sample reasoning evaluation dataset."""
    creator = DatasetCreator()
    
    dataset = creator.create_empty_dataset(
        name="Mathematical Reasoning",
        description="Test cases for evaluating step-by-step mathematical reasoning"
    )
    
    test_cases = [
        {
            "input": "Solve for x: 3x + 7 = 22",
            "expected": {
                "answer": "x = 5",
                "steps": [
                    "3x + 7 = 22",
                    "3x = 22 - 7",
                    "3x = 15", 
                    "x = 15 ÷ 3",
                    "x = 5"
                ],
                "verification": "3(5) + 7 = 15 + 7 = 22 ✓"
            },
            "category": "linear_equations",
            "difficulty": "easy"
        },
        {
            "input": "A train travels 240 miles in 3 hours. If it continues at the same speed, how long will it take to travel 400 miles?",
            "expected": {
                "answer": "5 hours",
                "steps": [
                    "Speed = Distance ÷ Time = 240 ÷ 3 = 80 mph",
                    "Time = Distance ÷ Speed = 400 ÷ 80 = 5 hours"
                ],
                "verification": "80 mph × 5 hours = 400 miles ✓"
            },
            "category": "word_problems",
            "difficulty": "medium"
        },
        {
            "input": "Find the compound interest on $1000 at 5% annual rate for 2 years, compounded annually.",
            "expected": {
                "answer": "$102.50",
                "steps": [
                    "A = P(1 + r)^t",
                    "A = 1000(1 + 0.05)^2",
                    "A = 1000(1.05)^2",
                    "A = 1000(1.1025)",
                    "A = $1102.50",
                    "Interest = $1102.50 - $1000 = $102.50"
                ],
                "verification": "Principal grows to $1102.50, earning $102.50 interest"
            },
            "category": "finance",
            "difficulty": "hard"
        }
    ]
    
    for case in test_cases:
        creator.add_test_case(
            dataset,
            input_text=case["input"],
            expected=case["expected"],
            category=case["category"],
            difficulty=case["difficulty"]
        )
    
    filepath = creator.save_dataset(dataset, "mathematical_reasoning.json")
    console.print(f"[green]Created reasoning dataset: {filepath}[/green]")
    
    return filepath


@app.command()
def create_interactive():
    """Create a dataset interactively."""
    console.print(Panel.fit("[bold green]Interactive Dataset Creator[/bold green]"))
    
    # Get basic info
    name = Prompt.ask("Dataset name")
    description = Prompt.ask("Description", default="")
    eval_type = Prompt.ask("Evaluation type", choices=["match", "includes", "fuzzy", "json", "model_graded", "custom"], default="custom")
    
    creator = DatasetCreator()
    dataset = creator.create_empty_dataset(name, description)
    dataset["eval_type"] = eval_type
    
    # Add test cases
    while True:
        console.print("\n[bold blue]Add Test Case[/bold blue]")
        
        input_text = Prompt.ask("Input text")
        
        if eval_type == "json":
            console.print("Enter expected JSON (one line):")
            expected = Prompt.ask("Expected")
            try:
                expected = json.loads(expected)
            except:
                console.print("[red]Invalid JSON, storing as string[/red]")
        else:
            expected = Prompt.ask("Expected output")
        
        category = Prompt.ask("Category", default="general")
        difficulty = Prompt.ask("Difficulty", choices=["easy", "medium", "hard"], default="medium")
        
        creator.add_test_case(dataset, input_text, expected, category, difficulty)
        
        if not Confirm.ask("Add another test case?"):
            break
    
    # Save dataset
    filename = Prompt.ask("Filename", default=f"{name.lower().replace(' ', '_')}.json")
    filepath = creator.save_dataset(dataset, filename)
    
    console.print(f"\n[green]Dataset saved to: {filepath}[/green]")
    console.print(f"[blue]Total test cases: {len(dataset['test_cases'])}[/blue]")


@app.command()
def create_samples():
    """Create sample datasets for demonstration."""
    console.print("[blue]Creating sample datasets...[/blue]")
    
    security_path = create_security_dataset()
    reasoning_path = create_reasoning_dataset()
    
    console.print(f"\n[green]Sample datasets created:[/green]")
    console.print(f"• Security Compliance: {security_path}")
    console.print(f"• Mathematical Reasoning: {reasoning_path}")


@app.command()
def import_csv(
    csv_file: str,
    input_col: str = "input",
    expected_col: str = "expected",
    output: str = None
):
    """Import dataset from CSV file."""
    
    if not os.path.exists(csv_file):
        console.print(f"[red]File not found: {csv_file}[/red]")
        return
    
    creator = DatasetCreator()
    
    try:
        dataset = creator.import_from_csv(csv_file, input_col, expected_col)
        
        if output is None:
            output = f"{Path(csv_file).stem}_dataset.json"
        
        filepath = creator.save_dataset(dataset, output)
        
        console.print(f"[green]Successfully imported {len(dataset['test_cases'])} test cases[/green]")
        console.print(f"[green]Dataset saved to: {filepath}[/green]")
        
    except Exception as e:
        console.print(f"[red]Import failed: {e}[/red]")


@app.command()
def list_datasets():
    """List all available datasets."""
    datasets_dir = Path("datasets")
    
    if not datasets_dir.exists():
        console.print("[yellow]No datasets directory found[/yellow]")
        return
    
    json_files = list(datasets_dir.glob("*.json"))
    
    if not json_files:
        console.print("[yellow]No datasets found[/yellow]")
        return
    
    table = Table(title="Available Datasets")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Cases", style="yellow")
    table.add_column("Categories", style="green")
    
    creator = DatasetCreator()
    
    for filepath in json_files:
        try:
            dataset = creator.load_dataset(filepath)
            categories = ", ".join(dataset.get("metadata", {}).get("categories", []))
            
            table.add_row(
                dataset.get("name", filepath.stem),
                dataset.get("description", "")[:50] + "...",
                str(len(dataset.get("test_cases", []))),
                categories[:30] + "..." if len(categories) > 30 else categories
            )
        except Exception as e:
            table.add_row(
                filepath.stem,
                f"[red]Error loading: {e}[/red]",
                "?",
                "?"
            )
    
    console.print(table)


@app.command()
def validate_dataset(filepath: str):
    """Validate a dataset file."""
    creator = DatasetCreator()
    
    try:
        dataset = creator.load_dataset(filepath)
        
        # Basic validation
        required_fields = ["name", "test_cases"]
        missing_fields = [field for field in required_fields if field not in dataset]
        
        if missing_fields:
            console.print(f"[red]Missing required fields: {missing_fields}[/red]")
            return False
        
        # Test case validation
        test_cases = dataset["test_cases"]
        issues = []
        
        for i, case in enumerate(test_cases):
            if "input" not in case:
                issues.append(f"Test case {i+1}: missing 'input' field")
            if "expected" not in case:
                issues.append(f"Test case {i+1}: missing 'expected' field")
        
        if issues:
            console.print("[red]Validation issues found:[/red]")
            for issue in issues:
                console.print(f"  • {issue}")
            return False
        
        console.print("[green]Dataset validation passed![/green]")
        console.print(f"  • {len(test_cases)} test cases")
        console.print(f"  • Categories: {', '.join(dataset.get('metadata', {}).get('categories', []))}")
        
        return True
        
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        return False


if __name__ == "__main__":
    app()