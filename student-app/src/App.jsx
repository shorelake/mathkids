import { useState, useEffect, useRef, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";

// In dev the Vite proxy rewrites /api -> backend; in production set VITE_API_BASE_URL.
const API = import.meta.env.VITE_API_BASE_URL || "/api";

function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => { setLoading(true); fetch(API + url).then(r => r.json()).then(d => { setData(d); setLoading(false); }).catch(() => setLoading(false)); }, [url]);
  return { data, loading };
}

// ===== COLORS =====
const C = {
  bg1: "#FFF4E6", bg2: "#E8F8F5", bg3: "#F0E6FF",
  pink: "#FF6B8A", orange: "#FF8C42", yellow: "#FFD93D", green: "#6BCB77",
  blue: "#4D96FF", purple: "#9B59B6", teal: "#1ABC9C", coral: "#FF6F61",
  text: "#2C3E50", textLight: "#7F8C8D", card: "#FFFFFF", border: "#F0E0D0",
  star: "#FFD700", starEmpty: "#E0D5C5",
};

// ===== CUTE SVG OBJECTS =====
const cuteItems = [
  (s) => <svg width={s} height={s} viewBox="0 0 60 60"><ellipse cx="30" cy="34" rx="22" ry="20" fill="#FFD89B"/><polygon points="12,20 8,4 22,16" fill="#FFD89B" stroke="#E8B86D" strokeWidth="1"/><polygon points="48,20 52,4 38,16" fill="#FFD89B" stroke="#E8B86D" strokeWidth="1"/><circle cx="22" cy="30" r="3.5" fill="#2C3E50"/><circle cx="38" cy="30" r="3.5" fill="#2C3E50"/><circle cx="23" cy="29" r="1.2" fill="#fff"/><circle cx="39" cy="29" r="1.2" fill="#fff"/><ellipse cx="30" cy="37" rx="3" ry="2" fill="#FF9A9E"/><path d="M27,40 Q30,44 33,40" fill="none" stroke="#E8B86D" strokeWidth="1.5" strokeLinecap="round"/></svg>,
  (s) => <svg width={s} height={s} viewBox="0 0 60 60"><ellipse cx="30" cy="34" rx="21" ry="20" fill="#C4A882"/><ellipse cx="14" cy="22" rx="10" ry="14" fill="#A0845C" transform="rotate(-15 14 22)"/><ellipse cx="46" cy="22" rx="10" ry="14" fill="#A0845C" transform="rotate(15 46 22)"/><circle cx="22" cy="30" r="3.5" fill="#2C3E50"/><circle cx="38" cy="30" r="3.5" fill="#2C3E50"/><circle cx="23" cy="29" r="1.2" fill="#fff"/><circle cx="39" cy="29" r="1.2" fill="#fff"/><ellipse cx="30" cy="39" rx="8" ry="6" fill="#F5E6D3"/><ellipse cx="30" cy="37" rx="4" ry="3" fill="#2C3E50"/><path d="M28,41 Q30,44 32,41" fill="none" stroke="#C4A882" strokeWidth="1.5" strokeLinecap="round"/></svg>,
  (s) => <svg width={s} height={s} viewBox="0 0 60 60"><ellipse cx="22" cy="14" rx="6" ry="16" fill="#F5E6F0" stroke="#E0C8D8" strokeWidth="1"/><ellipse cx="38" cy="14" rx="6" ry="16" fill="#F5E6F0" stroke="#E0C8D8" strokeWidth="1"/><ellipse cx="22" cy="12" rx="3" ry="10" fill="#FFB6C1"/><ellipse cx="38" cy="12" rx="3" ry="10" fill="#FFB6C1"/><ellipse cx="30" cy="38" rx="20" ry="18" fill="#F5E6F0"/><circle cx="23" cy="34" r="3" fill="#2C3E50"/><circle cx="37" cy="34" r="3" fill="#2C3E50"/><ellipse cx="30" cy="40" rx="2.5" ry="2" fill="#FFB6C1"/></svg>,
  (s) => <svg width={s} height={s} viewBox="0 0 60 60"><path d="M24,18 Q20,12 26,8 L30,6 L34,8 Q40,12 36,18" fill="#4CAF50"/><path d="M20,22 Q16,36 22,48 Q28,56 30,56 Q32,56 38,48 Q44,36 40,22 Z" fill="#FF4757"/><circle cx="28" cy="30" r="1.2" fill="#FFE66D"/><circle cx="34" cy="34" r="1.2" fill="#FFE66D"/><circle cx="26" cy="38" r="1.2" fill="#FFE66D"/><circle cx="32" cy="42" r="1.2" fill="#FFE66D"/></svg>,
  (s) => <svg width={s} height={s} viewBox="0 0 60 60"><ellipse cx="30" cy="40" rx="24" ry="14" fill="#F5DEB3"/><path d="M10,36 Q10,14 30,10 Q50,14 50,36" fill="#FFF8DC"/><path d="M22,16 Q26,10 30,14 Q34,10 38,16" fill="none" stroke="#DEB887" strokeWidth="2" strokeLinecap="round"/><circle cx="22" cy="30" r="2.5" fill="#2C3E50"/><circle cx="38" cy="30" r="2.5" fill="#2C3E50"/><path d="M27,35 Q30,38 33,35" fill="none" stroke="#DEB887" strokeWidth="1.5" strokeLinecap="round"/><ellipse cx="18" cy="33" rx="4" ry="3" fill="#FFB6C1" opacity="0.4"/><ellipse cx="42" cy="33" rx="4" ry="3" fill="#FFB6C1" opacity="0.4"/></svg>,
  (s) => <svg width={s} height={s} viewBox="0 0 60 60"><path d="M30,4 L36,22 L56,22 L40,34 L46,52 L30,42 L14,52 L20,34 L4,22 L24,22 Z" fill="#FFD700" stroke="#FFA500" strokeWidth="1"/><circle cx="25" cy="28" r="2.5" fill="#2C3E50"/><circle cx="35" cy="28" r="2.5" fill="#2C3E50"/><path d="M27,34 Q30,37 33,34" fill="none" stroke="#E89B00" strokeWidth="1.5" strokeLinecap="round"/></svg>,
  (s) => <svg width={s} height={s} viewBox="0 0 60 60"><path d="M30,12 Q34,6 38,10" stroke="#4CAF50" strokeWidth="2.5" fill="none" strokeLinecap="round"/><ellipse cx="30" cy="36" rx="18" ry="20" fill="#FF5555"/><ellipse cx="24" cy="30" rx="5" ry="6" fill="rgba(255,255,255,0.25)"/></svg>,
  (s) => <svg width={s} height={s} viewBox="0 0 60 60"><path d="M30,52 Q6,36 6,22 Q6,10 18,10 Q26,10 30,18 Q34,10 42,10 Q54,10 54,22 Q54,36 30,52 Z" fill="#FF6B8A"/><circle cx="24" cy="26" r="2.5" fill="#fff"/><circle cx="36" cy="26" r="2.5" fill="#fff"/><circle cx="24.8" cy="25.5" r="1.2" fill="#2C3E50"/><circle cx="36.8" cy="25.5" r="1.2" fill="#2C3E50"/><path d="M27,34 Q30,37 33,34" fill="none" stroke="#E0476E" strokeWidth="1.5" strokeLinecap="round"/></svg>,
];

function CuteObject({ index = 0, size = 44, highlighted = false, dimmed = false }) {
  return <div style={{ opacity: dimmed ? 0.25 : 1, filter: highlighted ? "drop-shadow(0 0 6px #FFD700)" : "none", transition: "all 0.3s" }}>{cuteItems[index % cuteItems.length](size)}</div>;
}
function useShapePool(count) {
  return useMemo(() => {
    const idx = Array.from({ length: cuteItems.length }, (_, i) => i);
    for (let i = idx.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [idx[i], idx[j]] = [idx[j], idx[i]]; }
    return Array.from({ length: count }, (_, i) => idx[i % idx.length]);
  }, [count]);
}

