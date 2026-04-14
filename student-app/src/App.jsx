import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API = "http://localhost:8000/api";

// ===== Utility hooks =====
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch(API + url).then(r => r.json()).then(d => { setData(d); setLoading(false); }).catch(() => setLoading(false));
  }, [url]);
  return { data, loading };
}

// ===== Color palette =====
const colors = {
  bg: "#FFF8F0", card: "#FFFFFF", primary: "#FF6B6B", secondary: "#4ECDC4",
  accent: "#FFE66D", purple: "#A78BFA", blue: "#60A5FA", green: "#34D399",
  text: "#2D3436", textLight: "#636E72", border: "#F0E6D8",
  star: "#FBBF24", starEmpty: "#E5E7EB"
};

// ===== Star display =====
function Stars({ count = 0, max = 3, size = 20 }) {
  return (
    <div style={{ display: "flex", gap: 2 }}>
      {Array.from({ length: max }, (_, i) => (
        <svg key={i} width={size} height={size} viewBox="0 0 24 24" fill={i < count ? colors.star : colors.starEmpty}>
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
      ))}
    </div>
  );
}

// ===== Apple/Star shape for animations =====
function FruitShape({ shape = "apple", size = 36, index = 0, highlighted = false, dimmed = false }) {
  const s = size;
  const opacity = dimmed ? 0.3 : 1;
  if (shape === "star") {
    return (
      <svg width={s} height={s} viewBox="0 0 24 24" style={{ opacity }}>
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
          fill={highlighted ? colors.accent : colors.primary} stroke={highlighted ? "#F59E0B" : "#E55555"} strokeWidth="0.5"/>
      </svg>
    );
  }
  return (
    <svg width={s} height={s} viewBox="0 0 100 100" style={{ opacity }}>
      <ellipse cx="50" cy="58" rx="35" ry="38" fill={highlighted ? colors.accent : "#FF6B6B"}/>
      <ellipse cx="50" cy="58" rx="35" ry="38" fill="none" stroke="#E55555" strokeWidth="2"/>
      <path d="M50 20 Q55 8 65 12" stroke="#5D8A3C" strokeWidth="3" fill="none" strokeLinecap="round"/>
      <ellipse cx="42" cy="50" rx="8" ry="10" fill="rgba(255,255,255,0.25)"/>
    </svg>
  );
}

// ============================================================
//  ANIMATION COMPONENTS
// ============================================================

