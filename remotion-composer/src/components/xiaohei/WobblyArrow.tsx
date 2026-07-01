import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export interface WobblyArrowProps {
  x: number;
  y: number;
  width?: number;
  height?: number;
  color?: string;
  delay?: number;
  flip?: boolean;
  label?: string;
}

export const WobblyArrow: React.FC<WobblyArrowProps> = ({
  x,
  y,
  width = 220,
  height = 90,
  color = "#111111",
  delay = 0,
  flip = false,
  label,
}) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame - delay, [0, 24], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const wiggle = Math.sin(frame * 0.18 + x * 0.03) * 3;
  const path = `M 8 ${height * 0.58} C ${width * 0.28} ${height * 0.16 + wiggle}, ${width * 0.58} ${height * 0.88 - wiggle}, ${width - 34} ${height * 0.42}`;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: flip ? "scaleX(-1)" : undefined,
        overflow: "visible",
      }}
    >
      <path
        d={path}
        fill="none"
        stroke={color}
        strokeWidth={7}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={420}
        strokeDashoffset={420 * (1 - draw)}
      />
      <path
        d={`M ${width - 38} ${height * 0.42} l -32 -22 m 32 22 l -16 34`}
        fill="none"
        stroke={color}
        strokeWidth={7}
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity={draw}
      />
      {label ? (
        <text x={width * 0.42} y={height * 0.22} fill={color} fontSize={30} fontFamily="Comic Sans MS, cursive" fontWeight={700}>
          {label}
        </text>
      ) : null}
    </svg>
  );
};
