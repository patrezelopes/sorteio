import { useState } from 'react';
import ParticipantForm from './components/ParticipantForm';
import RaffleManager from './components/RaffleManager';
import DrawInterface from './components/DrawInterface';
import TicketDisplay from './components/TicketDisplay';
import InstagramRaffle from './components/InstagramRaffle';
import { raffleAPI } from './services/api';
import './index.css';

function App() {
    const [activeTab, setActiveTab] = useState('register');
    const [selectedRaffleForTickets, setSelectedRaffleForTickets] = useState(null);
    const [tickets, setTickets] = useState([]);

    const handleRaffleCreated = (raffle) => {
        console.log('Raffle created:', raffle);
    };

    const handleDrawComplete = (result) => {
        console.log('Draw completed:', result);
        // Reload tickets to show winner
        if (selectedRaffleForTickets) {
            loadTickets(selectedRaffleForTickets);
        }
    };

    const loadTickets = async (raffleId) => {
        try {
            const data = await raffleAPI.getTickets(raffleId);
            setTickets(data);
        } catch (err) {
            console.error('Failed to load tickets:', err);
        }
    };

    const handleViewTickets = async () => {
        const raffles = await raffleAPI.list();
        if (raffles.length > 0) {
            const raffleId = raffles[0].id;
            setSelectedRaffleForTickets(raffleId);
            loadTickets(raffleId);
        }
    };

    return (
        <div style={{ minHeight: '100vh' }}>
            {/* Header */}
            <header style={{
                background: 'var(--gradient-primary)',
                padding: 'var(--spacing-xl) 0',
                textAlign: 'center',
                boxShadow: 'var(--shadow-lg)',
            }}>
                <div className="container">
                    <h1 style={{
                        fontSize: '3.5rem',
                        marginBottom: 'var(--spacing-sm)',
                        color: 'white',
                        textShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
                        background: 'none',
                        WebkitTextFillColor: 'white'
                    }}>
                        🎫 Sorteio de Ingressos
                    </h1>
                    <p style={{
                        fontSize: '1.2rem',
                        color: 'rgba(255, 255, 255, 0.9)',
                        maxWidth: '600px',
                        margin: '0 auto'
                    }}>
                        Sistema completo para gerenciar sorteios de forma justa e transparente
                    </p>
                </div>
            </header>

            {/* Navigation Tabs */}
            <div className="container mt-3">
                <div className="flex gap-2 justify-center" style={{ flexWrap: 'wrap' }}>
                    <button
                        className={`btn ${activeTab === 'instagram' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setActiveTab('instagram')}
                    >
                        📸 Instagram
                    </button>
                    <button
                        className={`btn ${activeTab === 'register' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setActiveTab('register')}
                    >
                        👤 Registrar
                    </button>
                    <button
                        className={`btn ${activeTab === 'manage' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setActiveTab('manage')}
                    >
                        ⚙️ Gerenciar
                    </button>
                    <button
                        className={`btn ${activeTab === 'draw' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setActiveTab('draw')}
                    >
                        🎲 Sortear
                    </button>
                    <button
                        className={`btn ${activeTab === 'tickets' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => {
                            setActiveTab('tickets');
                            handleViewTickets();
                        }}
                    >
                        🎟️ Ingressos
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <main className="container mt-3 mb-3">
                {activeTab === 'instagram' && <InstagramRaffle />}

                {activeTab === 'register' && (
                    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
                        <ParticipantForm onSuccess={() => console.log('Participant registered')} />
                    </div>
                )}

                {activeTab === 'manage' && (
                    <RaffleManager onRaffleCreated={handleRaffleCreated} />
                )}

                {activeTab === 'draw' && (
                    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                        <DrawInterface onDrawComplete={handleDrawComplete} />
                    </div>
                )}

                {activeTab === 'tickets' && (
                    <TicketDisplay tickets={tickets} />
                )}
            </main>

            {/* Footer */}
            <footer style={{
                background: 'var(--color-bg-secondary)',
                padding: 'var(--spacing-lg)',
                textAlign: 'center',
                marginTop: 'auto',
                borderTop: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
                <p style={{ color: 'var(--color-text-muted)', margin: 0 }}>
                    Sistema de Sorteio de Ingressos © 2025
                </p>
            </footer>
        </div>
    );
}

export default App;
