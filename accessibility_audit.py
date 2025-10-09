#!/usr/bin/env python3
"""
Accessibility Audit for NoFeePlaces.com
Check for common accessibility issues and generate improvement recommendations
"""

import os
import re
from pathlib import Path

def audit_react_files():
    """Audit React components for accessibility issues"""
    
    issues = {
        'heading_hierarchy': [],
        'missing_alt_text': [],
        'poor_contrast': [],
        'missing_aria_labels': [],
        'keyboard_navigation': [],
        'semantic_html': [],
        'focus_management': []
    }
    
    # Files to audit
    files_to_check = [
        '/app/frontend/src/ConversionHero.js',
        '/app/frontend/src/HamburgerMenu.js', 
        '/app/frontend/src/components.js',
        '/app/frontend/src/StaticPages.js',
        '/app/frontend/src/FloatingFeedbackButton.js',
        '/app/frontend/src/FeedbackModal.js',
        '/app/frontend/src/WordMark.js'
    ]
    
    print("🔍 ACCESSIBILITY AUDIT REPORT")
    print("=" * 50)
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\n📁 Auditing: {file_path}")
            
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for heading hierarchy issues
            h1_count = len(re.findall(r'<h1[^>]*>', content))
            h2_count = len(re.findall(r'<h2[^>]*>', content)) 
            h3_count = len(re.findall(r'<h3[^>]*>', content))
            
            if h1_count > 1:
                issues['heading_hierarchy'].append(f"{file_path}: Multiple H1 tags found ({h1_count})")
            
            # Check for images without alt text
            img_tags = re.findall(r'<img[^>]*>', content)
            for img in img_tags:
                if 'alt=' not in img:
                    issues['missing_alt_text'].append(f"{file_path}: Image without alt text: {img[:50]}...")
            
            # Check for buttons without aria-labels
            button_tags = re.findall(r'<button[^>]*>', content)
            for button in button_tags:
                if 'aria-label=' not in button and 'aria-labelledby=' not in button:
                    if 'onClick' in button or 'click' in button.lower():
                        issues['missing_aria_labels'].append(f"{file_path}: Button without aria-label: {button[:50]}...")
            
            # Check for clickable elements without proper semantics
            if 'onClick' in content and '<div' in content:
                div_clicks = re.findall(r'<div[^>]*onClick[^>]*>', content)
                for div in div_clicks:
                    if 'role=' not in div:
                        issues['semantic_html'].append(f"{file_path}: Clickable div without role: {div[:50]}...")
            
            # Check for focus management
            if 'modal' in content.lower() or 'Modal' in content:
                if 'focus' not in content and 'autoFocus' not in content:
                    issues['focus_management'].append(f"{file_path}: Modal without focus management")
                    
            print(f"   - H1 tags: {h1_count}")
            print(f"   - H2 tags: {h2_count}") 
            print(f"   - H3 tags: {h3_count}")
            print(f"   - Images: {len(img_tags)}")
            print(f"   - Buttons: {len(button_tags)}")
    
    # Print issues summary
    print(f"\n🚨 ACCESSIBILITY ISSUES FOUND:")
    print("=" * 50)
    
    total_issues = sum(len(issue_list) for issue_list in issues.values())
    print(f"Total Issues: {total_issues}")
    
    for category, issue_list in issues.items():
        if issue_list:
            print(f"\n📋 {category.replace('_', ' ').title()} ({len(issue_list)} issues):")
            for issue in issue_list[:3]:  # Show first 3 issues
                print(f"   • {issue}")
            if len(issue_list) > 3:
                print(f"   • ... and {len(issue_list) - 3} more")
    
    return issues

def generate_accessibility_recommendations():
    """Generate comprehensive accessibility improvement recommendations"""
    
    recommendations = """
🎯 ACCESSIBILITY IMPROVEMENT PLAN
================================

1. 📊 HEADING HIERARCHY:
   - Ensure only one H1 per page (main title)
   - Use H2 for main sections, H3 for subsections
   - No skipping heading levels (H1 → H2 → H3, not H1 → H3)
   - Add semantic heading structure to all pages

2. 🖼️ IMAGES & MEDIA:
   - Add descriptive alt text to all images
   - Use alt="" for decorative images
   - Add captions for videos/audio content
   - Ensure images convey meaning, not just decoration

3. 🎨 COLOR & CONTRAST:
   - Ensure 4.5:1 contrast ratio for normal text
   - Ensure 3:1 contrast ratio for large text (18px+ or 14px+ bold)
   - Don't rely solely on color to convey information
   - Test with color blindness simulators

4. ⌨️ KEYBOARD NAVIGATION:
   - All interactive elements accessible via keyboard
   - Visible focus indicators for all focusable elements
   - Logical tab order through page content
   - Skip links for main navigation

5. 🏷️ ARIA LABELS & SEMANTICS:
   - Add aria-label to buttons without visible text
   - Use semantic HTML elements (button, nav, main, etc.)
   - Add role attributes where appropriate
   - Use aria-expanded for collapsible content

6. 📱 RESPONSIVE & MOBILE:
   - Ensure 44px minimum touch target size
   - Test with screen magnification up to 200%
   - Horizontal scrolling should not be required
   - Content reflows properly on small screens

7. 🔊 SCREEN READER SUPPORT:
   - Add skip navigation links
   - Use proper form labels and descriptions
   - Announce dynamic content changes
   - Test with actual screen readers

8. ⚡ PERFORMANCE & LOADING:
   - Provide loading states for dynamic content
   - Show progress indicators for long operations
   - Ensure content is available without JavaScript
   - Fast loading times for assistive technology

PRIORITY FIXES:
===============
HIGH: Heading hierarchy, keyboard navigation, contrast ratios
MEDIUM: ARIA labels, semantic HTML, alt text
LOW: Advanced ARIA patterns, fine-tuning
"""
    
    return recommendations

if __name__ == "__main__":
    issues = audit_react_files()
    recommendations = generate_accessibility_recommendations()
    
    print(recommendations)
    
    # Save audit results
    with open('/app/accessibility_audit_results.txt', 'w') as f:
        f.write("NOFEEPLACES.COM ACCESSIBILITY AUDIT\n")
        f.write("=" * 50 + "\n\n")
        
        for category, issue_list in issues.items():
            if issue_list:
                f.write(f"{category.replace('_', ' ').title()}:\n")
                for issue in issue_list:
                    f.write(f"  - {issue}\n")
                f.write("\n")
        
        f.write(recommendations)
    
    print(f"\n💾 Full audit results saved to: /app/accessibility_audit_results.txt")