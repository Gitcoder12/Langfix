import os
import sys
import ast
import re
import subprocess
from typing import List, Tuple, Dict
from rich.console import Console
from rich.panel import Panel
from radon.complexity import cc_visit

# Initialize Rich console
console = Console()

# ==========================================
# 1. SECURITY SCANNER
# ==========================================
def security_scan(code_content: str) -> List[str]:
    """Scans for common security vulnerabilities using regex."""
    issues = []
    
    # Hardcoded secrets
    if re.search(r'(?i)(password|api_key|secret|token|passwd)\s*=\s*["\'][a-zA-Z0-9_\-]+["\']', code_content):
        issues.append("Hardcoded secret/password")
        
    # Dangerous execution functions
    if re.search(r'\b(eval|exec)\s*\(', code_content):
        issues.append("Dangerous eval()/exec()")
        
    # Raw SQL queries
    if re.search(r'(?i)(execute|query)\s*\(\s*["\'](SELECT|INSERT|UPDATE|DELETE)', code_content):
        issues.append("Potential SQL Injection")
        
    return issues

# ==========================================
# 2. DOCUMENTATION CHECKER
# ==========================================
def check_documentation(code_content: str, ext: str) -> Tuple[int, List[str]]:
    """Checks if functions/classes have docstrings or comments."""
    doc_score = 100
    notes = []

    if ext == '.py':
        try:
            tree = ast.parse(code_content)
            missing_docs, total_defs = 0, 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    total_defs += 1
                    if not ast.get_docstring(node):
                        missing_docs += 1
            if total_defs > 0 and missing_docs > 0:
                doc_score = max(0, 100 - int((missing_docs / total_defs) * 100))
                notes.append(f"{missing_docs}/{total_defs} missing docstrings")
        except Exception:
            pass # Handled by syntax checker

    elif ext in ['.js', '.ts', '.go', '.rs', '.java', '.c', '.cpp', '.rb', '.php']:
        lines = code_content.split('\n')
        missing_comments, total_funcs = 0, 0
        for i, line in enumerate(lines):
            if re.search(r'^\s*(def|class|function|pub fn|fn|public|private|protected|void|int|char|float)\s+\w+', line):
                total_funcs += 1
                if i > 0 and not re.search(r'^\s*(//|/\*|\*|#|--)', lines[i-1]):
                    missing_comments += 1
        
        if total_funcs > 0 and missing_comments > 0:
            doc_score = max(0, 100 - int((missing_comments / total_funcs) * 100))
            notes.append(f"{missing_comments}/{total_funcs} funcs lack comments")

    return doc_score, notes

# ==========================================
# 3. POLYGLOT SYNTAX CHECKER
# ==========================================
def check_syntax(file_path: str, ext: str) -> str:
    """Uses native compilers/interpreters to check for syntax errors."""
    try:
        if ext == '.py':
            with open(file_path, "r", encoding="utf-8") as f:
                ast.parse(f.read())
        elif ext in ['.js', '.ts']:
            res = subprocess.run(["node", "--check", file_path], capture_output=True, text=True)
            if res.returncode != 0: return res.stderr.split('\n')[0]
        elif ext == '.php':
            res = subprocess.run(["php", "-l", file_path], capture_output=True, text=True)
            if res.returncode != 0: return res.stdout
        elif ext == '.rb':
            res = subprocess.run(["ruby", "-c", file_path], capture_output=True, text=True)
            if res.returncode != 0: return res.stderr
        elif ext == '.go':
            res = subprocess.run(["gofmt", "-e", file_path], capture_output=True, text=True)
            if res.returncode != 0: return res.stderr
        elif ext == '.rs':
            res = subprocess.run(["rustc", "--emit=metadata", file_path, "-o", "NUL" if os.name == 'nt' else "/dev/null"], capture_output=True, text=True)
            if res.returncode != 0: return res.stderr.split('\n')[0]
        elif ext in ['.c', '.cpp']:
            compiler = "gcc" if ext == '.c' else "g++"
            res = subprocess.run([compiler, "-fsyntax-only", file_path], capture_output=True, text=True)
            if res.returncode != 0: return res.stderr.split('\n')[0]
        return "OK"
    except FileNotFoundError:
        return "SKIPPED (Compiler not installed)"
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 4. PERFORMANCE & COMPLEXITY CHECK
# ==========================================
def check_complexity(code_content: str, ext: str) -> List[str]:
    """Checks for overly complex code (spaghetti code)."""
    notes = []
    if ext == '.py':
        try:
            for block in cc_visit(code_content):
                if block.complexity > 10:
                    notes.append(f"'{block.name}' too complex ({block.complexity})")
        except Exception:
            pass
    return notes

