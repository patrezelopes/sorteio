import { useState } from 'react';
import { participantAPI } from '../services/api';

export default function ParticipantForm({ onSuccess }) {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            await participantAPI.create(formData);
            setSuccess(true);
            setFormData({ name: '', email: '', phone: '' });
            if (onSuccess) onSuccess();

            setTimeout(() => setSuccess(false), 3000);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card animate-fadeIn">
            <h2>Registrar Participante</h2>
            <p>Preencha os dados para participar do sorteio</p>

            {error && (
                <div className="alert alert-error">
                    ❌ {error}
                </div>
            )}

            {success && (
                <div className="alert alert-success">
                    ✅ Participante registrado com sucesso!
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <div className="input-group">
                    <label htmlFor="name" className="input-label">Nome Completo</label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        className="input"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Digite seu nome"
                        required
                    />
                </div>

                <div className="input-group">
                    <label htmlFor="email" className="input-label">E-mail</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        className="input"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="seu@email.com"
                        required
                    />
                </div>

                <div className="input-group">
                    <label htmlFor="phone" className="input-label">Telefone (Opcional)</label>
                    <input
                        type="tel"
                        id="phone"
                        name="phone"
                        className="input"
                        value={formData.phone}
                        onChange={handleChange}
                        placeholder="(00) 00000-0000"
                    />
                </div>

                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                    style={{ width: '100%' }}
                >
                    {loading ? (
                        <>
                            <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
                            Registrando...
                        </>
                    ) : (
                        '✨ Registrar'
                    )}
                </button>
            </form>
        </div>
    );
}
