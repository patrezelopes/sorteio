import { useState, useEffect } from 'react';
import { raffleAPI, participantAPI } from '../services/api';

export default function RaffleManager({ onRaffleCreated }) {
    const [raffles, setRaffles] = useState([]);
    const [participants, setParticipants] = useState([]);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
    });
    const [selectedRaffle, setSelectedRaffle] = useState(null);
    const [ticketAssignments, setTicketAssignments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    useEffect(() => {
        loadRaffles();
        loadParticipants();
    }, []);

    const loadRaffles = async () => {
        try {
            const data = await raffleAPI.list();
            setRaffles(data);
        } catch (err) {
            console.error('Failed to load raffles:', err);
        }
    };

    const loadParticipants = async () => {
        try {
            const data = await participantAPI.list();
            setParticipants(data);
        } catch (err) {
            console.error('Failed to load participants:', err);
        }
    };

    const handleCreateRaffle = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const raffle = await raffleAPI.create(formData);
            setSuccess('Sorteio criado com sucesso!');
            setFormData({ name: '', description: '' });
            loadRaffles();
            if (onRaffleCreated) onRaffleCreated(raffle);
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleAssignTickets = async () => {
        if (!selectedRaffle || ticketAssignments.length === 0) {
            setError('Selecione um sorteio e adicione pelo menos um ingresso');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            await raffleAPI.assignTickets(selectedRaffle, ticketAssignments);
            setSuccess('Ingressos atribuídos com sucesso!');
            setTicketAssignments([]);
            setSelectedRaffle(null);
            loadRaffles();
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const addTicketAssignment = () => {
        setTicketAssignments([
            ...ticketAssignments,
            { participant_id: '', ticket_number: '' }
        ]);
    };

    const updateTicketAssignment = (index, field, value) => {
        const updated = [...ticketAssignments];
        updated[index][field] = value;
        setTicketAssignments(updated);
    };

    const removeTicketAssignment = (index) => {
        setTicketAssignments(ticketAssignments.filter((_, i) => i !== index));
    };

    return (
        <div className="grid grid-2 gap-3">
            <div className="card animate-fadeIn">
                <h2>Criar Sorteio</h2>
                <p>Configure um novo sorteio de ingressos</p>

                {error && <div className="alert alert-error">❌ {error}</div>}
                {success && <div className="alert alert-success">✅ {success}</div>}

                <form onSubmit={handleCreateRaffle}>
                    <div className="input-group">
                        <label htmlFor="raffle-name" className="input-label">Nome do Sorteio</label>
                        <input
                            type="text"
                            id="raffle-name"
                            className="input"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            placeholder="Ex: Sorteio de Ingressos VIP"
                            required
                        />
                    </div>

                    <div className="input-group">
                        <label htmlFor="raffle-description" className="input-label">Descrição</label>
                        <input
                            type="text"
                            id="raffle-description"
                            className="input"
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            placeholder="Descreva o sorteio"
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
                        {loading ? '⏳ Criando...' : '🎫 Criar Sorteio'}
                    </button>
                </form>

                <div className="mt-3">
                    <h3>Sorteios Criados</h3>
                    {raffles.length === 0 ? (
                        <p style={{ color: 'var(--color-text-muted)' }}>Nenhum sorteio criado ainda</p>
                    ) : (
                        <div className="grid gap-2 mt-2">
                            {raffles.map((raffle) => (
                                <div key={raffle.id} className="card-glass" style={{ padding: 'var(--spacing-md)' }}>
                                    <div className="flex justify-between items-center">
                                        <div>
                                            <h4 style={{ margin: 0 }}>{raffle.name}</h4>
                                            <p style={{ margin: 0, fontSize: '0.9rem' }}>
                                                Status: <span className={`badge-${raffle.status}`}>{raffle.status}</span>
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <div className="card animate-fadeIn">
                <h2>Atribuir Ingressos</h2>
                <p>Distribua ingressos para os participantes</p>

                <div className="input-group">
                    <label htmlFor="select-raffle" className="input-label">Selecionar Sorteio</label>
                    <select
                        id="select-raffle"
                        className="input"
                        value={selectedRaffle || ''}
                        onChange={(e) => setSelectedRaffle(e.target.value)}
                    >
                        <option value="">Escolha um sorteio</option>
                        {raffles.filter(r => r.status !== 'completed').map((raffle) => (
                            <option key={raffle.id} value={raffle.id}>
                                {raffle.name}
                            </option>
                        ))}
                    </select>
                </div>

                {ticketAssignments.map((assignment, index) => (
                    <div key={index} className="card-glass mb-2" style={{ padding: 'var(--spacing-md)' }}>
                        <div className="grid grid-2 gap-2">
                            <div className="input-group" style={{ marginBottom: 0 }}>
                                <label className="input-label">Participante</label>
                                <select
                                    className="input"
                                    value={assignment.participant_id}
                                    onChange={(e) => updateTicketAssignment(index, 'participant_id', parseInt(e.target.value))}
                                >
                                    <option value="">Selecione</option>
                                    {participants.map((p) => (
                                        <option key={p.id} value={p.id}>{p.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="input-group" style={{ marginBottom: 0 }}>
                                <label className="input-label">Número do Ingresso</label>
                                <input
                                    type="text"
                                    className="input"
                                    value={assignment.ticket_number}
                                    onChange={(e) => updateTicketAssignment(index, 'ticket_number', e.target.value)}
                                    placeholder="001"
                                />
                            </div>
                        </div>
                        <button
                            type="button"
                            className="btn btn-secondary mt-1"
                            onClick={() => removeTicketAssignment(index)}
                            style={{ width: '100%' }}
                        >
                            ❌ Remover
                        </button>
                    </div>
                ))}

                <button
                    type="button"
                    className="btn btn-secondary mb-2"
                    onClick={addTicketAssignment}
                    style={{ width: '100%' }}
                >
                    ➕ Adicionar Ingresso
                </button>

                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleAssignTickets}
                    disabled={loading || !selectedRaffle || ticketAssignments.length === 0}
                    style={{ width: '100%' }}
                >
                    {loading ? '⏳ Atribuindo...' : '✅ Atribuir Ingressos'}
                </button>
            </div>
        </div>
    );
}
