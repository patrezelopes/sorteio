import { useState, useEffect } from 'react';
import { instagramAPI } from '../services/api';

export default function InstagramRaffle() {
    const [raffles, setRaffles] = useState([]);
    const [selectedRaffle, setSelectedRaffle] = useState(null);
    const [participants, setParticipants] = useState([]);
    const [formData, setFormData] = useState({
        post_url: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [scraping, setScraping] = useState(false);
    const [filter, setFilter] = useState('all'); // all, valid, invalid

    useEffect(() => {
        loadRaffles();
    }, []);

    useEffect(() => {
        if (selectedRaffle) {
            loadParticipants(selectedRaffle);
        }
    }, [selectedRaffle, filter]);

    const loadRaffles = async () => {
        try {
            const data = await instagramAPI.listRaffles();
            setRaffles(data);
        } catch (err) {
            console.error('Failed to load raffles:', err);
        }
    };

    const loadParticipants = async (raffleId) => {
        try {
            const validOnly = filter === 'valid';
            const data = await instagramAPI.getParticipants(raffleId, validOnly);

            if (filter === 'invalid') {
                setParticipants(data.filter(p => p.is_validated && !p.is_valid));
            } else {
                setParticipants(data);
            }
        } catch (err) {
            console.error('Failed to load participants:', err);
        }
    };

    const handleCreateRaffle = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const raffle = await instagramAPI.createRaffle({
                post_url: formData.post_url,
            });

            setSuccess('Sorteio do Instagram criado com sucesso!');
            setFormData({
                post_url: '',
            });
            loadRaffles();
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleScrapePost = async (raffleId) => {
        setScraping(true);
        setError(null);

        try {
            const result = await instagramAPI.scrapePost(raffleId);
            setSuccess(`✅ ${result.participants_found} participantes coletados!`);
            loadParticipants(raffleId);
            loadRaffles();
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError(err.message);
        } finally {
            setScraping(false);
        }
    };


    const handleDraw = async (raffleId) => {
        if (!confirm('Tem certeza que deseja realizar o sorteio?')) return;

        setLoading(true);
        setError(null);

        try {
            const result = await instagramAPI.draw(raffleId);
            setSuccess(`🎉 Vencedor: @${result.winner.username}!`);
            loadParticipants(raffleId);
            loadRaffles();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteRaffle = async (raffleId) => {
        if (!confirm('⚠️ Tem certeza que deseja deletar este sorteio? Esta ação não pode ser desfeita!')) return;

        setLoading(true);
        setError(null);

        try {
            await instagramAPI.deleteRaffle(raffleId);
            setSuccess('🗑️ Sorteio deletado com sucesso!');

            // Clear selected raffle if it was deleted
            if (selectedRaffle === raffleId) {
                setSelectedRaffle(null);
                setParticipants([]);
            }

            loadRaffles();
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status) => {
        const badges = {
            collecting: { text: 'Coletando', color: 'var(--color-warning)' },
            validating: { text: 'Validando', color: 'var(--color-accent)' },
            completed: { text: 'Concluído', color: 'var(--color-success)' },
        };
        const badge = badges[status] || badges.collecting;
        return (
            <span style={{
                background: badge.color,
                color: 'white',
                padding: '0.25rem 0.75rem',
                borderRadius: 'var(--radius-full)',
                fontSize: '0.85rem',
                fontWeight: 600,
            }}>
                {badge.text}
            </span>
        );
    };

    return (
        <div className="grid gap-3">
            {/* Create Raffle Form */}
            <div className="card animate-fadeIn">
                <h2>📸 Criar Sorteio</h2>
                <p>Configure o sorteio (participantes serão importados de base.txt)</p>

                {error && <div className="alert alert-error">❌ {error}</div>}
                {success && <div className="alert alert-success">{success}</div>}

                <form onSubmit={handleCreateRaffle}>
                    <div className="input-group">
                        <label htmlFor="post-url" className="input-label">Nome do Sorteio</label>
                        <input
                            type="text"
                            id="post-url"
                            className="input"
                            value={formData.post_url}
                            onChange={(e) => setFormData({ ...formData, post_url: e.target.value })}
                            placeholder="Nome do sorteio..."
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
                        {loading ? '⏳ Criando...' : '✨ Criar Sorteio'}
                    </button>
                </form>
            </div>

            {/* Raffles List */}
            <div className="card animate-fadeIn">
                <h2>Sorteios</h2>

                {raffles.length === 0 ? (
                    <p style={{ color: 'var(--color-text-muted)' }}>Nenhum sorteio criado ainda</p>
                ) : (
                    <div className="grid gap-2">
                        {raffles.map((raffle) => (
                            <div
                                key={raffle.id}
                                className="card-glass"
                                style={{
                                    padding: 'var(--spacing-md)',
                                    cursor: 'pointer',
                                    border: selectedRaffle === raffle.id ? '2px solid var(--color-primary)' : 'none',
                                }}
                                onClick={() => setSelectedRaffle(raffle.id)}
                            >
                                <div className="flex justify-between items-center mb-1">
                                    <div>
                                        <h4 style={{ margin: 0 }}>Post: {raffle.shortcode}</h4>
                                    </div>
                                    {getStatusBadge(raffle.status)}
                                </div>

                                <div className="flex gap-1 mt-2">
                                    {raffle.status === 'collecting' && (
                                        <button
                                            className="btn btn-primary"
                                            onClick={(e) => { e.stopPropagation(); handleScrapePost(raffle.id); }}
                                            disabled={scraping}
                                        >
                                            {scraping ? '⏳ Importando...' : '📥 Importar Participantes'}
                                        </button>
                                    )}

                                    {raffle.status === 'validating' && (
                                        <button
                                            className="btn btn-primary"
                                            onClick={(e) => { e.stopPropagation(); handleDraw(raffle.id); }}
                                        >
                                            🎲 Sortear
                                        </button>
                                    )}

                                    {raffle.status === 'completed' && (
                                        <button
                                            className="btn btn-primary"
                                            onClick={async (e) => {
                                                e.stopPropagation();
                                                try {
                                                    setLoading(true);
                                                    setError(null);

                                                    // Duplicate the raffle
                                                    const newRaffle = await instagramAPI.duplicateRaffle(raffle.id);

                                                    setSuccess(`✅ Novo sorteio criado: ${newRaffle.shortcode}`);

                                                    // Reload raffles and select the new one
                                                    await loadRaffles();
                                                    setSelectedRaffle(newRaffle.id);

                                                    setTimeout(() => setSuccess(null), 3000);
                                                } catch (err) {
                                                    setError(err.message);
                                                } finally {
                                                    setLoading(false);
                                                }
                                            }}
                                            disabled={loading}
                                        >
                                            🔄 Sortear Novamente
                                        </button>
                                    )}

                                    {/* Delete button - always visible */}
                                    <button
                                        className="btn"
                                        onClick={(e) => { e.stopPropagation(); handleDeleteRaffle(raffle.id); }}
                                        disabled={loading}
                                        style={{
                                            background: 'var(--color-error)',
                                            marginLeft: 'auto'
                                        }}
                                    >
                                        🗑️ Deletar
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Participants List */}
            {selectedRaffle && (
                <div className="card animate-fadeIn">
                    <div className="flex justify-between items-center mb-2">
                        <h2>Participantes</h2>
                        <div className="flex gap-1">
                            <button
                                className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setFilter('all')}
                            >
                                Todos
                            </button>
                            <button
                                className={`btn ${filter === 'valid' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setFilter('valid')}
                            >
                                Válidos
                            </button>
                            <button
                                className={`btn ${filter === 'invalid' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setFilter('invalid')}
                            >
                                Inválidos
                            </button>
                        </div>
                    </div>

                    {participants.length === 0 ? (
                        <p style={{ color: 'var(--color-text-muted)' }}>Nenhum participante encontrado</p>
                    ) : (
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead>
                                    <tr style={{ borderBottom: '2px solid var(--color-surface)' }}>
                                        <th style={{ padding: 'var(--spacing-sm)', textAlign: 'left' }}>Usuário</th>
                                        <th style={{ padding: 'var(--spacing-sm)', textAlign: 'left' }}>Comentário</th>
                                        <th style={{ padding: 'var(--spacing-sm)', textAlign: 'left' }}>Marcou</th>
                                        <th style={{ padding: 'var(--spacing-sm)', textAlign: 'center' }}>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {participants.map((p) => (
                                        <tr
                                            key={p.id}
                                            style={{
                                                borderBottom: '1px solid var(--color-surface)',
                                                background: p.is_winner ? 'var(--gradient-primary)' : 'transparent',
                                            }}
                                        >
                                            <td style={{ padding: 'var(--spacing-sm)' }}>
                                                <strong>@{p.username}</strong>
                                                {p.is_winner && <span style={{ marginLeft: '0.5rem' }}>🏆</span>}
                                            </td>
                                            <td style={{ padding: 'var(--spacing-sm)', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                {p.comment_text}
                                            </td>
                                            <td style={{ padding: 'var(--spacing-sm)' }}>
                                                {p.tagged_users.map(u => `@${u}`).join(', ')}
                                            </td>
                                            <td style={{ padding: 'var(--spacing-sm)', textAlign: 'center' }}>
                                                {p.is_validated ? (
                                                    p.is_valid ? (
                                                        <span style={{ color: 'var(--color-success)' }}>✓ Válido</span>
                                                    ) : (
                                                        <span
                                                            style={{ color: 'var(--color-error)', cursor: 'help' }}
                                                            title={p.validation_errors?.join(', ')}
                                                        >
                                                            ✗ Inválido
                                                        </span>
                                                    )
                                                ) : (
                                                    <span style={{ color: 'var(--color-text-muted)' }}>Pendente</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