// ----- Make Ten Animation -----
function MakeTenAnimation({ data, onComplete }) {
  const [step, setStep] = useState(0);
  const steps = data.steps;
  const currentStep = steps[step];
  const [autoPlay, setAutoPlay] = useState(false);

  const goNext = () => {
    if (step < steps.length - 1) setStep(s => s + 1);
    else if (onComplete) onComplete();
  };
  const goPrev = () => { if (step > 0) setStep(s => s - 1); };

  useEffect(() => {
    if (autoPlay && step < steps.length - 1) {
      const t = setTimeout(goNext, 2500);
      return () => clearTimeout(t);
    }
  }, [step, autoPlay]);

  // Get values from first step
  const firstStep = steps.find(s => s.action === "show_objects") || {};
  const leftCount = firstStep.left || 0;
  const rightCount = firstStep.right || 0;
  const shape = firstStep.shape || "apple";

  // Get split info
  const splitStep = steps.find(s => s.action === "split") || {};
  const splitParts = splitStep.parts || [0, 0];

  // Determine visual state based on current step index
  const splitDone = step >= steps.findIndex(s => s.action === "split");
  const moveDone = step >= steps.findIndex(s => s.action === "move_to_left");
  const tenDone = step >= steps.findIndex(s => s.action === "highlight_ten");
  const combineDone = step >= steps.findIndex(s => s.action === "combine");

  const leftItems = moveDone ? leftCount + splitParts[0] : leftCount;
  const rightItems = moveDone ? rightCount - splitParts[0] : rightCount;

  return (
    <div style={{ padding: "16px 0" }}>
      {/* Visual area */}
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 32, minHeight: 180, flexWrap: "wrap" }}>
        {/* Left group */}
        <motion.div style={{
          display: "flex", flexWrap: "wrap", gap: 4, maxWidth: 200, padding: 12,
          borderRadius: 16, border: tenDone ? `3px solid ${colors.accent}` : `2px dashed ${colors.border}`,
          background: tenDone ? "rgba(255,230,109,0.15)" : "transparent", justifyContent: "center"
        }} layout>
          {Array.from({ length: leftItems }, (_, i) => (
            <motion.div key={`l-${i}`}
              initial={i >= leftCount ? { x: 80, opacity: 0 } : { scale: 0 }}
              animate={{ x: 0, opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05, type: "spring", stiffness: 200 }}>
              <FruitShape shape={shape} size={32} highlighted={tenDone && i < leftItems}/>
            </motion.div>
          ))}
          {tenDone && <div style={{ width: "100%", textAlign: "center", fontWeight: 700, color: colors.primary, fontSize: 18 }}>{leftItems}</div>}
        </motion.div>

        {/* Plus sign */}
        <span style={{ fontSize: 28, fontWeight: 700, color: colors.text }}>+</span>

        {/* Right group */}
        <motion.div style={{
          display: "flex", flexWrap: "wrap", gap: 4, maxWidth: 200, padding: 12,
          borderRadius: 16, border: `2px dashed ${colors.border}`, justifyContent: "center", minWidth: 60, minHeight: 50
        }} layout>
          {splitDone && !moveDone ? (
            <>
              <div style={{ display: "flex", gap: 2, padding: 4, borderRadius: 8, background: "rgba(255,107,107,0.1)" }}>
                {Array.from({ length: splitParts[0] }, (_, i) => (
                  <motion.div key={`sp0-${i}`} initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}>
                    <FruitShape shape={shape} size={28} highlighted/>
                  </motion.div>
                ))}
              </div>
              <div style={{ display: "flex", gap: 2, padding: 4 }}>
                {Array.from({ length: splitParts[1] }, (_, i) => (
                  <motion.div key={`sp1-${i}`} initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 }}>
                    <FruitShape shape={shape} size={28}/>
                  </motion.div>
                ))}
              </div>
            </>
          ) : (
            Array.from({ length: Math.max(0, rightItems) }, (_, i) => (
              <motion.div key={`r-${i}`} initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: i * 0.05 }}>
                <FruitShape shape={shape} size={32}/>
              </motion.div>
            ))
          )}
          {(moveDone && !combineDone) && <div style={{ width: "100%", textAlign: "center", fontWeight: 700, color: colors.secondary, fontSize: 18 }}>{rightItems}</div>}
        </motion.div>
      </div>

      {/* Result */}
      <AnimatePresence>
        {combineDone && (
          <motion.div initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
            style={{ textAlign: "center", fontSize: 28, fontWeight: 800, color: colors.primary, margin: "12px 0" }}>
            {data.steps.find(s => s.action === "combine")?.values?.join(" + ")} = {data.steps.find(s => s.action === "combine")?.result}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Narration */}
      <motion.div key={step} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
        style={{ textAlign: "center", padding: "12px 20px", margin: "8px auto", maxWidth: 400,
          background: "rgba(78,205,196,0.1)", borderRadius: 12, color: colors.text, fontSize: 16, fontWeight: 500, lineHeight: 1.6 }}>
        💡 {currentStep.narration}
      </motion.div>

      {/* Controls */}
      <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 12 }}>
        <button onClick={goPrev} disabled={step === 0}
          style={{ padding: "8px 20px", borderRadius: 20, border: `2px solid ${colors.border}`,
            background: colors.card, cursor: step === 0 ? "not-allowed" : "pointer", opacity: step === 0 ? 0.4 : 1, fontSize: 14 }}>
          ◀ 上一步
        </button>
        <button onClick={() => setAutoPlay(!autoPlay)}
          style={{ padding: "8px 20px", borderRadius: 20, border: "none",
            background: autoPlay ? colors.secondary : colors.purple, color: "#fff", cursor: "pointer", fontSize: 14 }}>
          {autoPlay ? "⏸ 暂停" : "▶ 自动播放"}
        </button>
        <button onClick={goNext} disabled={step >= steps.length - 1}
          style={{ padding: "8px 20px", borderRadius: 20, border: "none",
            background: colors.primary, color: "#fff", cursor: step >= steps.length - 1 ? "not-allowed" : "pointer",
            opacity: step >= steps.length - 1 ? 0.4 : 1, fontSize: 14 }}>
          下一步 ▶
        </button>
      </div>

      {/* Step indicator */}
      <div style={{ display: "flex", justifyContent: "center", gap: 6, marginTop: 8 }}>
        {steps.map((_, i) => (
          <div key={i} onClick={() => setStep(i)}
            style={{ width: i === step ? 24 : 8, height: 8, borderRadius: 4, cursor: "pointer", transition: "all 0.3s",
              background: i <= step ? colors.secondary : colors.border }}/>
        ))}
      </div>
    </div>
  );
}

