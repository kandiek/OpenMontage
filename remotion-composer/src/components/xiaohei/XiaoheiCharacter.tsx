import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export interface XiaoheiCharacterProps {
  x: number;
  y: number;
  scale?: number;
  pose?: "neutral" | "point" | "nod" | "shock";
  delay?: number;
}

export const XiaoheiCharacter: React.FC<XiaoheiCharacterProps> = ({ x, y, scale = 1, pose = "neutral", delay = 0 }) => {
  const frame = useCurrentFrame();
  const appear = interpolate(frame - delay, [0, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const bounce = Math.sin(frame * 0.16) * (pose === "point" ? 9 : 5);
  const nod = pose === "nod" ? Math.sin(frame * 0.32) * 5 : 0;
  const shock = pose === "shock" ? interpolate(Math.sin(frame * 0.5), [-1, 1], [0.95, 1.05]) : 1;
  const arm = pose === "point" ? "M 135 122 C 205 96, 248 86, 305 76" : pose === "shock" ? "M 63 118 C 22 82, 19 52, 40 28 M 137 118 C 184 78, 190 45, 170 20" : "M 68 125 C 35 150, 24 190, 34 222 M 132 125 C 166 150, 176 190, 164 222";

  return (
    <svg width={360 * scale} height={360 * scale} viewBox="0 0 360 360" style={{ position: "absolute", left: x, top: y, overflow: "visible", opacity: appear, transform: `translateY(${bounce}px) scale(${scale * appear * shock}) rotate(${nod}deg)`, transformOrigin: "90px 150px" }}>
      <path d={arm} fill="none" stroke="#111" strokeWidth="18" strokeLinecap="round" strokeLinejoin="round" />
      {pose === "point" ? <path d="M 305 76 l -28 -12 m 28 12 l -22 20" fill="none" stroke="#111" strokeWidth="10" strokeLinecap="round" /> : null}
      <path d="M 43 116 C 42 55, 78 24, 116 39 C 163 57, 176 103, 160 160 C 146 216, 110 252, 66 232 C 25 213, 17 159, 43 116 Z" fill="#080808" />
      <circle cx="79" cy="113" r="8" fill="#fff" />
      <circle cx="124" cy="106" r="8" fill="#fff" />
      <path d="M 67 235 C 55 274, 48 301, 42 332 M 124 234 C 135 274, 142 302, 150 332" stroke="#111" strokeWidth="17" strokeLinecap="round" />
      {pose === "shock" ? <path d="M 184 67 C 207 48, 221 38, 239 17" stroke="#E2452F" strokeWidth="7" strokeLinecap="round" /> : null}
    </svg>
  );
};
