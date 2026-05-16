// Active link highlighting
document.addEventListener('DOMContentLoaded', function () {
    const anchors = document.querySelectorAll('.nav-links a');
    anchors.forEach((item) => {
        if (item.href === window.location.href) {
            item.classList.add('active-link');
        }
    });

    // Initialize form handlers
    initializeFormHandlers();
    
    // Initialize page-level scrolling
    initializePageScrolling();
});

/**
 * Initialize form event handlers
 */
function initializeFormHandlers() {
    const form = document.getElementById('eligibilityForm');
    if (form) {
        // Real-time EMI calculation preview
        const loanInput = document.getElementById('loan');
        const rateInput = document.getElementById('interest_rate');
        const tenureSelect = document.getElementById('tenure');
        const incomeInput = document.getElementById('income');
        const priceInput = document.getElementById('vehicle_price');
        const downPaymentInput = document.getElementById('down_payment');

        if (loanInput && rateInput && tenureSelect && incomeInput) {
            [loanInput, rateInput, tenureSelect, incomeInput].forEach(input => {
                input.addEventListener('change', calculateEMIPreview);
            });
        }

        if (priceInput && downPaymentInput && loanInput) {
            [priceInput, downPaymentInput].forEach(input => {
                input.addEventListener('input', calculateLoan);
            });
            calculateLoan();
        }
    }
}

/**
 * Calculate and display EMI preview
 */
function calculateEMIPreview() {
    const loanAmount = parseFloat(document.getElementById('loan')?.value || 0);
    const rate = parseFloat(document.getElementById('interest_rate')?.value || 10);
    const tenure = parseInt(document.getElementById('tenure')?.value || 5);
    const income = parseFloat(document.getElementById('income')?.value || 1);

    if (loanAmount > 0 && tenure > 0) {
        const emi = calculateEMI(loanAmount, rate, tenure);
        const ratio = income > 0 ? ((emi / income) * 100).toFixed(1) : 0;
        console.log(`EMI: ₹${emi.toFixed(2)}, Ratio: ${ratio}%`);
    }
}

/**
 * EMI Calculation Formula
 * P = Principal, R = Annual Rate, N = Number of years
 * EMI = P * R * (1 + R)^N / ((1 + R)^N - 1)
 */
function calculateEMI(principal, annualRate, years) {
    const months = years * 12;
    const monthlyRate = annualRate / 1200;
    
    if (principal <= 0 || months <= 0) return 0;
    if (monthlyRate === 0) return principal / months;
    
    const factor = Math.pow(1 + monthlyRate, months);
    return (principal * monthlyRate * factor) / (factor - 1);
}

/**
 * Calculate and update vehicle loan amount
 */
function calculateLoan() {
    const price = parseFloat(document.getElementById('vehicle_price')?.value || 0);
    const downPayment = parseFloat(document.getElementById('down_payment')?.value || 0);
    const loanField = document.getElementById('loan');
    const loanAmount = Math.max(price - downPayment, 0);
    if (loanField) {
        loanField.value = loanAmount.toFixed(2);
    }
}

function scrollToNextSection() {
    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
    }
    const nextSection = document.querySelector('.results-container') || document.querySelector('.benefit-panel');
    if (nextSection) {
        nextSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
    }
    window.scrollBy({ top: window.innerHeight * 0.8, behavior: 'smooth' });
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Show CIBIL Score Information Modal
 */
function showCIBILInfo() {
    const modal = document.getElementById('cibilModal');
    if (modal) {
        modal.style.display = 'block';
        modal.scrollTop = 0;
    }
}

/**
 * Close CIBIL Score Modal
 */
