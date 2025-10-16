"""
Admin Dashboard Diagnostic Tool
==============================
This script diagnoses issues with the admin dashboard section toggling.
It inspects both the server-side templates and client-side behavior.

Usage: python dashboard_diagnostics.py
"""

import os
import re
import sys
import django
import logging
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from django.conf import settings

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kampala_pharma.settings')
django.setup()

def check_template_structure():
    """Examines the admin_dashboard.html template for structural issues"""
    logger.info("Checking admin dashboard template structure...")
    
    template_path = os.path.join('templates', 'dashboards', 'admin_dashboard.html')
    if not os.path.exists(template_path):
        logger.error(f"Template file not found: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Check for section IDs
    sections_to_check = [
        'machine-management',
        'quality-control', 
        'inventory-status',
        'user-management',
        'system-health'
    ]
    
    missing_sections = []
    for section in sections_to_check:
        if f'id="{section}"' not in template_content:
            missing_sections.append(section)
    
    if missing_sections:
        logger.error(f"Missing section IDs in template: {', '.join(missing_sections)}")
        return False
    else:
        logger.info("All required section IDs found in template.")
    
    # Check for section links
    missing_links = []
    for section in sections_to_check:
        if f'data-section="{section}"' not in template_content:
            missing_links.append(section)
    
    if missing_links:
        logger.error(f"Missing section links in template: {', '.join(missing_links)}")
        return False
    else:
        logger.info("All required section links found in template.")
    
    # Parse the template with BeautifulSoup
    soup = BeautifulSoup(template_content, 'html.parser')
    
    # Check for CSS definitions
    style_tags = soup.find_all('style')
    css_content = ''.join([tag.string for tag in style_tags if tag.string])
    
    if '.content-section { display: none; }' not in css_content.replace(' ', '').replace('\n', ''):
        logger.error("Missing CSS to hide content sections by default")
        return False
    else:
        logger.info("Found CSS to hide content sections by default")
    
    # Check for JavaScript initialization
    script_tags = soup.find_all('script')
    js_content = ''.join([tag.string for tag in script_tags if tag.string])
    
    if 'addEventListener(\'click\'' not in js_content or 'data-section' not in js_content:
        logger.error("Missing JavaScript event listeners for section links")
        return False
    else:
        logger.info("Found JavaScript event listeners for section links")
        
    return True

def run_js_diagnostics():
    """Creates JavaScript code to diagnose issues in the browser"""
    diagnostic_js = """
// Admin Dashboard JS Diagnostics
console.log('======== DASHBOARD DIAGNOSTICS ========');

// Check section elements
const sections = document.querySelectorAll('.content-section');
console.log(`Found ${sections.length} content sections:`, Array.from(sections).map(s => s.id));

// Check section links
const sectionLinks = document.querySelectorAll('.section-link');
console.log(`Found ${sectionLinks.length} section links:`, Array.from(sectionLinks).map(l => l.getAttribute('data-section')));

// Check if event listeners are properly attached
const sectionLinkData = Array.from(sectionLinks).map(link => {
    return {
        id: link.id,
        dataSection: link.getAttribute('data-section'),
        hasEventListeners: link.onclick !== null || window.getComputedStyle(link).cursor === 'pointer'
    };
});
console.log('Section link details:', sectionLinkData);

// Check CSS
const sectionStyles = Array.from(sections).map(section => {
    const style = window.getComputedStyle(section);
    return {
        id: section.id,
        display: style.display,
        visibility: style.visibility,
        height: style.height,
        overflow: style.overflow
    };
});
console.log('Section CSS styles:', sectionStyles);

// Test clicking on a section link
function testSectionClick(sectionId) {
    const link = document.querySelector(`[data-section="${sectionId}"]`);
    if (link) {
        console.log(`Simulating click on ${sectionId} link`);
        link.click();
        
        // Check result
        setTimeout(() => {
            const section = document.getElementById(sectionId);
            if (section) {
                console.log(`After click, section ${sectionId} display:`, window.getComputedStyle(section).display);
            } else {
                console.error(`Section ${sectionId} not found in DOM`);
            }
        }, 100);
    } else {
        console.error(`Link for section ${sectionId} not found`);
    }
}

// Test links
console.log('======== TESTING SECTION LINKS ========');
['machine-management', 'quality-control', 'inventory-status', 'user-management', 'system-health'].forEach(id => {
    testSectionClick(id);
});
"""
    
    # Write the diagnostic JS to a file
    with open('static/js/dashboard_diagnostics.js', 'w') as f:
        f.write(diagnostic_js)
    
    logger.info("Created JavaScript diagnostics file at static/js/dashboard_diagnostics.js")
    logger.info("To use: Open browser console and run: fetch('/static/js/dashboard_diagnostics.js').then(r=>r.text()).then(eval)")

def check_live_dom():
    """Tries to connect to the running server and check the DOM structure"""
    logger.info("Attempting to check live DOM structure...")
    
    try:
        response = requests.get('http://127.0.0.1:8000/dashboard/admin-overview/')
        if response.status_code != 200:
            logger.error(f"Failed to connect to server: Status {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check sections
        sections = soup.select('.content-section')
        logger.info(f"Found {len(sections)} content sections")
        for section in sections:
            section_id = section.get('id', 'unknown')
            logger.info(f"Section: {section_id}, Display: {section.get('style', 'not set')}")
        
        # Check links
        links = soup.select('.section-link')
        logger.info(f"Found {len(links)} section links")
        for link in links:
            link_id = link.get('id', 'unknown')
            data_section = link.get('data-section', 'not set')
            logger.info(f"Link: {link_id}, data-section: {data_section}")
            
    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to the Django server. Make sure it's running.")

def inject_test_code():
    """Injects diagnostic code into the admin dashboard template"""
    logger.info("Creating temporary template with diagnostics...")
    
    template_path = os.path.join('templates', 'dashboards', 'admin_dashboard.html')
    if not os.path.exists(template_path):
        logger.error(f"Template file not found: {template_path}")
        return
        
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Create a diagnostic version with console logs
    diagnostic_js = """
<script>
// ===== ADMIN DASHBOARD DIAGNOSTICS =====
console.log('Dashboard diagnostics loaded');

// Run diagnostics when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - running diagnostics');
    
    // Check section elements
    const sections = document.querySelectorAll('.content-section');
    console.log(`Found ${sections.length} content sections:`, Array.from(sections).map(s => s.id));
    
    // Log CSS for each section
    sections.forEach(section => {
        const style = window.getComputedStyle(section);
        console.log(`Section ${section.id}: display=${style.display}, visibility=${style.visibility}`);
    });
    
    // Check section links
    const sectionLinks = document.querySelectorAll('.section-link');
    console.log(`Found ${sectionLinks.length} section links:`, 
        Array.from(sectionLinks).map(l => l.getAttribute('data-section')));
    
    // Add diagnostic click handlers
    sectionLinks.forEach(link => {
        const originalHandler = link.onclick;
        link.onclick = function(e) {
            console.log(`Link clicked: ${link.id}, data-section: ${link.getAttribute('data-section')}`);
            
            // Call any existing handler
            if (typeof originalHandler === 'function') {
                return originalHandler.call(this, e);
            }
        };
    });
    
    // Check showSection function
    if (typeof showSection === 'function') {
        console.log('showSection function exists');
        
        // Override with logging
        const originalShowSection = showSection;
        window.showSection = function(sectionId, clickedElement) {
            console.log(`showSection called: sectionId=${sectionId}`);
            
            // Check target section
            const targetSection = document.getElementById(sectionId);
            if (!targetSection) {
                console.error(`Target section #${sectionId} not found!`);
                return false;
            } else {
                console.log(`Target section #${sectionId} found, current display:`, 
                    window.getComputedStyle(targetSection).display);
            }
            
            // Call original function
            const result = originalShowSection.call(this, sectionId, clickedElement);
            
            // Check result
            console.log(`After showSection, display=`, window.getComputedStyle(targetSection).display);
            return result;
        };
    } else {
        console.error('showSection function not found!');
    }
    
    console.log('Diagnostics setup complete');
});
</script>
"""
    
    # Inject before the closing body tag
    modified_template = template_content.replace('</body>', diagnostic_js + '</body>')
    
    # Create a diagnostic version of the template
    diagnostic_template_path = os.path.join('templates', 'dashboards', 'admin_dashboard_diagnostic.html')
    with open(diagnostic_template_path, 'w', encoding='utf-8') as f:
        f.write(modified_template)
    
    logger.info(f"Created diagnostic template: {diagnostic_template_path}")
    logger.info("To use this template, temporarily modify the admin_dashboard view in dashboards/views.py")
    logger.info("Change: return render(request, 'dashboards/admin_dashboard.html', context)")
    logger.info("To:     return render(request, 'dashboards/admin_dashboard_diagnostic.html', context)")

def modify_view_temporarily():
    """Temporarily modify the view to use the diagnostic template"""
    logger.info("Temporarily modifying admin_dashboard view...")
    
    view_path = os.path.join('dashboards', 'views.py')
    if not os.path.exists(view_path):
        logger.error(f"Views file not found: {view_path}")
        return
    
    with open(view_path, 'r') as f:
        content = f.read()
    
    # Find the admin_dashboard function
    pattern = r"def admin_dashboard\(request\):(.*?)return render\(request, 'dashboards/admin_dashboard.html', context\)"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        logger.error("Could not find admin_dashboard view in views.py")
        return
    
    modified_content = content.replace(
        "return render(request, 'dashboards/admin_dashboard.html', context)",
        "# TEMPORARY FOR DIAGNOSTICS\n    return render(request, 'dashboards/admin_dashboard_diagnostic.html', context)"
    )
    
    # Create a backup
    with open(f"{view_path}.bak", 'w') as f:
        f.write(content)
    
    # Write modified version
    with open(view_path, 'w') as f:
        f.write(modified_content)
    
    logger.info(f"Modified views.py - backup saved as {view_path}.bak")
    logger.info("After testing, restore the original file")

def main():
    logger.info("Starting admin dashboard diagnostics...")
    
    # Check template structure
    template_ok = check_template_structure()
    if not template_ok:
        logger.warning("Found issues with template structure. Creating diagnostic tools...")
    
    # Create JavaScript diagnostics
    run_js_diagnostics()
    
    # Create diagnostic template
    inject_test_code()
    
    # Modify view temporarily
    modify_view_temporarily()
    
    # Try to check live DOM
    check_live_dom()
    
    logger.info("Diagnostic script complete.")
    logger.info("1. Restart the Django server")
    logger.info("2. Visit http://127.0.0.1:8000/dashboard/admin-overview/")
    logger.info("3. Open the browser developer console (F12)")
    logger.info("4. Check console logs for detailed diagnostics")
    logger.info("5. Restore views.py from the backup after testing")

if __name__ == "__main__":
    main()