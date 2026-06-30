import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const WIDTH = 1080;
const HEIGHT = 1920;
const FPS = 30;
const DURATION_IN_FRAMES = 750;

const palette = {
  bg: "#050814",
  cyan: "#36e7ff",
  blue: "#5a7cff",
  purple: "#9b5cff",
  green: "#48f5a8",
  text: "#eef6ff",
  muted: "#8ea2c6",
  surface: "rgba(12, 21, 45, 0.92)",
};

const clamp = {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
} as const;

type SceneWindow = {
  start: number;
  end: number;
  caption: string;
};

const sceneWindows: SceneWindow[] = [
  { start: 0, end: 3 * FPS, caption: "One idea starts the pipeline." },
  { start: 3 * FPS, end: 7 * FPS, caption: "Codex turns intent into code." },
  {
    start: 7 * FPS,
    end: 11 * FPS,
    caption: "OpenMontage organizes the production.",
  },
  {
    start: 11 * FPS,
    end: 16 * FPS,
    caption: "Remotion renders video from components.",
  },
  { start: 16 * FPS, end: 21 * FPS, caption: "FFmpeg packages the final MP4." },
  { start: 21 * FPS, end: DURATION_IN_FRAMES, caption: "Now the factory is real." },
];

const activeScene = (frame: number) =>
  sceneWindows.find(({ start, end }) => frame >= start && frame < end) ??
  sceneWindows[sceneWindows.length - 1];

const sceneOpacity = (frame: number, start: number, end: number) =>
  Math.min(
    interpolate(frame, [start, start + 14], [0, 1], clamp),
    interpolate(frame, [end - 16, end], [1, 0], clamp),
  );

const appear = (frame: number, start: number, duration = 16) =>
  interpolate(frame, [start, start + duration], [0, 1], clamp);

const Panel: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
  title?: string;
}> = ({ children, style, title }) => (
  <div
    style={{
      border: "1px solid rgba(92, 226, 255, 0.22)",
      background:
        "linear-gradient(145deg, rgba(12, 21, 45, 0.92), rgba(7, 11, 25, 0.96))",
      borderRadius: 34,
      boxShadow:
        "0 28px 80px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.08)",
      overflow: "hidden",
      ...style,
    }}
  >
    {title ? <PanelTitle title={title} /> : null}
    {children}
  </div>
);

const PanelTitle: React.FC<{ title: string }> = ({ title }) => (
  <div
    style={{
      alignItems: "center",
      borderBottom: "1px solid rgba(255,255,255,0.08)",
      color: palette.muted,
      display: "flex",
      fontFamily: "Inter, system-ui, sans-serif",
      fontSize: 22,
      gap: 12,
      height: 58,
      letterSpacing: 1.2,
      padding: "0 24px",
    }}
  >
    {["#ff5d73", "#ffc14d", palette.green].map((color) => (
      <span
        key={color}
        style={{
          background: color,
          borderRadius: 6,
          height: 12,
          width: 12,
        }}
      />
    ))}
    <span style={{ marginLeft: 10 }}>{title}</span>
  </div>
);

const Header: React.FC = () => (
  <div style={{ left: 66, position: "absolute", right: 66, top: 76 }}>
    <div
      style={{
        color: palette.muted,
        fontSize: 22,
        fontWeight: 800,
        letterSpacing: 5,
      }}
    >
      OPENMONTAGE DEMO
    </div>
    <div
      style={{
        color: palette.text,
        fontFamily: "Inter, system-ui, sans-serif",
        fontSize: 72,
        fontWeight: 900,
        letterSpacing: -3,
        lineHeight: 0.92,
        marginTop: 8,
      }}
    >
      AI Video Factory
    </div>
    <div
      style={{
        color: palette.cyan,
        fontFamily: "Fira Code, monospace",
        fontSize: 24,
        fontWeight: 700,
        letterSpacing: 0.8,
        marginTop: 24,
      }}
    >
      Prompt → Codex → OpenMontage → Remotion → MP4
    </div>
  </div>
);

const Caption: React.FC<{ text: string }> = ({ text }) => (
  <div
    style={{
      background: "rgba(6, 11, 28, 0.78)",
      border: "1px solid rgba(86, 231, 255, 0.22)",
      borderRadius: 28,
      bottom: 95,
      boxShadow: "0 18px 60px rgba(0,0,0,0.38)",
      color: palette.text,
      fontFamily: "Inter, system-ui, sans-serif",
      fontSize: 38,
      fontWeight: 700,
      left: 70,
      lineHeight: 1.15,
      padding: "26px 30px",
      position: "absolute",
      right: 70,
      textAlign: "center",
    }}
  >
    {text}
  </div>
);