// ----- Number Line Animation -----
function NumberLineAnimation({ data, onComplete }) {
  const [step, setStep] = useState(0);
  const steps = data.steps;
  const currentStep = steps[step];
  const lineStep = steps.find(s => s.action === "draw_line") || { from: 0, to: 20 };
  const rangeFrom = lineStep.from || 0;
  const rangeTo = lineStep.to || 20;

  const startStep = steps.find(s => s.action === "mark_start");
  const endStep = steps.find(s => s.action === "mark_end");
  const jumpStep = steps.find(s => s.action === "jump" || s.action === "jump_split");
  const startPos = startStep?.position ?? 0;
  const endPos = endStep?.position ?? 0;

  const showStart = step >= steps.findIndex(s => s.action === "mark_start");
  const showJump = step >= steps.findIndex(s => s.action === "jump" || s.action === "jump_split");
  const showEnd = step >= steps.findIndex(s => s.action === "mark_end");

  const goNext = () => { if (step < steps.length - 1) setStep(s => s + 1); else if (onComplete) onComplete(); };
  const goPrev = () => { if (step > 0) setStep(s => s - 1); };

  const W = 580, H = 120, pad = 30;
  const numToX = (n) => pad + ((n - rangeFrom) / (rangeTo - rangeFrom)) * (W - 2 * pad);

  const jumpCount = jumpStep?.count || (Math.abs(endPos - startPos));
  const dir = (jumpStep?.direction === "left") ? -1 : 1;

  return (
    <div style={{ padding: "16px 0" }}>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", maxWidth: 600, display: "block", margin: "0 auto" }}>
        {/* Number line */}
        <line x1={pad} y1={60} x2={W - pad} y2={60} stroke={colors.text} strokeWidth={2}/>
        {/* Tick marks */}
        {Array.from({ length: rangeTo - rangeFrom + 1 }, (_, i) => {
          const n = rangeFrom + i;
          const x = numToX(n);
          const isMajor = n % 5 === 0 || n === startPos || n === endPos;
          return (
            <g key={n}>
              <line x1={x} y1={54} x2={x} y2={66} stroke={colors.text} strokeWidth={isMajor ? 2 : 1}/>
              {isMajor && <text x={x} y={80} textAnchor="middle" fontSize={11} fill={colors.text} fontWeight={500}>{n}</text>}
            </g>
          );
        })}
        {/* Start marker */}
        {showStart && (
          <motion.g initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
            <circle cx={numToX(startPos)} cy={60} r={8} fill={colors.primary}/>
            <text x={numToX(startPos)} y={45} textAnchor="middle" fontSize={14} fontWeight={700} fill={colors.primary}>{startPos}</text>
          </motion.g>
        )}
        {/* Jump arcs */}
        {showJump && Array.from({ length: jumpCount }, (_, i) => {
          const fromN = startPos + dir * i;
          const toN = startPos + dir * (i + 1);
          const fx = numToX(fromN), tx = numToX(toN);
          const mx = (fx + tx) / 2;
          return (
            <motion.path key={i} d={`M${fx},55 Q${mx},${25 - i * 2} ${tx},55`}
              fill="none" stroke={colors.secondary} strokeWidth={2} strokeDasharray="4 2"
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: i * 0.3, duration: 0.4 }}/>
          );
        })}
        {/* End marker */}
        {showEnd && (
          <motion.g initial={{ scale: 0 }} animate={{ scale: 1 }}>
            <circle cx={numToX(endPos)} cy={60} r={10} fill={colors.secondary} stroke="#fff" strokeWidth={2}/>
            <text x={numToX(endPos)} y={100} textAnchor="middle" fontSize={14} fontWeight={700} fill={colors.secondary}>{endPos}</text>
          </motion.g>
        )}
      </svg>

      <motion.div key={step} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        style={{ textAlign: "center", padding: "12px 20px", margin: "8px auto", maxWidth: 400,
          background: "rgba(96,165,250,0.1)", borderRadius: 12, color: colors.text, fontSize: 16, fontWeight: 500 }}>
        📏 {currentStep.narration}
      </motion.div>

      <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 12 }}>
        <button onClick={goPrev} disabled={step === 0}
          style={{ padding: "8px 20px", borderRadius: 20, border: `2px solid ${colors.border}`, background: colors.card, cursor: step === 0 ? "not-allowed" : "pointer", opacity: step === 0 ? 0.4 : 1, fontSize: 14 }}>
          ◀ 上一步</button>
        <button onClick={goNext}
          style={{ padding: "8px 20px", borderRadius: 20, border: "none", background: colors.blue, color: "#fff", cursor: "pointer", fontSize: 14 }}>
          {step >= steps.length - 1 ? "✓ 完成" : "下一步 ▶"}</button>
      </div>
    </div>
  );
}

