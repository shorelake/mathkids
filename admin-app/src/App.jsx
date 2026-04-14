import { useState, useEffect, useCallback } from "react";

const API = "http://localhost:8000/api";

// ===== Utility =====
async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, { headers: { "Content-Type": "application/json" }, ...opts });
  return res.json();
}
async function apiPost(path, data) { return apiFetch(path, { method: "POST", body: JSON.stringify(data) }); }
async function apiPut(path, data) { return apiFetch(path, { method: "PUT", body: JSON.stringify(data) }); }
async function apiDelete(path) { return apiFetch(path, { method: "DELETE" }); }

// ===== Styles =====
const theme = {
  bg: "#f8fafc", card: "#ffffff", primary: "#6366f1", primaryHover: "#4f46e5",
  success: "#10b981", warning: "#f59e0b", danger: "#ef4444",
  text: "#1e293b", textMuted: "#64748b", border: "#e2e8f0",
  radius: 10, font: "'Inter', system-ui, sans-serif",
};

const btn = (color = theme.primary, outline = false) => ({
  padding: "8px 16px", borderRadius: 8, border: outline ? `1.5px solid ${color}` : "none",
  background: outline ? "transparent" : color, color: outline ? color : "#fff",
  fontSize: 13, fontWeight: 600, cursor: "pointer", transition: "all 0.2s",
});

const input = {
  width: "100%", padding: "8px 12px", borderRadius: 8, border: `1.5px solid ${theme.border}`,
  fontSize: 14, outline: "none", color: theme.text, boxSizing: "border-box",
};

const card = {
  background: theme.card, borderRadius: 12, padding: 20,
  border: `1px solid ${theme.border}`, marginBottom: 16,
};

// ============================================================
// SIDEBAR NAV
// ============================================================
function Sidebar({ active, onNav }) {
  const items = [
    { key: "courses", icon: "📚", label: "课程管理" },
    { key: "exercises", icon: "✏️", label: "题库管理" },
    { key: "ai", icon: "🤖", label: "AI 设置" },
    { key: "analytics", icon: "📊", label: "学情分析" },
  ];
  return (
    <div style={{
      width: 200, minHeight: "100vh", background: "#1e1b4b", padding: "20px 0",
      display: "flex", flexDirection: "column",
    }}>
      <h2 style={{ color: "#fff", fontSize: 18, fontWeight: 700, padding: "0 20px", margin: "0 0 24px" }}>
        🧮 MathKids
      </h2>
      <div style={{ fontSize: 11, color: "#a5b4fc", padding: "0 20px", marginBottom: 20, fontWeight: 500 }}>管理后台</div>
      {items.map(item => (
        <button key={item.key} onClick={() => onNav(item.key)}
          style={{
            display: "flex", alignItems: "center", gap: 10, padding: "10px 20px", border: "none",
            background: active === item.key ? "rgba(99,102,241,0.3)" : "transparent",
            color: active === item.key ? "#fff" : "#c7d2fe",
            fontSize: 14, fontWeight: 500, cursor: "pointer", textAlign: "left", width: "100%",
            borderLeft: active === item.key ? "3px solid #818cf8" : "3px solid transparent",
          }}>
          <span style={{ fontSize: 16 }}>{item.icon}</span> {item.label}
        </button>
      ))}
    </div>
  );
}

