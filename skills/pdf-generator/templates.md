# Document Templates

## Invoice

```python
from weasyprint import HTML, CSS

def generate_invoice(data):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ display: flex; justify-content: space-between; }}
            .company {{ font-size: 24px; font-weight: bold; }}
            .invoice-title {{ font-size: 32px; color: #333; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f5f5f5; }}
            .total {{ font-size: 18px; font-weight: bold; text-align: right; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="company">{data['company']['name']}</div>
            <div class="invoice-title">INVOICE</div>
        </div>
        
        <p><strong>Invoice #:</strong> {data['invoice']['number']}</p>
        <p><strong>Date:</strong> {data['invoice']['date']}</p>
        <p><strong>Due:</strong> {data['invoice']['due_date']}</p>
        
        <h3>Bill To:</h3>
        <p>{data['client']['name']}<br>{data['client']['address']}</p>
        
        <table>
            <tr><th>Description</th><th>Qty</th><th>Rate</th><th>Amount</th></tr>
            {''.join(f"<tr><td>{item['desc']}</td><td>{item['qty']}</td><td>${item['rate']}</td><td>${item['qty'] * item['rate']}</td></tr>" for item in data['items'])}
        </table>
        
        <p class="total">Total: ${sum(item['qty'] * item['rate'] for item in data['items'])}</p>
    </body>
    </html>
    """
    HTML(string=html).write_pdf(f"invoice-{data['invoice']['number']}.pdf")

# Usage
invoice_data = {
    "company": {"name": "Acme Inc"},
    "client": {"name": "Client Corp", "address": "123 Main St"},
    "invoice": {"number": "INV-001", "date": "2025-02-19", "due_date": "2025-03-19"},
    "items": [
        {"desc": "Consulting", "qty": 10, "rate": 150},
        {"desc": "Development", "qty": 20, "rate": 200},
    ]
}
generate_invoice(invoice_data)
```

## Report

```python
from weasyprint import HTML

def generate_report(title, sections):
    toc = "".join(f'<li><a href="#section-{i}">{s["title"]}</a></li>' 
                  for i, s in enumerate(sections))
    
    content = "".join(f'''
        <section id="section-{i}">
            <h2>{s["title"]}</h2>
            <p>{s["content"]}</p>
        </section>
    ''' for i, s in enumerate(sections))
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 2cm; }}
            body {{ font-family: Georgia, serif; line-height: 1.6; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
            h2 {{ color: #34495e; page-break-after: avoid; }}
            section {{ page-break-inside: avoid; }}
            .toc {{ background: #f9f9f9; padding: 20px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="toc">
            <h3>Table of Contents</h3>
            <ol>{toc}</ol>
        </div>
        {content}
    </body>
    </html>
    """
    HTML(string=html).write_pdf("report.pdf")
```

## Contract / Legal Document

```python
from weasyprint import HTML

def generate_contract(data):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ 
                size: letter; 
                margin: 1in;
                @bottom-center {{ content: "Page " counter(page) " of " counter(pages); }}
            }}
            body {{ font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.8; }}
            h1 {{ text-align: center; text-transform: uppercase; }}
            .parties {{ margin: 30px 0; }}
            .clause {{ margin: 20px 0; }}
            .clause-title {{ font-weight: bold; }}
            .signatures {{ margin-top: 50px; display: flex; justify-content: space-between; }}
            .signature-block {{ width: 45%; }}
            .signature-line {{ border-top: 1px solid black; margin-top: 50px; padding-top: 5px; }}
        </style>
    </head>
    <body>
        <h1>{data['title']}</h1>
        
        <div class="parties">
            <p>This Agreement is entered into as of {data['date']} by and between:</p>
            <p><strong>{data['party1']['name']}</strong> ("{data['party1']['short']}"), and</p>
            <p><strong>{data['party2']['name']}</strong> ("{data['party2']['short']}")</p>
        </div>
        
        {''.join(f'<div class="clause"><span class="clause-title">{i+1}. {c["title"]}.</span> {c["text"]}</div>' for i, c in enumerate(data['clauses']))}
        
        <div class="signatures">
            <div class="signature-block">
                <div class="signature-line">{data['party1']['name']}</div>
                <p>Date: _______________</p>
            </div>
            <div class="signature-block">
                <div class="signature-line">{data['party2']['name']}</div>
                <p>Date: _______________</p>
            </div>
        </div>
    </body>
    </html>
    """
    HTML(string=html).write_pdf("contract.pdf")
```

## Certificate

```python
from weasyprint import HTML

def generate_certificate(name, title, date, issuer):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: landscape; margin: 0; }}
            body {{ 
                font-family: 'Georgia', serif;
                text-align: center;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 50px;
                min-height: 100vh;
                box-sizing: border-box;
            }}
            .certificate {{ 
                border: 8px double #4a5568;
                padding: 60px;
                background: white;
                max-width: 900px;
                margin: 0 auto;
            }}
            .header {{ font-size: 14px; letter-spacing: 3px; color: #718096; }}
            .title {{ font-size: 48px; color: #2d3748; margin: 30px 0; }}
            .recipient {{ font-size: 36px; color: #4a5568; font-style: italic; margin: 30px 0; }}
            .description {{ font-size: 18px; color: #4a5568; margin: 30px 0; }}
            .footer {{ margin-top: 50px; display: flex; justify-content: space-around; }}
            .signature {{ border-top: 2px solid #4a5568; padding-top: 10px; width: 200px; }}
        </style>
    </head>
    <body>
        <div class="certificate">
            <div class="header">CERTIFICATE OF COMPLETION</div>
            <div class="title">{title}</div>
            <p>This is to certify that</p>
            <div class="recipient">{name}</div>
            <div class="description">has successfully completed the requirements</div>
            <div class="footer">
                <div class="signature">{issuer}</div>
                <div class="signature">{date}</div>
            </div>
        </div>
    </body>
    </html>
    """
    HTML(string=html).write_pdf("certificate.pdf")
```

## Resume / CV

```python
from weasyprint import HTML

def generate_resume(data):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: letter; margin: 0.5in; }}
            body {{ font-family: 'Helvetica', sans-serif; font-size: 10pt; line-height: 1.4; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .name {{ font-size: 24pt; font-weight: bold; }}
            .contact {{ color: #666; }}
            h2 {{ color: #2c3e50; border-bottom: 1px solid #3498db; font-size: 12pt; margin-top: 15px; }}
            .entry {{ margin: 10px 0; }}
            .entry-header {{ display: flex; justify-content: space-between; }}
            .title {{ font-weight: bold; }}
            .date {{ color: #666; }}
            ul {{ margin: 5px 0; padding-left: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="name">{data['name']}</div>
            <div class="contact">{data['email']} | {data['phone']} | {data['location']}</div>
        </div>
        
        <h2>Experience</h2>
        {''.join(f'''
        <div class="entry">
            <div class="entry-header">
                <span class="title">{exp['title']} - {exp['company']}</span>
                <span class="date">{exp['dates']}</span>
            </div>
            <ul>{''.join(f"<li>{b}</li>" for b in exp['bullets'])}</ul>
        </div>
        ''' for exp in data['experience'])}
        
        <h2>Education</h2>
        {''.join(f'''
        <div class="entry">
            <div class="entry-header">
                <span class="title">{edu['degree']} - {edu['school']}</span>
                <span class="date">{edu['year']}</span>
            </div>
        </div>
        ''' for edu in data['education'])}
        
        <h2>Skills</h2>
        <p>{', '.join(data['skills'])}</p>
    </body>
    </html>
    """
    HTML(string=html).write_pdf("resume.pdf")
```
