export default function TicketDisplay({ tickets }) {
    if (!tickets || tickets.length === 0) {
        return (
            <div className="card text-center">
                <p style={{ color: 'var(--color-text-muted)' }}>
                    Nenhum ingresso atribuído ainda
                </p>
            </div>
        );
    }

    return (
        <div className="card animate-fadeIn">
            <h2>Ingressos Distribuídos</h2>
            <p>Total de {tickets.length} ingresso(s)</p>

            <div className="grid grid-3 gap-2 mt-2">
                {tickets.map((ticket) => (
                    <div
                        key={ticket.id}
                        className={`ticket ${ticket.is_winner ? 'animate-pulse' : ''}`}
                        style={{
                            background: ticket.is_winner
                                ? 'linear-gradient(135deg, hsl(45, 93%, 58%) 0%, hsl(340, 82%, 52%) 100%)'
                                : 'var(--gradient-primary)',
                        }}
                    >
                        <div style={{ position: 'relative', zIndex: 1 }}>
                            <div className="ticket-number">#{ticket.ticket_number}</div>
                            <div style={{ textAlign: 'center', marginTop: 'var(--spacing-sm)' }}>
                                <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>
                                    {ticket.participant.name}
                                </div>
                                <div style={{ fontSize: '0.9rem', opacity: 0.9 }}>
                                    {ticket.participant.email}
                                </div>
                                {ticket.is_winner && (
                                    <div style={{
                                        marginTop: 'var(--spacing-sm)',
                                        fontSize: '1.5rem',
                                        animation: 'bounce 1s ease-in-out infinite'
                                    }}>
                                        🏆 VENCEDOR!
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
