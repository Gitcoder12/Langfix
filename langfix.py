import os
import sys
import ast
import re
import subprocess
import argparse
import json
import hashlib
from typing import List, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.panel import Panel
from radon.complexity import cc_visit

console = Console()
CACHE_FILE = ".langfix_cache.json"

def load_cache() -> Dict[str, str]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache: Dict[str, str]):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
    except Exception:
        pass

def get_file_hash(file_path: str) -> str:
    hasher = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    except Exception:
        return "error"

def security_scan(code_content: str, ext: str) -> List[str]:
    issues = []
    if re.search(r'(?i)(password|api_key|secret|token|passwd)\s*=\s*["\'][a-zA-Z0-9_\-]+["\']', code_content):
        issues.append("Hardcoded secret/password")
    if re.search(r'(?i)(execute|query)\s*\(\s*["\'](SELECT|INSERT|UPDATE|DELETE)', code_content):
        issues.append("Potential SQL Injection")
    if ext in ['.py', '.php', '.js', '.ts']:
        if re.search(r'\b(eval|exec)\s*\(', code_content):
            issues.append("Dangerous eval()/exec()")
    if ext in ['.js', '.ts']:
        if re.search(r'child_process', code_content):
            issues.append("Node.js child_process execution")
    if ext == '.php':
        if re.search(r'(shell_exec|system|passthru)\s*\(', code_content):
            issues.append("PHP shell execution risk")
    return issues

def check_syntax(file_path: str, ext: str) -> str:
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
        return "OK"
    except FileNotFoundError:
        return "SKIPPED (Compiler not installed)"
    except Exception as e:
        return f"Error: {str(e)}"

def check_complexity(code_content: str, ext: str) -> List[str]:
    notes = []
    if ext == '.py':
        try:
            for block in cc_visit(code_content):
                if block.complexity > 10:
                    notes.append(f"'{block.name}' too complex ({block.complexity})")
        except Exception:
            pass
    return notes

def check_documentation(code_content: str, ext: str) -> Tuple[int, List[str]]:
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
            pass
    return doc_score, notes

def auto_fix(file_path: str, ext: str) -> str:
    try:
        if ext == '.py':
            subprocess.run(["black", "-q", file_path], capture_output=True)
            return "Fixed with black"
        elif ext in ['.js', '.ts']:
            subprocess.run(["npx", "prettier", "--write", file_path], capture_output=True, shell=True)
            return "Fixed with prettier"
        elif ext == '.go':
            subprocess.run(["gofmt", "-w", file_path], capture_output=True)
            return "Fixed with gofmt"
        return "No auto-fixer"
    except Exception:
        return "Auto-fix failed"

def analyze_file(file_path: str) -> Dict[str, Any]:
    ext = os.path.splitext(file_path)[1]
    supported = ['.py', '.js', '.ts', '.php', '.rb', '.go', '.rs', '.c', '.cpp', '.java']
    
    if ext not in supported:
        return {"file": file_path, "score": 100, "vibe": "IGNORED", "note": "Unsupported"}

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code_content = f.read()
    except Exception:
        return {"file": file_path, "score": 0, "vibe": "ERROR", "note": "Could not read"}

    syntax_status = check_syntax(file_path, ext)
    if syntax_status != "OK" and "SKIPPED" not in syntax_status:
        return {"file": file_path, "score": 0, "vibe": "FAIL", "note": f"Syntax Error: {syntax_status}"}

    sec_issues = security_scan(code_content, ext)
    if sec_issues:
        return {"file": file_path, "score": 10, "vibe": "FAIL", "note": f"Security Risk: {', '.join(sec_issues)}"}

    comp_issues = check_complexity(code_content, ext)
    if comp_issues:
        return {"file": file_path, "score": 30, "vibe": "FAIL", "note": f"Performance Risk: {', '.join(comp_issues)}"}

    doc_score, doc_notes = check_documentation(code_content, ext)
    
    format_score = 100
    if ext == '.py':
        try:
            res = subprocess.run(["black", "--check", file_path], capture_output=True, text=True)
            if res.returncode != 0:
                format_score = 50
                doc_notes.append("Needs formatting")
        except FileNotFoundError:
            pass

    final_score = int((format_score + doc_score) / 2)
    vibe = "AWESOME" if final_score == 100 else "GOOD" if final_score >= 70 else "POOR" if final_score >= 40 else "FAIL"
    note = "Perfect code." if final_score == 100 else f"Issues: {', '.join(doc_notes)}"

    return {"file": file_path, "score": final_score, "vibe": vibe, "note": note}

