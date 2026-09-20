import React from 'react';

interface GaugeDialProps {
  label: string;
  value: number;
  expectedValue?: number;
  min: number;
  max: number;
  unit: string;
  zones?: {
    nominal: [number, number];
    warning: [number, number];
    critical: [number, number];
  };
  decimals?: number;
}

export const GaugeDial: React.FC<GaugeDialProps> = ({
  label,
  value,
  expectedValue,
  min,
  max,
  unit,
  zones,
  decimals = 0,
}) => {
  const clamp = (val: number) => Math.max(min, Math.min(max, val));
  const clampedVal = clamp(value);

  // Map value to 270 degree arc (from 135deg to 405deg, where 0 deg is right, 90 is bottom)
  // Let's use standard angle: start = -135 deg (bottom-left), end = +135 deg (bottom-right)
  const percent = (clampedVal - min) / (max - min);
  const angle = -135 + percent * 270;

  // Expected value angle
  const expectedPercent = expectedValue !== undefined ? (clamp(expectedValue) - min) / (max - min) : null;
  const expectedAngle = expectedPercent !== null ? -135 + expectedPercent * 270 : null;

  // Determine current status zone color
  let statusColor = '#00E5FF'; // default cyan
  let statusText = 'NOM';

  if (zones) {
    if (value >= zones.critical[0] && value <= zones.critical[1]) {
      statusColor = '#FF3355';
      statusText = 'CRIT';
    } else if (value >= zones.warning[0] && value <= zones.warning[1]) {
      statusColor = '#FFB300';
      statusText = 'WARN';
    } else {
      statusColor = '#00E676';
      statusText = 'NORM';
    }
  }

  // Radius and center for 180x180 SVG
  const cx = 90;
  const cy = 90;
  const r = 68;

  // Helper for arc coordinates
  const polarToCartesian = (centerX: number, centerY: number, radius: number, angleInDegrees: number) => {
    const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
    return {
      x: centerX + radius * Math.cos(angleInRadians),
      y: centerY + radius * Math.sin(angleInRadians),
    };
  };

  const describeArc = (x: number, y: number, radius: number, startAngle: number, endAngle: number) => {
    const start = polarToCartesian(x, y, radius, endAngle);
    const end = polarToCartesian(x, y, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
    return ['M', start.x, start.y, 'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y].join(' ');
  };

  // Residual (Actual - Expected)
  const residual = expectedValue !== undefined ? value - expectedValue : null;

  return (
    <div className="aerospace-panel p-3.5 flex flex-col items-center relative overflow-hidden transition-all duration-300 hover:border-tactical-cyan/40 group">
      {/* Gauge Title & Zone Badge */}
      <div className="w-full flex items-center justify-between text-xs font-mono text-slate-400 mb-1">
        <span className="font-semibold tracking-wider uppercase text-[11px] truncate">{label}</span>
        <span
          className="text-[10px] px-1 rounded font-bold uppercase tracking-widest border"
          style={{
            color: statusColor,
            borderColor: `${statusColor}40`,
            backgroundColor: `${statusColor}15`,
          }}
        >
          {statusText}
        </span>
      </div>

      {/* SVG Arc Gauge */}
      <div className="relative w-44 h-40 flex items-center justify-center -my-2">
        <svg viewBox="0 0 180 180" className="w-full h-full transform">
          {/* Background Outer Ring */}
          <path
            d={describeArc(cx, cy, r, -135, 135)}
            fill="none"
            stroke="#111E3A"
            strokeWidth="8"
            strokeLinecap="round"
          />

          {/* Zones Arc Backgrounds */}
          {zones && (
            <>
              {/* Nominal Zone Arc */}
              <path
                d={describeArc(
                  cx,
                  cy,
                  r,
                  -135 + ((zones.nominal[0] - min) / (max - min)) * 270,
                  -135 + ((zones.nominal[1] - min) / (max - min)) * 270
                )}
                fill="none"
                stroke="#00E676"
                strokeWidth="4"
                strokeOpacity="0.25"
              />
              {/* Warning Zone Arc */}
              <path
                d={describeArc(
                  cx,
                  cy,
                  r,
                  -135 + ((zones.warning[0] - min) / (max - min)) * 270,
                  -135 + ((zones.warning[1] - min) / (max - min)) * 270
                )}
                fill="none"
                stroke="#FFB300"
                strokeWidth="4"
                strokeOpacity="0.35"
              />
              {/* Critical Zone Arc */}
              <path
                d={describeArc(
                  cx,
                  cy,
                  r,
                  -135 + ((zones.critical[0] - min) / (max - min)) * 270,
                  -135 + ((zones.critical[1] - min) / (max - min)) * 270
                )}
                fill="none"
                stroke="#FF3355"
                strokeWidth="4"
                strokeOpacity="0.45"
              />
            </>
          )}

          {/* Active Value Arc */}
          <path
            d={describeArc(cx, cy, r, -135, angle)}
            fill="none"
            stroke={statusColor}
            strokeWidth="8"
            strokeLinecap="round"
            style={{
              filter: `drop-shadow(0 0 4px ${statusColor}80)`,
              transition: 'all 0.3s ease-out',
            }}
          />

          {/* Digital Twin Physics Expected Marker (Cyan Target Notch) */}
          {expectedAngle !== null && (
            <g transform={`rotate(${expectedAngle} ${cx} ${cy})`}>
              <line
                x1={cx}
                y1={cy - r - 8}
                x2={cx}
                y2={cy - r + 8}
                stroke="#00E5FF"
                strokeWidth="2.5"
                style={{ filter: 'drop-shadow(0 0 3px #00E5FF)' }}
              />
              <circle cx={cx} cy={cy - r - 9} r="2.5" fill="#00E5FF" />
            </g>
          )}

          {/* Needle Pointer */}
          <g
            transform={`rotate(${angle} ${cx} ${cy})`}
            style={{ transition: 'transform 0.3s ease-out' }}
          >
            <polygon
              points={`${cx - 2.5},${cy} ${cx + 2.5},${cy} ${cx},${cy - r + 4}`}
              fill={statusColor}
              style={{ filter: `drop-shadow(0 0 5px ${statusColor})` }}
            />
          </g>

          {/* Center Pivot Hub */}
          <circle cx={cx} cy={cy} r="7" fill="#080E1E" stroke="#1C315E" strokeWidth="2" />
          <circle cx={cx} cy={cy} r="3" fill={statusColor} />
        </svg>

        {/* Digital Readout Box Inside Dial Bottom */}
        <div className="absolute bottom-2 flex flex-col items-center">
          <div className="flex items-baseline gap-1">
            <span
              className="text-2xl font-black font-mono tracking-tight"
              style={{ color: statusColor }}
            >
              {value.toFixed(decimals)}
            </span>
            <span className="text-[10px] text-slate-400 font-mono font-semibold uppercase">{unit}</span>
          </div>
        </div>
      </div>

      {/* Footer: Expected vs Residual Metrics */}
      <div className="w-full flex items-center justify-between text-[11px] font-mono border-t border-space-800 pt-2 mt-1">
        <span className="text-slate-400 flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-tactical-cyan inline-block" />
          EXP: <strong className="text-slate-300">{expectedValue !== undefined ? expectedValue.toFixed(decimals) : '—'}</strong>
        </span>
        <span className="text-slate-400">
          Δ RES:{' '}
          <strong
            className={
              residual === null
                ? 'text-slate-500'
                : Math.abs(residual) < 5
                ? 'text-tactical-emerald'
                : Math.abs(residual) < 18
                ? 'text-tactical-amber'
                : 'text-tactical-red'
            }
          >
            {residual !== null ? (residual >= 0 ? `+${residual.toFixed(decimals)}` : residual.toFixed(decimals)) : '—'}
          </strong>
        </span>
      </div>
    </div>
  );
};
