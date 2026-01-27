/**
 * SummaryMatrix Component - Matriz dinámica de resumen
 */

import React from 'react';
import Badge from '../atoms/Badge.jsx';
import { colors, spacing, fontSizes } from '../styles/theme.js';

const SummaryMatrix = ({
  data = null,
  rows = [],
  columns = [],
  loading = false,
  error = null,
}) => {
  if (loading) {
    return <p>Cargando matriz...</p>;
  }

  if (error) {
    return <p style={{ color: colors.danger }}>Error: {error}</p>;
  }

  if (!data || !data.groups || data.groups.length === 0) {
    return <p>No hay datos para mostrar</p>;
  }

  return (
    <div
      style={{
        overflowX: 'auto',
        backgroundColor: colors.white,
        borderRadius: '4px',
        padding: spacing.lg,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      }}
    >
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: fontSizes.sm,
        }}
      >
        <thead>
          <tr style={{ backgroundColor: colors.darkBlue, color: colors.white }}>
            <th style={{ padding: spacing.md, textAlign: 'left' }}>
              Grupo / Contrato
            </th>
            {data.dates?.map((date) => (
              <th key={date} style={{ padding: spacing.md, textAlign: 'center' }}>
                {date}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.groups?.map((group, groupIdx) => (
            <React.Fragment key={groupIdx}>
              {/* Header del grupo */}
              <tr style={{ backgroundColor: colors.skyBlue }}>
                <td
                  colSpan={data.dates?.length + 1}
                  style={{
                    padding: spacing.md,
                    fontWeight: 600,
                    color: colors.darkBlue,
                  }}
                >
                  {group.group_name}
                </td>
              </tr>

              {/* Contratos dentro del grupo */}
              {group.data?.map((contract, contractIdx) => (
                <tr key={`${groupIdx}-${contractIdx}`}>
                  <td
                    style={{
                      padding: spacing.md,
                      borderBottom: `1px solid ${colors.gray200}`,
                      paddingLeft: spacing.xl,
                      color: colors.gray600,
                    }}
                  >
                    {contract.contract_name}
                  </td>

                  {contract.daily_data?.map((dayStats, dayIdx) => (
                    <td
                      key={`${groupIdx}-${contractIdx}-${dayIdx}`}
                      style={{
                        padding: spacing.md,
                        borderBottom: `1px solid ${colors.gray200}`,
                        textAlign: 'center',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          gap: spacing.xs,
                          alignItems: 'center',
                        }}
                      >
                        <Badge variant="success" size="sm">
                          C: {dayStats.connected}
                        </Badge>
                        <Badge variant="danger" size="sm">
                          D: {dayStats.disconnected}
                        </Badge>
                        <small style={{ color: colors.gray500 }}>
                          {dayStats.percentage_connected.toFixed(1)}%
                        </small>
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SummaryMatrix;