// ============================================================
// COURSE MANAGEMENT
// ============================================================
function CourseManager() {
  const [courses, setCourses] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [editingLesson, setEditingLesson] = useState(null);
  const [showNewCourse, setShowNewCourse] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");

  const loadCourses = useCallback(async () => { setCourses(await apiFetch("/courses")); }, []);
  const loadLessons = useCallback(async (cid) => { setLessons(await apiFetch(`/courses/${cid}/lessons`)); }, []);

  useEffect(() => { loadCourses(); }, []);
  useEffect(() => { if (selectedCourse) loadLessons(selectedCourse); }, [selectedCourse]);

  const createCourse = async () => {
    if (!newTitle.trim()) return;
    await apiPost("/courses", { title: newTitle, description: newDesc });
    setNewTitle(""); setNewDesc(""); setShowNewCourse(false);
    loadCourses();
  };

  const toggleLessonStatus = async (lesson) => {
    const newStatus = lesson.status === "published" ? "draft" : "published";
    await apiPut(`/lessons/${lesson.id}`, { status: newStatus });
    loadLessons(selectedCourse);
  };

  const saveAnimationData = async () => {
    if (!editingLesson) return;
    try {
      const parsed = JSON.parse(editingLesson._animJson);
      await apiPut(`/lessons/${editingLesson.id}`, { animation_data: parsed });
      setEditingLesson(null);
      loadLessons(selectedCourse);
    } catch (e) { alert("JSON 格式错误: " + e.message); }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h2 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: theme.text }}>📚 课程管理</h2>
        <button style={btn()} onClick={() => setShowNewCourse(true)}>+ 新建课程</button>
      </div>

      {showNewCourse && (
        <div style={card}>
          <h4 style={{ margin: "0 0 12px", color: theme.text }}>新建课程</h4>
          <input style={{ ...input, marginBottom: 8 }} placeholder="课程标题" value={newTitle} onChange={e => setNewTitle(e.target.value)}/>
          <input style={{ ...input, marginBottom: 12 }} placeholder="课程描述" value={newDesc} onChange={e => setNewDesc(e.target.value)}/>
          <div style={{ display: "flex", gap: 8 }}>
            <button style={btn()} onClick={createCourse}>创建</button>
            <button style={btn(theme.textMuted, true)} onClick={() => setShowNewCourse(false)}>取消</button>
          </div>
        </div>
      )}

      {/* Course list */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 24 }}>
        {courses.map(c => (
          <div key={c.id} onClick={() => setSelectedCourse(c.id)}
            style={{
              ...card, marginBottom: 0, cursor: "pointer",
              borderColor: selectedCourse === c.id ? theme.primary : theme.border,
              borderWidth: selectedCourse === c.id ? 2 : 1,
            }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h4 style={{ margin: 0, fontSize: 15, color: theme.text }}>{c.title}</h4>
              <span style={{
                fontSize: 11, padding: "2px 8px", borderRadius: 10, fontWeight: 600,
                background: c.status === "published" ? "#d1fae5" : "#fef3c7",
                color: c.status === "published" ? "#065f46" : "#92400e",
              }}>{c.status === "published" ? "已发布" : "草稿"}</span>
            </div>
            <p style={{ margin: "4px 0 0", fontSize: 12, color: theme.textMuted }}>{c.description}</p>
          </div>
        ))}
      </div>

      {/* Lessons for selected course */}
      {selectedCourse && (
        <div>
          <h3 style={{ margin: "0 0 12px", fontSize: 16, color: theme.text }}>📝 课时列表</h3>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "#f1f5f9" }}>
                <th style={{ padding: "8px 12px", textAlign: "left", color: theme.textMuted, fontWeight: 600 }}>序号</th>
                <th style={{ padding: "8px 12px", textAlign: "left", color: theme.textMuted, fontWeight: 600 }}>标题</th>
                <th style={{ padding: "8px 12px", textAlign: "left", color: theme.textMuted, fontWeight: 600 }}>教学方法</th>
                <th style={{ padding: "8px 12px", textAlign: "left", color: theme.textMuted, fontWeight: 600 }}>状态</th>
                <th style={{ padding: "8px 12px", textAlign: "right", color: theme.textMuted, fontWeight: 600 }}>操作</th>
              </tr>
            </thead>
            <tbody>
              {lessons.map(l => (
                <tr key={l.id} style={{ borderBottom: `1px solid ${theme.border}` }}>
                  <td style={{ padding: "10px 12px" }}>{l.order}</td>
                  <td style={{ padding: "10px 12px", fontWeight: 600, color: theme.text }}>{l.title}</td>
                  <td style={{ padding: "10px 12px" }}>
                    {l.teaching_methods?.map((m, i) => (
                      <span key={i} style={{
                        display: "inline-block", padding: "2px 8px", borderRadius: 10, fontSize: 11,
                        background: "#ede9fe", color: "#5b21b6", marginRight: 4, fontWeight: 500,
                      }}>{m}</span>
                    ))}
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    <span style={{
                      fontSize: 11, padding: "2px 8px", borderRadius: 10, fontWeight: 600, cursor: "pointer",
                      background: l.status === "published" ? "#d1fae5" : "#fef3c7",
                      color: l.status === "published" ? "#065f46" : "#92400e",
                    }} onClick={() => toggleLessonStatus(l)}>
                      {l.status === "published" ? "已发布" : "草稿"}
                    </span>
                  </td>
                  <td style={{ padding: "10px 12px", textAlign: "right" }}>
                    <button style={{ ...btn(theme.primary, true), padding: "4px 10px", fontSize: 12 }}
                      onClick={() => setEditingLesson({ ...l, _animJson: JSON.stringify(l.animation_data, null, 2) })}>
                      编辑动画
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Animation data editor modal */}
      {editingLesson && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div style={{ background: "#fff", borderRadius: 16, padding: 24, width: "90%", maxWidth: 700, maxHeight: "80vh", overflow: "auto" }}>
            <h3 style={{ margin: "0 0 12px", color: theme.text }}>编辑动画数据 - {editingLesson.title}</h3>
            <textarea value={editingLesson._animJson}
              onChange={e => setEditingLesson({ ...editingLesson, _animJson: e.target.value })}
              style={{ ...input, height: 400, fontFamily: "monospace", fontSize: 12, lineHeight: 1.5, resize: "vertical" }}/>
            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
              <button style={btn(theme.success)} onClick={saveAnimationData}>保存</button>
              <button style={btn(theme.textMuted, true)} onClick={() => setEditingLesson(null)}>取消</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================
// EXERCISE MANAGEMENT
// ============================================================
function ExerciseManager() {
  const [courses, setCourses] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [exercises, setExercises] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState("");
  const [selectedLesson, setSelectedLesson] = useState("");

  useEffect(() => { apiFetch("/courses").then(setCourses); }, []);
  useEffect(() => {
    if (selectedCourse) apiFetch(`/courses/${selectedCourse}/lessons`).then(setLessons);
  }, [selectedCourse]);
  useEffect(() => {
    if (selectedLesson) apiFetch(`/lessons/${selectedLesson}/exercises`).then(setExercises);
  }, [selectedLesson]);

  const deleteEx = async (id) => {
    if (!confirm("确认删除？")) return;
    await apiDelete(`/exercises/${id}`);
    setExercises(exercises.filter(e => e.id !== id));
  };

  return (
    <div>
      <h2 style={{ margin: "0 0 20px", fontSize: 22, fontWeight: 700, color: theme.text }}>✏️ 题库管理</h2>

      <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
        <select style={{ ...input, width: "auto", minWidth: 180 }} value={selectedCourse}
          onChange={e => { setSelectedCourse(e.target.value); setSelectedLesson(""); setExercises([]); }}>
          <option value="">选择课程...</option>
          {courses.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
        </select>
        <select style={{ ...input, width: "auto", minWidth: 220 }} value={selectedLesson}
          onChange={e => setSelectedLesson(e.target.value)} disabled={!selectedCourse}>
          <option value="">选择课时...</option>
          {lessons.map(l => <option key={l.id} value={l.id}>{l.order}. {l.title}</option>)}
        </select>
      </div>

      {exercises.length > 0 && (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "#f1f5f9" }}>
              <th style={{ padding: "8px 12px", textAlign: "left", color: theme.textMuted }}>序号</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: theme.textMuted }}>题目</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: theme.textMuted }}>类型</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: theme.textMuted }}>答案</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: theme.textMuted }}>难度</th>
              <th style={{ padding: "8px 12px", textAlign: "right", color: theme.textMuted }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {exercises.map(ex => (
              <tr key={ex.id} style={{ borderBottom: `1px solid ${theme.border}` }}>
                <td style={{ padding: "10px 12px" }}>{ex.order}</td>
                <td style={{ padding: "10px 12px", fontWeight: 600 }}>{ex.question}</td>
                <td style={{ padding: "10px 12px" }}>
                  <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 10, background: "#dbeafe", color: "#1e40af" }}>
                    {ex.type === "fill_blank" ? "填空" : ex.type === "choice" ? "选择" : ex.type}
                  </span>
                </td>
                <td style={{ padding: "10px 12px", fontWeight: 700, color: theme.success }}>{ex.correct_answer}</td>
                <td style={{ padding: "10px 12px" }}>
                  {"⭐".repeat(ex.difficulty)}
                </td>
                <td style={{ padding: "10px 12px", textAlign: "right" }}>
                  <button style={{ ...btn(theme.danger, true), padding: "4px 10px", fontSize: 12 }}
                    onClick={() => deleteEx(ex.id)}>删除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selectedLesson && exercises.length === 0 && (
        <p style={{ color: theme.textMuted, textAlign: "center", padding: 40 }}>该课时暂无题目</p>
      )}
    </div>
  );
}

