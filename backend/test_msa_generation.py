"""
Test script for MSA document generation
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mailmerge import MailMerge
from datetime import datetime
import base64

async def test_msa_generation():
    print("=" * 60)
    print("Testing MSA Document Generation")
    print("=" * 60)
    
    # Template path
    template_path = Path(__file__).parent.parent / "Zuci MSA Template.docx"
    
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return False
    
    print(f"✅ Template found")
    
    # Test data
    test_data = {
        "date": "November 5, 2025",
        "company_name": "Zuci Systems Inc.",
        "customer_company_address": "123 Business Avenue, Suite 500, San Francisco, CA 94102",
        "point_of_contact": "John Smith",
        "customer_company_name": "ABC Corporation",
        "title": "Chief Technology Officer",
        "name": "Jane Doe"
    }
    
    try:
        print(f"\n📄 Opening template...")
        document = MailMerge(str(template_path))
        
        print(f"📝 Merging fields...")
        document.merge(**test_data)
        
        output_path = Path(__file__).parent / "test_output" / "MSA_test.docx"
        output_path.parent.mkdir(exist_ok=True)
        
        print(f"💾 Saving to: {output_path}")
        document.write(str(output_path))
        
        print(f"✅ DOCX generated successfully!")
        
        # Try PDF conversion
        try:
            from docx2pdf import convert
            pdf_path = output_path.with_suffix('.pdf')
            print(f"\n📑 Converting to PDF...")
            convert(str(output_path), str(pdf_path))
            print(f"✅ PDF generated successfully!")
            print(f"   Location: {pdf_path}")
        except Exception as pdf_error:
            print(f"⚠️  PDF conversion failed: {pdf_error}")
            print(f"   Note: This is expected on some systems. DOCX generation still works.")
        
        print(f"\n✨ Test completed successfully!")
        print(f"   DOCX: {output_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_msa_generation())
    print("\n" + "=" * 60)
    if result:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
    print("=" * 60)
