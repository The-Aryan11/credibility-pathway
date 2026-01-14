"""
Lightweight Report Generator (HTML/Text)
Uses 0MB Server RAM - Renders in User's Browser
"""
from datetime import datetime

def generate_report(claim: str, result: dict, sources: list = None) -> str:
    """Generate a printable HTML report"""
    
    score = result.get('score', 50)
    verdict = result.get('verdict', 'UNVERIFIED')
    category = result.get('category', 'OTHER')
    reasoning = result.get('reasoning', 'No reasoning available')
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # HTML Template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Credibility Report - {claim[:20]}</title>
        <style>
            body {{ font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; border-bottom: 2px solid #3b82f6; padding-bottom: 20px; }}
            .box {{ background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #3b82f6; }}
            .score {{ font-size: 24px; font-weight: bold; }}
            h2 {{ color: #1e3a8a; border-bottom: 1px solid #eee; margin-top: 30px; }}
            .source {{ padding: 5px; background: #f1f5f9; margin-bottom: 5px; }}
            .footer {{ margin-top: 50px; font-size: 12px; color: #666; text-align: center; border-top: 1px solid #eee; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Credibility Analysis Report</h1>
            <p>Generated: {date_str}</p>
        </div>

        <div class="section">
            <h2>Claim Analyzed</h2>
            <p><em>"{claim}"</em></p>
        </div>

        <div class="box">
            <div class="score">Score: {score}%</div>
            <p><strong>Verdict:</strong> {verdict} | <strong>Category:</strong> {category}</p>
        </div>

        <div class="section">
            <h2>AI Analysis</h2>
            <p>{reasoning}</p>
        </div>

        <div class="section">
            <h2>Key Evidence</h2>
            <ul>
    """
    
    for e in result.get('key_evidence', []):
        html += f"<li>{e}</li>"
    
    html += """
            </ul>
        </div>
        
        <div class="section">
            <h2>Sources Referenced</h2>
    """
    
    if sources:
        for s in sources:
            name = s.get('source', 'Unknown') if isinstance(s, dict) else str(s)
            html += f'<div class="source">📰 {name}</div>'
    else:
        html += "<p>No specific sources linked.</p>"
        
    html += """
        </div>

        <div class="footer">
            <p>© 2025 Aryan & Khushboo • Powered by Pathway + Groq</p>
            <p>Disclaimer: AI-generated. Verify with official sources.</p>
        </div>
        
        <script>
            // Auto-print when opened
            window.onload = function() { setTimeout(function() { window.print(); }, 500); }
        </script>
    </body>
    </html>
    """
    return html