function FloatingDecos() {
  const decos = useMemo(() => Array.from({ length: 12 }, (_, i) => ({ x: Math.random()*100, y: Math.random()*100, sz: 8+Math.random()*16, dl: Math.random()*5, dur: 4+Math.random()*6, sh: i%4 })), []);
  return <div style={{ position:"fixed",inset:0,pointerEvents:"none",zIndex:0,overflow:"hidden" }}>
    {decos.map((d,i) => <motion.div key={i} animate={{y:[0,-15,0],rotate:[0,d.sh===0?20:-20,0]}} transition={{duration:d.dur,repeat:Infinity,delay:d.dl,ease:"easeInOut"}} style={{position:"absolute",left:`${d.x}%`,top:`${d.y}%`,opacity:0.12}}>
      {d.sh===0&&<svg width={d.sz} height={d.sz} viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill={C.yellow}/></svg>}
      {d.sh===1&&<svg width={d.sz} height={d.sz} viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill={C.pink}/></svg>}
      {d.sh===2&&<svg width={d.sz} height={d.sz} viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="4" fill={C.blue} opacity=".5"/></svg>}
      {d.sh===3&&<svg width={d.sz} height={d.sz} viewBox="0 0 24 24"><path d="M12,21 Q2,14 2,8 Q2,3 7,3 Q10,3 12,6 Q14,3 17,3 Q22,3 22,8 Q22,14 12,21Z" fill={C.coral}/></svg>}
    </motion.div>)}
  </div>;
}
function Stars({ count=0, max=3, size=22 }) {
  return <div style={{display:"flex",gap:2}}>{Array.from({length:max},(_,i)=><motion.svg key={i} width={size} height={size} viewBox="0 0 24 24" animate={i<count?{scale:[1,1.4,1]}:{}} transition={{delay:i*0.15,duration:0.4}}><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" fill={i<count?C.star:C.starEmpty}/></motion.svg>)}</div>;
}
function Mascot({ mood="happy", size=80, message="" }) {
  return <div style={{display:"flex",alignItems:"flex-end",gap:10,margin:"8px 0"}}>
    <svg width={size} height={size} viewBox="0 0 100 100"><polygon points="25,35 15,8 40,28" fill="#FF8C42"/><polygon points="75,35 85,8 60,28" fill="#FF8C42"/><ellipse cx="50" cy="55" rx="35" ry="32" fill="#FF8C42"/><ellipse cx="50" cy="62" rx="20" ry="16" fill="#FFF8DC"/><circle cx="38" cy="48" r="5" fill="#2C3E50"/><circle cx="62" cy="48" r="5" fill="#2C3E50"/><circle cx="39.5" cy="46.5" r="2" fill="#fff"/><circle cx="63.5" cy="46.5" r="2" fill="#fff"/><ellipse cx="50" cy="58" rx="4" ry="3" fill="#2C3E50"/>{mood==="happy"&&<path d="M40,64 Q50,74 60,64" fill="none" stroke="#E8764A" strokeWidth="2.5" strokeLinecap="round"/>}{mood==="think"&&<path d="M42,66 L58,66" stroke="#E8764A" strokeWidth="2.5" strokeLinecap="round"/>}{mood==="wow"&&<ellipse cx="50" cy="68" rx="5" ry="6" fill="#E8764A"/>}<ellipse cx="30" cy="56" rx="6" ry="5" fill="#FFB088" opacity=".5"/><ellipse cx="70" cy="56" rx="6" ry="5" fill="#FFB088" opacity=".5"/></svg>
    {message&&<motion.div initial={{opacity:0,y:10}} animate={{opacity:1,y:0}} style={{padding:"10px 16px",background:C.card,borderRadius:"18px 18px 18px 4px",boxShadow:"0 2px 10px rgba(0,0,0,0.08)",fontSize:15,color:C.text,fontWeight:600,maxWidth:280,lineHeight:1.5,border:`2px solid ${C.border}`}}>{message}</motion.div>}
  </div>;
}

const btnStyle = (bg) => ({ padding:"9px 20px",borderRadius:22,border:"none",background:bg,color:"#fff",fontSize:14,fontWeight:700,cursor:"pointer",boxShadow:"0 2px 6px rgba(0,0,0,0.1)" });

function AnimControls({ step, total, onPrev, onNext, auto, onAutoToggle }) {
  return <div style={{marginTop:12}}>
    <div style={{display:"flex",justifyContent:"center",gap:10}}>
      {onPrev&&<button onClick={onPrev} disabled={step===0} style={{...btnStyle(C.border),color:C.text,opacity:step===0?0.3:1}}>◀ 上一步</button>}
      {onAutoToggle&&<button onClick={onAutoToggle} style={btnStyle(auto?C.teal:C.purple)}>{auto?"⏸ 暂停":"▶ 自动"}</button>}
      <button onClick={onNext} style={btnStyle(step>=total-1?C.green:C.blue)}>{step>=total-1?"✓ 完成":"下一步 ▶"}</button>
    </div>
    <div style={{display:"flex",justifyContent:"center",gap:5,marginTop:8}}>
      {Array.from({length:total},(_,i)=><div key={i} style={{width:i===step?22:8,height:8,borderRadius:4,transition:"all 0.3s",background:i<=step?C.teal:C.border}}/>)}
    </div>
  </div>;
}

// ============================================================
//  MAKE TEN ANIMATION (进位加法)
// ============================================================
function MakeTenAnimation({ data, onComplete }) {
  const [step, setStep] = useState(0);
  const steps = data.steps; const cur = steps[step];
  const [auto, setAuto] = useState(false);
  const first = steps.find(s=>s.action==="show_objects")||{};
  const L=first.left||0, R=first.right||0;
  const splitS = steps.find(s=>s.action==="split")||{}; const parts = splitS.parts||[0,0];
  const shapes = useShapePool(L+R);
  const splitI=steps.findIndex(s=>s.action==="split"), moveI=steps.findIndex(s=>s.action==="move_to_left");
  const tenI=steps.findIndex(s=>s.action==="highlight_ten"), combI=steps.findIndex(s=>s.action==="combine");
  const isSplit=splitI>=0&&step>=splitI, isMoved=moveI>=0&&step>=moveI, isTen=tenI>=0&&step>=tenI, isComb=combI>=0&&step>=combI;
  const leftN=isMoved?L+parts[0]:L, rightN=isMoved?R-parts[0]:R;
  const goNext=()=>{if(step<steps.length-1)setStep(s=>s+1);else onComplete?.()};
  const goPrev=()=>{if(step>0)setStep(s=>s-1)};
  useEffect(()=>{if(auto&&step<steps.length-1){const t=setTimeout(goNext,2800);return()=>clearTimeout(t)}if(auto&&step>=steps.length-1)setAuto(false)},[step,auto]);

  return <div style={{padding:"12px 0"}}>
    <div style={{display:"flex",justifyContent:"center",alignItems:"center",gap:24,minHeight:160,flexWrap:"wrap"}}>
      <motion.div layout style={{display:"flex",flexWrap:"wrap",gap:3,maxWidth:200,padding:10,borderRadius:20,border:isTen?`3px solid ${C.yellow}`:`2px dashed ${C.border}`,background:isTen?"rgba(255,217,61,0.12)":"transparent",justifyContent:"center",minWidth:60,minHeight:50}}>
        {Array.from({length:leftN},(_,i)=><motion.div key={`l${i}`} initial={i>=L?{x:60,opacity:0,scale:0.5}:{scale:0}} animate={{x:0,opacity:1,scale:1}} transition={{delay:i>=L?0.3:i*0.04,type:"spring",stiffness:300}}><CuteObject index={shapes[i]??0} size={34} highlighted={isTen}/></motion.div>)}
        {isTen&&<motion.div initial={{scale:0}} animate={{scale:1}} style={{width:"100%",textAlign:"center",fontWeight:800,color:C.orange,fontSize:20}}>10</motion.div>}
      </motion.div>
      <span style={{fontSize:30,fontWeight:800,color:C.text}}>+</span>
      <motion.div layout style={{display:"flex",flexWrap:"wrap",gap:3,maxWidth:200,padding:10,borderRadius:20,border:`2px dashed ${C.border}`,justifyContent:"center",minWidth:60,minHeight:50}}>
        {isSplit&&!isMoved?<>
          <div style={{display:"flex",gap:2,padding:4,borderRadius:12,background:"rgba(255,140,66,0.12)",border:`1.5px dashed ${C.orange}`}}>
            {Array.from({length:parts[0]},(_,i)=><motion.div key={`s0-${i}`} initial={{y:-20,opacity:0}} animate={{y:0,opacity:1}} transition={{delay:i*0.1}}><CuteObject index={shapes[L+i]??1} size={30} highlighted/></motion.div>)}
            <span style={{fontSize:11,color:C.orange,fontWeight:700,alignSelf:"center"}}>{parts[0]}</span>
          </div>
          <div style={{display:"flex",gap:2,padding:4}}>
            {Array.from({length:parts[1]},(_,i)=><motion.div key={`s1-${i}`} initial={{y:-20,opacity:0}} animate={{y:0,opacity:1}} transition={{delay:0.2+i*0.1}}><CuteObject index={shapes[L+parts[0]+i]??2} size={30}/></motion.div>)}
            <span style={{fontSize:11,color:C.textLight,fontWeight:700,alignSelf:"center"}}>{parts[1]}</span>
          </div>
        </>:Array.from({length:Math.max(0,rightN)},(_,i)=><motion.div key={`r${i}`} initial={{scale:0}} animate={{scale:1}} transition={{delay:i*0.04}}><CuteObject index={shapes[L+(isMoved?parts[0]:0)+i]??3} size={34}/></motion.div>)}
        {isMoved&&!isComb&&rightN>0&&<div style={{width:"100%",textAlign:"center",fontWeight:800,color:C.teal,fontSize:18}}>{rightN}</div>}
      </motion.div>
    </div>
    <AnimatePresence>{isComb&&<motion.div initial={{scale:0}} animate={{scale:1}} transition={{type:"spring"}} style={{textAlign:"center",fontSize:30,fontWeight:900,color:C.pink,margin:"8px 0"}}>{steps[combI]?.values?.join(" + ")} = {steps[combI]?.result} 🎉</motion.div>}</AnimatePresence>
    <Mascot mood={isComb?"wow":isTen?"happy":"think"} size={56} message={cur.narration}/>
    <AnimControls step={step} total={steps.length} onPrev={goPrev} onNext={goNext} auto={auto} onAutoToggle={()=>setAuto(!auto)}/>
  </div>;
}

// ============================================================
//  SUBTRACTION ANIMATION (10以内减法 - 拿走法) ← NEW
// ============================================================
function SubtractionAnimation({ data, onComplete }) {
  const [step, setStep] = useState(0);
  const steps = data.steps; const cur = steps[step];
  const totalStep = steps.find(s => s.action === "show_total") || {};
  const total = totalStep.total || 0;
  const removeStep = steps.find(s => s.action === "remove") || {};
  const removeCount = removeStep.count || 0;
  const resultStep = steps.find(s => s.action === "show_result") || {};
  const result = resultStep.result || 0;
  const shapes = useShapePool(total);

  const removeI = steps.findIndex(s => s.action === "remove");
  const doneI = steps.findIndex(s => s.action === "show_result");
  const isRemoving = removeI >= 0 && step >= removeI;
  const isDone = doneI >= 0 && step >= doneI;

  // Animate removal one by one
  const [removedCount, setRemovedCount] = useState(0);
  useEffect(() => {
    if (isRemoving && !isDone) {
      setRemovedCount(0);
      let c = 0;
      const iv = setInterval(() => { c++; setRemovedCount(c); if (c >= removeCount) clearInterval(iv); }, 400);
      return () => clearInterval(iv);
    }
    if (isDone) setRemovedCount(removeCount);
  }, [step]);

  const goNext = () => { if (step < steps.length - 1) setStep(s => s + 1); else onComplete?.(); };
  const goPrev = () => { if (step > 0) setStep(s => s - 1); };

  return <div style={{ padding: "12px 0" }}>
    <div style={{ display: "flex", justifyContent: "center", gap: 4, flexWrap: "wrap", maxWidth: 400, margin: "0 auto", minHeight: 100 }}>
      {Array.from({ length: total }, (_, i) => {
        const isBeingRemoved = isRemoving && i >= (total - removeCount) && i < (total - removeCount + removedCount);
        const isRemoved = isDone && i >= (total - removeCount);
        return (
          <motion.div key={i} initial={{ scale: 0 }} animate={{
            scale: isRemoved ? 0 : isBeingRemoved ? 0.3 : 1,
            opacity: isRemoved ? 0 : isBeingRemoved ? 0.2 : 1,
            y: isBeingRemoved ? -30 : 0,
          }} transition={{ duration: 0.4, type: "spring" }}
            style={{ position: "relative", margin: 2 }}>
            <CuteObject index={shapes[i]} size={40}/>
            {/* Show X mark on removed items */}
            {isBeingRemoved && (
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}
                style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <svg width="28" height="28" viewBox="0 0 24 24"><line x1="4" y1="4" x2="20" y2="20" stroke={C.coral} strokeWidth="3" strokeLinecap="round"/><line x1="20" y1="4" x2="4" y2="20" stroke={C.coral} strokeWidth="3" strokeLinecap="round"/></svg>
              </motion.div>
            )}
          </motion.div>
        );
      })}
    </div>

    {/* Show count during removal */}
    {isRemoving && !isDone && (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        style={{ textAlign: "center", fontSize: 18, fontWeight: 800, color: C.coral, margin: "8px 0" }}>
        拿走了 {removedCount} / {removeCount} 个
      </motion.div>
    )}

    {isDone && (
      <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} style={{ textAlign: "center", fontSize: 28, fontWeight: 900, color: C.green, margin: "8px 0" }}>
        还剩 {result} 个！
      </motion.div>
    )}

    <Mascot mood={isDone ? "happy" : isRemoving ? "wow" : "think"} size={56} message={cur.narration}/>
    <AnimControls step={step} total={steps.length} onPrev={goPrev} onNext={goNext}/>
  </div>;
}