// ============================================================
// AI CONFIG
// ============================================================
function AIConfig() {
  const [config, setConfig] = useState(null);
  const [providers, setProviders] = useState({});
  const [saving, setSaving] = useState(false);
  const [genTopic, setGenTopic] = useState("20以内进位加法");
  const [genResult, setGenResult] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [exTopic, setExTopic] = useState("20以内进位加法");
  const [exCount, setExCount] = useState(5);
  const [exResult, setExResult] = useState(null);

  useEffect(() => {
    apiFetch("/ai/config").then(setConfig);
    apiFetch("/ai/providers").then(setProviders);
  }, []);

  const saveConfig = async () => {
    setSaving(true);
    const updated = await apiPut("/ai/config", config);
    setConfig(updated);
    setSaving(false);
  };

  const selectProvider = (p) => {
    const defaults = providers[p] || {};
    setConfig({ ...config, provider: p, base_url: defaults.base_url || "", model: defaults.model || "" });
  };

  const generateLesson = async () => {
    setGenerating(true); setGenResult(null);
    try {
      const res = await apiPost("/ai/generate-lesson", { topic: genTopic });
      setGenResult(res);
    } catch (e) {
      setGenResult({ success: false, errors: [e.message] });
    }
    setGenerating(false);
  };

  const generateExercises = async () => {
    setGenerating(true); setExResult(null);
    try {
      const res = await apiPost("/ai/generate-exercises", { topic: exTopic, count: exCount });
      setExResult(res);
    } catch (e) {
      setExResult({ success: false, errors: [e.message] });
    }
    setGenerating(false);
  };

  if (!config) return <div>加载中...</div>;

  return (
    <div>
      <h2 style={{ margin: "0 0 20px", fontSize: 22, fontWeight: 700, color: theme.text }}>🤖 AI 配置</h2>

      {/* Provider selection */}
      <div style={card}>
        <h4 style={{ margin: "0 0 12px", color: theme.text }}>选择 AI 服务商</h4>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
          {Object.keys(providers).map(p => (
            <button key={p} onClick={() => selectProvider(p)}
              style={{
                padding: "8px 16px", borderRadius: 10, fontSize: 13, fontWeight: 600, cursor: "pointer",
                border: config.provider === p ? `2px solid ${theme.primary}` : `1.5px solid ${theme.border}`,
                background: config.provider === p ? "#eef2ff" : "#fff",
                color: config.provider === p ? theme.primary : theme.text,
              }}>
              {p === "openai" ? "OpenAI" : p === "claude" ? "Claude" : p === "grok" ? "Grok (xAI)" :
               p === "kimi" ? "Kimi (月之暗面)" : p === "deepseek" ? "DeepSeek" : p}
            </button>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: theme.textMuted, display: "block", marginBottom: 4 }}>API Key</label>
            <input style={input} type="password" value={config.api_key || ""} placeholder="sk-xxx..."
              onChange={e => setConfig({ ...config, api_key: e.target.value })}/>
          </div>
          <div>
            <label style={{ fontSize: 12, fontWeight: 600, color: theme.textMuted, display: "block", marginBottom: 4 }}>模型</label>
            <input style={input} value={config.model || ""} placeholder="gpt-4o-mini"
              onChange={e => setConfig({ ...config, model: e.target.value })}/>
          </div>
          <div style={{ gridColumn: "1 / -1" }}>
            <label style={{ fontSize: 12, fontWeight: 600, color: theme.textMuted, display: "block", marginBottom: 4 }}>Base URL</label>
            <input style={input} value={config.base_url || ""} placeholder="https://api.openai.com/v1"
              onChange={e => setConfig({ ...config, base_url: e.target.value })}/>
          </div>
        </div>
        <button style={{ ...btn(), marginTop: 12 }} onClick={saveConfig} disabled={saving}>
          {saving ? "保存中..." : "💾 保存配置"}
        </button>
      </div>

      {/* Generate lesson */}
      <div style={card}>
        <h4 style={{ margin: "0 0 12px", color: theme.text }}>🎨 AI 生成教程</h4>
        <div style={{ display: "flex", gap: 8 }}>
          <input style={{ ...input, flex: 1 }} value={genTopic} onChange={e => setGenTopic(e.target.value)}
            placeholder="输入主题，如：20以内进位加法"/>
          <button style={btn()} onClick={generateLesson} disabled={generating}>
            {generating ? "⏳ 生成中..." : "✨ 生成"}
          </button>
        </div>
        {genResult && (
          <div style={{ marginTop: 12 }}>
            {genResult.success ? (
              <div>
                <span style={{ color: theme.success, fontWeight: 600 }}>✅ 生成成功</span>
                <pre style={{ background: "#f8fafc", border: `1px solid ${theme.border}`, borderRadius: 8,
                  padding: 12, fontSize: 12, overflow: "auto", maxHeight: 300, marginTop: 8 }}>
                  {JSON.stringify(genResult.data, null, 2)}
                </pre>
              </div>
            ) : (
              <div style={{ color: theme.danger }}>❌ 生成失败: {genResult.errors?.join(", ") || JSON.stringify(genResult)}</div>
            )}
          </div>
        )}
      </div>

      {/* Generate exercises */}
      <div style={card}>
        <h4 style={{ margin: "0 0 12px", color: theme.text }}>📝 AI 生成题目</h4>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input style={{ ...input, flex: 1 }} value={exTopic} onChange={e => setExTopic(e.target.value)}
            placeholder="题目主题"/>
          <input style={{ ...input, width: 60 }} type="number" value={exCount} min={1} max={20}
            onChange={e => setExCount(parseInt(e.target.value) || 5)}/>
          <span style={{ fontSize: 12, color: theme.textMuted, whiteSpace: "nowrap" }}>题</span>
          <button style={btn()} onClick={generateExercises} disabled={generating}>
            {generating ? "⏳..." : "✨ 生成"}
          </button>
        </div>
        {exResult && (
          <div style={{ marginTop: 12 }}>
            {exResult.success ? (
              <div>
                <span style={{ color: theme.success, fontWeight: 600 }}>✅ 成功生成 {exResult.total_valid}/{exResult.total_generated} 题</span>
                <pre style={{ background: "#f8fafc", border: `1px solid ${theme.border}`, borderRadius: 8,
                  padding: 12, fontSize: 12, overflow: "auto", maxHeight: 300, marginTop: 8 }}>
                  {JSON.stringify(exResult.exercises, null, 2)}
                </pre>
              </div>
            ) : (
              <div style={{ color: theme.danger }}>❌ {exResult.errors?.join(", ") || JSON.stringify(exResult)}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================
// ANALYTICS
// ============================================================
function Analytics() {
  const [data, setData] = useState(null);
  useEffect(() => { apiFetch("/analytics").then(setData); }, []);

  if (!data) return <div>加载中...</div>;

  return (
    <div>
      <h2 style={{ margin: "0 0 20px", fontSize: 22, fontWeight: 700, color: theme.text }}>📊 学情分析</h2>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 24 }}>
        <div style={card}>
          <div style={{ fontSize: 12, color: theme.textMuted, fontWeight: 600 }}>总学习人数</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: theme.primary }}>{data.total_users}</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: 12, color: theme.textMuted, fontWeight: 600 }}>课时数量</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: theme.success }}>{data.lesson_stats?.length || 0}</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: 12, color: theme.textMuted, fontWeight: 600 }}>平均星级</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: theme.warning }}>
            {data.lesson_stats?.length ? (data.lesson_stats.reduce((s, l) => s + (l.avg_stars || 0), 0) / data.lesson_stats.length).toFixed(1) : "0"}
          </div>
        </div>
      </div>

      {data.lesson_stats?.length > 0 && (
        <div style={card}>
          <h4 style={{ margin: "0 0 16px", color: theme.text }}>各课时学习情况</h4>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "#f1f5f9" }}>
                <th style={{ padding: "8px 12px", textAlign: "left", color: theme.textMuted }}>课时</th>
                <th style={{ padding: "8px 12px", textAlign: "center", color: theme.textMuted }}>学习人次</th>
                <th style={{ padding: "8px 12px", textAlign: "center", color: theme.textMuted }}>平均星级</th>
                <th style={{ padding: "8px 12px", textAlign: "center", color: theme.textMuted }}>平均正确率</th>
                <th style={{ padding: "8px 12px", textAlign: "center", color: theme.textMuted }}>平均用时(秒)</th>
              </tr>
            </thead>
            <tbody>
              {data.lesson_stats.map(l => (
                <tr key={l.id} style={{ borderBottom: `1px solid ${theme.border}` }}>
                  <td style={{ padding: "10px 12px", fontWeight: 600 }}>{l.title}</td>
                  <td style={{ padding: "10px 12px", textAlign: "center" }}>{l.attempts || 0}</td>
                  <td style={{ padding: "10px 12px", textAlign: "center" }}>{"⭐".repeat(Math.round(l.avg_stars || 0))}</td>
                  <td style={{ padding: "10px 12px", textAlign: "center" }}>
                    <span style={{
                      padding: "2px 8px", borderRadius: 10, fontSize: 12, fontWeight: 600,
                      background: (l.avg_accuracy || 0) >= 80 ? "#d1fae5" : (l.avg_accuracy || 0) >= 50 ? "#fef3c7" : "#fee2e2",
                      color: (l.avg_accuracy || 0) >= 80 ? "#065f46" : (l.avg_accuracy || 0) >= 50 ? "#92400e" : "#991b1b",
                    }}>
                      {(l.avg_accuracy || 0).toFixed(0)}%
                    </span>
                  </td>
                  <td style={{ padding: "10px 12px", textAlign: "center" }}>{(l.avg_time || 0).toFixed(0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ============================================================
// APP ROOT
// ============================================================
export default function AdminApp() {
  const [page, setPage] = useState("courses");

  return (
    <div style={{ display: "flex", fontFamily: theme.font, color: theme.text, background: theme.bg, minHeight: "100vh" }}>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
      <Sidebar active={page} onNav={setPage}/>
      <div style={{ flex: 1, padding: 28, overflow: "auto" }}>
        {page === "courses" && <CourseManager/>}
        {page === "exercises" && <ExerciseManager/>}
        {page === "ai" && <AIConfig/>}
        {page === "analytics" && <Analytics/>}
      </div>
    </div>
  );
}
