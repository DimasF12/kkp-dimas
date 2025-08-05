document.addEventListener('DOMContentLoaded', () => {
    // Button interaction
    const ctaButton = document.querySelector('.cta-button');
    
    ctaButton.addEventListener('click', () => {
        // Add ripple effect
        const ripple = document.createElement('span');
        ripple.classList.add('ripple-effect');
        ctaButton.appendChild(ripple);
        
        // Remove ripple after animation
        setTimeout(() => {
            ripple.remove();
        }, 600);
        
        window.location.href = ('/login.html')
    });

    // Entrance animations
    const animateElements = () => {
        const elements = [
            document.querySelector('.app-logo'),
            document.querySelector('.app-title'),
            document.querySelector('.app-tagline'),
            document.querySelector('.cta-button')
        ];
        
        elements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = `all 0.5s ${index * 0.15}s ease-out`;
            
            setTimeout(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, 50);
        });
    };
    
    animateElements();
});