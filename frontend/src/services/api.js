const API_BASE_URL = 'http://localhost:8000/api';

// Participant API
export const participantAPI = {
    create: async (data) => {
        const response = await fetch(`${API_BASE_URL}/participants/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create participant');
        }
        return response.json();
    },

    list: async () => {
        const response = await fetch(`${API_BASE_URL}/participants/`);
        if (!response.ok) throw new Error('Failed to fetch participants');
        return response.json();
    },

    get: async (id) => {
        const response = await fetch(`${API_BASE_URL}/participants/${id}`);
        if (!response.ok) throw new Error('Failed to fetch participant');
        return response.json();
    },
};

// Raffle API
export const raffleAPI = {
    create: async (data) => {
        const response = await fetch(`${API_BASE_URL}/raffles/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create raffle');
        }
        return response.json();
    },

    list: async () => {
        const response = await fetch(`${API_BASE_URL}/raffles/`);
        if (!response.ok) throw new Error('Failed to fetch raffles');
        return response.json();
    },

    get: async (id) => {
        const response = await fetch(`${API_BASE_URL}/raffles/${id}`);
        if (!response.ok) throw new Error('Failed to fetch raffle');
        return response.json();
    },

    getTickets: async (id) => {
        const response = await fetch(`${API_BASE_URL}/raffles/${id}/tickets`);
        if (!response.ok) throw new Error('Failed to fetch tickets');
        return response.json();
    },

    assignTickets: async (id, tickets) => {
        const response = await fetch(`${API_BASE_URL}/raffles/${id}/assign-tickets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tickets }),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to assign tickets');
        }
        return response.json();
    },

    draw: async (id) => {
        const response = await fetch(`${API_BASE_URL}/raffles/${id}/draw`, {
            method: 'POST'
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to draw raffle');
        }
        return response.json();
    },

    duplicate: async (id) => {
        const response = await fetch(`${API_BASE_URL}/raffles/${id}/duplicate`, {
            method: 'POST'
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to duplicate raffle');
        }
        return response.json();
    },
};

// Instagram API
export const instagramAPI = {
    createRaffle: async (data) => {
        const response = await fetch(`${API_BASE_URL}/instagram/raffles/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const error = await response.json();
            // Handle both string and object error formats
            const errorMessage = typeof error.detail === 'string'
                ? error.detail
                : error.detail?.message || JSON.stringify(error.detail) || 'Failed to create Instagram raffle';
            throw new Error(errorMessage);
        }
        return response.json();
    },

    scrapePost: async (raffleId) => {
        const response = await fetch(`${API_BASE_URL}/instagram/raffles/${raffleId}/scrape`, {
            method: 'POST',
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to scrape Instagram post');
        }
        return response.json();
    },

    getParticipants: async (raffleId, validOnly = false) => {
        const url = `${API_BASE_URL}/instagram/raffles/${raffleId}/participants?valid_only=${validOnly}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch participants');
        return response.json();
    },

    validateParticipants: async (raffleId) => {
        const response = await fetch(`${API_BASE_URL}/instagram/raffles/${raffleId}/validate`, {
            method: 'POST',
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to validate participants');
        }
        return response.json();
    },

    draw: async (raffleId) => {
        const response = await fetch(`${API_BASE_URL}/instagram/raffles/${raffleId}/draw`, {
            method: 'POST',
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to draw raffle');
        }
        return response.json();
    },

    listRaffles: async () => {
        const response = await fetch(`${API_BASE_URL}/instagram/raffles/`);
        if (!response.ok) throw new Error('Failed to fetch Instagram raffles');
        return response.json();
    },

    getRaffle: async (raffleId) => {
        const response = await fetch(`${API_BASE_URL}/instagram/raffles/${raffleId}`);
        if (!response.ok) throw new Error('Failed to fetch Instagram raffle');
        return response.json();
    },

    deleteRaffle: async (raffleId) => {
        const response = await fetch(`${API_BASE_URL}/instagram/raffles/${raffleId}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete raffle');
        }
        return response.json();
    },

    login: async (username, password) => {
        const response = await fetch(`${API_BASE_URL}/instagram/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Instagram login failed');
        }
        return response.json();
    },

    duplicateRaffle: async (raffleId) => {
        const response = await fetch(`${API_BASE_URL}/instagram/raffles/${raffleId}/duplicate`, {
            method: 'POST'
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to duplicate raffle');
        }
        return response.json();
    },
};