// ----- Counting Animation -----
function CountingAnimation({ data, onComplete }) {
  const [step, setStep] = useState(0);
  const steps = data.steps;
  const currentStep = steps[step];
  const firstStep = steps[0] || {};
  const left = firstStep.left || 0;
  const right = firstStep.right || 0;
  const shape = firstStep.shape || "apple";
  const total = left + right;

  const countStep = steps.find(s => s.action === "count_on" || s.action === "count_all");
  const showResult = step >= steps.findIndex(s => s.action === "show_result" || s.action === "count_on");

  const goNext = () => { if (step < steps.length - 1) setStep(s => s + 1); else if (onComplete) onComplete(); };

  return (
    <div style={{ padding: "16px 0" }}>
      <div style={{ display: "flex", justifyContent: "center", gap: 4, flexWrap: "wrap", maxWidth: 400, margin: "0 auto" }}>
        {Array.from({ length: total }, (_, i) => (
          <motion.div key={i} initial={{ scale: 0, rotate: -180 }} animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: showResult ? i * 0.1 : i * 0.05, type: "spring" }}
            style={{ position: "relative" }}>
            <FruitShape shape={shape} size={36}/>
            {showResult && (
              <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: i * 0.1 + 0.3 }}
                style={{ position: "absolute", top: -8, right: -4, background: colors.secondary, color: "#fff",
                  borderRadius: "50%", width: 18, height: 18, fontSize: 10, fontWeight: 700,
                  display: "flex", alignItems: "center", justifyContent: "center" }}>
                {i + 1}
              </motion.span>
            )}
          </motion.div>
        ))}
      </div>

      <motion.div key={step} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
        style={{ textAlign: "center", padding: "12px 20px", margin: "12px auto", maxWidth: 400,
          background: "rgba(52,211,153,0.1)", borderRadius: 12, color: colors.text, fontSize: 16, fontWeight: 500 }}>
        🔢 {currentStep.narration}
      </motion.div>

      <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 12 }}>
        <button onClick={goNext}
          style={{ padding: "8px 24px", borderRadius: 20, border: "none",
            background: colors.green, color: "#fff", cursor: "pointer", fontSize: 14, fontWeight: 600 }}>
          {step >= steps.length - 1 ? "✓ 完成" : "下一步 ▶"}</button>
      </div>
    </div>
  );
}

// ----- Animation Router -----
function AnimationPlayer({ methodData, onComplete }) {
  const { type } = methodData;
  const props = { data: methodData, onComplete };
  switch (type) {
    case "make_ten": return <MakeTenAnimation {...props}/>;
    case "number_line": return <NumberLineAnimation {...props}/>;
    case "counting": return <CountingAnimation {...props}/>;
    case "break_ten": return <MakeTenAnimation {...props}/>; // reuse with minor diff
    default: return <CountingAnimation {...props}/>;
  }
}

// ============================================================
//  EXERCISE / GAME COMPONENTS
// ============================================================

