document.addEventListener('DOMContentLoaded', function() {
    const productTypeField = document.querySelector('#id_product_type');
    const coatingTypeRow = document.querySelector('.field-coating_type').closest('.form-row');
    const tabletTypeRow = document.querySelector('.field-tablet_type').closest('.form-row');
    const coatingTypeField = document.querySelector('#id_coating_type');
    const tabletTypeField = document.querySelector('#id_tablet_type');
    
    function toggleTabletFields() {
        const isTablet = productTypeField.value === 'tablet';
        
        if (coatingTypeRow && tabletTypeRow) {
            // Show/hide tablet-specific fields
            coatingTypeRow.style.display = isTablet ? 'block' : 'none';
            tabletTypeRow.style.display = isTablet ? 'block' : 'none';
            
            // Clear values if not a tablet
            if (!isTablet) {
                if (coatingTypeField) coatingTypeField.value = '';
                if (tabletTypeField) tabletTypeField.value = '';
            }
            
            // Add visual indicators
            const productTypeLabel = document.querySelector('label[for="id_product_type"]');
            if (productTypeLabel) {
                const indicator = productTypeLabel.querySelector('.tablet-indicator');
                if (indicator) indicator.remove();
                
                if (isTablet) {
                    const span = document.createElement('span');
                    span.className = 'tablet-indicator';
                    span.style.color = '#28a745';
                    span.style.fontWeight = 'bold';
                    span.innerHTML = ' (Tablet options below)';
                    productTypeLabel.appendChild(span);
                }
            }
        }
    }
    
    // Initial check
    if (productTypeField) {
        toggleTabletFields();
        
        // Listen for changes
        productTypeField.addEventListener('change', toggleTabletFields);
    }
    
    // Add styling to make it clear these are conditional fields
    if (coatingTypeRow && tabletTypeRow) {
        [coatingTypeRow, tabletTypeRow].forEach(row => {
            row.style.border = '1px dashed #007cba';
            row.style.padding = '10px';
            row.style.margin = '5px 0';
            row.style.backgroundColor = '#f8f9fa';
        });
        
        // Add a header for tablet-specific section
        const header = document.createElement('h3');
        header.textContent = 'Tablet-Specific Options';
        header.style.color = '#007cba';
        header.style.marginTop = '20px';
        header.style.marginBottom = '10px';
        header.style.borderBottom = '2px solid #007cba';
        header.style.paddingBottom = '5px';
        header.id = 'tablet-options-header';
        
        if (coatingTypeRow.parentNode) {
            coatingTypeRow.parentNode.insertBefore(header, coatingTypeRow);
        }
    }
});