// ============================================================
//  BREAK TEN ANIMATION (20以内退位减法 - 破十法) ← NEW
// ============================================================
function BreakTenAnimation({ data, onComplete }) {
  const [step, setStep] = useState(0);
  const steps = data.steps; const cur = steps[step];
  const totalStep = steps.find(s => s.action === "show_total") || {};
  const total = totalStep.total || 0;
  const decompStep = steps.find(s => s.action === "decompose") || {};
  const tens = decompStep.tens || 10, ones = decompStep.ones || 0;
  const subStep = steps.find(s => s.action === "subtract_from_ten") || {};
  const subVal = subStep.sub || 0, subResult = subStep.result || 0;
  const combStep = steps.find(s => s.action === "combine") || {};
  const finalResult = combStep.result || 0;
  const shapes = useShapePool(total);

  const decompI = steps.findIndex(s => s.action === "decompose");
  const subI = steps.findIndex(s => s.action === "subtract_from_ten");
  const combI = steps.findIndex(s => s.action === "combine");
  const isDecomp = decompI >= 0 && step >= decompI;
  const isSub = subI >= 0 && step >= subI;
  const isComb = combI >= 0 && step >= combI;

  const goNext = () => { if (step < steps.length - 1) setStep(s => s + 1); else onComplete?.(); };
  const goPrev = () => { if (step > 0) setStep(s => s - 1); };

  return <div style={{ padding: "12px 0" }}>
    {!isDecomp ? (
      /* Phase 1: Show all objects */
      <div style={{ display: "flex", justifyContent: "center", gap: 3, flexWrap: "wrap", maxWidth: 420, margin: "0 auto" }}>
        {Array.from({ length: total }, (_, i) => (
          <motion.div key={i} initial={{ scale: 0, rotate: -90 }} animate={{ scale: 1, rotate: 0 }} transition={{ delay: i * 0.04, type: "spring" }}>
            <CuteObject index={shapes[i]} size={36}/>
          </motion.div>
        ))}
      </div>
    ) : (
      /* Phase 2+: Split into tens group and ones group */
      <div style={{ display: "flex", justifyContent: "center", alignItems: "flex-start", gap: 20, flexWrap: "wrap" }}>
        {/* Tens group */}
        <motion.div layout style={{
          display: "flex", flexWrap: "wrap", gap: 3, padding: 10, borderRadius: 20, justifyContent: "center",
          border: isSub ? `3px solid ${C.coral}` : `2px dashed ${C.orange}`,
          background: isSub ? "rgba(255,111,97,0.08)" : "rgba(255,140,66,0.08)", minWidth: 80,
        }}>
          {Array.from({ length: 10 }, (_, i) => {
            const removed = isSub && i >= (10 - subVal);
            return (
              <motion.div key={`t${i}`} animate={{ opacity: removed ? 0.15 : 1, scale: removed ? 0.6 : 1, y: removed ? -10 : 0 }}
                transition={{ duration: 0.3 }}>
                <CuteObject index={shapes[i]} size={30} dimmed={removed}/>
              </motion.div>
            );
          })}
          <div style={{ width: "100%", textAlign: "center", fontWeight: 800, fontSize: 16, color: isSub ? C.coral : C.orange }}>
            {isSub ? `10 - ${subVal} = ${subResult}` : "10"}
          </div>
        </motion.div>

        {/* Ones group */}
        <motion.div layout style={{
          display: "flex", flexWrap: "wrap", gap: 3, padding: 10, borderRadius: 20, justifyContent: "center",
          border: `2px dashed ${C.teal}`, background: "rgba(26,188,156,0.08)", minWidth: 50,
        }}>
          {Array.from({ length: ones }, (_, i) => (
            <motion.div key={`o${i}`} initial={{ x: -30, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: i * 0.1 }}>
              <CuteObject index={shapes[10 + i]} size={30}/>
            </motion.div>
          ))}
          <div style={{ width: "100%", textAlign: "center", fontWeight: 800, fontSize: 16, color: C.teal }}>{ones}</div>
        </motion.div>
      </div>
    )}

    {/* Final combine result */}
    <AnimatePresence>{isComb && (
      <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring" }}
        style={{ textAlign: "center", fontSize: 28, fontWeight: 900, color: C.green, margin: "12px 0" }}>
        {subResult} + {ones} = {finalResult} 🎉
      </motion.div>
    )}</AnimatePresence>

    <Mascot mood={isComb ? "wow" : isSub ? "happy" : isDecomp ? "think" : "happy"} size={56} message={cur.narration}/>
    <AnimControls step={step} total={steps.length} onPrev={goPrev} onNext={goNext}/>
  </div>;
}