const PromptScene: React.FC<{ frame: number }> = ({ frame }) => {
  const typedCharacters = Math.floor(interpolate(frame, [20, 74], [0, 39], clamp));
  const promptText = "Make a short video from this idea".slice(0, typedCharacters);

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity(frame, 0, 3 * FPS) }}>
      <div style={{ left: 126, position: "absolute", right: 126, top: 440 }}>
        <Panel style={{ borderRadius: 52, height: 770 }}>
          <div style={{ padding: 42 }}>
            <div
              style={{
                background: "rgba(255,255,255,0.08)",
                borderRadius: 18,
                height: 34,
                margin: "0 auto 54px",
                width: 160,
              }}
            />
            <div
              style={{
                color: palette.muted,
                fontSize: 27,
                fontWeight: 700,
                marginBottom: 20,
              }}
            >
              Prompt
            </div>
            <div
              style={{
                background: "rgba(255,255,255,0.045)",
                borderRadius: 30,
                color: palette.text,
                fontSize: 48,
                fontWeight: 800,
                lineHeight: 1.18,
                minHeight: 245,
                padding: 34,
              }}
            >
              {promptText}
              <span style={{ color: palette.cyan }}>
                {Math.floor(frame / 10) % 2 ? "" : "|"}
              </span>
            </div>
            <div style={{ display: "flex", gap: 18, marginTop: 36 }}>
              {["Format: vertical", "Length: 25s", "Style: dark tech"].map((label) => (
                <div
                  key={label}
                  style={{
                    background: "rgba(54,231,255,0.09)",
                    borderRadius: 16,
                    color: palette.cyan,
                    fontSize: 20,
                    fontWeight: 800,
                    padding: "14px 18px",
                  }}
                >
                  {label}
                </div>
              ))}
            </div>
          </div>
        </Panel>
      </div>
    </AbsoluteFill>
  );
};

const CodexScene: React.FC<{ frame: number }> = ({ frame }) => {
  const files = ["Explainer.tsx", "demo-props.json", "render_demo.py", "components/Reel.tsx"];
  const lines = [
    "const plan = createScenePlan(prompt);",
    "compose(<VerticalReel scenes={plan} />);",
    "renderMedia({ codec: 'h264' });",
    "assertDuration(750);",
  ];
  const activeFile = Math.floor((frame - 3 * FPS) / FPS) % files.length;

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity(frame, 3 * FPS, 7 * FPS) }}>
      <Panel
        title="codex/workspace"
        style={{ height: 820, left: 70, position: "absolute", right: 70, top: 360 }}
      >
        <div style={{ display: "flex", height: "100%" }}>
          <div
            style={{
              borderRight: "1px solid rgba(255,255,255,0.08)",
              padding: 26,
              width: 310,
            }}
          >
            {files.map((file, index) => (
              <div
                key={file}
                style={{
                  background:
                    index === activeFile ? "rgba(90,124,255,0.24)" : "transparent",
                  borderRadius: 15,
                  color: index === activeFile ? palette.text : palette.muted,
                  fontSize: 24,
                  fontWeight: 750,
                  marginBottom: 18,
                  padding: 16,
                }}
              >
                {file}
              </div>
            ))}
          </div>
          <div
            style={{
              color: palette.text,
              flex: 1,
              fontFamily: "Fira Code, monospace",
              fontSize: 25,
              padding: 32,
            }}
          >
            {lines.map((line, index) => {
              const progress = appear(frame, 105 + index * 18, 27);
              return (
                <div key={line} style={{ marginBottom: 28, opacity: progress }}>
                  <span style={{ color: palette.purple }}>0{index + 1}</span>
                  <span style={{ color: palette.muted }}>  </span>
                  <span>{line.slice(0, Math.floor(line.length * progress))}</span>
                </div>
              );
            })}
            <div
              style={{
                background: "rgba(255,255,255,0.08)",
                borderRadius: 5,
                height: 9,
                marginTop: 50,
              }}
            >
              <div
                style={{
                  background: `linear-gradient(90deg, ${palette.cyan}, ${palette.purple})`,
                  borderRadius: 5,
                  height: "100%",
                  width: `${interpolate(frame, [100, 198], [8, 100], clamp)}%`,
                }}
              />
            </div>
          </div>
        </div>
      </Panel>
    </AbsoluteFill>
  );
};

