import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const W = 1080;
const H = 1920;
const BLACK = "#111111";
const RED = "#d92727";
const ORANGE = "#e77724";
const BLUE = "#2468c9";

const scenes = [
  { start: 0, end: 150, caption: "Not everyone starts with the same amount." },
  { start: 150, end: 330, caption: "A master gave each servant according to ability." },
  { start: 330, end: 540, caption: "The first servant used what he received." },
  { start: 540, end: 750, caption: "The second servant also multiplied what he had." },
  { start: 750, end: 960, caption: "The third servant was afraid, so he hid it." },
  { start: 960, end: 1170, caption: "The issue was not the amount. It was faithfulness." },
  { start: 1170, end: 1350, caption: "Your gift grows when you use it." },
];

type P = { x: number; y: number };
const path = (pts: P[]) => pts.map((p, i) => `${i ? "L" : "M"}${p.x} ${p.y}`).join(" ");
const wob = (n: number, amp = 2) => Math.sin(n * 1.7) * amp;

const RoughLine: React.FC<{ pts: P[]; color?: string; width?: number; dash?: string; progress?: number }> = ({ pts, color = BLACK, width = 5, dash, progress = 1 }) => {
  const d = path(pts.map((p, i) => ({ x: p.x + wob(i + pts.length), y: p.y + wob(i * 3) })));
  const length = 1800;
  return <path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dash ?? length} strokeDashoffset={dash ? 0 : length * (1 - progress)} />;
};

const RoughRect: React.FC<{ x: number; y: number; w: number; h: number; color?: string; width?: number; children?: React.ReactNode }> = ({ x, y, w, h, color = BLACK, width = 5, children }) => (
  <g>
    <path d={`M${x + 8} ${y + 2} L${x + w - 5} ${y + 9} L${x + w - 2} ${y + h - 10} L${x + 3} ${y + h - 2} Z`} fill="none" stroke={color} strokeWidth={width} strokeLinejoin="round" />
    {children}
  </g>
);

const Text: React.FC<{ x: number; y: number; size?: number; color?: string; children: React.ReactNode; weight?: number; anchor?: "start" | "middle" }> = ({ x, y, size = 42, color = BLACK, children, weight = 700, anchor = "start" }) => (
  <text x={x} y={y} fill={color} fontSize={size} fontWeight={weight} textAnchor={anchor} fontFamily="Comic Sans MS, Bradley Hand, Chalkboard SE, sans-serif" letterSpacing={-0.8}>{children}</text>
);

const Xiaohei: React.FC<{ x: number; y: number; s?: number; pose?: "point" | "shock" | "nod" | "stand" }> = ({ x, y, s = 1, pose = "stand" }) => {
  const frame = useCurrentFrame();
  const bob = Math.sin(frame / 7) * 5;
  const arm = pose === "point" ? "M38 45 C85 25 105 8 126 0" : pose === "shock" ? "M28 38 C-5 0 -8 -25 8 -44 M70 37 C104 3 107 -23 90 -42" : "M30 42 C7 56 0 75 -10 90 M68 42 C90 58 98 74 104 91";
  return <g transform={`translate(${x} ${y + bob}) scale(${s})`}>
    <path d="M22 8 C-5 22 -14 68 1 99 C19 136 76 133 95 100 C113 68 100 17 70 4 C54 -3 38 -1 22 8 Z" fill={BLACK} />
    <circle cx="34" cy="55" r="5.5" fill="white" />
    <circle cx="62" cy="52" r="5.5" fill="white" />
    <path d={arm} fill="none" stroke={BLACK} strokeWidth="7" strokeLinecap="round" />
    <path d="M28 125 C22 146 18 163 12 184 M69 125 C76 148 79 164 85 184" fill="none" stroke={BLACK} strokeWidth="7" strokeLinecap="round" />
  </g>;
};

const Bag: React.FC<{ x: number; y: number; label: string; pop?: number }> = ({ x, y, label, pop = 1 }) => <g transform={`translate(${x} ${y}) scale(${pop})`}>
  <path d="M48 18 C34 40 15 61 12 100 C9 151 102 153 99 101 C97 62 76 40 63 18 Z" fill="white" stroke={BLACK} strokeWidth="5" />
  <path d="M37 21 C49 29 59 28 72 20 M35 45 C50 52 65 50 79 43" fill="none" stroke={BLACK} strokeWidth="5" strokeLinecap="round" />
  <Text x={56} y={111} size={52} anchor="middle">{label}</Text>