// ============================================================
//  COUNTING ANIMATION (加法数数法)
// ============================================================
function CountingAnimation({ data, onComplete }) {
  const [step, setStep] = useState(0);
  const steps = data.steps; const cur = steps[step];
  const first = steps[0] || {};
  const L = first.left || 0, R = first.right || 0, total = L + R;
  const shapes = useShapePool(total);
  const countOnStep = steps.find(s => s.action === "count_on");
  const countAllStep = steps.find(s => s.action === "count_all");
  const showResultI = steps.findIndex(s => s.action === "show_result");
  const countPhaseI = steps.findIndex(s => s.action === "count_on" || s.action === "count_all");
  const isCountPhase = countPhaseI >= 0 && step >= countPhaseI;
  const isDone = showResultI >= 0 && step >= showResultI;
  const startVal = countOnStep?.start || 0;
  const countSeq = countOnStep?.sequence || countAllStep?.sequence || [];
  const [hl, setHl] = useState(-1);

  useEffect(() => {
    if (isCountPhase && countSeq.length > 0) {
      setHl(-1); let i = 0;
      const iv = setInterval(() => { if (i < countSeq.length) { setHl(i); i++; } else clearInterval(iv); }, 500);
      return () => clearInterval(iv);
    }
  }, [step]);

  const goNext = () => { if (step < steps.length - 1) setStep(s => s + 1); else onComplete?.(); };

  return <div style={{ padding: "12px 0" }}>
    <div style={{ display: "flex", justifyContent: "center", gap: 4, flexWrap: "wrap", maxWidth: 420, margin: "0 auto" }}>
      {Array.from({ length: total }, (_, i) => {
        const isRight = i >= L;
        const lit = isCountPhase && ((countOnStep && isRight && (i - L) <= hl) || (countAllStep && i <= hl));
        return <motion.div key={i} initial={{ scale: 0, rotate: -90 }} animate={{ scale: 1, rotate: 0 }}
          transition={{ delay: i * 0.06, type: "spring", stiffness: 250 }} style={{ position: "relative", margin: 2 }}>
          <CuteObject index={shapes[i]} size={40} highlighted={lit} dimmed={isCountPhase && !lit && !isDone}/>
          {isCountPhase && countOnStep && isRight && (i - L) <= hl && (
            <motion.div initial={{ scale: 0, y: -10 }} animate={{ scale: 1, y: 0 }}
              style={{ position: "absolute", top: -10, right: -6, background: C.orange, color: "#fff",
                borderRadius: "50%", width: 22, height: 22, fontSize: 12, fontWeight: 800,
                display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 1px 4px rgba(0,0,0,0.2)" }}>
              {startVal + (i - L) + 1}
            </motion.div>
          )}
        </motion.div>;
      })}
    </div>
    {/* Counting sequence display */}
    {isCountPhase && countOnStep && (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        style={{ display: "flex", justifyContent: "center", gap: 6, margin: "12px 0", flexWrap: "wrap", alignItems: "baseline" }}>
        <span style={{ fontSize: 18, fontWeight: 700, color: C.text }}>{startVal},</span>
        {countSeq.map((n, i) => (
          <motion.span key={n} animate={{ scale: i <= hl ? 1.15 : 0.8, opacity: i <= hl ? 1 : 0.3 }}
            style={{ fontSize: i <= hl ? 22 : 16, fontWeight: 800, color: i <= hl ? C.orange : C.textLight, transition: "all 0.3s" }}>
            {n}{i < countSeq.length - 1 ? "," : "!"}
          </motion.span>
        ))}
      </motion.div>
    )}
    <Mascot mood={isDone ? "happy" : isCountPhase ? "wow" : "think"} size={56} message={cur.narration}/>
    <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 12 }}>
      <button onClick={goNext} style={btnStyle(C.green)}>{step >= steps.length - 1 ? "✓ 看完啦" : "下一步 ▶"}</button>
    </div>
  </div>;
}

