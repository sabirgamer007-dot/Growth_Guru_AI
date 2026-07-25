/**
 * GrowthGuru AI — Sales Chart Component
 * ========================================
 * Bar chart showing revenue by product using Recharts.
 * Per UI/UX spec §6: Monochromatic green (#22C55E), dark axis labels.
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';



/**
 * Custom tooltip for the dark theme.
 */
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-sidebar border border-border rounded-card px-sm py-xs shadow-lg">
      <p className="text-small text-text-main font-medium mb-xxs">{label}</p>
      <p className="text-body text-primary">
        Revenue: ₹{payload[0].value.toLocaleString('en-IN')}
      </p>
      {payload[0].payload.quantity !== undefined && (
        <p className="text-body text-text-muted">
          Units sold: {payload[0].payload.quantity}
        </p>
      )}
    </div>
  );
}

export default function SalesChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="card p-md flex items-center justify-center h-64">
        <p className="text-text-muted">No sales data to display.</p>
      </div>
    );
  }

  return (
    <div className="card p-md">
      <h2 className="text-h2 text-text-main mb-md">Sales Overview</h2>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="rgba(255,255,255,0.05)"
              vertical={false}
            />
            <XAxis
              dataKey="name"
              tick={{ fill: '#94A3B8', fontSize: 12 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
              tickLine={false}
              interval={0}
              angle={-45}
              textAnchor="end"
              height={80}
              tickFormatter={(value) =>
                value.length > 12 ? `${value.substring(0, 12)}...` : value
              }
            />
            <YAxis
              tick={{ fill: '#94A3B8', fontSize: 12 }}
              axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
              tickLine={false}
              tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
            <Bar
              dataKey="revenue"
              fill="#22C55E"
              radius={[4, 4, 0, 0]}
              maxBarSize={50}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
