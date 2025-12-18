import { useState, useEffect } from 'react';
import { raffleAPI } from '../services/api';

export default function DrawInterface({ onDrawComplete }) {
    const [raffles, setRaffles] = useState([]);
    const [selectedRaffle, setSelectedRaffle] = useState(null);
    const [tickets, setTickets] = useState([]);
    const [drawing, setDrawing] = useState(false);
    const [winner, setWinner] = useState(null);
    const [animatingNumber, setAnimatingNumber] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadRaffles();
    }, []);

    const loadRaffles = async () => {
        try {
            const data = await raffleAPI.list();
            setRaffles(data.filter(r => r.status === 'active'));
        } catch (err) {
            console.error('Failed to load raffles:', err);
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

    const handleRaffleSelect = (raffleId) => {
        setSelectedRaffle(raffleId);
        setWinner(null);
        setError(null);
        if (raffleId) {
            loadTickets(raffleId);
        } else {
            setTickets([]);
        }
    };

    const performDraw = async () => {
        if (!selectedRaffle) {
            setError('Selecione um sorteio primeiro');
            return;
        }

        if (tickets.length === 0) {
            setError('Nenhum ingresso disponível para sorteio');
            return;
        }

        setDrawing(true);
        setError(null);
        setWinner(null);

        // Animation: cycle through random numbers
        const animationDuration = 3000;
        const intervalTime = 100;
        const iterations = animationDuration / intervalTime;
        let count = 0;

        const interval = setInterval(() => {
            const randomTicket = tickets[Math.floor(Math.random() * tickets.length)];
            setAnimatingNumber(randomTicket.ticket_number);
            count++;

            if (count >= iterations) {
                clearInterval(interval);
                // Perform actual draw
                executeDraw();
            }
        }, intervalTime);
    };

    const executeDraw = async () => {
        try {
            const result = await raffleAPI.draw(selectedRaffle);
            setWinner(result.winner_ticket);
            setAnimatingNumber(null);

            // Trigger confetti or celebration
            setTimeout(() => {
                if (onDrawComplete) onDrawComplete(result);
            }, 2000);
        } catch (err) {
            setError(err.message);
            setAnimatingNumber(null);
        } finally {
            setDrawing(false);
        }
    };

    return (
        <div className="card animate-fadeIn">
            <h2 className="text-center">🎲 Realizar Sorteio</h2>
            <p className="text-center">Selecione um sorteio e clique para sortear o vencedor</p>

            {error && <div className="alert alert-error">❌ {error}</div>}

            <div className="input-group">
                <label htmlFor="draw-raffle" className="input-label">Selecionar Sorteio</label>
                <select
                    id="draw-raffle"
                    className="input"
                    value={selectedRaffle || ''}
                    onChange={(e) => handleRaffleSelect(e.target.value)}
                    disabled={drawing}
                >
                    <option value="">Escolha um sorteio ativo</option>
                    {raffles.map((raffle) => (
                        <option key={raffle.id} value={raffle.id}>
                            {raffle.name}
                        </option>
                    ))}
                </select>
            </div>

            {selectedRaffle && tickets.length > 0 && (
                <div className="text-center mb-2">
                    <p style={{ color: 'var(--color-text-secondary)' }}>
                        Total de {tickets.length} ingresso(s) participando
                    </p>
                </div>
            )}

            {/* Animation Display */}
            {(drawing || winner) && (
                <div
                    className="card-glass text-center mb-3"
                    style={{
                        padding: 'var(--spacing-xl)',
                        background: winner
                            ? 'linear-gradient(135deg, hsl(45, 93%, 58%) 0%, hsl(340, 82%, 52%) 100%)'
                            : 'var(--gradient-primary)'
                    }}
                >
                    {drawing && animatingNumber && (
                        <div className="animate-pulse">
                            <div style={{ fontSize: '4rem', fontWeight: 800, color: 'white' }}>
                                #{animatingNumber}
                            </div>
                            <div style={{ fontSize: '1.2rem', color: 'white', marginTop: 'var(--spacing-sm)' }}>
                                Sorteando...
                            </div>
                        </div>
                    )}

                    {winner && (
                        <div className="animate-fadeIn">
                            <div style={{ fontSize: '5rem', marginBottom: 'var(--spacing-md)' }}>
                                🎉
                            </div>
                            <div style={{ fontSize: '4rem', fontWeight: 800, color: 'white', marginBottom: 'var(--spacing-sm)' }}>
                                #{winner.ticket_number}
                            </div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 600, color: 'white' }}>
                                {winner.participant.name}
                            </div>
                            <div style={{ fontSize: '1.1rem', color: 'white', opacity: 0.9, marginTop: 'var(--spacing-xs)' }}>
                                {winner.participant.email}
                            </div>
                            <div style={{
                                fontSize: '2rem',
                                fontWeight: 700,
                                color: 'white',
                                marginTop: 'var(--spacing-md)',
                                textTransform: 'uppercase',
                                letterSpacing: '2px'
                            }}>
                                🏆 Vencedor! 🏆
                            </div>
                        </div>
                    )}
                </div>
            )}

            <button
                type="button"
                className="btn btn-primary"
                onClick={performDraw}
                disabled={drawing || !selectedRaffle || tickets.length === 0 || winner}
                style={{
                    width: '100%',
                    fontSize: '1.2rem',
                    padding: 'var(--spacing-md) var(--spacing-xl)'
                }}
            >
                {drawing ? (
                    <>
                        <div className="spinner" style={{ width: '24px', height: '24px', borderWidth: '3px' }}></div>
                        Sorteando...
                    </>
                ) : winner ? (
                    '✅ Sorteio Concluído'
                ) : (
                    '🎲 Realizar Sorteio'
                )}
            </button>

            {winner && (
                <>
                    <button
                        type="button"
                        className="btn btn-primary mt-2"
                        onClick={async () => {
                            try {
                                setDrawing(true);
                                setError(null);

                                // Duplicate the raffle with same participants
                                const newRaffle = await raffleAPI.duplicate(selectedRaffle);

                                // Select the new raffle automatically
                                setSelectedRaffle(newRaffle.id);
                                setWinner(null);
                                setAnimatingNumber(null);

                                // Load tickets for the new raffle
                                await loadTickets(newRaffle.id);

                                // Reload raffles list
                                await loadRaffles();

                                setDrawing(false);
                            } catch (err) {
                                setError(err.message);
                                setDrawing(false);
                            }
                        }}
                        disabled={drawing}
                        style={{ width: '100%' }}
                    >
                        {drawing ? (
                            <>
                                <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
                                Preparando...
                            </>
                        ) : (
                            '🔄 Sortear Novamente'
                        )}
                    </button>

                    <button
                        type="button"
                        className="btn btn-secondary mt-2"
                        onClick={() => {
                            setWinner(null);
                            setSelectedRaffle(null);
                            setTickets([]);
                            loadRaffles();
                        }}
                        style={{ width: '100%' }}
                    >
                        ↩️ Novo Sorteio
                    </button>
                </>
            )}
        </div>
    );
}
