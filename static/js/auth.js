const Auth = {
    // Keys
    TOKEN_KEY: 'sentiment_jwt_token',
    USER_KEY: 'sentiment_user_info',

    // API Endpoints
    API_LOGIN: '/auth/login',
    API_REGISTER: '/auth/register',
    API_ME: '/auth/me',

    // Methods
    async login(username, password) {
        try {
            const response = await fetch(this.API_LOGIN, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                this.setToken(data.access_token);
                this.setUser(data.user);
                return true;
            } else {
                throw new Error(data.message || 'Login failed');
            }
        } catch (error) {
            console.error('Login Error:', error);
            throw error;
        }
    },

    async register(username, email, password) {
        try {
            const response = await fetch(this.API_REGISTER, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                return true;
            } else {
                throw new Error(data.message || 'Registration failed');
            }
        } catch (error) {
            console.error('Register Error:', error);
            throw error;
        }
    },

    logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        window.location.href = '/login';
    },

    // Token Management
    setToken(token) {
        localStorage.setItem(this.TOKEN_KEY, token);
    },

    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    },

    setUser(user) {
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    },

    getUser() {
        const user = localStorage.getItem(this.USER_KEY);
        return user ? JSON.parse(user) : null;
    },

    isLoggedIn() {
        return !!this.getToken();
    },

    // Helper for authenticated fetch
    async fetchAuth(url, options = {}) {
        const token = this.getToken();
        if (!token) return null;

        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };

        const response = await fetch(url, { ...options, headers });

        if (response.status === 401) {
            this.logout(); // Token expired
            return null;
        }

        return response;
    }
};