// ============================================================
//  NUMBER LINE ANIMATION
// ============================================================
function NumberLineAnimation({ data, onComplete }) {
  const [step, setStep] = useState(0);
  const steps = data.steps; const cur = steps[step];
  const lineS = steps.find(s => s.action === "draw_line") || { from: 0, to: 20 };
  const startS = steps.find(s => s.action === "mark_start");
  const endS = steps.find(s => s.action === "mark_end");
  const jumpS = steps.find(s => s.action === "jump" || s.action === "jump_split");
  const rf = lineS.from || 0, rt = lineS.to || 20;
  const sp = startS?.position ?? 0, ep = endS?.position ?? 0;
  const showStart = step >= steps.findIndex(s => s.action === "mark_start");
  const showJump = step >= steps.findIndex(s => s.action === "jump" || s.action === "jump_split");
  const showEnd = step >= steps.findIndex(s => s.action === "mark_end");
  const jumpN = jumpS?.count || Math.abs(ep - sp);
  const dir = (jumpS?.direction === "left") ? -1 : 1;
  const [aj, setAj] = useState(0);
  useEffect(() => { if (showJump) { setAj(0); let i=0; const iv = setInterval(() => { i++; setAj(i); if (i >= jumpN) clearInterval(iv); }, 400); return () => clearInterval(iv); } }, [step]);
  const W = 600, H = 130, pad = 40;
  const nx = (n) => pad + ((n - rf) / (rt - rf)) * (W - 2 * pad);
  const goNext = () => { if (step < steps.length - 1) setStep(s => s + 1); else onComplete?.(); };
  const goPrev = () => { if (step > 0) setStep(s => s - 1); };

  return <div style={{ padding: "12px 0" }}>
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", maxWidth: 580, display: "block", margin: "0 auto" }}>
      <line x1={pad - 5} y1={65} x2={W - pad + 5} y2={65} stroke={C.text} strokeWidth={2.5} strokeLinecap="round"/>
      {Array.from({ length: rt - rf + 1 }, (_, i) => { const n = rf + i, x = nx(n), major = n % 5 === 0 || n === sp || n === ep;
        return <g key={n}><line x1={x} y1={58} x2={x} y2={72} stroke={C.text} strokeWidth={major ? 2 : 0.8} opacity={major ? 1 : 0.4}/>{major && <text x={x} y={86} textAnchor="middle" fontSize={11} fill={C.text} fontWeight={600}>{n}</text>}</g>; })}
      {showStart && <motion.g initial={{ scale: 0 }} animate={{ scale: 1 }}><circle cx={nx(sp)} cy={65} r={10} fill={C.pink} stroke="#fff" strokeWidth={2}/><text x={nx(sp)} y={48} textAnchor="middle" fontSize={15} fontWeight={800} fill={C.pink}>{sp}</text></motion.g>}
      {showJump && Array.from({ length: Math.min(aj, jumpN) }, (_, i) => {
        const fn = sp + dir * i, tn = sp + dir * (i + 1); const fx = nx(fn), tx = nx(tn), mx = (fx + tx) / 2;
        return <motion.g key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <path d={`M${fx},58 Q${mx},22 ${tx},58`} fill="none" stroke={C.blue} strokeWidth={2.5} strokeLinecap="round"/>
          <circle cx={tx} cy={58} r={3} fill={C.blue}/>
          <text x={tx} y={16} textAnchor="middle" fontSize={12} fontWeight={700} fill={C.blue}>{tn}</text>
        </motion.g>; })}
      {showEnd && <motion.g initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring" }}><circle cx={nx(ep)} cy={65} r={13} fill={C.green} stroke="#fff" strokeWidth={3}/><text x={nx(ep)} y={105} textAnchor="middle" fontSize={16} fontWeight={900} fill={C.green}>{ep}</text></motion.g>}
    </svg>
    <Mascot mood={showEnd ? "happy" : showJump ? "wow" : "think"} size={56} message={cur.narration}/>
    <AnimControls step={step} total={steps.length} onPrev={goPrev} onNext={goNext}/>
  </div>;
}

// ============================================================
//  STEP-BY-STEP ANIMATION (分步法)
//  支持两种子结构：
//    1. 个位/十位分解 (decompose → add_ones → combine)   lesson-04
//    2. 顺序计算     (highlight_first_pair → compute…)   lesson-08
// ============================================================
function StepByStepAnimation({ data, onComplete }) {
  const [step, setStep] = useState(0);
  const steps = data.steps;
  const cur = steps[step];
  const goNext = () => { if (step < steps.length - 1) setStep(s => s + 1); else onComplete?.(); };
  const goPrev = () => { if (step > 0) setStep(s => s - 1); };

  // ── 样式判断 ────────────────────────────────────────────
  const isPlaceValue = steps.some(s => s.action === "decompose");

  // ── 个位/十位分解 ────────────────────────────────────────
  if (isPlaceValue) {
    const decompS = steps.find(s => s.action === "decompose") || {};
    const addOnesS = steps.find(s => s.action === "add_ones") || {};
    const combineS = steps.find(s => s.action === "combine") || {};
    const decompI  = steps.findIndex(s => s.action === "decompose");
    const addOnesI = steps.findIndex(s => s.action === "add_ones");
    const combineI = steps.findIndex(s => s.action === "combine");
    const isDecomp   = decompI  >= 0 && step >= decompI;
    const isAddOnes  = addOnesI >= 0 && step >= addOnesI;
    const isCombined = combineI >= 0 && step >= combineI;

    const tens       = decompS.parts?.[0] ?? 0;
    const onesA      = decompS.parts?.[1] ?? 0;
    const addend     = addOnesS.values?.[1] ?? 0;
    const onesResult = addOnesS.result ?? 0;
    const finalResult = combineS.result ?? 0;

    return <div style={{ padding: "12px 0" }}>
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 14, minHeight: 160, flexWrap: "wrap" }}>

        {/* 十位 box */}
        <motion.div layout style={{ padding: "14px 22px", borderRadius: 22,
          border: `3px solid ${isCombined ? C.green : C.blue}`,
          background: isCombined ? "rgba(107,203,119,0.12)" : "rgba(77,150,255,0.08)",
          textAlign: "center", minWidth: 90 }}>
          <div style={{ fontSize: 12, color: C.blue, fontWeight: 700, marginBottom: 4 }}>十位</div>
          <motion.div initial={{ scale: 0 }} animate={{ scale: isDecomp ? 1 : 0 }}
            style={{ fontSize: 44, fontWeight: 900, color: isCombined ? C.green : C.blue }}>
            {tens}
          </motion.div>
        </motion.div>

        {/* 中间符号 */}
        <AnimatePresence mode="wait">
          {isCombined
            ? <motion.span key="eq" initial={{ scale: 0 }} animate={{ scale: 1 }}
                style={{ fontSize: 32, fontWeight: 900, color: C.green }}>=</motion.span>
            : isDecomp
              ? <motion.span key="plus" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  style={{ fontSize: 32, fontWeight: 900, color: C.text }}>+</motion.span>
              : null}
        </AnimatePresence>

        {/* 个位 box 或 最终结果 */}
        <AnimatePresence mode="wait">
          {isCombined ? (
            <motion.div key="result" initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring" }}
              style={{ fontSize: 64, fontWeight: 900, color: C.green }}>{finalResult}</motion.div>
          ) : (
            <motion.div key="ones" layout style={{ padding: "14px 22px", borderRadius: 22,
              border: `3px solid ${isAddOnes ? C.orange : C.border}`,
              background: isAddOnes ? "rgba(255,140,66,0.10)" : "transparent",
              textAlign: "center", minWidth: 90 }}>
              <div style={{ fontSize: 12, color: C.orange, fontWeight: 700, marginBottom: 4 }}>个位</div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
                <motion.span initial={{ scale: 0 }} animate={{ scale: isDecomp ? 1 : 0 }}
                  style={{ fontSize: 38, fontWeight: 900, color: C.orange }}>{onesA}</motion.span>
                {isAddOnes && <>
                  <span style={{ fontSize: 24, fontWeight: 800, color: C.text }}>+</span>
                  <motion.span initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }}
                    style={{ fontSize: 38, fontWeight: 900, color: C.pink }}>{addend}</motion.span>
                  <span style={{ fontSize: 24, fontWeight: 800, color: C.text }}>=</span>
                  <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }}
                    style={{ fontSize: 38, fontWeight: 900, color: C.teal }}>{onesResult}</motion.span>
                </>}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <Mascot mood={isCombined ? "wow" : isAddOnes ? "happy" : "think"} size={56} message={cur.narration}/>
      <AnimControls step={step} total={steps.length} onPrev={goPrev} onNext={goNext}/>
    </div>;
  }

  // ── 顺序计算 (highlight_first_pair + compute) ────────────
  // 找出到当前步骤为止已到达的最新 compute step
  const computeSteps = steps
    .map((s, i) => ({ ...s, _idx: i }))
    .filter(s => s.action === "compute");
  const reachedCompute = computeSteps.filter(s => step >= s._idx);
  const latest = reachedCompute[reachedCompute.length - 1] ?? null;
  const isDone = latest && latest === computeSteps[computeSteps.length - 1];

  const highlightI = steps.findIndex(s => s.action === "highlight_first_pair");
  const highlightS = steps[highlightI] || {};
  const isHighlighted = highlightI >= 0 && step >= highlightI;

  // 从顶层 expression 解析数字列表，用于高亮展示
  const topExpr = data.expression || "";
  const allNums = topExpr.match(/\d+/g) || [];

  return <div style={{ padding: "12px 0" }}>
    <AnimatePresence mode="wait">
      {!latest ? (
        // 初始：展示原式，高亮第一对加数
        <motion.div key="init" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 10, flexWrap: "wrap", minHeight: 100 }}>
          {allNums.map((n, i) => {
            const isHl = isHighlighted && highlightS.values?.includes(Number(n)) && i < 2;
            return <motion.span key={i} animate={{ scale: isHl ? 1.3 : 1 }}
              style={{ fontSize: 44, fontWeight: 900,
                color: isHl ? C.orange : C.text,
                background: isHl ? "rgba(255,140,66,0.12)" : "transparent",
                borderRadius: 12, padding: "4px 10px",
                border: isHl ? `3px solid ${C.orange}` : "3px solid transparent" }}>
              {i % 2 === 0 ? n : "+"}
            </motion.span>;
          })}
        </motion.div>
      ) : (
        // 显示当前计算式
        <motion.div key={latest.expression} initial={{ scale: 0.7, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.7, opacity: 0 }}
          style={{ textAlign: "center", minHeight: 100, display: "flex", alignItems: "center", justifyContent: "center", gap: 14 }}>
          <span style={{ fontSize: 38, fontWeight: 900, color: C.text }}>{latest.expression}</span>
          <span style={{ fontSize: 38, fontWeight: 900, color: C.text }}>=</span>
          <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.2, type: "spring" }}
            style={{ fontSize: 52, fontWeight: 900, color: isDone ? C.green : C.teal }}>{latest.result}</motion.span>
        </motion.div>
      )}
    </AnimatePresence>

    <Mascot mood={isDone ? "wow" : latest ? "happy" : "think"} size={56} message={cur.narration}/>
    <AnimControls step={step} total={steps.length} onPrev={goPrev} onNext={goNext}/>
  </div>;
}

