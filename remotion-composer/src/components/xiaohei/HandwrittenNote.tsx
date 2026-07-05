import React from "react";
import { interpolate, useCurrentFrame } from "remotion";

export interface HandwrittenNoteProps {
  text: string;
  x?: number;
  y?: number;
  color?: string;
  size?: number;
  rotate?: number;
  align?: "left" | "center" | "right";
  width?: number;
  delay?: number;
}

export const handwrittenFont = "Comic Sans MS, Bradley Hand, Marker Felt, cursive";

export const HandwrittenNote: React.FC<HandwrittenNoteProps> = ({
  text,
  x = 0,
  y = 0,
  color = "#E85D2A",
  size = 42,
  rotate = -2,
  align = "left",
  width,
  delay = 0,
}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - delay, [0, 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const wiggle = Math.sin(frame * 0.23 + x * 0.01) * 0.7;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width,
        color,
        fontFamily: handwrittenFont,
        fontSize: size,
        lineHeight: 1.08,
        fontWeight: 700,
        textAlign: align,
        transform: `rotate(${rotate + wiggle}deg) scale(${0.96 + progress * 0.04})`,
        opacity: progress,
        whiteSpace: "pre-line",
      }}
    >
      {text}
    </div>
  );
};