function closeCIBILModal() {
    const modal = document.getElementById('cibilModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Close Warning Modal
 */
function closeWarningModal() {
    const modal = document.getElementById('warningModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Download PDF Report
 */
function downloadReport() {
    const name = document.querySelector('input[name="name"]')?.value || 'Applicant';
    const cibilScore = document.querySelector('.cibil-card .card-value')?.textContent || '';
    const cibilCategory = document.querySelector('.cibil-card .card-category')?.textContent || '';
    const emiValue = document.querySelector('.emi-card .card-value')?.textContent || '';
    const emiRatio = document.querySelector('.emi-card .card-category')?.textContent || '';
    const riskValue = document.querySelector('.risk-card .card-value')?.textContent || '';
    const approvalValue = document.querySelector('.approval-card .card-value')?.textContent || '';

    const data = {
        // Basic Information
        loan_type: document.querySelector('input[name="loan_type"]')?.value || '',
        name: document.querySelector('input[name="name"]')?.value || '',
        email: document.querySelector('input[name="email"]')?.value || '',
        phone: document.querySelector('input[name="phone"]')?.value || '',
        occupation: document.querySelector('input[name="occupation"]')?.value || '',
        location: document.querySelector('input[name="location"]')?.value || '',
        age: document.querySelector('input[name="age"]')?.value || '',
        
        // Financial Information
        income: document.querySelector('input[name="income"]')?.value || '',
        loan: document.querySelector('input[name="loan"]')?.value || '',
        interest_rate: document.querySelector('input[name="interest_rate"]')?.value || '',
        tenure: document.querySelector('select[name="tenure"]')?.value || '',
        
        // CIBIL Information
        cibil_score: document.querySelector('input[name="cibil_score"]')?.value || '',
        cibil_category: extractText(cibilCategory),
        
        // Report Results
        emi: emiValue.replace('₹', '').trim() || '',
        emi_ratio: extractPercentage(emiRatio),
        approval_status: extractText(approvalValue),
        risk_level: extractText(riskValue),
        decision_reason: document.querySelector('.reason-text')?.textContent || '',
        
        // Vehicle Loan Fields (if applicable)
        vehicle_type: document.querySelector('select[name="vehicle_type"]')?.value || '',
        vehicle_price: document.querySelector('input[name="vehicle_price"]')?.value || '',
        down_payment: document.querySelector('input[name="down_payment"]')?.value || '',
        
        // Education Loan Fields (if applicable)
        parent_name: document.querySelector('input[name="parent_name"]')?.value || '',
        parent_occupation: document.querySelector('input[name="parent_occupation"]')?.value || '',
        parent_income: document.querySelector('input[name="parent_income"]')?.value || '',
        parent_cibil: document.querySelector('input[name="parent_cibil"]')?.value || '',
        education_purpose: document.querySelector('select[name="education_purpose"]')?.value || ''
    };
    
    fetch('/generate_report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) throw new Error('PDF generation failed');
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `loan_eligibility_${name}_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(url);
        link.remove();
        showNotification('Report downloaded successfully!', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error downloading report. Please try again.', 'error');
    });
}

/**
 * Extract percentage value from text
 */
function extractPercentage(text) {
    const match = text.match(/(\d+(?:\.\d+)?)/);
    return match ? match[1] : '0';
}

/**
 * Extract clean text
 */
function extractText(text) {
    return text.replace(/[₹%]/g, '').trim();
}

/**
 * Show Low CIBIL Score Warning
 */
function showLowCIBILWarning(score) {
    const warningModal = document.getElementById('warningModal');
    const messageEl = document.getElementById('warningMessage');
    
    if (warningModal && messageEl) {
        messageEl.innerHTML = `
            <strong>⚠️ Low CIBIL Score Alert</strong><br><br>
            Your CIBIL score is <strong>${score}</strong>, which is below the excellent range (750+). 
            This may affect your loan approval terms and interest rates.<br><br>
            <strong>Recommendations to improve your score:</strong>
            <ul style="text-align: left; margin-top: 12px;">
                <li>Pay all bills and EMIs on time</li>
                <li>Reduce outstanding debt</li>
                <li>Don't apply for multiple loans simultaneously</li>
                <li>Check your credit report for errors</li>
            </ul>
        `;
        warningModal.style.display = 'block';
    }
}

/**
 * Show High EMI Burden Warning
 */
function showHighEMIWarning(ratio) {
    const warningModal = document.getElementById('warningModal');
    const messageEl = document.getElementById('warningMessage');
    
    if (warningModal && messageEl) {
        messageEl.innerHTML = `
            <strong>⚠️ High EMI Burden Alert</strong><br><br>
            Your monthly EMI is <strong>${ratio}%</strong> of your income, which is considered high. 
            A sustainable EMI burden is typically ≤ 50% of monthly income.<br><br>
            <strong>Options to reduce EMI burden:</strong>
            <ul style="text-align: left; margin-top: 12px;">
                <li>Request a lower loan amount</li>
                <li>Extend the loan tenure to reduce monthly payments</li>
                <li>Increase your monthly income if possible</li>
                <li>Look for better interest rates from other lenders</li>
            </ul>
        `;
        warningModal.style.display = 'block';
    }
}

/**
 * Show Notification Message
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#dcfce7' : '#fee2e2'};
        color: ${type === 'success' ? '#166534' : '#991b1b'};
        border: 2px solid ${type === 'success' ? '#bbf7d0' : '#fecaca'};
        border-radius: 12px;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Modal Close on Outside Click
 */
window.addEventListener('click', function(event) {
    const cibilModal = document.getElementById('cibilModal');
    const warningModal = document.getElementById('warningModal');
    
    if (cibilModal && event.target === cibilModal) {
        cibilModal.style.display = 'none';
    }
    if (warningModal && event.target === warningModal) {
        warningModal.style.display = 'none';
    }
});

/**
 * Add slide animations
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

/**
 * ============================================================
 * ENHANCED FORM SCROLLING FUNCTIONALITY
 * ============================================================
 */

/**
 * Initialize form scrolling behavior
 */
function initializeFormScrolling() {
    const formWrappers = document.querySelectorAll('.form-wrapper, .login-wrapper');
    
    formWrappers.forEach(wrapper => {
        // Add scroll event listener for smooth scrolling
        wrapper.addEventListener('scroll', handleFormScroll);
        
        // Scroll to first error field if present
        const errorPanel = wrapper.querySelector('.error-panel');
        if (errorPanel) {
            scrollToElement(errorPanel, wrapper);
        }
    });
    
    // Handle form submission with auto-scroll to errors
    const forms = document.querySelectorAll('.form-grid');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Initialize scroll button visibility
    updateScrollButtonsVisibility();
}

/**
 * Handle form wrapper scrolling
 */
function handleFormScroll(e) {
    const wrapper = e.target;
    const scrollTop = wrapper.scrollTop;
    const scrollHeight = wrapper.scrollHeight;
    const clientHeight = wrapper.clientHeight;
    
    // Update scroll buttons visibility
    updateScrollButtonsVisibility(wrapper);
    
    // Show section title shadow on scroll
    const sectionTitles = wrapper.querySelectorAll('.form-section-title');
    sectionTitles.forEach(title => {
        if (wrapper.scrollTop > title.offsetTop) {
            title.style.boxShadow = '0 4px 12px rgba(96, 165, 250, 0.12)';
        } else {
            title.style.boxShadow = '0 2px 8px rgba(96, 165, 250, 0.08)';
        }
    });
}

/**
 * Update scroll buttons visibility based on scroll position
 */
function updateScrollButtonsVisibility(formWrapper) {
    const scrollButton = document.getElementById('scrollButton');
    const scrollUpButton = document.getElementById('scrollUpButton');
    
    if (!scrollButton || !scrollUpButton) return;
    
    let wrapper = formWrapper;
    if (!wrapper) {
        wrapper = document.querySelector('.form-wrapper');
    }
    
    if (!wrapper) {
        scrollButton.style.opacity = '0.5';
        scrollUpButton.style.opacity = '0.5';
        scrollButton.style.pointerEvents = 'none';
        scrollUpButton.style.pointerEvents = 'none';
        return;
    }
    
    const scrollTop = wrapper.scrollTop;
    const scrollHeight = wrapper.scrollHeight;
    const clientHeight = wrapper.clientHeight;
    const isAtTop = scrollTop <= 0;
    const isAtBottom = scrollTop >= scrollHeight - clientHeight - 10;
    
    // Update scroll down button
    if (isAtBottom) {
        scrollButton.style.opacity = '0.4';
        scrollButton.style.pointerEvents = 'none';
    } else {
        scrollButton.style.opacity = '1';
        scrollButton.style.pointerEvents = 'auto';
    }
    
    // Update scroll up button
    if (isAtTop) {
        scrollUpButton.style.opacity = '0.4';
        scrollUpButton.style.pointerEvents = 'none';
    } else {
        scrollUpButton.style.opacity = '1';
        scrollUpButton.style.pointerEvents = 'auto';
    }
}

/**
 * Enhanced scroll to next section within form
 */
function scrollToNextSection() {
    const formWrapper = document.querySelector('.form-wrapper');
    if (!formWrapper) {
        window.scrollBy({ top: window.innerHeight * 0.8, behavior: 'smooth' });
        return;
    }
    
    const scrollAmount = formWrapper.clientHeight * 0.7;
    formWrapper.scrollBy({
        top: scrollAmount,
        behavior: 'smooth'
    });
    
    setTimeout(() => {
        updateScrollButtonsVisibility(formWrapper);
    }, 300);
}

/**
 * Enhanced scroll to top within form
 */
function scrollToTop() {
    const formWrapper = document.querySelector('.form-wrapper');
    if (formWrapper) {
        formWrapper.scrollBy({
            top: -(formWrapper.clientHeight * 0.7),
            behavior: 'smooth'
        });
        setTimeout(() => {
            updateScrollButtonsVisibility(formWrapper);
        }, 300);
    } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Smooth scroll to a specific element within a container
 */
function scrollToElement(element, container) {
    if (!element || !container) return;
    
    const elementRect = element.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    
    if (elementRect.top < 0) {
        container.scrollBy({
            top: elementRect.top - 20,
            behavior: 'smooth'
        });
    } else if (elementRect.bottom > containerRect.bottom) {
        container.scrollBy({
            top: elementRect.bottom - containerRect.bottom + 20,
            behavior: 'smooth'
        });
    }
}

/**
 * Handle form submission - scroll to first error
 */
function handleFormSubmit(e) {
    const form = e.currentTarget;
    const formWrapper = form.closest('.form-wrapper, .login-wrapper');
    
    // Check for HTML5 validation
    if (!form.checkValidity()) {
        // Find first invalid field
        const invalidField = form.querySelector(':invalid');
        if (invalidField && formWrapper) {
            invalidField.focus();
            scrollToElement(invalidField, formWrapper);
        }
    }
}

/**
 * Auto-focus and scroll to form field
 */
function focusFormField(fieldId) {
    const field = document.getElementById(fieldId);
    const formWrapper = field?.closest('.form-wrapper, .login-wrapper');
    
    if (field && formWrapper) {
        field.focus();
        scrollToElement(field, formWrapper);
    } else if (field) {
        field.focus();
        field.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Initialize form scrolling on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeFormScrolling();
    
    // Re-initialize when dynamic content is added
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                initializeFormScrolling();
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        addedNodes: true
    });
});

/**
 * ============================================================
 * PAGE-LEVEL SCROLLING FUNCTIONALITY
 * ============================================================
 */

/**
 * Initialize page-level scrolling features
 */
function initializePageScrolling() {
    // Create scroll progress bar
    createScrollProgressBar();
    
    // Create scroll-to-top button
    createScrollToTopButton();
    
    // Add page scroll event listeners
    window.addEventListener('scroll', handlePageScroll);
    
    // Smooth scroll behavior for anchor links
    initializeAnchorScrolling();
}

/**
 * Create animated scroll progress bar
 */
function createScrollProgressBar() {
    // Check if progress bar already exists
    if (document.getElementById('scrollProgressBar')) {
        return;
    }
    
    const progressBar = document.createElement('div');
    progressBar.id = 'scrollProgressBar';
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 4px;
        background: linear-gradient(90deg, #60a5fa 0%, #3b82f6 50%, #1e40af 100%);
        width: 0%;
        z-index: 1000;
        transition: width 0.2s ease;
        box-shadow: 0 0 10px rgba(96, 165, 250, 0.4);
    `;
    document.body.appendChild(progressBar);
}

/**
 * Create floating scroll-to-top button
 */
function createScrollToTopButton() {
    // Check if button already exists
    if (document.getElementById('scrollToTopBtn')) {
        return;
    }
    
    const button = document.createElement('button');
    button.id = 'scrollToTopBtn';
    button.innerHTML = '↑';
    button.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: none;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        color: white;
        font-size: 24px;
        font-weight: bold;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s ease, visibility 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 12px rgba(96, 165, 250, 0.3);
        z-index: 999;
    `;
    
    button.addEventListener('click', scrollToPageTop);
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'scale(1.1)';
        button.style.boxShadow = '0 6px 20px rgba(96, 165, 250, 0.4)';
    });
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'scale(1)';
        button.style.boxShadow = '0 4px 12px rgba(96, 165, 250, 0.3)';
    });
    
    document.body.appendChild(button);
}

/**
 * Handle page scroll events
 */
function handlePageScroll() {
    // Update scroll progress bar
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    
    const progressBar = document.getElementById('scrollProgressBar');
    if (progressBar) {
        progressBar.style.width = scrollPercent + '%';
    }
    
    // Update scroll-to-top button visibility
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (scrollToTopBtn) {
        if (scrollTop > 300) {
            scrollToTopBtn.style.opacity = '1';
            scrollToTopBtn.style.visibility = 'visible';
        } else {
            scrollToTopBtn.style.opacity = '0';
            scrollToTopBtn.style.visibility = 'hidden';
        }
    }
    
    // Update active navigation link based on scroll position
    updateActiveNavLink();
}

/**
 * Smooth scroll to top of page
 */
function scrollToPageTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

/**
 * Scroll page down by viewport height
 */
function scrollPageDown() {
    window.scrollBy({
        top: window.innerHeight * 0.8,
        behavior: 'smooth'
    });
}

/**
 * Scroll page up by viewport height
 */
function scrollPageUp() {
    window.scrollBy({
        top: -(window.innerHeight * 0.8),
        behavior: 'smooth'
    });
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initializeAnchorScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Update active navigation link based on scroll position
 */
function updateActiveNavLink() {
    const sections = document.querySelectorAll('section, [id]');
    const scrollPosition = window.scrollY + 100;
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            const id = section.getAttribute('id');
            if (id) {
                document.querySelectorAll('.nav-links a').forEach(link => {
                    link.classList.remove('active-link');
                    if (link.getAttribute('href') === '#' + id) {
                        link.classList.add('active-link');
                    }
                });
            }
        }
    });
}

/**
 * Create keyboard shortcuts for scrolling
 */
document.addEventListener('keydown', function(e) {
    // Space bar - scroll down
    if (e.code === 'Space' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
        e.preventDefault();
        scrollPageDown();
    }
    // Shift + Space - scroll up
    if (e.code === 'Space' && e.shiftKey) {
        e.preventDefault();
        scrollPageUp();
    }
    // Home key - scroll to top
    if (e.code === 'Home') {
        e.preventDefault();
        scrollToPageTop();
    }
    // End key - scroll to bottom
    if (e.code === 'End') {
        e.preventDefault();
        window.scrollTo({
            top: document.documentElement.scrollHeight,
            behavior: 'smooth'
        });
    }
});
