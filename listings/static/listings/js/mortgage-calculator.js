// mortgage-calculator.js - Mortgage calculator functionality

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const mortgageModal = document.getElementById('mortgageModal');
    const mortgageTriggers = document.querySelectorAll('.mc-trigger');
    const closeMortgageModal = document.querySelector('.close-mortgage-modal');
    
    // Input elements
    const mcPrincipal = document.getElementById('mcPrincipal');
    const mcRate = document.getElementById('mcRate');
    const mcYears = document.getElementById('mcYears');
    const mcTax = document.getElementById('mcTax');
    const mcInsurance = document.getElementById('mcInsurance');
    const mcPMI = document.getElementById('mcPMI');
    const mcHOA = document.getElementById('mcHOA');
    const mcCalcBtn = document.getElementById('mcCalcBtn');
    const mcError = document.getElementById('mcError');
    
    // Result elements
    const mcMonthly = document.getElementById('mcMonthly');
    const mcTotalPaid = document.getElementById('mcTotalPaid');
    const mcTotalInterest = document.getElementById('mcTotalInterest');
    const mcMonths = document.getElementById('mcMonths');
    
    // Initialize if elements exist
    if (!mortgageModal) {
        console.warn('Mortgage calculator modal not found');
        return;
    }
    
    // Mortgage calculation function
    function calculateMortgage() {
        if (!mcPrincipal || !mcMonthly) return;
        
        mcError.textContent = '';
        
        // Get values
        const principal = parseFloat(mcPrincipal.value) || 0;
        const rate = parseFloat(mcRate.value) || 0;
        const years = parseInt(mcYears.value) || 30;
        const tax = parseFloat(mcTax ? mcTax.value : 0) || 0;
        const insurance = parseFloat(mcInsurance ? mcInsurance.value : 0) || 0;
        const pmi = parseFloat(mcPMI ? mcPMI.value : 0) || 0;
        const hoa = parseFloat(mcHOA ? mcHOA.value : 0) || 0;
        
        // Validation
        if (principal <= 0 || rate <= 0) {
            mcError.textContent = 'Please enter valid principal and interest rate values.';
            return;
        }
        
        // Calculate monthly interest rate
        const monthlyRate = rate / 100 / 12;
        const months = years * 12;
        
        // Calculate principal + interest
        let monthlyPI = 0;
        if (monthlyRate === 0) {
            monthlyPI = principal / months;
        } else {
            monthlyPI = principal * monthlyRate * Math.pow(1 + monthlyRate, months) / 
                       (Math.pow(1 + monthlyRate, months) - 1);
        }
        
        // Add other monthly costs
        const monthlyTax = tax / 12;
        const monthlyInsurance = insurance / 12;
        const monthlyPMI = pmi / 12;
        const monthlyHOA = hoa / 12;
        
        const totalMonthly = monthlyPI + monthlyTax + monthlyInsurance + monthlyPMI + monthlyHOA;
        
        // Calculate totals
        const totalPaid = totalMonthly * months;
        const totalInterest = (monthlyPI * months) - principal;
        
        // Update UI
        mcMonthly.textContent = totalMonthly.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        if (mcTotalPaid) mcTotalPaid.textContent = Math.round(totalPaid).toLocaleString();
        if (mcTotalInterest) mcTotalInterest.textContent = Math.round(totalInterest).toLocaleString();
        if (mcMonths) mcMonths.textContent = months;
    }
    
    // Open mortgage modal
    function openMortgageModal(principal = null) {
        if (principal && mcPrincipal) {
            mcPrincipal.value = principal;
        }
        
        mortgageModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Calculate initial values
        calculateMortgage();
    }
    
    // Close mortgage modal
    function closeMortgageModalFunc() {
        mortgageModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    // Event listeners for mortgage triggers
    if (mortgageTriggers.length > 0) {
        mortgageTriggers.forEach(trigger => {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                const principalAmount = this.getAttribute('data-mc-principal');
                openMortgageModal(principalAmount);
            });
        });
    }
    
    // Close button event
    if (closeMortgageModal) {
        closeMortgageModal.addEventListener('click', closeMortgageModalFunc);
    }
    
    // Close modal when clicking outside
    mortgageModal.addEventListener('click', function(e) {
        if (e.target === mortgageModal) {
            closeMortgageModalFunc();
        }
    });
    
    // Calculate button event
    if (mcCalcBtn) {
        mcCalcBtn.addEventListener('click', calculateMortgage);
    }
    
    // Auto-calculate when inputs change
    const mortgageInputs = [
        mcPrincipal, mcRate, mcYears, mcTax, 
        mcInsurance, mcPMI, mcHOA
    ];
    
    mortgageInputs.forEach(input => {
        if (input) {
            input.addEventListener('input', calculateMortgage);
            input.addEventListener('change', calculateMortgage);
        }
    });
    
    // Initial calculation
    setTimeout(calculateMortgage, 100);
});