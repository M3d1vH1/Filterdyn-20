/**
 * Floating Buttons Coordinator
 * Manages positioning and interaction of all floating buttons
 */

class FloatingButtonsCoordinator {
    constructor() {
        this.buttons = new Map();
        this.positions = {
            right: 20,
            bottom: 20,
            gap: 15
        };
        this.init();
    }

    init() {
        this.setupPositioning();
        this.handleResize();
    }

    registerButton(id, element, priority = 1) {
        this.buttons.set(id, {
            element: element,
            priority: priority,
            visible: true
        });
        this.updatePositions();
    }

    unregisterButton(id) {
        this.buttons.delete(id);
        this.updatePositions();
    }

    updatePositions() {
        // Sort buttons by priority (higher priority = closer to corner)
        const sortedButtons = Array.from(this.buttons.entries())
            .filter(([id, button]) => button.visible)
            .sort((a, b) => b[1].priority - a[1].priority);

        let currentRight = this.positions.right;
        
        sortedButtons.forEach(([id, button], index) => {
            const element = button.element;
            if (element) {
                if (window.innerWidth <= 768) {
                    // Mobile: stack vertically
                    element.style.right = this.positions.right + 'px';
                    element.style.bottom = (this.positions.bottom + (index * 65)) + 'px';
                } else {
                    // Desktop: arrange horizontally
                    element.style.right = currentRight + 'px';
                    element.style.bottom = this.positions.bottom + 'px';
                    currentRight += 75; // 60px button + 15px gap
                }
            }
        });
    }

    setupPositioning() {
        // Override inline styles with coordinated positioning
        const style = document.createElement('style');
        style.id = 'floating-buttons-coordinator';
        style.textContent = `
            .floating-dictation-btn,
            .ai-assistant-floating,
            .quick-add-floating {
                position: fixed !important;
                transition: all 0.3s ease !important;
            }
            
            .floating-dictation-btn {
                z-index: 10002 !important;
            }
            
            .ai-assistant-floating {
                z-index: 10001 !important;
            }
            
            .dictation-status {
                z-index: 10003 !important;
            }
        `;
        
        if (!document.getElementById('floating-buttons-coordinator')) {
            document.head.appendChild(style);
        }
    }

    handleResize() {
        window.addEventListener('resize', () => {
            this.updatePositions();
        });
    }

    setButtonVisibility(id, visible) {
        const button = this.buttons.get(id);
        if (button) {
            button.visible = visible;
            button.element.style.display = visible ? 'flex' : 'none';
            this.updatePositions();
        }
    }
}

// Initialize coordinator when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (!window.floatingButtonsCoordinator) {
        window.floatingButtonsCoordinator = new FloatingButtonsCoordinator();
        
        // Register existing buttons after a short delay
        setTimeout(() => {
            const dictationBtn = document.querySelector('.floating-dictation-btn');
            const aiAssistantBtn = document.querySelector('.ai-assistant-floating');
            
            if (dictationBtn) {
                window.floatingButtonsCoordinator.registerButton('dictation', dictationBtn, 3);
            }
            
            if (aiAssistantBtn) {
                window.floatingButtonsCoordinator.registerButton('ai-assistant', aiAssistantBtn, 2);
            }
        }, 500);
    }
});