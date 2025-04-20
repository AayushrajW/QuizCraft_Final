/**
 * QuizCraft - Main JavaScript
 * Handles interactive elements across the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Password visibility toggle
    setupPasswordToggle();
    
    // Flash message dismiss functionality
    setupFlashMessages();
    
    // Handle file inputs to show filenames
    setupFileInputs();
    
    // Set current year in footer
    setCurrentYear();
});

/**
 * Toggle password visibility in login/register forms
 */
function setupPasswordToggle() {
    const toggleButtons = document.querySelectorAll('[id^="togglePassword"]');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const target = this.previousElementSibling;
            if (!target || target.tagName !== 'INPUT') return;
            
            // Toggle password visibility
            const type = target.getAttribute('type') === 'password' ? 'text' : 'password';
            target.setAttribute('type', type);
            
            // Toggle eye icon
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-eye');
                icon.classList.toggle('fa-eye-slash');
            }
        });
    });
}

/**
 * Setup flash message dismiss functionality
 */
function setupFlashMessages() {
    const closeButtons = document.querySelectorAll('.flash-close');
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const flashMessage = this.closest('[role="alert"]');
            if (flashMessage) {
                flashMessage.classList.add('opacity-0');
                setTimeout(() => {
                    flashMessage.style.display = 'none';
                }, 300);
            }
        });
    });
    
    // Auto-dismiss flash messages after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('[role="alert"]').forEach(alert => {
            alert.classList.add('opacity-0');
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        });
    }, 5000);
}

/**
 * Setup file input display logic
 */
function setupFileInputs() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileNameElement = document.getElementById(this.id + '-name');
            if (!fileNameElement) return;
            
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                fileNameElement.textContent = fileName;
                fileNameElement.parentElement.classList.remove('hidden');
            } else {
                fileNameElement.parentElement.classList.add('hidden');
            }
        });
    });
}

/**
 * Set current year in the footer
 */
function setCurrentYear() {
    const yearElements = document.querySelectorAll('.current-year');
    const currentYear = new Date().getFullYear();
    
    yearElements.forEach(element => {
        element.textContent = currentYear;
    });
}

/**
 * Format file size to a human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} - Formatted file size (e.g., "2.5 MB")
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Handle form submission with validation
 * @param {HTMLFormElement} form - The form element
 * @param {Function} callback - Optional callback after validation
 */
function validateForm(form, callback) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            
            // Add error styling
            field.classList.add('border-red-500');
            
            // Add error message if it doesn't exist
            const errorId = `${field.id}-error`;
            if (!document.getElementById(errorId)) {
                const errorMsg = document.createElement('p');
                errorMsg.id = errorId;
                errorMsg.className = 'text-red-500 text-xs mt-1';
                errorMsg.textContent = `${field.getAttribute('placeholder') || 'This field'} is required`;
                field.parentNode.appendChild(errorMsg);
            }
            
            // Reset styling on input
            field.addEventListener('input', function() {
                if (this.value.trim()) {
                    this.classList.remove('border-red-500');
                    const errorMsg = document.getElementById(errorId);
                    if (errorMsg) errorMsg.remove();
                }
            }, { once: true });
        }
    });
    
    if (isValid && typeof callback === 'function') {
        callback();
    }
    
    return isValid;
}
