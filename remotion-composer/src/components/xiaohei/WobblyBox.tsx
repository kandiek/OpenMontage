import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export interface WobblyBoxProps {
  x: number;
  y: number;
  width: number;
  height: number;
  color?: string;
  strokeWidth?: number;
  delay?: number;
  children?: React.ReactNode;
}

export const WobblyBox: React.FC<WobblyBoxProps> = ({ x, y, width, height, color = "#111", strokeWidth = 7, delay = 0, children }) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame - delay, [0, 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const wob = Math.sin(frame * 0.19) * 4;
  const d = `M ${10 + wob} 12 L ${width - 12} ${8 - wob} L ${width - 8 + wob} ${height - 12} L ${12 - wob} ${height - 8} Z`;
  return (
    <div style={{ position: "absolute", left: x, top: y, width, height }}>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ position: "absolute", inset: 0 }}>
        <path d={d} fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={2 * (width + height)} strokeDashoffset={2 * (width + height) * (1 - draw)} />
      </svg>
      <div style={{ position: "absolute", inset: 26 }}>{children}</div>
    </div>
  );
};