// ===== ANIMATION ROUTER =====
function AnimationPlayer({ methodData, onComplete }) {
  const t = methodData.type;
  const p = { data: methodData, onComplete };
  if (t === "make_ten") return <MakeTenAnimation {...p}/>;
  if (t === "break_ten") return <BreakTenAnimation {...p}/>;
  if (t === "subtraction") return <SubtractionAnimation {...p}/>;
  if (t === "number_line") return <NumberLineAnimation {...p}/>;
  if (t === "counting") return <CountingAnimation {...p}/>;
  if (t === "step_by_step") return <StepByStepAnimation {...p}/>;
  return <CountingAnimation {...p}/>;
}

// ============================================================
//  EXERCISE GAME
// ============================================================
function ExerciseGame({ lessonId, exerciseCount = 10, onComplete, username = "同学" }) {
  const [exercises, setExercises] = useState(null);
  const [current, setCurrent] = useState(0);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState(null);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [showSolution, setShowSolution] = useState(false);
  const [timeLeft, setTimeLeft] = useState(null);
  const [started, setStarted] = useState(false);
  const inputRef = useRef(null);

  // ⚠️ 所有 Hook 必须在任何 early return 之前调用
  useEffect(() => {
    fetch(`${API}/lessons/${lessonId}/random-exercises?count=${exerciseCount}`)
      .then(r => r.json()).then(setExercises);
  }, [lessonId]);

  useEffect(() => {
    if (!started || timeLeft <= 0) return;
    const t = setInterval(() => setTimeLeft(v => Math.max(0, v - 1)), 1000);
    return () => clearInterval(t);
  }, [started, timeLeft]);

  // 所有 Hook 已调用完毕，此处可以安全 early return
  if (!exercises) return <div style={{ textAlign: "center", padding: 40, color: C.textLight }}>加载题目中...</div>;
  if (exercises.length === 0) return (
    <div style={{ textAlign: "center", padding: 40 }}>
      <Mascot mood="think" size={70} message="这节课还没有题目，等老师来出题吧～"/>
    </div>
  );

  const ex = exercises[current];
  const startGame = () => { setStarted(true); setTimeLeft(150); };

  const checkAns = (ans) => { const a = ans || answer; if (!a.toString().trim()) return;
    const correct = String(a).trim() === String(ex.correct_answer).trim();
    setResult({ correct, hints: ex.hints || [], solutions: ex.solutions || [] });
    setScore(s => ({ correct: s.correct + (correct ? 1 : 0), total: s.total + 1 })); };
  const next = () => { if (current + 1 >= exercises.length || timeLeft <= 0) { onComplete?.(score); return; }
    setCurrent(c => c + 1); setAnswer(""); setResult(null); setShowSolution(false);
    setTimeout(() => inputRef.current?.focus(), 100); };

  if (!started) return <div style={{ textAlign: "center", padding: 40 }}>
    <Mascot mood="happy" size={70} message={`${username}，准备好了吗？我们来挑战吧！`}/>
    <div style={{ marginTop: 20 }}>
      <p style={{ color: C.textLight, margin: "0 0 16px" }}>从题库中随机抽取 {exercises.length} 道题</p>
      <button onClick={startGame} style={{ ...btnStyle(`linear-gradient(135deg,${C.pink},${C.purple})`), padding: "16px 48px", fontSize: 20, borderRadius: 30, background: `linear-gradient(135deg,${C.pink},${C.purple})` }}>开始挑战 🚀</button>
    </div>
  </div>;

  if (timeLeft <= 0 || (result && current + 1 >= exercises.length)) {
    const s = score; const pct = s.total > 0 ? s.correct / s.total : 0;
    const stars = pct >= 0.9 ? 3 : pct >= 0.65 ? 2 : pct >= 0.3 ? 1 : 0;
    return <div style={{ textAlign: "center", padding: 30 }}><motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring" }}>
      <Mascot mood={stars >= 2 ? "wow" : "happy"} size={80} message={stars >= 2 ? `${username}太厉害了！你是数学小天才！` : stars >= 1 ? `${username}，不错哦，继续加油！` : `${username}，别灰心，多练习就好啦！`}/>
      <div style={{ display: "flex", justifyContent: "center", margin: "16px 0" }}><Stars count={stars} size={36}/></div>
      <p style={{ color: C.text, fontSize: 18, fontWeight: 700 }}>答对 {s.correct} / {s.total} 题</p>
      <button onClick={() => onComplete?.(s)} style={{ ...btnStyle(C.teal), marginTop: 16, padding: "12px 36px", fontSize: 16 }}>返回</button>
    </motion.div></div>;
  }

  return <div style={{ padding: "12px 0" }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
      <span style={{ fontSize: 13, color: C.textLight, fontWeight: 600 }}>第 {current + 1}/{exercises.length}</span>
      <span style={{ fontSize: 14, fontWeight: 700, color: timeLeft < 30 ? C.coral : C.text, padding: "4px 12px", background: timeLeft < 30 ? "rgba(255,111,97,0.1)" : C.border, borderRadius: 12 }}>⏱ {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, "0")}</span>
      <span style={{ fontSize: 13, color: C.green, fontWeight: 700 }}>✓ {score.correct}</span>
    </div>
    <div style={{ height: 6, background: C.border, borderRadius: 3, marginBottom: 16 }}>
      <motion.div animate={{ width: `${((current + 1) / exercises.length) * 100}%` }} style={{ height: "100%", background: `linear-gradient(90deg,${C.teal},${C.green})`, borderRadius: 3 }}/>
    </div>
    <motion.div key={current} initial={{ x: 40, opacity: 0 }} animate={{ x: 0, opacity: 1 }}
      style={{ textAlign: "center", padding: "28px 20px", background: C.card, borderRadius: 24, boxShadow: "0 4px 20px rgba(0,0,0,0.06)", border: `2px solid ${C.border}` }}>
      <p style={{ fontSize: 32, fontWeight: 900, color: C.text, margin: "0 0 20px", letterSpacing: 3 }}>{ex.question}</p>
      {ex.type === "choice" && ex.options?.length > 0 ? (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, maxWidth: 280, margin: "0 auto" }}>
          {ex.options.map((opt, i) => {
            const isC = result && String(opt) === String(ex.correct_answer);
            const isW = result && String(opt) === String(answer) && !result.correct;
            return <button key={i} onClick={() => { setAnswer(opt); checkAns(opt); }} disabled={!!result}
              style={{ padding: "14px", borderRadius: 16, fontSize: 22, fontWeight: 800, cursor: result ? "default" : "pointer",
                border: isC ? `3px solid ${C.green}` : isW ? `3px solid ${C.coral}` : `2px solid ${C.border}`,
                background: isC ? "rgba(107,203,119,0.12)" : isW ? "rgba(255,111,97,0.1)" : "#fff", color: C.text }}>{opt}</button>; })}
        </div>
      ) : (
        <div style={{ display: "flex", justifyContent: "center", gap: 10, alignItems: "center" }}>
          <input ref={inputRef} type="number" value={answer} onChange={e => setAnswer(e.target.value)}
            onKeyDown={e => e.key === "Enter" && checkAns()} disabled={!!result} autoFocus
            style={{ width: 100, fontSize: 32, fontWeight: 800, textAlign: "center", padding: "8px 12px", borderRadius: 16,
              border: `3px solid ${result ? (result.correct ? C.green : C.coral) : C.border}`, outline: "none", color: C.text,
              background: result ? (result.correct ? "rgba(107,203,119,0.08)" : "rgba(255,111,97,0.06)") : "#fff" }}/>
          {!result && <button onClick={() => checkAns()} style={btnStyle(C.pink)}>确认</button>}
        </div>
      )}
      <AnimatePresence>{result && (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} style={{ marginTop: 16 }}>
          {result.correct ? <motion.p initial={{ scale: 0.5 }} animate={{ scale: 1 }} style={{ color: C.green, fontSize: 20, fontWeight: 800, margin: 0 }}>✅ {username} 答对啦！太棒了！</motion.p>
          : <div>
            <p style={{ color: C.coral, fontSize: 17, fontWeight: 700, margin: "0 0 8px" }}>再想想～答案是 <b>{ex.correct_answer}</b></p>
            {result.hints?.length > 0 && !showSolution && <button onClick={() => setShowSolution(true)} style={{ ...btnStyle(C.purple), padding: "5px 14px", fontSize: 13 }}>💡 看解题思路</button>}
            {showSolution && result.hints.map((h, i) => <p key={i} style={{ color: C.textLight, fontSize: 13, margin: "4px 0" }}>💡 {h}</p>)}
          </div>}
          <button onClick={next} style={{ ...btnStyle(C.teal), marginTop: 10, padding: "10px 30px" }}>{current + 1 >= exercises.length ? "看成绩" : "下一题 ▶"}</button>
        </motion.div>
      )}</AnimatePresence>
    </motion.div>
  </div>;
}

