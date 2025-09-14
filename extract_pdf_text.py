"""
Extract text from the Indian Digital Personal Data Protection Act PDF
"""
import pdfplumber
import os

def extract_text_from_pdf(pdf_path, output_path):
    """
    Extract text from PDF and save to a text file
    """
    text_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)
    
    # Save to text file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text_content))
    
    print(f"Extracted text saved to {output_path}")
    return output_path

if __name__ == "__main__":
    pdf_path = "/Users/vasanthadithya/SIH 2025/Sovereign's Edict/data/indian_digital_privacy_act_2023_official.pdf"
    output_path = "/Users/vasanthadithya/SIH 2025/Sovereign's Edict/data/indian_digital_privacy_act_2023.txt"
    
    if os.path.exists(pdf_path):
        extract_text_from_pdf(pdf_path, output_path)
    else:
        print(f"PDF file not found: {pdf_path}")