# ==========================================
# 5. ANALYZE FILE (The Brain)
# ==========================================
def analyze_file(file_path: str) -> Tuple[int, str, str]:
    """Orchestrates all checks and calculates the final score."""
    ext = os.path.splitext(file_path)[1]
    supported = ['.py', '.js', '.ts', '.php', '.rb', '.go', '.rs', '.c', '.cpp', '.java']
    
    if ext not in supported:
        return 100, "IGNORED", "Unsupported language"

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code_content = f.read()
    except Exception:
        return 0, "ERROR", "Could not read file"

    # 1. Syntax
    syntax_status = check_syntax(file_path, ext)
    if syntax_status != "OK" and "SKIPPED" not in syntax_status:
        return 0, "COOKED", f"Syntax Error: {syntax_status}"

    # 2. Security
    if (sec_issues := security_scan(code_content)):
        return 10, "COOKED", f"Security Risk: {', '.join(sec_issues)}"

    # 3. Complexity
    if (comp_issues := check_complexity(code_content, ext)):
        return 30, "COOKED", f"Performance Risk: {', '.join(comp_issues)}"

    # 4. Documentation
    doc_score, doc_notes = check_documentation(code_content, ext)
    
    # 5. Formatting (Python only)
    format_score = 100
    if ext == '.py':
        try:
            res = subprocess.run(["black", "--check", file_path], capture_output=True, text=True)
            if res.returncode != 0:
                format_score = 50
                doc_notes.append("Needs formatting (black)")
        except FileNotFoundError:
            doc_notes.append("Black not installed")

    # Final Calculation
    final_score = int((format_score + doc_score) / 2)
    if final_score == 100:
        return 100, "AWESOME", "Perfect code."
    elif final_score >= 70:
        return final_score, "GOOD", f"Minor issues: {', '.join(doc_notes)}"
    else:
        return final_score, "COOKED", f"Needs work: {', '.join(doc_notes)}"

# ==========================================
# 6. MAIN CLI
# ==========================================
def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/bold red] python langfix.py <directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a directory.")
        sys.exit(1)

    console.print(f"\n[bold cyan]🔍 LangFix v1.0.0 | Analyzing {target_dir}...[/bold cyan]\n")

    total_score, file_count = 0, 0

    for root, _, files in os.walk(target_dir):
        for file in files:
            filepath = os.path.join(root, file)
            ext = os.path.splitext(file)[1]
            
            if ext in ['.py', '.js', '.ts', '.php', '.rb', '.go', '.rs', '.c', '.cpp', '.java']:
                score, vibe, note = analyze_file(filepath)
                total_score += score
                file_count += 1

                color = "green" if vibe == "AWESOME" else "red" if vibe == "COOKED" else "blue" if vibe == "GOOD" else "yellow"
                icon = "🏆" if vibe == "AWESOME" else "❌" if vibe == "COOKED" else "👍" if vibe == "GOOD" else "⚠️"

                console.print(f"[bold]{filepath}[/bold]")
                console.print(f"  - Score: [{color}]{score}/100 ({vibe})[/{color}] {icon}")
                console.print(f"  - Note: {note}\n")

    if file_count > 0:
        avg_score = total_score // file_count
        project_vibe = "COOKED" if avg_score < 70 else ("AWESOME" if avg_score == 100 else "GOOD")
        project_color = "red" if avg_score < 70 else ("green" if avg_score == 100 else "blue")
        
        panel = Panel(
            f"Project Average: [{project_color}]{avg_score}/100 ({project_vibe})[/{project_color}]",
            title="🏁 Final Vibe Check",
            expand=False
        )
        console.print(panel)
    else:
        console.print("[yellow]No supported files found.[/yellow]")

if __name__ == "__main__":
    main()
