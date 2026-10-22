import os
import sys
import random
from rich.console import Console
from rich.panel import Panel

console = Console()

def analyze_file(file_path):
    # This is a mock analyzer for v0.1
    ext = os.path.splitext(file_path)[1]
    
    # Simulate finding issues based on the file extension
    if ext == '.py':
        score = random.randint(40, 100)
        vibe = "COOKED" if score < 70 else "AWESOME"
        return score, vibe, "Formatting fixed by Black"
    elif ext == '.js':
        score = random.randint(40, 100)
        vibe = "COOKED" if score < 70 else "AWESOME"
        return score, vibe, "Missing semicolons added"
    elif ext == '.php':
        score = 50 # NSA bug related
        vibe = "VULNERABLE"
        return score, vibe, "Outdated PHP version detected"
    else:
        return 100, "IGNORED", "Unsupported language"

def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage:[/bold red] python langfix.py <directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    
    if not os.path.isdir(target_dir):
        console.print(f"[bold red]Error:[/bold red] Directory '{target_dir}' not found.")
        sys.exit(1)

    console.print(f"\n[bold cyan]🔍 Analyzing {target_dir}...[/bold cyan]\n")

    total_score = 0
    file_count = 0

    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.py', '.js', '.php', '.go', '.rb')):
                filepath = os.path.join(root, file)
                score, vibe, note = analyze_file(filepath)
                
                total_score += score
                file_count += 1

                # Styling based on vibe
                if vibe == "AWESOME":
                    color = "green"
                    icon = "🏆"
                elif vibe == "COOKED":
                    color = "red"
                    icon = "❌"
                else:
                    color = "yellow"
                    icon = "⚠️"

                console.print(f"[bold]{filepath}[/bold]")
                console.print(f"  - Score: [{color}]{score}/100 ({vibe})[/{color}] {icon}")
                console.print(f"  - Note: {note}\n")

    if file_count > 0:
        avg_score = total_score // file_count
        project_vibe = "COOKED" if avg_score < 70 else "AWESOME"
        project_color = "red" if avg_score < 70 else "green"
        
        panel = Panel(
            f"Project Average: [{project_color}]{avg_score}/100 ({project_vibe})[/{project_color}]",
            title="🏁 Final Vibe Check",
            expand=False
        )
        console.print(panel)
    else:
        console.print("[yellow]No supported files found to analyze.[/yellow]")

if __name__ == "__main__":
    main()
