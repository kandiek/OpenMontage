import React from "react";
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { HandwrittenNote, handwrittenFont } from "./xiaohei/HandwrittenNote";
import { WobblyArrow } from "./xiaohei/WobblyArrow";
import { WobblyBox } from "./xiaohei/WobblyBox";
import { XiaoheiCharacter } from "./xiaohei/XiaoheiCharacter";

const BLACK = "#101010";
const RED = "#E2452F";
const ORANGE = "#F06A22";
const BLUE = "#2E75D4";

export interface XiaoheiParableTalentsDemoProps {
  title?: string;
}

const pop = (frame: number, delay = 0) => interpolate(frame - delay, [0, 10, 18], [0, 1.08, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
const fade = (frame: number, delay = 0) => interpolate(frame - delay, [0, 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

const Caption: React.FC<{ children: React.ReactNode; delay?: number }> = ({ children, delay = 10 }) => {
  const frame = useCurrentFrame();
  const opacity = fade(frame, delay);
  const y = interpolate(frame - delay, [0, 18], [24, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <div style={{ position: "absolute", left: 80, right: 80, bottom: 116, color: BLACK, fontFamily: handwrittenFont, fontSize: 58, lineHeight: 1.06, fontWeight: 800, textAlign: "center", opacity, transform: `translateY(${y}px)` }}>{children}</div>;
};

const StickServant: React.FC<{ x: number; y: number; label?: string; afraid?: boolean; approved?: boolean; delay?: number }> = ({ x, y, label, afraid, approved, delay = 0 }) => {
  const frame = useCurrentFrame();
  const s = pop(frame, delay);
  return <svg width="180" height="260" viewBox="0 0 180 260" style={{ position: "absolute", left: x, top: y, overflow: "visible", transform: `scale(${s})`, transformOrigin: "90px 130px" }}>
    {approved ? <path d="M 36 20 L 68 54 L 135 0" fill="none" stroke="#2F9E44" strokeWidth="14" strokeLinecap="round" strokeLinejoin="round" /> : null}
    <circle cx="90" cy="62" r="31" fill="none" stroke={BLACK} strokeWidth="8" />
    <path d="M 90 94 L 90 158 M 90 114 C 52 126, 35 149, 24 176 M 90 115 C 129 125, 145 149, 157 175 M 90 158 L 54 226 M 90 158 L 130 226" fill="none" stroke={BLACK} strokeWidth="8" strokeLinecap="round" />
    {afraid ? <><circle cx="79" cy="58" r="4" fill={BLACK}/><circle cx="101" cy="58" r="4" fill={BLACK}/><path d="M80 79 C88 72,96 72,104 79" fill="none" stroke={BLACK} strokeWidth="5" strokeLinecap="round"/></> : <><circle cx="79" cy="58" r="4" fill={BLACK}/><circle cx="101" cy="58" r="4" fill={BLACK}/><path d="M79 78 C88 86,98 86,106 77" fill="none" stroke={BLACK} strokeWidth="5" strokeLinecap="round"/></>}
    {label ? <text x="90" y="255" textAnchor="middle" fontFamily="Comic Sans MS, cursive" fontSize="34" fontWeight="800" fill={BLACK}>{label}</text> : null}
  </svg>;
};

const Bag: React.FC<{ x: number; y: number; amount: string; delay?: number; color?: string }> = ({ x, y, amount, delay = 0, color = BLACK }) => {
  const frame = useCurrentFrame();
  const s = pop(frame, delay);
  return <svg width="145" height="150" viewBox="0 0 145 150" style={{ position: "absolute", left: x, top: y, transform: `scale(${s})`, transformOrigin: "72px 75px" }}>
    <path d="M 52 28 C 48 14, 96 14, 91 29 C 113 45, 125 80, 119 116 C 111 148, 31 147, 24 117 C 17 79, 30 45, 52 28 Z" fill="none" stroke={color} strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M 45 35 C 61 44, 82 44, 99 35" fill="none" stroke={color} strokeWidth="7" strokeLinecap="round" />
    <text x="72" y="102" textAnchor="middle" fontFamily="Comic Sans MS, cursive" fontSize="56" fontWeight="900" fill={color}>{amount}</text>
  </svg>;
};

const Plant: React.FC<{ x: number; y: number; delay?: number }> = ({ x, y, delay = 0 }) => {
  const frame = useCurrentFrame();
  const grow = pop(frame, delay);
  return <svg width="170" height="210" viewBox="0 0 170 210" style={{ position: "absolute", left: x, top: y, transform: `scale(${grow})`, transformOrigin: "85px 185px" }}>
    <path d="M 85 190 C 84 142, 85 103, 87 58" stroke={BLACK} strokeWidth="8" strokeLinecap="round" />
    <path d="M 86 126 C 47 105, 33 82, 31 58 C 67 58, 85 79, 86 126 Z M 87 94 C 125 74, 142 51, 141 30 C 106 30, 88 53, 87 94 Z" fill="none" stroke={BLACK} strokeWidth="7" />
    <path d="M 34 191 C 72 178, 112 178, 148 191" fill="none" stroke={BLACK} strokeWidth="8" strokeLinecap="round" />
  </svg>;
};

const SketchbookScene: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  const x = interpolate(frame, [0, 16], [width * 0.08, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ backgroundColor: "#fff", transform: `translateX(${x}px)`, overflow: "hidden" }}>{children}</AbsoluteFill>;
};

const Scene1 = () => <SketchbookScene><XiaoheiCharacter x={105} y={790} scale={1.55} pose="neutral" /><HandwrittenNote text="The Parable\nof the Talents" x={360} y={485} size={86} color={BLACK} rotate={-2} width={600} /><HandwrittenNote text="Same mission.\nDifferent starting points." x={350} y={740} size={39} color={ORANGE} rotate={2} width={520} delay={16}/><Caption>Not everyone starts with the same amount.</Caption></SketchbookScene>;
const Scene2 = () => <SketchbookScene><HandwrittenNote text="entrusted differently" x={210} y={330} size={48} color={RED} /><svg style={{position:"absolute",left:160,top:402}} width="720" height="70"><path d="M20 50 C190 12,510 12,700 50" fill="none" stroke={RED} strokeWidth="8" strokeLinecap="round"/></svg><StickServant x={130} y={720} delay={6}/><StickServant x={440} y={720} delay={10}/><StickServant x={735} y={720} delay={14}/><Bag x={145} y={605} amount="5" delay={8}/><Bag x={455} y={605} amount="2" delay={12}/><Bag x={750} y={605} amount="1" delay={16}/><StickServant x={430} y={330} label="master" delay={2}/><XiaoheiCharacter x={690} y={1110} scale={1.05} pose="point" delay={20}/><Caption>A master gave each servant according to their ability.</Caption></SketchbookScene>;
const Scene3 = () => <SketchbookScene><StickServant x={150} y={620}/><Bag x={190} y={530} amount="5"/><WobblyArrow x={405} y={585} width={270} color={BLUE} delay={8}/><Bag x={710} y={510} amount="10" delay={20}/><Plant x={410} y={870} delay={10}/><Plant x={600} y={835} delay={18}/><HandwrittenNote text="used what he had" x={120} y={360} color={BLUE} size={48}/><HandwrittenNote text="faithful" x={635} y={380} color={RED} size={58} rotate={4} delay={20}/><Caption>The first servant used what he received and multiplied it.</Caption></SketchbookScene>;
const Scene4 = () => <SketchbookScene><StickServant x={185} y={675}/><Bag x={210} y={560} amount="2"/><WobblyArrow x={430} y={620} width={235} color={ORANGE} delay={8}/><Bag x={710} y={555} amount="4" delay={18}/><Plant x={470} y={905} delay={10}/><XiaoheiCharacter x={610} y={1015} scale={1.25} pose="nod" delay={15}/><HandwrittenNote text="small gift,\nreal faithfulness" x={165} y={365} color={BLUE} size={48}/><Caption>The second servant also used what he had.</Caption></SketchbookScene>;
const Scene5 = () => <SketchbookScene><StickServant x={190} y={620} afraid/><Bag x={245} y={850} amount="1" delay={8}/><svg style={{position:"absolute",left:330,top:1035}} width="360" height="180"><path d="M40 120 C110 70,240 68,320 122" fill="none" stroke={BLACK} strokeWidth="9" strokeLinecap="round"/><path d="M70 122 C130 96,230 94,295 124" fill="none" stroke="#8B5A2B" strokeWidth="16" strokeLinecap="round"/></svg><WobblyArrow x={220} y={800} width={230} color={BLACK} delay={14}/><HandwrittenNote text="fear hid\nthe gift" x={560} y={500} color={RED} size={60} rotate={-5} delay={12}/><XiaoheiCharacter x={610} y={1030} scale={1.18} pose="shock" delay={18}/><Caption>The third servant was afraid, so he hid what he was given.</Caption></SketchbookScene>;
const Scene6 = () => <SketchbookScene><StickServant x={90} y={615} approved/><Bag x={120} y={505} amount="10"/><StickServant x={380} y={640} approved delay={6}/><Bag x={410} y={535} amount="4" delay={8}/><StickServant x={705} y={655} afraid delay={12}/><svg style={{position:"absolute",left:735,top:960}} width="260" height="110"><path d="M20 80 C80 25,185 22,240 80" fill="none" stroke="#8B5A2B" strokeWidth="15" strokeLinecap="round"/></svg><HandwrittenNote text="He lost what he\nrefused to use." x={245} y={330} color={ORANGE} size={48} align="center" width={560}/><Caption>The issue was not the amount. It was faithfulness.</Caption></SketchbookScene>;
const Scene7 = () => <SketchbookScene><XiaoheiCharacter x={115} y={770} scale={1.55} pose="point"/><WobblyBox x={300} y={420} width={680} height={590} delay={4}><div style={{fontFamily: handwrittenFont, color: BLACK, fontWeight: 900, fontSize: 70, lineHeight: 1.14}}>Moral:<br/><span style={{fontSize: 59}}>Use what you've<br/>been given.</span><br/><span style={{fontSize: 40}}>Faithfulness grows<br/>what is entrusted<br/>to you.</span></div><svg width="340" height="80" style={{marginTop: 8}}><path d="M18 42 C95 62,218 64,322 40" stroke={RED} strokeWidth="10" strokeLinecap="round" fill="none"/><path d="M60 20 C45 0,10 18,31 47 C46 70,70 78,82 76 C101 53,122 27,101 10 C85 -3,69 8,60 20 Z" fill="none" stroke={RED} strokeWidth="7"/></svg></WobblyBox><Caption>Your gift grows when you use it.</Caption></SketchbookScene>;

export const XiaoheiParableTalentsDemo: React.FC<XiaoheiParableTalentsDemoProps> = () => {
  return <AbsoluteFill style={{ backgroundColor: "#fff" }}>
    <Sequence from={0} durationInFrames={120}><Scene1 /></Sequence>
    <Sequence from={120} durationInFrames={180}><Scene2 /></Sequence>
    <Sequence from={300} durationInFrames={210}><Scene3 /></Sequence>
    <Sequence from={510} durationInFrames={210}><Scene4 /></Sequence>
    <Sequence from={720} durationInFrames={210}><Scene5 /></Sequence>
    <Sequence from={930} durationInFrames={210}><Scene6 /></Sequence>
    <Sequence from={1140} durationInFrames={210}><Scene7 /></Sequence>
  </AbsoluteFill>;
};
