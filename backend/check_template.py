"""
Script to check MSA template merge fields
Run this to verify your template has the correct merge fields
"""

from pathlib import Path
from mailmerge import MailMerge

def check_template():
    template_path = Path(__file__).parent.parent / "Zuci MSA Template.docx"
    
    if not template_path.exists():
        print(f"❌ Template not found at: {template_path}")
        print("Please ensure 'Zuci MSA Template.docx' is in the project root directory")
        return False
    
    print(f"✅ Template found at: {template_path}")
    
    try:
        document = MailMerge(str(template_path))
        merge_fields = document.get_merge_fields()
        
        print(f"\n📋 Merge fields found in template: {len(merge_fields)}")
        for field in sorted(merge_fields):
            print(f"   - {field}")
        
        # Expected fields for MSA
        expected_fields = {
            'date',
            'company_name',
            'customer_company_address',
            'point_of_contact',
            'customer_company_name',
            'title',
            'name'
        }
        
        print(f"\n🎯 Expected fields for MSA form:")
        for field in sorted(expected_fields):
            status = "✅" if field in merge_fields else "❌"
            print(f"   {status} {field}")
        
        missing = expected_fields - merge_fields
        extra = merge_fields - expected_fields
        
        if missing:
            print(f"\n⚠️  Missing fields (add these to your template):")
            for field in sorted(missing):
                print(f"   - {field}")
        
        if extra:
            print(f"\n📝 Extra fields in template (not used by form):")
            for field in sorted(extra):
                print(f"   - {field}")
        
        if not missing and not extra:
            print("\n✨ Perfect! Template fields match the form exactly!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error reading template: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MSA Template Field Checker")
    print("=" * 60)
    check_template()
    print("\n" + "=" * 60)