</g>;

const Servant: React.FC<{ x: number; y: number; afraid?: boolean }> = ({ x, y, afraid }) => <g transform={`translate(${x} ${y})`}>
  <circle cx="0" cy="0" r="26" fill="white" stroke={BLACK} strokeWidth="5" />
  <path d="M-4 32 C-18 78 -24 126 -22 170 M7 32 C22 78 29 124 31 170 M-45 74 C-18 61 6 60 37 76" fill="none" stroke={BLACK} strokeWidth="5" strokeLinecap="round" />
  {afraid && <Text x={36} y={-28} size={44} color={RED}>?</Text>}
</g>;

const Arrow: React.FC<{ from: P; to: P; color?: string; progress: number; label?: string }> = ({ from, to, color = ORANGE, progress, label }) => {
  const mid = { x: (from.x + to.x) / 2, y: (from.y + to.y) / 2 - 40 };
  const cur = Math.max(0, Math.min(1, progress));
  return <g>
    <RoughLine pts={[from, mid, to]} color={color} width={6} progress={cur} />
    {cur > 0.82 && <path d={`M${to.x - 24} ${to.y - 18} L${to.x} ${to.y} L${to.x - 30} ${to.y + 8}`} fill="none" stroke={color} strokeWidth="6" strokeLinecap="round" />}
    {label && <Text x={mid.x} y={mid.y - 16} color={color} size={52} anchor="middle">{label}</Text>}
  </g>;
};

const SceneFrame: React.FC<{ children: React.ReactNode; caption: string; local: number }> = ({ children, caption, local }) => {
  const entry = spring({ frame: local, fps: 30, config: { damping: 18, stiffness: 90 } });
  const wig = Math.sin(local / 9) * 1.2;
  return <AbsoluteFill style={{ background: "#fff", transform: `translateY(${interpolate(entry, [0, 1], [30, 0])}px) rotate(${wig * 0.05}deg)`, opacity: entry }}>
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
      {children}
      <RoughRect x={82} y={1678} w={916} h={130} width={4} />
      <Text x={540} y={1758} size={44} anchor="middle" weight={650}>{caption}</Text>
    </svg>
  </AbsoluteFill>;
};

