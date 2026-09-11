import React, { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// --- Data Types ---
interface GraphNode {
  id: string;
  label: string;
  x: number; // percentage 0-100
  y: number; // percentage 0-100
  type: 'paper' | 'gap' | 'method';
  size: number;
}

interface GraphEdge {
  from: string;
  to: string;
  strength: number; // 0-1
}

// --- Static Data (Scaled up sizes) ---
const nodes: GraphNode[] = [
  { id: 'p1', label: 'Kim et al. 2023', x: 18, y: 22, type: 'paper', size: 28 },
  { id: 'p2', label: 'Patel 2024', x: 72, y: 18, type: 'paper', size: 24 },
  { id: 'p3', label: 'Zhang & Liu', x: 45, y: 80, type: 'paper', size: 26 },
  { id: 'p4', label: 'Davis et al.', x: 82, y: 65, type: 'paper', size: 22 },
  { id: 'p5', label: 'Müller 2023', x: 12, y: 68, type: 'paper', size: 20 },
  { id: 'm1', label: 'Transformer', x: 38, y: 35, type: 'method', size: 22 },
  { id: 'm2', label: 'GAN', x: 60, y: 48, type: 'method', size: 22 },
  { id: 'g1', label: 'Research Gap', x: 48, y: 52, type: 'gap', size: 36 },
];

const edges: GraphEdge[] = [
  { from: 'p1', to: 'm1', strength: 0.8 },
  { from: 'p2', to: 'm1', strength: 0.6 },
  { from: 'p2', to: 'm2', strength: 0.7 },
  { from: 'p3', to: 'm2', strength: 0.9 },
  { from: 'p3', to: 'p5', strength: 0.4 },
  { from: 'p4', to: 'm2', strength: 0.5 },
  { from: 'm1', to: 'g1', strength: 1.0 },
  { from: 'm2', to: 'g1', strength: 0.9 },
  { from: 'p5', to: 'm1', strength: 0.3 },
  { from: 'p1', to: 'p3', strength: 0.35 },
  { from: 'p4', to: 'p2', strength: 0.25 },
];

// --- Theme Helpers ---
const VIEW_W = 800;
const VIEW_H = 600;

function getNodeColor(type: GraphNode['type']): string {
  switch (type) {
    case 'paper': return 'rgb(var(--accent))';
    case 'method': return 'rgb(var(--success))';
    case 'gap': return 'rgb(var(--alert))';
  }
}

// --- Main Component ---
export const InteractiveGraph: React.FC = () => {
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  const connectedIds = useMemo(() => {
    if (!hoveredNode) return new Set<string>();
    const ids = new Set<string>([hoveredNode]);
    edges.forEach(edge => {
      if (edge.from === hoveredNode) ids.add(edge.to);
      if (edge.to === hoveredNode) ids.add(edge.from);
    });
    return ids;
  }, [hoveredNode]);

  const nodeMap = useMemo(() => new Map(nodes.map(n => [n.id, n])), []);

  return (
    <div className="relative w-full min-h-[400px] aspect-square md:aspect-video bg-[rgb(var(--surface))] rounded-2xl overflow-hidden border border-[rgb(var(--border))] shadow-lg">
      <svg
        viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
        className="w-full h-full"
        style={{ cursor: 'crosshair' }}
      >
        <defs>
          {/* Dot Grid Pattern - uses primary text color at very low opacity */}
          <pattern id="dotGrid" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1.5" fill="rgb(var(--text-primary))" opacity="0.05" />
          </pattern>
          {/* Glow Filter */}
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="8" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {/* Background */}
        <rect width="100%" height="100%" fill="url(#dotGrid)" />

        {/* Edges Layer */}
        <g>
          {edges.map((edge, i) => {
            const from = nodeMap.get(edge.from);
            const to = nodeMap.get(edge.to);
            if (!from || !to) return null;

            const isConnectedToHover = hoveredNode === edge.from || hoveredNode === edge.to;
            const isDimmed = hoveredNode !== null && !isConnectedToHover;
            const activeOpacity = isConnectedToHover ? 0.8 : edge.strength * 0.4;

            return (
              <motion.line
                key={`${edge.from}-${edge.to}`}
                x1={(from.x / 100) * VIEW_W}
                y1={(from.y / 100) * VIEW_H}
                x2={(to.x / 100) * VIEW_W}
                y2={(to.y / 100) * VIEW_H}
                stroke={getNodeColor(from.type)}
                strokeWidth={isConnectedToHover ? 3 : 1.5}
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{
                  pathLength: 1,
                  opacity: isDimmed ? 0.05 : activeOpacity,
                }}
                transition={{ duration: 1, delay: i * 0.05, ease: 'easeOut' }}
              />
            );
          })}
        </g>

        {/* Nodes Layer */}
        <g>
          {nodes.map((node, i) => {
            const cx = (node.x / 100) * VIEW_W;
            const cy = (node.y / 100) * VIEW_H;
            const isHovered = hoveredNode === node.id;
            const isConnected = connectedIds.has(node.id);
            const isDimmed = hoveredNode !== null && !isConnected;
            const color = getNodeColor(node.type);
            const isGap = node.type === 'gap';

            return (
              <motion.g
                key={node.id}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: isDimmed ? 0.15 : 1 }}
                transition={{ type: 'spring', stiffness: 200, damping: 15, delay: i * 0.05 }}
              >
                {/* Concentric Pulses for Gap Nodes */}
                {isGap && (
                  <>
                    <motion.circle cx={cx} cy={cy} r={node.size * 1.8} fill="none" stroke={color} strokeWidth="1.5" animate={{ r: [node.size * 1.8, node.size * 3.5], opacity: [0.4, 0] }} transition={{ duration: 3, repeat: Infinity, ease: "easeOut" }} />
                    <motion.circle cx={cx} cy={cy} r={node.size * 2.5} fill="none" stroke={color} strokeWidth="1" animate={{ r: [node.size * 2.5, node.size * 4.5], opacity: [0.2, 0] }} transition={{ duration: 3, delay: 1.5, repeat: Infinity, ease: "easeOut" }} />
                  </>
                )}

                {/* Main Glowing Orb */}
                <motion.circle
                  cx={cx}
                  cy={cy}
                  r={isHovered ? node.size + 6 : node.size}
                  fill={color}
                  fillOpacity={isHovered ? 1 : 0.85}
                  filter="url(#glow)"
                  transition={{ duration: 0.2 }}
                />
                
                {/* Core Inner Dot */}
                <circle cx={cx} cy={cy} r={node.size * 0.25} fill="rgb(var(--surface))" />

                {/* Node Label */}
                <motion.text
                  x={cx}
                  y={cy + node.size + 20}
                  textAnchor="middle"
                  fill="rgb(var(--text-primary))"
                  fontSize={isGap ? "16px" : "14px"}
                  fontWeight={isGap ? 600 : 500}
                  className="font-sans tracking-wide pointer-events-none select-none"
                  animate={{ 
                    opacity: isDimmed ? 0 : (isHovered || isConnected ? 1 : 0.7),
                    y: isHovered ? cy + node.size + 24 : cy + node.size + 20
                  }}
                >
                  {node.label}
                </motion.text>
              </motion.g>
            );
          })}
        </g>
      </svg>

      {/* Legend mapped to CSS variables */}
      <div className="absolute bottom-6 left-6 flex gap-4 bg-[rgb(var(--surface-raised))] px-4 py-2 rounded-full border border-[rgb(var(--border))] shadow-md">
        {[
          { type: 'paper' as const, label: 'Paper' },
          { type: 'method' as const, label: 'Method' },
          { type: 'gap' as const, label: 'Gap' },
        ].map(({ type, label }) => (
          <div key={label} className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-full shadow-sm" 
              style={{ backgroundColor: getNodeColor(type) }} 
            />
            <span className="text-xs text-[rgb(var(--text-secondary))] font-semibold tracking-wider uppercase">
              {label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};