def generate_sarif(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    sarif_results = []
    for res in results:
        if res["score"] < 50:
            sarif_results.append({
                "ruleId": "LANGFIX-ISSUE",
                "level": "error",
                "message": {"text": f"LangFix Score: {res['score']}/100. {res['note']}"},
                "locations": [{"physicalLocation": {"artifactLocation": {"uri": res["file"].replace("\\", "/")}}}]
            })
            
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{
            "tool": {"driver": {"name": "LangFix", "version": "1.3.0", "informationUri": "https://github.com/Gitcoder12/Langfix"}},
            "results": sarif_results
        }]
    }

def process_single_file(filepath: str, fix: bool) -> Dict[str, Any]:
    ext = os.path.splitext(filepath)[1]
    if fix:
        auto_fix(filepath, ext)
    return analyze_file(filepath)

def main():
    parser = argparse.ArgumentParser(description="LangFix - Polyglot Static Analysis Engine")
    parser.add_argument("directory", help="Directory to analyze")
    parser.add_argument("--fix", action="store_true", help="Auto-fix formatting issues")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--sarif", action="store_true", help="Output SARIF for GitHub Security")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent threads")
    args = parser.parse_args()

    target_dir = args.directory
    if not os.path.isdir(target_dir):
        console.print(f"[bold red]Error:[/bold red] '{target_dir}' is not a directory.")
        sys.exit(1)

    if not args.json and not args.sarif:
        console.print(f"\n[bold cyan]🔍 LangFix v1.3.0 | Analyzing {target_dir} (Threads: {args.workers})...[/bold cyan]\n")

    cache = load_cache() if not args.fix else {}
    new_cache = {}
    files_to_scan = []
    
    ignore_dirs = [".git", "venv", "__pycache__", "node_modules", ".github"]
    ignore_files = ["langfix.py", "test_langfix.py"]

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file in ignore_files: continue
            filepath = os.path.join(root, file)
            ext = os.path.splitext(file)[1]
            
            if ext in ['.py', '.js', '.ts', '.php', '.rb', '.go', '.rs', '.c', '.cpp', '.java']:
                file_hash = get_file_hash(filepath)
                new_cache[filepath] = file_hash
                
                if filepath in cache and cache[filepath] == file_hash and not args.fix:
                    if not args.json and not args.sarif:
                        console.print(f"[dim]⏩ Skipping {filepath} (Cached)[/dim]")
                    continue
                files_to_scan.append(filepath)

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(process_single_file, f, args.fix) for f in files_to_scan]
        for future in futures:
            results.append(future.result())

    total_score = sum(r["score"] for r in results)
    file_count = len(results)
    avg_score = (total_score // file_count) if file_count > 0 else 0
    project_vibe = "FAIL" if avg_score < 40 else "POOR" if avg_score < 70 else "GOOD" if avg_score < 100 else "AWESOME"

    if args.sarif:
        sarif_data = generate_sarif(results)
        with open("langfix.sarif", "w") as f:
            json.dump(sarif_data, f, indent=2)
        if not args.json:
            console.print("[bold green]✅ SARIF report saved to langfix.sarif[/bold green]")
            
    elif args.json:
        print(json.dumps({"average_score": avg_score, "vibe": project_vibe, "files": results}, indent=2))
        
    elif file_count > 0:
        for result in results:
            color = "green" if result["vibe"] == "AWESOME" else "red" if result["vibe"] == "FAIL" else "blue" if result["vibe"] == "GOOD" else "yellow"
            console.print(f"[bold]{result['file']}[/bold]")
            console.print(f"  - Score: [{color}]{result['score']}/100 ({result['vibe']})[/{color}]")
            console.print(f"  - Note: {result['note']}\n")

        project_color = "red" if avg_score < 40 else "yellow" if avg_score < 70 else "blue" if avg_score < 100 else "green"
        panel = Panel(f"Project Average: [{project_color}]{avg_score}/100 ({project_vibe})[/{project_color}]", title="🏁 Final Vibe Check", expand=False)
        console.print(panel)

    save_cache(new_cache)

if __name__ == "__main__":
    main()
