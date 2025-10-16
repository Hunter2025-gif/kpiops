document.addEventListener('DOMContentLoaded', function() {
    const productTypeField = document.querySelector('#id_product_type');
    const tabletFields = document.querySelector('.field-is_coated').parentElement.parentElement;
    
    function toggleTabletFields() {
        const isTablet = productTypeField.value === 'tablet';
        if (tabletFields) {
            tabletFields.style.display = isTablet ? 'block' : 'none';
        }
        
        // Clear tablet-specific fields if not a tablet
        if (!isTablet) {
            const isCoatedField = document.querySelector('#id_is_coated');
            const tabletTypeField = document.querySelector('#id_tablet_type');
            if (isCoatedField) isCoatedField.checked = false;
            if (tabletTypeField) tabletTypeField.value = '';
        }
    }
    
    // Initial check
    toggleTabletFields();
    
    // Listen for changes
    if (productTypeField) {
        productTypeField.addEventListener('change', toggleTabletFields);
    }
});