const Panel = ({ idx, local }: { idx: number; local: number }) => {
  const p = interpolate(local, [6, 42], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.quad) });
  const pop = (d: number) => spring({ frame: local - d, fps: 30, config: { damping: 9, stiffness: 130 } });
  const caption = scenes[idx].caption;
  if (idx === 0) return <SceneFrame caption={caption} local={local}><Text x={540} y={230} size={70} anchor="middle">The Parable of the Talents</Text><RoughLine pts={[{x:240,y:720},{x:410,y:560},{x:560,y:720},{x:730,y:560},{x:850,y:720}]} color={ORANGE} progress={p}/><Bag x={350} y={690} label="5" pop={pop(10)}/><Bag x={520} y={520} label="2" pop={pop(18)}/><Bag x={700} y={690} label="1" pop={pop(26)}/><Xiaohei x={165} y={925} s={1.45} pose="point"/><Text x={500} y={1020} size={40} color={BLUE}>same mission, different starting points</Text></SceneFrame>;
  if (idx === 1) return <SceneFrame caption={caption} local={local}><Text x={250} y={315} size={48}>master</Text><Servant x={235} y={420}/><Bag x={345} y={570} label="5" pop={pop(5)}/><Bag x={500} y={570} label="2" pop={pop(15)}/><Bag x={655} y={570} label="1" pop={pop(25)}/><Servant x={385} y={940}/><Servant x={560} y={940}/><Servant x={735} y={940}/><RoughLine pts={[{x:315,y:470},{x:455,y:620},{x:565,y:620},{x:715,y:620}]} color={ORANGE} progress={p}/><Text x={540} y={500} size={42} color={RED} anchor="middle">entrusted differently</Text><Xiaohei x={150} y={1210} s={1.25} pose="point"/></SceneFrame>;
  if (idx === 2) return <SceneFrame caption={caption} local={local}><Servant x={245} y={610}/><Bag x={310} y={750} label="5" pop={1}/><Arrow from={{x:430,y:835}} to={{x:705,y:835}} progress={p} label="5 → 10"/><Bag x={710} y={750} label="10" pop={pop(26)}/><RoughRect x={175} y={1070} w={275} h={155}/><RoughLine pts={[{x:210,y:1120},{x:300,y:1085},{x:390,y:1140}]} color={BLUE} progress={p}/><Text x={610} y={1075} size={42} color={BLUE}>used what he had</Text><Text x={675} y={1150} size={48} color={RED}>faithful</Text><Xiaohei x={125} y={1240} s={1.2} pose="point"/></SceneFrame>;
  if (idx === 3) return <SceneFrame caption={caption} local={local}><Servant x={250} y={690}/><Bag x={300} y={855} label="2"/><RoughLine pts={[{x:565,y:1040},{x:565,y:930},{x:520,y:875},{x:610,y:875},{x:565,y:930}]} color={BLUE} progress={p}/><path d="M565 1045 C500 995 478 937 486 872 M565 1045 C625 992 650 942 642 876" fill="none" stroke={BLACK} strokeWidth="5" strokeLinecap="round"/><Arrow from={{x:415,y:900}} to={{x:735,y:900}} progress={p} label="2 → 4"/><Bag x={740} y={815} label="4" pop={pop(28)}/><Text x={520} y={1215} size={42} color={BLUE}>used it well</Text><Xiaohei x={725} y={1165} s={1.15} pose="nod"/></SceneFrame>;
  if (idx === 4) return <SceneFrame caption={caption} local={local}><Servant x={310} y={585} afraid/><Bag x={390} y={870} label="1" pop={interpolate(p,[0,1],[1,0.45])}/><path d="M475 1038 C558 1004 645 1008 716 1040 C640 1092 535 1088 475 1038 Z" fill="none" stroke={BLACK} strokeWidth="5"/><RoughLine pts={[{x:420,y:945},{x:540,y:1040}]} color={ORANGE} progress={p}/><Text x={540} y={805} size={45} color={RED}>fear hid the gift</Text><Xiaohei x={655} y={1110} s={1.35} pose="shock"/></SceneFrame>;
  if (idx === 5) return <SceneFrame caption={caption} local={local}><Servant x={215} y={590}/><Bag x={285} y={755} label="10"/><Servant x={535} y={590}/><Bag x={605} y={755} label="4"/><Servant x={830} y={670} afraid/><path d="M795 1020 C850 990 925 996 965 1028" fill="none" stroke={BLACK} strokeWidth="5"/><RoughRect x={190} y={1160} w={705} h={155} color={BLACK}/><Text x={542} y={1250} size={43} anchor="middle">He lost what he refused to use.</Text><Xiaohei x={105} y={1345} s={1.12} pose="point"/></SceneFrame>;
  return <SceneFrame caption={caption} local={local}><Xiaohei x={115} y={765} s={1.55} pose="point"/><RoughRect x={300} y={540} w={610} h={585} width={6}/><Text x={360} y={660} size={64} color={RED}>Moral:</Text><Text x={360} y={800} size={58}>Use what you've</Text><Text x={360} y={880} size={58}>been given.</Text><RoughLine pts={[{x:360,y:930},{x:820,y:930}]} color={ORANGE} progress={p}/><Text x={360} y={1030} size={41} color={BLUE}>Faithfulness grows what is entrusted to you.</Text><Bag x={730} y={1170} label="+" pop={pop(20)}/></SceneFrame>;
};

export const XiaoheiParableTalents: React.FC = () => {
  const frame = useCurrentFrame();
  const idx = scenes.findIndex((s) => frame >= s.start && frame < s.end);
  const sceneIndex = idx === -1 ? scenes.length - 1 : idx;
  const local = frame - scenes[sceneIndex].start;
  return <AbsoluteFill style={{ background: "#fff" }}><Panel idx={sceneIndex} local={local} /></AbsoluteFill>;
};