// ============================================================
//  PAGES
// ============================================================
function CourseMap({ onSelectLesson, username, onSetUsername }) {
  const { data: courses, loading } = useFetch("/courses?status=published");
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState([]);
  const [editingName, setEditingName] = useState(false);
  const [nameInput, setNameInput] = useState(username);
  useEffect(() => { if (courses?.length) { fetch(API + `/courses/${courses[0].id}/lessons`).then(r => r.json()).then(setLessons); fetch(API + `/progress/student-001`).then(r => r.json()).then(setProgress); } }, [courses]);
  const getStars = (lid) => (progress.find(p => p.lesson_id === lid))?.stars || 0;
  if (loading) return <div style={{ textAlign: "center", padding: 60 }}><Mascot mood="think" size={80} message="正在准备课程..."/></div>;

  const commitName = () => { onSetUsername(nameInput); setEditingName(false); };
  const emojis = ["🐣","🌈","🎵","🌸","🍎","🧩","🎲","🔢"];
  const colors = [C.pink, C.blue, C.green, C.orange, C.purple, C.teal, C.coral, C.yellow];

  return <div style={{ padding: "20px 16px", maxWidth: 460, margin: "0 auto", position: "relative", zIndex: 1 }}>
    {/* 姓名标签 */}
    <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
      {editingName ? (
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <input autoFocus value={nameInput} onChange={e => setNameInput(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter") commitName(); if (e.key === "Escape") setEditingName(false); }}
            maxLength={8}
            style={{ width: 80, fontSize: 15, fontWeight: 700, textAlign: "center", padding: "4px 8px",
              borderRadius: 12, border: `2px solid ${C.pink}`, outline: "none", color: C.text }}/>
          <button onClick={commitName} style={{ ...btnStyle(C.pink), padding: "4px 12px", fontSize: 13, borderRadius: 12 }}>确定</button>
        </div>
      ) : (
        <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
          onClick={() => { setNameInput(username); setEditingName(true); }}
          style={{ display: "flex", alignItems: "center", gap: 5, padding: "5px 12px", borderRadius: 20,
            border: `2px solid ${C.border}`, background: C.card, cursor: "pointer",
            fontSize: 14, fontWeight: 700, color: C.text, boxShadow: "0 1px 4px rgba(0,0,0,0.06)" }}>
          <span>👤</span><span>{username}</span><span style={{ fontSize: 11, color: C.textLight }}>✏️</span>
        </motion.button>
      )}
    </div>
    <div style={{ textAlign: "center", marginBottom: 20 }}><Mascot mood="happy" size={72} message={`欢迎来到数学小天地，${username}！选一个开始吧～`}/></div>
    <h2 style={{ textAlign: "center", fontSize: 22, fontWeight: 800, color: C.text, margin: "0 0 4px" }}>🧮 {courses?.[0]?.title || "数学启蒙"}</h2>
    <p style={{ textAlign: "center", fontSize: 13, color: C.textLight, margin: "0 0 20px" }}>{courses?.[0]?.description}</p>
    <div style={{ position: "relative" }}>
      <div style={{ position: "absolute", left: "50%", top: 0, bottom: 0, width: 4, background: `linear-gradient(180deg,${C.yellow},${C.teal},${C.pink})`, transform: "translateX(-50%)", borderRadius: 2, zIndex: 0, opacity: 0.3 }}/>
      {lessons.filter(l => l.status === "published").map((lesson, i) => {
        const stars = getStars(lesson.id); const prevStars = i > 0 ? getStars(lessons[i - 1]?.id) : 1;
        const locked = i > 0 && prevStars === 0; const side = i % 2 === 0 ? "left" : "right";
        return <motion.div key={lesson.id} initial={{ opacity: 0, x: side === "left" ? -30 : 30 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }}
          style={{ display: "flex", justifyContent: side === "left" ? "flex-start" : "flex-end", position: "relative", zIndex: 1, marginBottom: 10 }}>
          <motion.button onClick={() => !locked && onSelectLesson(lesson.id)} disabled={locked}
            whileHover={locked ? {} : { scale: 1.03 }} whileTap={locked ? {} : { scale: 0.97 }}
            style={{ width: "46%", padding: "12px 14px", borderRadius: 20, textAlign: "left",
              border: stars > 0 ? `2.5px solid ${colors[i % colors.length]}` : `2px solid ${C.border}`,
              background: locked ? "#f5f0e8" : C.card, cursor: locked ? "not-allowed" : "pointer", opacity: locked ? 0.45 : 1,
              boxShadow: stars > 0 ? `0 3px 12px ${colors[i % colors.length]}25` : "0 1px 4px rgba(0,0,0,0.04)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 22 }}>{locked ? "🔒" : stars >= 3 ? "🌟" : emojis[i] || "📖"}</span><Stars count={stars} size={14}/>
            </div>
            <p style={{ margin: "5px 0 0", fontSize: 14, fontWeight: 700, color: C.text, lineHeight: 1.3 }}>{lesson.title}</p>
            <p style={{ margin: "2px 0 0", fontSize: 11, color: C.textLight, lineHeight: 1.3 }}>{lesson.description}</p>
          </motion.button>
        </motion.div>; })}
    </div>
  </div>;
}

function LessonPage({ lessonId, onBack, username }) {
  const { data: lesson, loading } = useFetch(`/lessons/${lessonId}`);
  const [tab, setTab] = useState("tutorial");
  const [methodIdx, setMethodIdx] = useState(0);
  const [variantIdx, setVariantIdx] = useState(-1);
  if (loading || !lesson) return <div style={{ textAlign: "center", padding: 60 }}><Mascot mood="think" size={70} message="加载中..."/></div>;
  const variants = lesson.animation_variants || [];
  const allAnimData = [lesson.animation_data, ...variants];
  const currentAnim = variantIdx < 0 ? lesson.animation_data : variants[variantIdx];
  const methods = currentAnim?.methods || [];

  const pickRandom = () => { if (allAnimData.length <= 1) return; let n; do { n = Math.floor(Math.random() * allAnimData.length) - 1; } while (n === variantIdx && allAnimData.length > 1); setVariantIdx(n); setMethodIdx(0); };

  const handleExComplete = async (score) => {
    const pct = score.total > 0 ? score.correct / score.total : 0;
    const stars = pct >= 0.9 ? 3 : pct >= 0.65 ? 2 : pct >= 0.3 ? 1 : 0;
    try { await fetch(API + "/progress/student-001", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lesson_id: lessonId, stars, correct_count: score.correct, total_count: score.total, time_spent: 150 }) }); } catch {}
    setTab("tutorial");
  };

  return <div style={{ padding: "14px 16px", maxWidth: 560, margin: "0 auto", position: "relative", zIndex: 1 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
      <button onClick={onBack} style={{ width: 38, height: 38, borderRadius: 14, border: `2px solid ${C.border}`, background: C.card, cursor: "pointer", fontSize: 18, display: "flex", alignItems: "center", justifyContent: "center" }}>←</button>
      <div style={{ flex: 1 }}><h2 style={{ margin: 0, fontSize: 18, fontWeight: 800, color: C.text }}>{lesson.title}</h2>
        <p style={{ margin: 0, fontSize: 12, color: C.textLight }}>{lesson.description}</p></div>
    </div>
    <div style={{ display: "flex", gap: 6, marginBottom: 14, background: C.border, borderRadius: 16, padding: 4 }}>
      {[["tutorial", "📖 教程"], ["practice", "🎮 练习"]].map(([k, l]) =>
        <button key={k} onClick={() => setTab(k)} style={{ flex: 1, padding: "10px 0", borderRadius: 14, border: "none", fontSize: 15, fontWeight: 700,
          background: tab === k ? C.card : "transparent", color: tab === k ? C.text : C.textLight,
          boxShadow: tab === k ? "0 2px 8px rgba(0,0,0,0.06)" : "none", cursor: "pointer" }}>{l}</button>)}
    </div>

    {tab === "tutorial" && <div>
      <div style={{ textAlign: "center", padding: "14px 0", margin: "0 0 10px",
        background: `linear-gradient(135deg,rgba(255,107,138,0.08),rgba(155,89,182,0.08))`, borderRadius: 18 }}>
        <span style={{ fontSize: 30, fontWeight: 900, color: C.text, letterSpacing: 4 }}>{currentAnim?.expression || ""}</span>
      </div>
      {allAnimData.length > 1 && <div style={{ textAlign: "center", marginBottom: 10 }}>
        <button onClick={pickRandom} style={{ ...btnStyle(C.purple), padding: "6px 16px", fontSize: 13, borderRadius: 16 }}>🔄 换一道题 ({allAnimData.length} 种)</button>
      </div>}
      {methods.length > 1 && <div style={{ display: "flex", gap: 6, marginBottom: 10, overflowX: "auto" }}>
        {methods.map((m, i) => <button key={i} onClick={() => setMethodIdx(i)} style={{ padding: "7px 14px", borderRadius: 18, border: "none", whiteSpace: "nowrap",
          background: methodIdx === i ? C.purple : C.border, color: methodIdx === i ? "#fff" : C.text, fontSize: 13, fontWeight: 700, cursor: "pointer" }}>{m.title}</button>)}
      </div>}
      {methods.length > 0 && <div style={{ background: C.card, borderRadius: 22, padding: 14, boxShadow: "0 3px 16px rgba(0,0,0,0.05)", border: `2px solid ${C.border}` }}>
        <AnimatePresence mode="wait"><motion.div key={`${variantIdx}-${methodIdx}`} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <AnimationPlayer methodData={methods[methodIdx]}/></motion.div></AnimatePresence>
      </div>}
      <button onClick={() => setTab("practice")} style={{ width: "100%", padding: "14px 0", borderRadius: 22, border: "none", marginTop: 14,
        background: `linear-gradient(135deg,${C.pink},${C.purple})`, color: "#fff", fontSize: 18, fontWeight: 800, cursor: "pointer", boxShadow: `0 4px 12px ${C.pink}40` }}>
        开始练习 🎮 (随机 10 题)
      </button>
    </div>}
    {tab === "practice" && <ExerciseGame lessonId={lessonId} exerciseCount={10} onComplete={handleExComplete} username={username}/>}
  </div>;
}

// ===== APP ROOT =====
export default function App() {
  const [currentLesson, setCurrentLesson] = useState(null);
  const [username, setUsername] = useState(() => localStorage.getItem("mathkids_username") || "当当");

  const handleSetUsername = (name) => {
    const trimmed = name.trim() || "当当";
    setUsername(trimmed);
    localStorage.setItem("mathkids_username", trimmed);
  };

  return <div style={{ minHeight: "100vh", fontFamily: "'Nunito','PingFang SC','Microsoft YaHei',sans-serif",
    background: `linear-gradient(180deg,${C.bg1} 0%,${C.bg2} 50%,${C.bg3} 100%)` }}>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet"/>
    <FloatingDecos/>
    <AnimatePresence mode="wait">
      {currentLesson ? <motion.div key="lesson" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
        <LessonPage lessonId={currentLesson} onBack={() => setCurrentLesson(null)} username={username}/></motion.div>
      : <motion.div key="map" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
        <CourseMap onSelectLesson={setCurrentLesson} username={username} onSetUsername={handleSetUsername}/></motion.div>}
    </AnimatePresence>
  </div>;
}
