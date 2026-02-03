// frontend/src/components/EditRegisterModal.jsx
import React, { useState } from 'react';
import { colors, spacing, typography } from '../styles/theme.js';

const EditRegisterModal = ({ register, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    tipo: register.tipo || 'MAL FUNCIONAMIENTO',
    estatus_final: register.estatus_final || '',
    responsable: register.responsable || 'SIN ESTATUS DEL DISTRIBUIDOR',
    comentario: register.comentario || '',
  });

  const tipoOptions = [
    { value: 'MAL FUNCIONAMIENTO', label: 'Mal Funcionamiento' },
    { value: 'OPERACIÓN', label: 'Operación' },
  ];

  const estatusOptions = [
    { value: 'POSIBLE MANIPULACIÓN', label: 'Posible Manipulación' },
    { value: 'PERDIDA DE SEÑAL', label: 'Perdida de Señal' },
    { value: 'TALLER', label: 'Taller' },
    { value: 'CORTACORRIENTE', label: 'Cortacorriente' },
    { value: 'BASE', label: 'Base' },
    { value: 'ACCIDENTADA', label: 'Accidentada' },
  ];

  const responsableOptions = [
    { value: 'SIN ESTATUS DEL DISTRIBUIDOR', label: 'Sin Estatus del Distribuidor' },
    { value: 'SIN ESTATUS DEL CLIENTE', label: 'Sin Estatus del Cliente' },
    { value: 'NO OPERACIONAL', label: 'No Operacional' },
    { value: 'REVISIÓN FÍSICA', label: 'Revisión Física' },
  ];

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ ...register, ...formData });
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: colors.white,
          borderRadius: '8px',
          padding: spacing.xl,
          maxWidth: '600px',
          width: '90%',
          maxHeight: '90vh',
          overflow: 'auto',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ marginBottom: spacing.lg, ...typography.h2 }}>
          Editar Registro
        </h2>

        <form onSubmit={handleSubmit}>
          {/* Información no editable */}
          <div style={{ marginBottom: spacing.lg, padding: spacing.md, backgroundColor: colors.lightGray, borderRadius: '4px' }}>
            <p style={{ marginBottom: spacing.sm }}><strong>VIN:</strong> {register.vin}</p>
            <p style={{ marginBottom: spacing.sm }}><strong>Cliente:</strong> {register.client_description}</p>
            <p style={{ marginBottom: spacing.sm }}><strong>Problema:</strong> {register.problem}</p>
            <p><strong>Última Conexión:</strong> {new Date(register.last_connection).toLocaleString('es-MX')}</p>
          </div>

          {/* Tipo */}
          <div style={{ marginBottom: spacing.md }}>
            <label style={{ display: 'block', marginBottom: spacing.sm, fontWeight: 'bold' }}>
              Tipo
            </label>
            <select
              value={formData.tipo}
              onChange={(e) => handleChange('tipo', e.target.value)}
              style={{
                width: '100%',
                padding: spacing.sm,
                borderRadius: '4px',
                border: `1px solid ${colors.border}`,
                fontSize: typography.body.fontSize,
              }}
            >
              {tipoOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Estatus Final */}
          <div style={{ marginBottom: spacing.md }}>
            <label style={{ display: 'block', marginBottom: spacing.sm, fontWeight: 'bold' }}>
              Estatus Final
            </label>
            <select
              value={formData.estatus_final}
              onChange={(e) => handleChange('estatus_final', e.target.value)}
              style={{
                width: '100%',
                padding: spacing.sm,
                borderRadius: '4px',
                border: `1px solid ${colors.border}`,
                fontSize: typography.body.fontSize,
              }}
            >
              <option value="">Seleccionar...</option>
              {estatusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Responsable */}
          <div style={{ marginBottom: spacing.md }}>
            <label style={{ display: 'block', marginBottom: spacing.sm, fontWeight: 'bold' }}>
              Responsable
            </label>
            <select
              value={formData.responsable}
              onChange={(e) => handleChange('responsable', e.target.value)}
              style={{
                width: '100%',
                padding: spacing.sm,
                borderRadius: '4px',
                border: `1px solid ${colors.border}`,
                fontSize: typography.body.fontSize,
              }}
            >
              {responsableOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Comentario */}
          <div style={{ marginBottom: spacing.lg }}>
            <label style={{ display: 'block', marginBottom: spacing.sm, fontWeight: 'bold' }}>
              Comentario
            </label>
            <textarea
              value={formData.comentario}
              onChange={(e) => handleChange('comentario', e.target.value)}
              rows={4}
              style={{
                width: '100%',
                padding: spacing.sm,
                borderRadius: '4px',
                border: `1px solid ${colors.border}`,
                fontSize: typography.body.fontSize,
                fontFamily: 'inherit',
                resize: 'vertical',
              }}
              placeholder="Agregar comentarios adicionales..."
            />
          </div>

          {/* Botones */}
          <div style={{ display: 'flex', gap: spacing.md, justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: `${spacing.sm} ${spacing.lg}`,
                borderRadius: '4px',
                border: `1px solid ${colors.border}`,
                backgroundColor: colors.white,
                cursor: 'pointer',
                fontSize: typography.body.fontSize,
              }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              style={{
                padding: `${spacing.sm} ${spacing.lg}`,
                borderRadius: '4px',
                border: 'none',
                backgroundColor: colors.primary,
                color: colors.white,
                cursor: 'pointer',
                fontSize: typography.body.fontSize,
                fontWeight: 'bold',
              }}
            >
              Guardar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditRegisterModal;
