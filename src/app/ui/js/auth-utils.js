class AuthUtils {
    static showPageTransition(message = 'Redirecting...') {
        this.hidePageTransition();
        
        const overlay = document.createElement('div');
        overlay.className = 'page-transition';
        overlay.id = 'page-transition';
        overlay.innerHTML = `
            <div class="transition-content">
                <div class="transition-spinner"></div>
                <div class="transition-text">${message}</div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        setTimeout(() => {
            overlay.classList.add('show');
        }, 10);
        
        return overlay;
    }
    
    static hidePageTransition() {
        const overlay = document.getElementById('page-transition');
        if (overlay) {
            overlay.classList.remove('show');
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }
    }
    
    static showAuthCheckOverlay(message = 'Checking authentication...') {
        this.hideAuthCheckOverlay();
        
        const overlay = document.createElement('div');
        overlay.className = 'auth-check-overlay';
        overlay.id = 'auth-check-overlay';
        overlay.innerHTML = `
            <div class="auth-check-content">
                <div class="auth-check-spinner"></div>
                <div class="auth-check-text">${message}</div>
                <div class="auth-check-subtext">Please wait...</div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        setTimeout(() => {
            overlay.classList.add('show');
        }, 10);
        
        return overlay;
    }
    
    static hideAuthCheckOverlay() {
        const overlay = document.getElementById('auth-check-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }
    }
    
    static showErrorOverlay(title, message, actions = []) {
        this.hideErrorOverlay();
        
        const actionsHtml = actions.map(action => 
            `<button class="error-btn ${action.type || 'primary'}" onclick="${action.onClick}">${action.text}</button>`
        ).join('');
        
        const overlay = document.createElement('div');
        overlay.className = 'error-overlay';
        overlay.id = 'error-overlay';
        overlay.innerHTML = `
            <div class="error-content">
                <div class="error-icon"><i class="fas fa-triangle-exclamation fa-xl" style="color: #FFD43B;"></i></div>
                <div class="error-title">${title}</div>
                <div class="error-message">${message}</div>
                <div class="error-actions">
                    ${actionsHtml || '<button class="error-btn primary" onclick="AuthUtils.hideErrorOverlay()">OK</button>'}
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        setTimeout(() => {
            overlay.classList.add('show');
        }, 10);
        
        return overlay;
    }
    
    static hideErrorOverlay() {
        const overlay = document.getElementById('error-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }
    }
    
    static async smoothRedirect(url, message = 'Redirecting...', delay = 1000) {
        this.showPageTransition(message);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        
        window.location.href = url;
    }
    
    static async checkAuthentication() {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                throw new Error('No access token found');
            }

            const response = await fetch('/api/v1/auth/user/', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error('Token invalid or expired');
            }
        } catch (error) {
            throw error;
        }
    }
    
    static async refreshToken() {
        try {
            const response = await fetch('/api/v1/auth/user/refresh', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.access_token) {
                    localStorage.setItem('access_token', data.access_token);
                    return data.access_token;
                }
            }
            throw new Error('Token refresh failed');
        } catch (error) {
            console.error('Token refresh failed:', error);
            throw error;
        }
    }

    static async checkAuthenticationWithRefresh() {
        try {
            return await this.checkAuthentication();
        } catch (error) {
            try {
                await this.refreshToken();
                return await this.checkAuthentication();
            } catch (refreshError) {
                throw refreshError;
            }
        }
    }
    
    static clearAuthData() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    }
    
    static async handleAuthFailure(error, customMessage = null) {
        console.error('Authentication failed:', error);
        
        this.clearAuthData();
        
        const message = customMessage || 'Your session has expired. Please log in again.';
        
        this.showErrorOverlay(
            'Authentication Required',
            message,
            [
                {
                    text: 'Go to Login',
                    type: 'primary',
                    onClick: 'AuthUtils.goToLogin()'
                }
            ]
        );
    }
    
    static goToLogin() {
        this.hideErrorOverlay();
        this.smoothRedirect('/login', 'Redirecting to login...', 500);
    }
    
    static setButtonLoading(buttonId, loading = true) {
        const button = document.getElementById(buttonId);
        if (button) {
            if (loading) {
                button.classList.add('loading');
                button.disabled = true;
            } else {
                button.classList.remove('loading');
                button.disabled = false;
            }
        }
    }
    
    static showAlert(message, type = 'info', containerId = 'alert-container', autoHide = true) {
        const alertContainer = document.getElementById(containerId);
        if (!alertContainer) return;
        
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;
        
        if (autoHide && (type === 'info' || type === 'success')) {
            setTimeout(() => {
                alertContainer.innerHTML = '';
            }, 3000);
        }
    }
    
    static async withRetry(operation, maxRetries = 2, delay = 1000) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                if (attempt === maxRetries) {
                    throw error;
                }
                
                await new Promise(resolve => setTimeout(resolve, delay));
                delay *= 1.5;
            }
        }
    }

    static async checkAuthenticationWithRetry() {
        return this.withRetry(async () => {
            return await this.checkAuthenticationWithRefresh();
        }, 2, 500);
    }

    static showNetworkErrorOverlay(error, onRetry) {
        this.showErrorOverlay(
            'Connection Problem',
            'Unable to connect to the server. Please check your internet connection and try again.',
            [
                {
                    text: 'Retry',
                    type: 'primary',
                    onClick: `AuthUtils.hideErrorOverlay(); (${onRetry.toString()})()`
                },
                {
                    text: 'Go to Login',
                    type: 'secondary',
                    onClick: 'AuthUtils.goToLogin()'
                }
            ]
        );
    }
}

window.AuthUtils = AuthUtils;

document.addEventListener('DOMContentLoaded', function() {
    const protectedPages = ['/dashboard'];
    const currentPath = window.location.pathname;
    
    if (protectedPages.includes(currentPath)) {
        checkPageAuthentication();
    }
});

async function checkPageAuthentication() {
    const authOverlay = AuthUtils.showAuthCheckOverlay('Checking your session...');
    
    try {
        const token = localStorage.getItem('access_token');
        if (!token) {
            throw new Error('No authentication token found');
        }
        
        await AuthUtils.checkAuthenticationWithRetry();
        
        setTimeout(() => {
            AuthUtils.hideAuthCheckOverlay();
        }, 300);
        
    } catch (error) {
        console.error('Page authentication check failed:', error);
        
        AuthUtils.hideAuthCheckOverlay();
        
        if (error.message.includes('fetch') || error.message.includes('network')) {
            setTimeout(() => {
                AuthUtils.showNetworkErrorOverlay(error, checkPageAuthentication);
            }, 500);
        } else {
            AuthUtils.clearAuthData();
            
            setTimeout(() => {
                AuthUtils.handleAuthFailure(
                    error, 
                    'You need to be logged in to access this page. Please sign in to continue.'
                );
            }, 500);
        }
    }
}