const PipelineScene: React.FC<{ frame: number }> = ({ frame }) => {
  const nodes = ["Research", "Script", "Scene Plan", "Assets", "Compose", "Render"];

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity(frame, 7 * FPS, 11 * FPS) }}>
      <div style={{ left: 92, position: "absolute", right: 92, top: 450 }}>
        {nodes.map((node, index) => {
          const progress = appear(frame, 220 + index * 15, 18);
          return (
            <React.Fragment key={node}>
              <div
                style={{
                  alignItems: "center",
                  display: "flex",
                  gap: 24,
                  marginBottom: 38,
                  opacity: progress,
                  transform: `translateX(${interpolate(progress, [0, 1], [-40, 0])}px)`,
                }}
              >
                <div
                  style={{
                    background: "rgba(54,231,255,0.12)",
                    border: `2px solid ${palette.cyan}`,
                    borderRadius: 24,
                    boxShadow: `0 0 ${30 * progress}px rgba(54,231,255,0.55)`,
                    height: 78,
                    width: 78,
                  }}
                />
                <div
                  style={{
                    background: "rgba(13,24,52,0.86)",
                    border: "1px solid rgba(255,255,255,0.09)",
                    borderRadius: 24,
                    color: palette.text,
                    flex: 1,
                    fontSize: 39,
                    fontWeight: 850,
                    padding: "24px 30px",
                  }}
                >
                  {node}
                </div>
              </div>
              {index < nodes.length - 1 ? (
                <div
                  style={{
                    background: `linear-gradient(${palette.cyan}, transparent)`,
                    height: 62,
                    left: 38,
                    opacity: progress,
                    position: "absolute",
                    top: index * 118 + 80,
                    width: 3,
                  }}
                />
              ) : null}
            </React.Fragment>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const RemotionScene: React.FC<{ frame: number }> = ({ frame }) => {
  const progress = interpolate(frame, [345, 470], [0, 1], clamp);
  const labels = ["React", "CSS", "SVG", "Animation", "1080x1920", "30 FPS"];

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity(frame, 11 * FPS, 16 * FPS) }}>
      <div
        style={{
          display: "flex",
          gap: 28,
          height: 1010,
          left: 86,
          position: "absolute",
          top: 330,
          width: 908,
        }}
      >
        <Panel style={{ height: 925, padding: 26, width: 520 }}>
          <div
            style={{
              background:
                "linear-gradient(160deg, rgba(54,231,255,0.16), rgba(155,92,255,0.16))",
              border: "1px solid rgba(255,255,255,0.12)",
              borderRadius: 28,
              height: 760,
              overflow: "hidden",
              position: "relative",
            }}
          >
            <div
              style={{
                background: "rgba(255,255,255,0.09)",
                borderRadius: 24,
                height: 150,
                left: 45,
                position: "absolute",
                right: 45,
                top: 105,
                transform: `translateY(${Math.sin(frame / 16) * 18}px)`,
              }}
            />
            <div
              style={{
                border: `3px solid ${palette.cyan}`,
                borderRadius: 30,
                bottom: 135,
                height: 260,
                left: 80,
                opacity: 0.75,
                position: "absolute",
                right: 80,
              }}
            />
          </div>
          <div
            style={{
              background: "rgba(255,255,255,0.08)",
              borderRadius: 12,
              height: 22,
              marginTop: 26,
            }}
          >
            <div
              style={{
                background: palette.green,
                borderRadius: 12,
                height: "100%",
                width: `${progress * 100}%`,
              }}
            />
          </div>
        </Panel>
        <div style={{ flex: 1 }}>
          {labels.map((label, index) => (
            <div
              key={label}
              style={{
                background: "rgba(12,22,48,0.88)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 20,
                color: palette.text,
                fontSize: 30,
                fontWeight: 850,
                marginBottom: 20,
                opacity: appear(frame, 350 + index * 11, 15),
                padding: "21px 24px",
              }}
            >
              {label}
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const ExportScene: React.FC<{ frame: number }> = ({ frame }) => {
  const percent = Math.round(interpolate(frame, [495, 600], [0, 100], clamp));

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity(frame, 16 * FPS, 21 * FPS) }}>
      <Panel
        title="render/export"
        style={{ height: 680, left: 86, position: "absolute", right: 86, top: 470 }}
      >
        <div style={{ padding: 44 }}>
          <div
            style={{
              color: palette.text,
              fontSize: 55,
              fontWeight: 900,
              marginBottom: 38,
            }}
          >
            Encoding final video
          </div>
          <div
            style={{
              background: "rgba(255,255,255,0.08)",
              borderRadius: 18,
              height: 34,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                background: `linear-gradient(90deg, ${palette.cyan}, ${palette.green})`,
                height: "100%",
                width: `${percent}%`,
              }}
            />
          </div>
          <div
            style={{
              color: palette.cyan,
              fontSize: 46,
              fontWeight: 900,
              marginTop: 20,
            }}
          >
            {percent}%
          </div>
          <div
            style={{
              background: "rgba(72,245,168,0.10)",
              border: "1px solid rgba(72,245,168,0.35)",
              borderRadius: 30,
              color: palette.text,
              marginTop: 54,
              padding: 34,
            }}
          >
            <div style={{ fontSize: 43, fontWeight: 900 }}>video-output.mp4</div>
            <div
              style={{
                color: palette.muted,
                display: "grid",
                fontSize: 29,
                fontWeight: 800,
                gap: 18,
                gridTemplateColumns: "1fr 1fr",
                marginTop: 22,
              }}
            >
              <div>H.264</div>
              <div>25s</div>
              <div style={{ color: palette.green }}>Ready</div>
              <div>MP4</div>
            </div>
          </div>
        </div>
      </Panel>
    </AbsoluteFill>
  );
};

const FinalScene: React.FC<{ frame: number }> = ({ frame }) => {
  const steps = [
    "Telegram / Prompt",
    "Codex",
    "OpenMontage",
    "Remotion",
    "MP4",
    "Approve / Post",
  ];

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity(frame, 21 * FPS, DURATION_IN_FRAMES) }}>
      <div style={{ left: 62, position: "absolute", right: 62, top: 390 }}>
        {steps.map((step, index) => (
          <div
            key={step}
            style={{
              alignItems: "center",
              display: "flex",
              marginBottom: 26,
              opacity: appear(frame, 640 + index * 10, 16),
            }}
          >
            <div
              style={{
                background: "rgba(13,24,52,0.9)",
                border: `1px solid ${
                  index === steps.length - 1 ? palette.green : "rgba(255,255,255,0.1)"
                }`,
                borderRadius: 26,
                color: palette.text,
                flex: 1,
                fontSize: 34,
                fontWeight: 900,
                padding: "28px 30px",
              }}
            >
              {step}
            </div>
            {index < steps.length - 1 ? (
              <div
                style={{
                  color: palette.cyan,
                  fontSize: 36,
                  fontWeight: 900,
                  margin: "0 12px",
                }}
              >
                →
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const Background: React.FC<{ frame: number; pulse: number }> = ({ frame, pulse }) => (
  <>
    <div
      style={{
        backgroundImage:
          "linear-gradient(rgba(54,231,255,0.055) 1px, transparent 1px), linear-gradient(90deg, rgba(54,231,255,0.055) 1px, transparent 1px)",
        backgroundSize: "54px 54px",
        inset: 0,
        position: "absolute",
        transform: `translateY(${-frame % 54}px)`,
      }}
    />
    <div
      style={{
        background: "rgba(54,231,255,0.18)",
        borderRadius: 360,
        filter: "blur(130px)",
        height: 720,
        left: -250,
        position: "absolute",
        top: 260,
        transform: `scale(${0.85 + pulse * 0.2})`,
        width: 720,
      }}
    />
    <div
      style={{
        background: "rgba(155,92,255,0.16)",
        borderRadius: 380,
        bottom: 120,
        filter: "blur(150px)",
        height: 760,
        position: "absolute",
        right: -280,
        width: 760,
      }}
    />
  </>
);

export const AiVideoFactoryDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pulse = spring({ frame, fps, config: { damping: 18, stiffness: 70 } });
  const currentScene = activeScene(frame);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: palette.bg,
        fontFamily: "Inter, system-ui, sans-serif",
        height: HEIGHT,
        overflow: "hidden",
        width: WIDTH,
      }}
    >
      <Background frame={frame} pulse={pulse} />
      <Header />
      <PromptScene frame={frame} />
      <CodexScene frame={frame} />
      <PipelineScene frame={frame} />
      <RemotionScene frame={frame} />
      <ExportScene frame={frame} />
      <FinalScene frame={frame} />
      <div
        style={{
          background: "rgba(255,255,255,0.08)",
          borderRadius: 4,
          bottom: 42,
          height: 6,
          left: 70,
          position: "absolute",
          right: 70,
        }}
      >
        <div
          style={{
            background: `linear-gradient(90deg, ${palette.blue}, ${palette.cyan}, ${palette.green})`,
            borderRadius: 4,
            height: "100%",
            width: `${(frame / (DURATION_IN_FRAMES - 1)) * 100}%`,
          }}
        />
      </div>
      <Caption text={currentScene.caption} />
    </AbsoluteFill>
  );
};
