import os
from typing import List, Tuple
from src.models.blueprint import Blueprint
from src.solver.diamond_solver import DiamondSolver

class FileRepository:
    """
    Handles file storage and persistence operations.
    Conforms to SRP by separating database/file access from domain business rules.
    """
    @staticmethod
    def read_text_file(filepath: str) -> str:
        resolved_path = filepath
        if not os.path.exists(resolved_path):
            alt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", filepath))
            if os.path.exists(alt_path):
                resolved_path = alt_path
            else:
                raise FileNotFoundError(f"Blueprint file '{filepath}' not found.")
        try:
            with open(resolved_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            raise ValueError(f"Failed to read blueprint file '{resolved_path}': {str(e)}")

    @staticmethod
    def write_text_file(content: str, filepath: str) -> None:
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            raise ValueError(f"Failed to write file '{filepath}': {str(e)}")


class ReportFormatter:
    """
    Handles presentation layer formatting rules for analyzer outputs.
    Conforms to SRP by isolating formatting structures.
    """
    @staticmethod
    def format_evaluation_report(results: List[Tuple[int, int]], best_bp_id: int) -> str:
        report_lines = [f"Blueprint {bp_id}: {quality}" for bp_id, quality in results]
        return "\n".join(report_lines) + f"\n\nBest blueprint is the blueprint {best_bp_id}.\n"


class BlueprintAnalyzer:
    """
    Facade class maintaining the public static methods API contract for backwards compatibility.
    Internally delegates parsing and evaluations, resolving SOLID concerns.
    """
    @staticmethod
    def read_blueprint_file(filepath: str) -> str:
        return FileRepository.read_text_file(filepath)

    @staticmethod
    def parse_blueprints(content: str) -> List[Blueprint]:
        """Parses blueprints from the file content. Raises ValueError if malformed."""
        if not content:
            raise ValueError("The blueprint file is empty.")
        
        blueprints = []
        for i, line in enumerate(content.splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                blueprints.append(Blueprint.parse(line))
            except ValueError as e:
                raise ValueError(f"Error parsing blueprint line {i + 1}: {str(e)}")
        
        if not blueprints:
            raise ValueError("No valid blueprints found in the content.")
        
        return blueprints

    @staticmethod
    def evaluate_blueprints(blueprints: List[Blueprint], time_limit: int = 24) -> Tuple[List[Tuple[int, int]], int]:
        if not blueprints:
            raise ValueError("No blueprints to evaluate.")

        results = []
        best_bp_id = None
        max_quality = -1
        
        for bp in blueprints:
            max_diamonds = DiamondSolver(bp, time_limit).solve()
            quality = bp.id * max_diamonds
            results.append((bp.id, quality))
            if quality > max_quality:
                max_quality = quality
                best_bp_id = bp.id
                
        if best_bp_id is None:
             raise ValueError("Blueprint evaluation did not identify a best blueprint.")
             
        return results, best_bp_id

    @staticmethod
    def generate_report(results: List[Tuple[int, int]], best_bp_id: int) -> str:
        """Formats the textual report from the evaluation results."""
        return ReportFormatter.format_evaluation_report(results, best_bp_id)

    @staticmethod
    def save_and_print_report(report_content: str, output_path: str = "analysis.txt") -> None:
        """Saves the report to a file and prints it to stdout."""
        print(report_content, end="", flush=True)
        FileRepository.write_text_file(report_content, output_path)