function ExerciseGame({ exercises, onComplete }) {
  const [current, setCurrent] = useState(0);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState(null); // null | { correct, hints, solutions }
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [showSolution, setShowSolution] = useState(false);
  const [timeLeft, setTimeLeft] = useState(null);
  const [gameStarted, setGameStarted] = useState(false);
  const inputRef = useRef(null);

  const ex = exercises[current];
  if (!ex) return null;

  const startGame = () => { setGameStarted(true); setTimeLeft(120); };

  useEffect(() => {
    if (!gameStarted || timeLeft === null || timeLeft <= 0) return;
    const t = setInterval(() => setTimeLeft(v => v - 1), 1000);
    return () => clearInterval(t);
  }, [gameStarted, timeLeft]);

  const checkAnswer = async (ans) => {
    const finalAns = ans || answer;
    if (!finalAns.trim()) return;
    const res = { correct: String(finalAns).trim() === String(ex.correct_answer).trim(), correct_answer: ex.correct_answer, hints: ex.hints || [], solutions: ex.solutions || [] };
    setResult(res);
    setScore(s => ({ correct: s.correct + (res.correct ? 1 : 0), total: s.total + 1 }));
  };

  const nextQuestion = () => {
    if (current + 1 >= exercises.length) {
      onComplete?.(score);
      return;
    }
    setCurrent(c => c + 1);
    setAnswer("");
    setResult(null);
    setShowSolution(false);
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  if (!gameStarted) {
    return (
      <div style={{ textAlign: "center", padding: 40 }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>🎮</div>
        <h3 style={{ margin: "0 0 8px", color: colors.text, fontWeight: 700, fontSize: 22 }}>趣味闯关</h3>
        <p style={{ color: colors.textLight, margin: "0 0 24px" }}>共 {exercises.length} 题，120秒内完成挑战</p>
        <button onClick={startGame}
          style={{ padding: "14px 48px", borderRadius: 28, border: "none", fontSize: 18, fontWeight: 700,
            background: `linear-gradient(135deg, ${colors.primary}, ${colors.purple})`, color: "#fff", cursor: "pointer" }}>
          开始挑战 🚀
        </button>
      </div>
    );
  }

  if (timeLeft <= 0 || (result && current + 1 >= exercises.length)) {
    const finalScore = score;
    const stars = finalScore.correct === exercises.length ? 3 : finalScore.correct >= exercises.length * 0.7 ? 2 : finalScore.correct >= exercises.length * 0.4 ? 1 : 0;
    return (
      <div style={{ textAlign: "center", padding: 40 }}>
        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring" }}>
          <div style={{ fontSize: 64, marginBottom: 12 }}>{stars >= 2 ? "🎉" : stars >= 1 ? "👍" : "💪"}</div>
          <h3 style={{ margin: "0 0 8px", color: colors.text, fontSize: 24, fontWeight: 700 }}>
            {stars >= 2 ? "太棒了！" : stars >= 1 ? "不错哦！" : "继续加油！"}
          </h3>
          <div style={{ display: "flex", justifyContent: "center", margin: "12px 0" }}><Stars count={stars}/></div>
          <p style={{ color: colors.textLight, fontSize: 16 }}>答对 {finalScore.correct} / {finalScore.total} 题</p>
          <button onClick={() => onComplete?.(finalScore)}
            style={{ marginTop: 20, padding: "12px 36px", borderRadius: 24, border: "none",
              background: colors.secondary, color: "#fff", fontSize: 16, fontWeight: 600, cursor: "pointer" }}>
            返回课时
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div style={{ padding: "16px 0" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <span style={{ fontSize: 14, color: colors.textLight }}>第 {current + 1}/{exercises.length} 题</span>
        <span style={{ fontSize: 14, fontWeight: 600, color: timeLeft < 30 ? colors.primary : colors.text }}>
          ⏱ {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, "0")}
        </span>
        <Stars count={score.correct >= 3 ? 3 : score.correct >= 2 ? 2 : score.correct >= 1 ? 1 : 0}/>
      </div>

      {/* Progress bar */}
      <div style={{ height: 6, background: colors.border, borderRadius: 3, marginBottom: 20 }}>
        <motion.div animate={{ width: `${((current + 1) / exercises.length) * 100}%` }}
          style={{ height: "100%", background: `linear-gradient(90deg, ${colors.secondary}, ${colors.green})`, borderRadius: 3 }}/>
      </div>

      {/* Question */}
      <motion.div key={current} initial={{ x: 50, opacity: 0 }} animate={{ x: 0, opacity: 1 }}
        style={{ textAlign: "center", padding: 24, background: colors.card, borderRadius: 20,
          boxShadow: "0 2px 12px rgba(0,0,0,0.06)" }}>
        <p style={{ fontSize: 28, fontWeight: 800, color: colors.text, margin: "0 0 20px", letterSpacing: 2 }}>
          {ex.question}
        </p>

        {ex.type === "choice" && ex.options?.length > 0 ? (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, maxWidth: 300, margin: "0 auto" }}>
            {ex.options.map((opt, i) => (
              <button key={i} onClick={() => { setAnswer(opt); checkAnswer(opt); }}
                disabled={!!result}
                style={{
                  padding: "12px 16px", borderRadius: 14, fontSize: 20, fontWeight: 700, cursor: result ? "default" : "pointer",
                  border: result && String(opt) === String(ex.correct_answer) ? `3px solid ${colors.green}` :
                    result && String(opt) === String(answer) && !result.correct ? `3px solid ${colors.primary}` : `2px solid ${colors.border}`,
                  background: result && String(opt) === String(ex.correct_answer) ? "rgba(52,211,153,0.15)" :
                    result && String(opt) === String(answer) && !result.correct ? "rgba(255,107,107,0.1)" : colors.card,
                  color: colors.text,
                }}>
                {opt}
              </button>
            ))}
          </div>
        ) : (
          <div style={{ display: "flex", justifyContent: "center", gap: 12, alignItems: "center" }}>
            <input ref={inputRef} type="number" value={answer} onChange={e => setAnswer(e.target.value)}
              onKeyDown={e => e.key === "Enter" && checkAnswer()}
              disabled={!!result} autoFocus
              style={{ width: 100, fontSize: 28, fontWeight: 700, textAlign: "center", padding: "8px 12px",
                borderRadius: 14, border: `3px solid ${result ? (result.correct ? colors.green : colors.primary) : colors.border}`,
                outline: "none", color: colors.text, background: result ? (result.correct ? "rgba(52,211,153,0.1)" : "rgba(255,107,107,0.1)") : "#fff" }}/>
            {!result && (
              <button onClick={() => checkAnswer()}
                style={{ padding: "10px 24px", borderRadius: 14, border: "none",
                  background: colors.primary, color: "#fff", fontSize: 16, fontWeight: 700, cursor: "pointer" }}>
                确认
              </button>
            )}
          </div>
        )}

        {/* Result feedback */}
        <AnimatePresence>
          {result && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ marginTop: 16 }}>
              {result.correct ? (
                <p style={{ color: colors.green, fontSize: 20, fontWeight: 700, margin: 0 }}>✅ 答对了！太棒了！</p>
              ) : (
                <div>
                  <p style={{ color: colors.primary, fontSize: 18, fontWeight: 600, margin: "0 0 8px" }}>
                    ❌ 再想想～正确答案是 {result.correct_answer}
                  </p>
                  {result.hints?.length > 0 && !showSolution && (
                    <button onClick={() => setShowSolution(true)}
                      style={{ padding: "6px 16px", borderRadius: 12, border: `1px solid ${colors.purple}`,
                        background: "transparent", color: colors.purple, fontSize: 14, cursor: "pointer" }}>
                      💡 看看解题思路
                    </button>
                  )}
                  {showSolution && result.hints?.map((h, i) => (
                    <p key={i} style={{ color: colors.textLight, fontSize: 14, margin: "4px 0" }}>💡 {h}</p>
                  ))}
                </div>
              )}
              <button onClick={nextQuestion}
                style={{ marginTop: 12, padding: "10px 32px", borderRadius: 20, border: "none",
                  background: colors.secondary, color: "#fff", fontSize: 16, fontWeight: 600, cursor: "pointer" }}>
                {current + 1 >= exercises.length ? "查看成绩" : "下一题 ▶"}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

// ============================================================
//  PAGE COMPONENTS
// ============================================================

// ----- Course Map (Home) -----
function CourseMap({ onSelectLesson }) {
  const { data: courses, loading: cl } = useFetch("/courses?status=published");
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState([]);
  const userId = "student-001";

  useEffect(() => {
    if (courses?.length) {
      fetch(API + `/courses/${courses[0].id}/lessons`).then(r => r.json()).then(setLessons);
      fetch(API + `/progress/${userId}`).then(r => r.json()).then(setProgress);
    }
  }, [courses]);

  const getStars = (lessonId) => {
    const p = progress.find(pp => pp.lesson_id === lessonId);
    return p?.stars || 0;
  };

  if (cl) return <div style={{ textAlign: "center", padding: 60, color: colors.textLight }}>加载中...</div>;

  return (
    <div style={{ padding: "20px 16px", maxWidth: 480, margin: "0 auto" }}>
      <div style={{ textAlign: "center", marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 28, fontWeight: 800, color: colors.text }}>🧮 数学小天地</h1>
        <p style={{ margin: "4px 0 0", color: colors.textLight, fontSize: 14 }}>{courses?.[0]?.title || "加减法启蒙"}</p>
      </div>

      <div style={{ position: "relative" }}>
        {/* Path line */}
        <div style={{ position: "absolute", left: "50%", top: 0, bottom: 0, width: 3, background: colors.border, transform: "translateX(-50%)", zIndex: 0 }}/>

        {lessons.map((lesson, i) => {
          const stars = getStars(lesson.id);
          const isLocked = i > 0 && getStars(lessons[i - 1]?.id) === 0 && lesson.status === "published";
          const side = i % 2 === 0 ? "left" : "right";

          return (
            <motion.div key={lesson.id} initial={{ opacity: 0, x: side === "left" ? -30 : 30 }}
              animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
              style={{ display: "flex", justifyContent: side === "left" ? "flex-start" : "flex-end",
                position: "relative", zIndex: 1, marginBottom: 12 }}>

              <button onClick={() => !isLocked && onSelectLesson(lesson.id)}
                disabled={isLocked}
                style={{
                  width: "44%", padding: "14px 16px", borderRadius: 18,
                  border: stars > 0 ? `2px solid ${colors.secondary}` : `2px solid ${colors.border}`,
                  background: isLocked ? "#f5f0e8" : colors.card,
                  cursor: isLocked ? "not-allowed" : "pointer",
                  opacity: isLocked ? 0.5 : 1,
                  boxShadow: stars > 0 ? `0 2px 8px rgba(78,205,196,0.2)` : "0 1px 4px rgba(0,0,0,0.05)",
                  textAlign: "left", transition: "transform 0.2s",
                }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: 20, marginRight: 8 }}>
                    {isLocked ? "🔒" : stars >= 3 ? "🌟" : stars > 0 ? "⭐" : ["📚","✏️","🎯","📐","🍎","🧩","🎲","🔢"][i] || "📖"}
                  </span>
                  <Stars count={stars} size={14}/>
                </div>
                <p style={{ margin: "6px 0 0", fontSize: 14, fontWeight: 600, color: colors.text }}>{lesson.title}</p>
                <p style={{ margin: "2px 0 0", fontSize: 11, color: colors.textLight }}>{lesson.description}</p>
              </button>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

// ----- Lesson Detail Page -----
function LessonPage({ lessonId, onBack }) {
  const { data: lesson, loading } = useFetch(`/lessons/${lessonId}`);
  const [activeTab, setActiveTab] = useState("tutorial"); // tutorial | practice
  const [selectedMethod, setSelectedMethod] = useState(0);

  if (loading || !lesson) return <div style={{ textAlign: "center", padding: 60, color: colors.textLight }}>加载中...</div>;

  const methods = lesson.animation_data?.methods || [];
  const exercises = lesson.exercises || [];

  const handleExerciseComplete = async (score) => {
    const stars = score.correct === exercises.length ? 3 : score.correct >= exercises.length * 0.7 ? 2 : score.correct >= 1 ? 1 : 0;
    try {
      await fetch(API + "/progress/student-001", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lesson_id: lessonId, stars, correct_count: score.correct, total_count: score.total, time_spent: 120 })
      });
    } catch (e) {}
    setActiveTab("tutorial");
  };

  return (
    <div style={{ padding: "16px", maxWidth: 560, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
        <button onClick={onBack}
          style={{ width: 36, height: 36, borderRadius: 12, border: `2px solid ${colors.border}`,
            background: colors.card, cursor: "pointer", fontSize: 16, display: "flex", alignItems: "center", justifyContent: "center" }}>
          ←
        </button>
        <div style={{ flex: 1 }}>
          <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: colors.text }}>{lesson.title}</h2>
          <p style={{ margin: 0, fontSize: 13, color: colors.textLight }}>{lesson.description}</p>
        </div>
      </div>

      {/* Tab switch */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16, background: colors.border, borderRadius: 14, padding: 4 }}>
        {[["tutorial", "📖 教程演示"], ["practice", "🎮 趣味练习"]].map(([key, label]) => (
          <button key={key} onClick={() => setActiveTab(key)}
            style={{ flex: 1, padding: "10px 0", borderRadius: 12, border: "none", fontSize: 15, fontWeight: 600,
              background: activeTab === key ? colors.card : "transparent",
              color: activeTab === key ? colors.text : colors.textLight,
              boxShadow: activeTab === key ? "0 2px 8px rgba(0,0,0,0.08)" : "none", cursor: "pointer" }}>
            {label}
          </button>
        ))}
      </div>

      {/* Tutorial tab */}
      {activeTab === "tutorial" && (
        <div>
          {/* Expression */}
          <div style={{ textAlign: "center", padding: "16px 0", margin: "0 0 12px",
            background: `linear-gradient(135deg, rgba(255,107,107,0.08), rgba(167,139,250,0.08))`, borderRadius: 16 }}>
            <span style={{ fontSize: 32, fontWeight: 800, color: colors.text, letterSpacing: 3 }}>
              {lesson.animation_data?.expression || ""}
            </span>
          </div>

          {/* Method selector */}
          {methods.length > 1 && (
            <div style={{ display: "flex", gap: 8, marginBottom: 12, overflowX: "auto" }}>
              {methods.map((m, i) => (
                <button key={i} onClick={() => setSelectedMethod(i)}
                  style={{ padding: "8px 16px", borderRadius: 20, border: "none", whiteSpace: "nowrap",
                    background: selectedMethod === i ? colors.purple : colors.border,
                    color: selectedMethod === i ? "#fff" : colors.text,
                    fontSize: 14, fontWeight: 600, cursor: "pointer" }}>
                  {m.title}
                </button>
              ))}
            </div>
          )}

          {/* Animation */}
          {methods.length > 0 && (
            <div style={{ background: colors.card, borderRadius: 20, padding: 16, boxShadow: "0 2px 12px rgba(0,0,0,0.06)" }}>
              <AnimatePresence mode="wait">
                <motion.div key={selectedMethod} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                  <AnimationPlayer methodData={methods[selectedMethod]}/>
                </motion.div>
              </AnimatePresence>
            </div>
          )}

          {/* Start practice button */}
          {exercises.length > 0 && (
            <button onClick={() => setActiveTab("practice")}
              style={{ width: "100%", padding: "14px 0", borderRadius: 20, border: "none", marginTop: 16,
                background: `linear-gradient(135deg, ${colors.primary}, ${colors.purple})`,
                color: "#fff", fontSize: 18, fontWeight: 700, cursor: "pointer" }}>
              开始练习 🎮 ({exercises.length} 题)
            </button>
          )}
        </div>
      )}

      {/* Practice tab */}
      {activeTab === "practice" && (
        <ExerciseGame exercises={exercises} onComplete={handleExerciseComplete}/>
      )}
    </div>
  );
}

// ============================================================
//  APP ROOT
// ============================================================

export default function App() {
  const [currentLesson, setCurrentLesson] = useState(null);

  return (
    <div style={{
      minHeight: "100vh", fontFamily: "'Nunito', 'PingFang SC', 'Microsoft YaHei', sans-serif",
      background: `linear-gradient(180deg, ${colors.bg} 0%, #FFF0E6 50%, #F0F8FF 100%)`,
    }}>
      <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet"/>

      <AnimatePresence mode="wait">
        {currentLesson ? (
          <motion.div key="lesson" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
            <LessonPage lessonId={currentLesson} onBack={() => setCurrentLesson(null)}/>
          </motion.div>
        ) : (
          <motion.div key="map" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <CourseMap onSelectLesson={setCurrentLesson}/>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
