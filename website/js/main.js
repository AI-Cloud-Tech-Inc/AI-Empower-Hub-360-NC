// ============================================================
// Empower Hub 360 - Main JavaScript
// UI interactions, navigation, forms, animations
// ============================================================

// ===== Mobile Menu Toggle =====
const mobileMenuBtn = document.querySelector('.mobile-menu');
const navLinks = document.querySelector('.nav-links');

if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        mobileMenuBtn.classList.toggle('active');
    });
}

// Close mobile menu on outside click
document.addEventListener('click', (e) => {
    if (navLinks && mobileMenuBtn) {
        if (!navLinks.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
            navLinks.classList.remove('active');
            mobileMenuBtn.classList.remove('active');
        }
    }
});

// ===== Smooth Scroll for Navigation =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        const target = document.querySelector(href);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            if (navLinks) navLinks.classList.remove('active');
            if (mobileMenuBtn) mobileMenuBtn.classList.remove('active');
        }
    });
});

// ===== Navbar Scroll Effect =====
const navbar = document.querySelector('.navbar');
if (navbar) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(15, 23, 42, 0.97)';
            navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.background = 'rgba(15, 23, 42, 0.85)';
            navbar.style.boxShadow = 'none';
        }
    });
}

// ===== Solutions Tabs =====
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;
        tabBtns.forEach(b => b.classList.remove('active'));
        tabPanels.forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const panel = document.getElementById(tabId);
        if (panel) panel.classList.add('active');
    });
});

// ===== Contact / Consultation Form =====
const contactForm = document.querySelector('#contact-form');

if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(contactForm);
        const data = Object.fromEntries(formData.entries());

        const btn = contactForm.querySelector('button[type="submit"]');
        const originalText = btn.textContent;
        btn.textContent = 'Sending...';
        btn.disabled = true;

        try {
            const result = await API.submitConsultation(data);
            if (result.ok) {
                btn.textContent = '✓ Sent!';
                btn.style.background = 'linear-gradient(135deg, #22c55e, #16a34a)';
                contactForm.reset();
                Toast.success("Message sent! We'll be in touch within 24 hours.");
            } else {
                throw new Error('Submission failed');
            }
        } catch (error) {
            btn.textContent = 'Error - Try Again';
            btn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
            Toast.error('Something went wrong. Please email empowerhub360nc@gmail.com');
        }

        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
            btn.disabled = false;
        }, 3500);
    });
}

// ===== Tool / Service Request Forms =====
document.querySelectorAll('.tool-request-form').forEach(form => {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        data.service_type = data.service_type || document.title.split('|')[0].trim();

        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.textContent;
        btn.textContent = 'Requesting...';
        btn.disabled = true;

        try {
            const result = await API.submitConsultation(data);
            if (result.ok) {
                btn.textContent = 'Request Sent!';
                form.reset();
                Toast.success('Demo request received! We will contact you soon.');
            } else {
                throw new Error('Failed');
            }
        } catch {
            Toast.error('Failed to send request. Please try again.');
            btn.textContent = originalText;
            btn.disabled = false;
            return;
        }
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
            btn.disabled = false;
        }, 3500);
    });
});

// ===== Intersection Observer for Animations =====
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.service-card, .solution-item, .why-card, .tool-card').forEach((item, i) => {
    item.style.opacity = '0';
    item.style.transform = 'translateY(24px)';
    item.style.transition = 'opacity 0.5s ease ' + (i * 0.07) + 's, transform 0.5s ease ' + (i * 0.07) + 's';
    observer.observe(item);
});

const animStyle = document.createElement('style');
animStyle.textContent = '.animate-in { opacity: 1 !important; transform: translateY(0) !important; }';
document.head.appendChild(animStyle);

// ===== Parallax Effect for Hero =====
if (document.querySelector('.hero')) {
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroVisual = document.querySelector('.agent-visual');
        if (heroVisual && scrolled < window.innerHeight) {
            heroVisual.style.transform = 'translateY(' + (scrolled * 0.08) + 'px)';
        }
    });
}

// ===== Load Services from API (if placeholder exists) =====
const servicesApiList = document.getElementById('services-api-list');
if (servicesApiList && typeof API !== 'undefined') {
    (async () => {
        const result = await API.getServices();
        if (result.ok && result.data && result.data.services) {
            servicesApiList.innerHTML = result.data.services.map(s =>
                '<div class="service-card"><h3>' + s.name + '</h3><p class="service-price">Starting at <strong>$' + s.price + '</strong></p><a href="#contact" class="service-link">Get Started</a></div>'
            ).join('');
        }
    })();
}

// ===== Console Branding =====
console.log('%c Empower Hub 360 NC', 'font-size:22px;font-weight:bold;background:linear-gradient(135deg,#6366f1,#0ea5e9);color:white;padding:10px 20px;border-radius:8px;');
console.log('%cAutonomous Agentic AI Solutions  |  API Docs: http://localhost:8003/docs', 'color:#94a3b8;');
