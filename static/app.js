/**
 * Smart Healthcare Navigator - Client Application
 * Premium Green & Black Theme: High Contrast, Animated UI, Larger Typography
 */

// Global State
let conversationHistory = [];
let currentProvider = "local";
let currentModelName = "llama3";
let apiKey = "";
let currentThreshold = 0.20;
let patientName = "Alex Morgan";
let lastSpecialists = [];
let lastRecommendedSpecialist = "General Physician";

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  // Load settings
  const savedProvider = localStorage.getItem("shn_provider");
  if (savedProvider) currentProvider = savedProvider;

  const savedModel = localStorage.getItem("shn_modelname");
  if (savedModel) currentModelName = savedModel;
  const modelInput = document.getElementById("ollamaModelInput");
  if (modelInput) modelInput.value = currentModelName;

  const savedKey = localStorage.getItem("shn_apikey");
  if (savedKey) {
    apiKey = savedKey;
    const keyInput = document.getElementById("apiKeyInput");
    if (keyInput) keyInput.value = apiKey;
  }

  const savedThreshold = localStorage.getItem("shn_threshold");
  if (savedThreshold) {
    const val = parseFloat(savedThreshold);
    currentThreshold = (val < 0.18) ? 0.20 : val;
  }
  
  const slider = document.getElementById("thresholdSlider");
  if (slider) slider.value = currentThreshold;
  updateThresholdLabel(currentThreshold);

  // Set selected provider radio
  const targetRadio = document.querySelector(`input[name='provider'][value='${currentProvider}']`);
  if (targetRadio) {
    targetRadio.checked = true;
  }
  updateProviderFormFields();

  // Listen to provider radio changes
  document.querySelectorAll("input[name='provider']").forEach(radio => {
    radio.addEventListener("change", updateProviderFormFields);
  });

  // Set default booking date to tomorrow
  const dateInput = document.getElementById("modalDateInput");
  if (dateInput) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split("T")[0];
    dateInput.value = dateStr;
    dateInput.min = dateStr;
  }

  loadCorpusDiagnostics();
  loadSpecialists();
});

function updateProviderFormFields() {
  const selected = document.querySelector("input[name='provider']:checked")?.value || "local";
  const apiKeyGroup = document.getElementById("apiKeyGroup");
  const ollamaGroup = document.getElementById("ollamaModelGroup");
  if (apiKeyGroup) {
    apiKeyGroup.classList.toggle("hidden", selected !== "gemini" && selected !== "openai");
  }
  if (ollamaGroup) {
    ollamaGroup.classList.toggle("hidden", selected !== "ollama");
  }
}

// Tab Navigation
function switchTab(tabName) {
  document.querySelectorAll(".tab-pane").forEach(el => el.classList.add("hidden"));
  document.querySelectorAll(".tab-pane").forEach(el => el.classList.remove("active"));
  
  document.querySelectorAll(".tab-btn").forEach(el => {
    el.classList.remove("active", "text-[#00ff88]", "bg-[#0f2419]", "border-[#10b981]");
    el.classList.add("text-slate-300");
  });

  const activePane = document.getElementById(`tab-${tabName}`);
  const activeBtn = document.getElementById(`tab-btn-${tabName}`);
  
  if (activePane) {
    activePane.classList.remove("hidden");
    activePane.classList.add("active");
  }
  if (activeBtn) {
    activeBtn.classList.add("active", "text-[#00ff88]", "bg-[#0f2419]", "border-[#10b981]");
    activeBtn.classList.remove("text-slate-300");
  }
}

// Quick Prompt Insertion
function insertPrompt(text) {
  const input = document.getElementById("chatInput");
  if (input) {
    input.value = text;
    input.focus();
  }
}

// Update Threshold Slider UI
function updateThresholdLabel(val) {
  currentThreshold = parseFloat(val);
  const display = document.getElementById("thresholdDisplay");
  const headerLabel = document.getElementById("currentThresholdLabel");
  const diagThresh = document.getElementById("diagThresholdValue");
  if (display) display.textContent = currentThreshold.toFixed(2);
  if (headerLabel) headerLabel.textContent = currentThreshold.toFixed(2);
  if (diagThresh) diagThresh.textContent = currentThreshold.toFixed(2);
}

// Reset Chat
function clearChat() {
  conversationHistory = [];
  const container = document.getElementById("chatMessages");
  container.innerHTML = `
    <div class="flex items-start gap-4">
      <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-black flex-shrink-0 flex items-center justify-center text-base shadow-md shadow-emerald-500/20 font-bold">
        <i class="fa-solid fa-stethoscope"></i>
      </div>
      <div class="chat-bubble-ai p-5 max-w-[88%] text-[15px] text-slate-200 leading-relaxed shadow-lg border border-[#1b3828]">
        <p class="font-display font-extrabold text-white mb-1.5 text-base">Chat history reset.</p>
        <p class="text-slate-300 text-sm">How are you feeling right now? Describe any symptoms or questions to begin.</p>
      </div>
    </div>
  `;
  resetDiagnosticPanel();
}

function resetDiagnosticPanel() {
  document.getElementById("diagIntent").textContent = "Awaiting query...";
  document.getElementById("diagRouting").innerHTML = `<span>Route: <strong>Standing by</strong></span>`;
  document.getElementById("diagScoreText").textContent = `0.000 / ${currentThreshold.toFixed(2)}`;
  document.getElementById("diagScoreBar").style.width = "0%";
  document.getElementById("diagScoreBar").className = "bg-gradient-to-r from-emerald-500 via-teal-400 to-[#00ff88] h-2.5 rounded-full transition-all duration-700 ease-out";
  document.getElementById("diagDecisionText").textContent = "No query evaluated yet";
  document.getElementById("diagDecisionBox").style.backgroundColor = "#0e1913";
  document.getElementById("diagDecisionBox").style.borderColor = "#1c3828";
  document.getElementById("diagSourcesList").innerHTML = `<div class="p-3 bg-[#0f1b14] rounded-xl border border-[#1a3627] text-slate-500 italic text-xs">No sources cited yet</div>`;
  document.getElementById("diagnosticStatus").textContent = "Ready";
  document.getElementById("diagnosticStatus").className = "text-xs font-bold px-3 py-1 rounded-full bg-[#11241a] text-[#00ff88] border border-[#10b981]/50";
}

// Handle Chat Submission
async function handleSendChat(event) {
  event.preventDefault();
  const input = document.getElementById("chatInput");
  const query = input.value.trim();
  if (!query) return;

  // Render User Message
  appendUserMessage(query);
  input.value = "";
  conversationHistory.push({ role: "user", content: query });

  // Render Typing Indicator
  const typingId = appendTypingIndicator();

  try {
    const payload = {
      message: query,
      history: conversationHistory,
      provider: currentProvider,
      api_key: apiKey || null,
      model_name: currentModelName,
      threshold: currentThreshold,
      patient_name: patientName
    };

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    removeTypingIndicator(typingId);

    if (!res.ok) {
      const err = await res.json();
      appendAIMessage(`[Error]: ${err.detail || "Unable to reach server"}`);
      return;
    }

    const data = await res.json();
    conversationHistory.push({ role: "assistant", content: data.response });

    if (data.recommended_specialist) {
      lastRecommendedSpecialist = data.recommended_specialist;
    }

    // Render AI Response
    appendAIMessage(data.response, data);

    // Update Right Diagnostics Panel
    updateDiagnosticPanel(data);

    // Update Inspector Chunks
    updateInspectorChunks(data.matches);

  } catch (error) {
    removeTypingIndicator(typingId);
    appendAIMessage(`[Network Error]: Unable to connect to backend: ${error.message}`);
  }
}

// Append User Bubble
function appendUserMessage(text) {
  const container = document.getElementById("chatMessages");
  const msgEl = document.createElement("div");
  msgEl.className = "flex items-start justify-end gap-3.5";
  msgEl.innerHTML = `
    <div class="chat-bubble-user p-4 max-w-[80%] text-[15px] leading-relaxed shadow-lg font-medium">
      ${escapeHtml(text)}
    </div>
    <div class="w-10 h-10 rounded-2xl bg-[#0e1f16] border border-[#10b981] text-[#00ff88] flex-shrink-0 flex items-center justify-center text-sm font-bold shadow-md shadow-emerald-500/20">
      ${patientName.charAt(0) || "U"}
    </div>
  `;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

// Append AI Message Bubble with Modern Green & Black Cards
function appendAIMessage(rawText, data = null) {
  const container = document.getElementById("chatMessages");
  const msgEl = document.createElement("div");
  msgEl.className = "flex items-start gap-4";

  let bodyHtml = renderStructuredAIResponse(rawText, data);

  // If specialists are returned
  let specialistCardsHtml = "";
  if (data && data.specialists && data.specialists.length > 0) {
    specialistCardsHtml = `
      <div class="mt-4 pt-4 border-t border-[#1a3828]">
        <div class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
          <i class="fa-solid fa-calendar-check text-[#00ff88]"></i> Recommended Specialists with Open Slots:
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
          ${data.specialists.slice(0, 2).map(doc => `
            <div class="p-4 bg-[#09120d] border border-[#1c3a28] rounded-2xl flex items-center justify-between text-xs hover:border-[#00ff88] transition shadow-md">
              <div>
                <div class="font-bold text-white text-sm">${doc.name}</div>
                <div class="text-xs text-[#00ff88] font-semibold">${doc.specialty}</div>
                <div class="text-[11px] text-slate-400 mt-0.5">${doc.hospital}</div>
              </div>
              <button onclick="openBookingModal('${doc.id}', '${doc.name}', '${doc.specialty}')" class="px-3.5 py-2 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-black rounded-xl text-xs font-extrabold shadow-sm active:scale-95 transition">
                Book
              </button>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }

  // Safety and Grounding Badge
  let groundingBadge = "";
  if (data) {
    if (data.is_grounded && data.intent === "HEALTHCARE_SYMPTOM") {
      groundingBadge = `
        <div class="mt-4 pt-3.5 border-t border-[#1a3828] flex flex-wrap items-center justify-between gap-3 text-xs">
          <div class="flex items-center gap-2">
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#102419] text-[#00ff88] font-bold border border-[#10b981]/50 shadow-xs">
              <i class="fa-solid fa-shield-check text-[#00ff88]"></i> Grounded in Verified Medical Corpus (${(data.rag_score).toFixed(3)})
            </span>
          </div>
          ${data.sources && data.sources.length ? `<span class="text-slate-400 font-medium text-xs">Sources: ${data.sources.slice(0, 2).join(", ")}</span>` : ""}
        </div>
      `;
    } else if (data.intent === "GREETING") {
      groundingBadge = `
        <div class="mt-3.5 text-xs text-[#00ff88] bg-[#0c1b13] px-3.5 py-2 rounded-xl border border-[#10b981]/40 flex items-center gap-2">
          <i class="fa-solid fa-hand-wave text-emerald-400"></i> Smart Healthcare Navigator is ready to evaluate your symptoms.
        </div>
      `;
    } else if (data.intent === "UNRELATED") {
      groundingBadge = `
        <div class="mt-3.5 text-xs text-rose-300 bg-[#201013] px-3.5 py-2 rounded-xl border border-rose-500/50 flex items-center gap-2 font-medium">
          <i class="fa-solid fa-ban text-rose-400"></i> Out-of-Domain Filter: Dedicated exclusively to medical and appointment inquiries.
        </div>
      `;
    } else if (data.intent === "EMERGENCY_ALERT") {
      groundingBadge = `
        <div class="mt-3.5 text-xs text-rose-200 bg-[#281115] px-3.5 py-2.5 rounded-xl border border-rose-500 flex items-center gap-2 font-bold">
          <i class="fa-solid fa-triangle-exclamation text-rose-400 text-sm animate-pulse"></i> Critical Medical Red-Flag Screened.
        </div>
      `;
    } else if (!data.is_grounded && data.intent === "HEALTHCARE_SYMPTOM") {
      groundingBadge = `
        <div class="mt-3.5 text-xs text-amber-200 bg-[#1c180e] px-3.5 py-2 rounded-xl border border-amber-500/50 flex items-center gap-2">
          <i class="fa-solid fa-shield-exclamation text-amber-400 text-base"></i>
          <span>Retrieval Score (${(data.rag_score || 0).toFixed(3)}) &lt; Threshold (${(data.threshold || 0.20).toFixed(2)}) • Safe fallback enforced (Refusal to guess).</span>
        </div>
      `;
    }
  }

  msgEl.innerHTML = `
    <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-black flex-shrink-0 flex items-center justify-center text-base shadow-md shadow-emerald-500/20 font-bold">
      <i class="fa-solid fa-stethoscope"></i>
    </div>
    <div class="chat-bubble-ai p-6 max-w-[88%] text-[15px] text-slate-100 leading-relaxed shadow-xl border border-[#1b3828]">
      ${bodyHtml}
      ${specialistCardsHtml}
      ${groundingBadge}
    </div>
  `;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

// Structured Medical Response Renderer
function renderStructuredAIResponse(rawText, data) {
  if (!data || !data.is_grounded || data.intent !== "HEALTHCARE_SYMPTOM") {
    return `<div class="text-slate-200 font-medium text-[15px]">${formatMarkdown(rawText)}</div>`;
  }

  // Parse out 3 possible common ailments
  const ailmentRegex = /\d+\.\s+\*\*([^*]+)\*\*:\s*([^\n\r]+)/g;
  let ailments = [];
  let match;
  while ((match = ailmentRegex.exec(rawText)) !== null) {
    ailments.push({ title: match[1].trim(), desc: match[2].trim() });
  }

  // Render 3 distinct cards
  if (ailments.length > 0) {
    let cleanIntro = rawText.split("### Possible Common Ailments")[0] || "Based on your symptoms and our verified reference documents:";

    const icons = ["🤒", "🫁", "🩹", "🤢", "🤕"];

    let ailmentCardsHtml = `
      <div class="my-4 space-y-3">
        <div class="text-xs font-extrabold uppercase tracking-wider text-[#00ff88] mb-1 flex items-center gap-2">
          <i class="fa-solid fa-notes-medical text-base"></i> 3 Possible Common Ailments (Verified Reference Guidelines):
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
          ${ailments.slice(0, 3).map((a, i) => `
            <div class="ailment-card flex flex-col justify-between">
              <div>
                <div class="text-xl mb-1.5">${icons[i % icons.length]}</div>
                <div class="font-bold text-white text-sm leading-snug mb-1">${escapeHtml(a.title)}</div>
                <div class="text-xs text-slate-300 leading-relaxed">${escapeHtml(a.desc)}</div>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;

    // Specialist banner
    let specialistBanner = `
      <div class="my-3.5 p-4 bg-[#0a1610] border border-[#1b3a28] rounded-2xl flex items-center justify-between text-xs sm:text-sm">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-[#11241a] border border-[#1a3828] text-[#00ff88] flex items-center justify-center text-sm font-bold">
            <i class="fa-solid fa-user-doctor"></i>
          </div>
          <div>
            <span class="text-slate-400 text-xs">Recommended Specialist:</span>
            <div class="font-extrabold text-[#00ff88] text-sm">${escapeHtml(data.recommended_specialist || "General Physician")}</div>
          </div>
        </div>
        <button onclick="switchTab('hospital'); document.getElementById('specialtyFilter').value='${data.recommended_specialist || ""}'; loadSpecialists();" class="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-black rounded-xl text-xs font-extrabold transition shadow-sm">
          Find Specialist
        </button>
      </div>
    `;

    // Extract supportive self care if present
    let selfCareHtml = "";
    if (rawText.includes("Supportive Self-Care Tips")) {
      const careSection = rawText.split("### Supportive Self-Care Tips")[1]?.split("###")[0] || "";
      const tips = careSection.match(/-\s+\*\*([^*]+)\*\*:\s*([^\n\r]+)/g);
      if (tips) {
        selfCareHtml = `
          <div class="my-3.5 p-4 bg-[#09120d] rounded-2xl border border-[#193325] text-xs">
            <div class="font-bold text-white mb-2 flex items-center gap-2">
              <i class="fa-solid fa-hand-holding-medical text-[#00ff88]"></i> Supportive Self-Care (While Awaiting Evaluation):
            </div>
            <ul class="space-y-1.5 text-slate-300 list-disc pl-4 text-xs leading-relaxed">
              ${tips.map(t => `<li>${formatMarkdown(t.replace(/-\s+/, ''))}</li>`).join("")}
            </ul>
          </div>
        `;
      }
    }

    return `
      <div>
        <p class="text-slate-200 font-medium mb-2.5 text-[15px]">${formatMarkdown(cleanIntro)}</p>
        ${ailmentCardsHtml}
        ${specialistBanner}
        ${selfCareHtml}
        <div class="mt-3.5 p-3.5 bg-[#09110d] rounded-xl text-xs text-slate-400 leading-normal border border-[#183022]">
          <strong>Medical Notice:</strong> Preliminary assessment provided for educational purposes based on verified clinical data. It does not constitute a clinical diagnosis or prescription.
        </div>
      </div>
    `;
  }

  return `<div>${formatMarkdown(rawText)}</div>`;
}

// Typing Indicator
function appendTypingIndicator() {
  const container = document.getElementById("chatMessages");
  const id = `typing-${Date.now()}`;
  const typingEl = document.createElement("div");
  typingEl.id = id;
  typingEl.className = "flex items-start gap-4";
  typingEl.innerHTML = `
    <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-black flex-shrink-0 flex items-center justify-center text-base shadow-md shadow-emerald-500/20 font-bold">
      <i class="fa-solid fa-stethoscope"></i>
    </div>
    <div class="bg-[#0d1712] border border-[#1b3828] p-4 rounded-2xl rounded-tl-none flex items-center gap-2.5 shadow-lg">
      <span class="w-2.5 h-2.5 rounded-full bg-[#00ff88] animate-bounce"></span>
      <span class="w-2.5 h-2.5 rounded-full bg-[#00ff88] animate-bounce" style="animation-delay: 0.15s"></span>
      <span class="w-2.5 h-2.5 rounded-full bg-[#00ff88] animate-bounce" style="animation-delay: 0.3s"></span>
    </div>
  `;
  container.appendChild(typingEl);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// Update Right Diagnostics Panel
function updateDiagnosticPanel(data) {
  const intentEl = document.getElementById("diagIntent");
  const routingEl = document.getElementById("diagRouting");
  const scoreText = document.getElementById("diagScoreText");
  const scoreBar = document.getElementById("diagScoreBar");
  const decisionBox = document.getElementById("diagDecisionBox");
  const decisionText = document.getElementById("diagDecisionText");
  const sourcesList = document.getElementById("diagSourcesList");
  const statusBadge = document.getElementById("diagnosticStatus");

  // Intent
  intentEl.textContent = (data.intent || "UNKNOWN").replace("_", " ");
  routingEl.innerHTML = `<span>Route: <strong class="text-white">${data.routed_to || "None"}</strong></span>`;

  // Score
  const score = data.rag_score || 0.0;
  const thresh = data.threshold || currentThreshold;
  scoreText.textContent = `${score.toFixed(3)} / ${thresh.toFixed(2)}`;
  
  // Progress Bar Width
  const pct = Math.min(Math.round((score / Math.max(thresh * 1.6, 0.45)) * 100), 100);
  scoreBar.style.width = `${pct}%`;

  if (data.is_grounded && data.intent === "HEALTHCARE_SYMPTOM") {
    scoreBar.className = "bg-gradient-to-r from-emerald-500 via-teal-400 to-[#00ff88] h-2.5 rounded-full transition-all duration-700 ease-out shadow-[0_0_15px_rgba(0,255,136,0.7)]";
    statusBadge.textContent = "Verified Grounded";
    statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-[#102419] text-[#00ff88] border border-[#10b981]/50";

    decisionBox.style.backgroundColor = "#0e1c15";
    decisionBox.style.borderColor = "#10b981";
    decisionText.innerHTML = `
      <div class="text-[#00ff88] font-bold flex items-center gap-2 text-xs">
        <i class="fa-solid fa-circle-check text-sm"></i> Score &gt;= Threshold (${score.toFixed(3)} &gt;= ${thresh.toFixed(2)})
      </div>
      <p class="text-xs text-emerald-200 mt-1 leading-normal font-normal">
        Confidence cleared. Response was synthesized strictly from verified medical reference corpus without hallucination.
      </p>
    `;
  } else if (data.intent === "GREETING") {
    scoreBar.className = "bg-gradient-to-r from-emerald-500 via-teal-400 to-[#00ff88] h-2.5 rounded-full transition-all duration-700 ease-out";
    statusBadge.textContent = "Greeting";
    statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-[#102419] text-[#00ff88] border border-[#10b981]/50";

    decisionBox.style.backgroundColor = "#0e1c15";
    decisionBox.style.borderColor = "#1b3828";
    decisionText.innerHTML = `
      <div class="text-[#00ff88] font-bold flex items-center gap-2 text-xs">
        <i class="fa-solid fa-handshake text-sm"></i> Conversational Greeting Recognized
      </div>
      <p class="text-xs text-slate-300 mt-1 leading-normal font-normal">
        Friendly welcome and orientation provided to assist user with symptom inputs.
      </p>
    `;
  } else if (data.intent === "UNRELATED") {
    scoreBar.className = "bg-gradient-to-r from-rose-600 to-red-500 h-2.5 rounded-full transition-all duration-700 ease-out shadow-[0_0_12px_rgba(244,63,94,0.6)]";
    statusBadge.textContent = "Rejected";
    statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-[#201013] text-rose-300 border border-rose-500/50";

    decisionBox.style.backgroundColor = "#1a0e10";
    decisionBox.style.borderColor = "#e11d48";
    decisionText.innerHTML = `
      <div class="text-rose-400 font-bold flex items-center gap-2 text-xs">
        <i class="fa-solid fa-circle-xmark text-sm"></i> Non-Healthcare Intent Filtered
      </div>
      <p class="text-xs text-rose-200 mt-1 leading-normal font-normal">
        The agent safely rejected this query without searching the medical RAG vector store or guessing.
      </p>
    `;
  } else if (data.intent === "EMERGENCY_ALERT") {
    scoreBar.className = "bg-rose-500 h-2.5 rounded-full transition-all duration-700 ease-out";
    statusBadge.textContent = "Emergency";
    statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-[#281115] text-rose-200 border border-rose-500 font-extrabold";

    decisionBox.style.backgroundColor = "#240d12";
    decisionBox.style.borderColor = "#f43f5e";
    decisionText.innerHTML = `
      <div class="text-rose-300 font-bold flex items-center gap-2 text-xs">
        <i class="fa-solid fa-triangle-exclamation text-sm"></i> Critical Red-Flag Detected
      </div>
      <p class="text-xs text-rose-200 mt-1 leading-normal font-normal">
        Patient instructed immediately to call emergency medical services (911/112).
      </p>
    `;
  } else {
    scoreBar.className = "bg-gradient-to-r from-amber-600 to-yellow-500 h-2.5 rounded-full transition-all duration-700 ease-out shadow-[0_0_12px_rgba(245,158,11,0.5)]";
    statusBadge.textContent = "Safe Fallback";
    statusBadge.className = "text-xs font-bold px-3 py-1 rounded-full bg-[#1c180e] text-amber-300 border border-amber-500/50";

    decisionBox.style.backgroundColor = "#18140c";
    decisionBox.style.borderColor = "#f59e0b";
    decisionText.innerHTML = `
      <div class="text-amber-400 font-bold flex items-center gap-2 text-xs">
        <i class="fa-solid fa-shield-exclamation text-sm"></i> Score &lt; Threshold (${score.toFixed(3)} &lt; ${thresh.toFixed(2)})
      </div>
      <p class="text-xs text-amber-200 mt-1 leading-normal font-normal">
        Knowledge base lacks sufficient verified evidence. Fallback strictly enforced to prevent hallucinations.
      </p>
    `;
  }

  // Sources
  if (data.sources && data.sources.length > 0) {
    sourcesList.innerHTML = data.sources.map(s => `
      <div class="p-2.5 bg-[#0e1a14] rounded-xl text-xs text-slate-200 flex items-center gap-2.5 border border-[#1c3828]">
        <i class="fa-solid fa-circle-check text-[#00ff88] text-xs"></i>
        <span class="truncate font-medium">${escapeHtml(s)}</span>
      </div>
    `).join("");
  } else {
    sourcesList.innerHTML = `<div class="p-3 bg-[#0f1b14] rounded-xl border border-[#1a3627] text-slate-500 italic text-xs">No sources cited</div>`;
  }
}

// Update Chunks in Inspector
function updateInspectorChunks(matches) {
  const container = document.getElementById("inspectorChunks");
  if (!matches || matches.length === 0) {
    container.innerHTML = `
      <div class="p-6 bg-[#16130b] border border-amber-500/50 rounded-2xl text-sm text-amber-200 flex items-start gap-3">
        <i class="fa-solid fa-circle-info text-amber-400 mt-0.5 text-base"></i>
        <div>
          <strong class="font-bold">No verified document chunks passed the confidence threshold.</strong>
          <p class="mt-1 text-amber-300">The agent safely executed the fallback message to protect patient safety.</p>
        </div>
      </div>
    `;
    return;
  }

  container.innerHTML = matches.map((m, idx) => `
    <div class="p-5 bg-[#09120d] border border-[#1a3628] rounded-2xl shadow-md text-xs sm:text-sm space-y-2.5 hover:border-[#00ff88] transition">
      <div class="flex items-center justify-between">
        <span class="font-bold text-white flex items-center gap-2.5">
          <span class="w-6 h-6 rounded-full bg-[#11241a] border border-[#10b981] text-[#00ff88] flex items-center justify-center text-xs font-bold">${idx + 1}</span>
          ${escapeHtml(m.title)} - ${escapeHtml(m.section)}
        </span>
        <span class="px-3 py-1 bg-[#102419] text-[#00ff88] font-mono rounded-lg font-extrabold text-xs border border-[#10b981]/50">
          Score: ${m.score.toFixed(4)}
        </span>
      </div>
      <div class="text-slate-300 bg-[#0c1611] p-4 rounded-xl border border-[#172e21] whitespace-pre-wrap leading-relaxed">
        ${escapeHtml(m.content)}
      </div>
      <div class="text-xs text-slate-400 flex items-center justify-between pt-1">
        <span><strong>Source:</strong> ${escapeHtml(m.source)}</span>
        <span><strong>Specialist:</strong> ${escapeHtml(m.specialty)}</span>
      </div>
    </div>
  `).join("");
}

// Load Corpus Diagnostics
async function loadCorpusDiagnostics() {
  try {
    const res = await fetch("/api/rag-diagnostics");G
    if (!res.ok) return;
    const data = await res.json();
    
    const container = document.getElementById("corpusDocsList");
    if (container && data.corpus_documents) {
      container.innerHTML = data.corpus_documents.map(doc => `
        <div class="p-4 bg-[#0a120e] border border-[#193324] rounded-2xl flex items-center justify-between text-xs sm:text-sm hover:border-[#00ff88] hover:bg-[#0c1712] transition shadow-md">
          <div class="flex items-center gap-3.5">
            <div class="w-10 h-10 rounded-xl bg-[#11241a] text-[#00ff88] border border-[#1b3a28] flex items-center justify-center text-base">
              <i class="fa-solid fa-file-medical"></i>
            </div>
            <div>
              <div class="font-bold text-white">${escapeHtml(doc)}</div>
              <div class="text-xs text-slate-400">Verified Clinical Protocol</div>
            </div>
          </div>
          <span class="px-3 py-1 rounded-full bg-[#102419] text-[#00ff88] text-xs font-bold border border-[#10b981]/50">Indexed</span>
        </div>
      `).join("");
    }
  } catch (e) {
    console.error("Diagnostics load error:", e);
  }
}

// Load Specialists (Level 2)
async function loadSpecialists() {
  const filter = document.getElementById("specialtyFilter")?.value || "";
  const grid = document.getElementById("specialistsGrid");
  if (!grid) return;

  grid.innerHTML = `<div class="col-span-full py-12 text-center text-slate-400 text-base font-medium">Loading verified medical specialists...</div>`;

  try {
    const url = filter ? `/api/specialists?specialty=${encodeURIComponent(filter)}` : "/api/specialists";
    const res = await fetch(url);
    if (!res.ok) return;
    const docs = await res.json();
    lastSpecialists = docs;

    if (docs.length === 0) {
      grid.innerHTML = `<div class="col-span-full py-12 text-center text-slate-500 text-base">No specialists matching that filter.</div>`;
      return;
    }

    grid.innerHTML = docs.map(doc => `
      <div class="doctor-card p-6 bg-[#0a120e] border border-[#183324] rounded-3xl shadow-xl hover:shadow-2xl transition flex flex-col justify-between">
        <div>
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#11241a] to-[#163524] text-[#00ff88] flex items-center justify-center font-bold text-2xl border border-[#10b981]/40 shadow-md">
                <i class="fa-solid fa-user-doctor"></i>
              </div>
              <div>
                <h3 class="font-display font-extrabold text-white text-base">${escapeHtml(doc.name)}</h3>
                <span class="text-xs text-[#00ff88] font-bold">${escapeHtml(doc.specialty)}</span>
              </div>
            </div>
            <div class="flex items-center gap-1.5 text-xs bg-[#1a170b] text-amber-300 px-3 py-1 rounded-full border border-amber-500/50 font-bold shadow-xs">
              <i class="fa-solid fa-star text-amber-400 text-xs"></i> ${doc.rating}
            </div>
          </div>

          <div class="mt-5 space-y-2 text-xs sm:text-sm text-slate-300">
            <div class="flex items-center gap-2.5"><i class="fa-solid fa-hospital text-emerald-500 w-4"></i> <span>${escapeHtml(doc.hospital)}</span></div>
            <div class="flex items-center gap-2.5"><i class="fa-solid fa-location-dot text-emerald-500 w-4"></i> <span>${escapeHtml(doc.address)}</span></div>
            <div class="flex items-center gap-2.5"><i class="fa-solid fa-award text-emerald-500 w-4"></i> <span>${doc.experience_years} years clinical experience</span></div>
          </div>

          <div class="mt-4 pt-3.5 border-t border-[#172e21]">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Available Slots:</div>
            <div class="flex flex-wrap gap-2">
              ${doc.available_slots.map(s => `
                <button onclick="openBookingModal('${doc.id}', '${doc.name}', '${doc.specialty}', '${s}')" class="px-3 py-1.5 bg-[#0e1c14] hover:bg-[#142e20] text-slate-200 hover:text-[#00ff88] border border-[#1b3a28] rounded-xl text-xs font-semibold transition">
                  ${s}
                </button>
              `).join("")}
            </div>
          </div>
        </div>

        <div class="mt-6 pt-4 border-t border-[#172e21] flex items-center justify-between">
          <span class="text-xs text-emerald-400 font-bold flex items-center gap-1.5">
            <i class="fa-solid fa-circle-check text-xs"></i> Accepting Patients
          </span>
          <button onclick="openBookingModal('${doc.id}', '${doc.name}', '${doc.specialty}')" class="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-black rounded-xl text-xs font-extrabold shadow-lg shadow-emerald-500/20 active:scale-95 transition">
            Book Visit
          </button>
        </div>
      </div>
    `).join("");

  } catch (e) {
    grid.innerHTML = `<div class="col-span-full py-12 text-center text-rose-400 text-base">Error loading specialist directory.</div>`;
  }
}

// Open Booking Modal
function openBookingModal(doctorId, doctorName, specialty, preselectedSlot = null) {
  document.getElementById("modalDoctorId").value = doctorId;
  document.getElementById("modalDoctorName").innerHTML = `
    <i class="fa-solid fa-user-doctor text-[#00ff88] mr-2"></i>
    <span>${doctorName} (${specialty})</span>
  `;
  document.getElementById("modalPatientName").value = patientName;
  
  if (preselectedSlot) {
    document.getElementById("modalTimeSlotSelect").value = preselectedSlot;
  }

  const lastUserMsg = conversationHistory.filter(m => m.role === "user").pop();
  if (lastUserMsg) {
    document.getElementById("modalSymptomsSummary").value = lastUserMsg.content;
  }

  document.getElementById("bookingDialog").showModal();
}

// Handle Execute Booking
async function handleExecuteBooking(event) {
  event.preventDefault();
  const doctorId = document.getElementById("modalDoctorId").value;
  const date = document.getElementById("modalDateInput").value;
  const timeSlot = document.getElementById("modalTimeSlotSelect").value;
  const pName = document.getElementById("modalPatientName").value;
  const summary = document.getElementById("modalSymptomsSummary").value;

  try {
    const res = await fetch("/api/book-appointment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        patient_name: pName,
        doctor_id: doctorId,
        date: date,
        time_slot: timeSlot,
        symptoms_summary: summary
      })
    });

    if (!res.ok) {
      alert("Booking failed. Please try again.");
      return;
    }

    const data = await res.json();
    document.getElementById("bookingDialog").close();

    // Show Confirmation Modal
    const b = data.booking;
    document.getElementById("confCode").textContent = b.confirmation_code;
    document.getElementById("confDoctor").textContent = `${b.doctor_name} (${b.specialty})`;
    document.getElementById("confDateTime").textContent = `${b.appointment_date} at ${b.appointment_time}`;
    document.getElementById("confFacility").textContent = `${b.hospital}, ${b.address}`;
    document.getElementById("bookingSuccessDialog").showModal();

    // Add confirmation message to chat
    appendAIMessage(`**Appointment Confirmed!**\nYour consultation with **${b.doctor_name}** is scheduled for **${b.appointment_date} at ${b.appointment_time}** at ${b.hospital}.\nConfirmation Code: \`${b.confirmation_code}\`.`);

  } catch (e) {
    alert("Error executing booking: " + e.message);
  }
}

// Level 3: Request Intake Handoff (SOAP + FHIR)
async function requestIntakeHandoff() {
  const soapBox = document.getElementById("soapNoteBox");
  const fhirBox = document.getElementById("fhirJsonBox");
  soapBox.textContent = "Synthesizing clinical SOAP note from intake conversation turns...";
  fhirBox.textContent = "Generating FHIR-aligned structured JSON chart...";

  try {
    const res = await fetch("/api/intake-summary", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        patient_name: patientName,
        history: conversationHistory,
        recommended_specialist: lastRecommendedSpecialist,
        sources: ["CDC Clinical Pathways", "WHO Guidelines"]
      })
    });

    if (!res.ok) {
      soapBox.textContent = "Error generating clinical summary.";
      fhirBox.textContent = "Error generating FHIR JSON.";
      return;
    }

    const data = await res.json();
    soapBox.textContent = data.soap_note;
    fhirBox.textContent = JSON.stringify(data.machine_usable_json, null, 2);

  } catch (e) {
    soapBox.textContent = "Connection error generating intake summary.";
  }
}

function copySoapNote() {
  const text = document.getElementById("soapNoteBox").textContent;
  navigator.clipboard.writeText(text);
  alert("SOAP Clinical Note copied to clipboard!");
}

function copyFhirJson() {
  const text = document.getElementById("fhirJsonBox").textContent;
  navigator.clipboard.writeText(text);
  alert("FHIR JSON copied to clipboard!");
}

// Level 4: Load Sample Lab Report
async function loadSampleReport(type) {
  try {
    const res = await fetch(`/api/sample-lab-report/${type}`);
    if (!res.ok) {
      alert("Sample report not found.");
      return;
    }
    const data = await res.json();
    renderLabAnalysis(data.analysis);
  } catch (e) {
    alert("Error loading sample report: " + e.message);
  }
}

// Level 4: Handle File Upload
async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/upload-lab-report", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      alert("Failed to analyze uploaded file.");
      return;
    }

    const data = await res.json();
    renderLabAnalysis(data.analysis);
  } catch (e) {
    alert("Error uploading file: " + e.message);
  }
}

// Render Lab Analysis
function renderLabAnalysis(analysis) {
  const container = document.getElementById("labResultsContainer");
  container.classList.remove("hidden");

  // Banner
  const banner = document.getElementById("labBanner");
  if (analysis.has_low_iron) {
    banner.className = "p-6 rounded-3xl border border-rose-500/60 bg-[#1c1012] flex flex-wrap items-center justify-between gap-4 text-xs sm:text-sm shadow-xl";
    banner.innerHTML = `
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center text-2xl flex-shrink-0 shadow-sm border border-rose-500/40">
          <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <div>
          <div class="font-display font-extrabold text-rose-200 text-base">Low Iron / Hemoglobin Levels Identified</div>
          <div class="text-rose-300 font-medium">${analysis.report_name}: ${analysis.abnormalities_count} biomarker(s) flagged below reference baseline.</div>
        </div>
      </div>
      <button onclick="switchTab('hospital'); document.getElementById('specialtyFilter').value='Hematologist'; loadSpecialists();" class="px-5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-extrabold rounded-xl text-xs sm:text-sm transition flex items-center gap-2 shadow-lg shadow-rose-600/30">
        <i class="fa-solid fa-stethoscope"></i> Consult Hematologist
      </button>
    `;
  } else {
    banner.className = "p-6 rounded-3xl border border-emerald-500/60 bg-[#0d1f15] flex flex-wrap items-center justify-between gap-4 text-xs sm:text-sm shadow-xl";
    banner.innerHTML = `
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-2xl bg-emerald-500/20 text-[#00ff88] flex items-center justify-center text-2xl flex-shrink-0 shadow-sm border border-[#10b981]/40">
          <i class="fa-solid fa-circle-check"></i>
        </div>
        <div>
          <div class="font-display font-extrabold text-emerald-100 text-base">Standard Cell Counts Observed</div>
          <div class="text-emerald-300 font-medium">${analysis.report_name}: Tested blood parameters align within expected reference boundaries.</div>
        </div>
      </div>
    `;
  }

  // Biomarkers Table
  const tbody = document.getElementById("labBiomarkersTable");
  tbody.innerHTML = analysis.biomarkers.map(b => {
    let flagBadge = `<span class="px-3 py-1 rounded-full bg-[#102419] text-[#00ff88] font-extrabold text-xs border border-[#10b981]/50">NORMAL</span>`;
    if (b.status === "LOW") {
      flagBadge = `<span class="px-3 py-1 rounded-full bg-[#2a0e13] text-rose-400 font-extrabold text-xs border border-rose-500/60 animate-pulse">LOW</span>`;
    } else if (b.status === "HIGH") {
      flagBadge = `<span class="px-3 py-1 rounded-full bg-[#231b0e] text-amber-400 font-extrabold text-xs border border-amber-500/60">HIGH</span>`;
    }

    return `
      <tr class="hover:bg-[#0f1b14] transition">
        <td class="py-4 px-5 font-bold text-white">${escapeHtml(b.name)}</td>
        <td class="py-4 px-5 font-extrabold ${b.status === 'LOW' ? 'text-rose-400' : 'text-white'} text-sm">${b.value} ${b.unit}</td>
        <td class="py-4 px-5">${flagBadge}</td>
        <td class="py-4 px-5 text-slate-400 font-mono text-xs">${b.reference_range}</td>
        <td class="py-4 px-5 text-slate-300 text-xs">${escapeHtml(b.role)}</td>
      </tr>
    `;
  }).join("");

  // Plain Explanation
  document.getElementById("labPlainExplanation").innerHTML = formatMarkdown(analysis.plain_explanation);

  // Dietary Suggestions
  const dietList = document.getElementById("labDietaryList");
  if (analysis.dietary_recommendations && analysis.dietary_recommendations.length > 0) {
    dietList.innerHTML = analysis.dietary_recommendations.map(d => `<li>${formatMarkdown(d)}</li>`).join("");
  } else {
    dietList.innerHTML = `<li>Maintain a balanced, nutritious diet with adequate hydration and whole foods.</li>`;
  }

  container.scrollIntoView({ behavior: "smooth" });
}

// Settings Save
function saveSettings(event) {
  event.preventDefault();
  const provider = document.querySelector("input[name='provider']:checked").value;
  const key = document.getElementById("apiKeyInput").value;
  const pName = document.getElementById("patientNameInput").value;
  const modelInput = document.getElementById("ollamaModelInput");

  currentProvider = provider;
  apiKey = key;
  patientName = pName || "Alex Morgan";
  if (modelInput) {
    currentModelName = modelInput.value.trim() || "llama3";
    localStorage.setItem("shn_modelname", currentModelName);
  }

  localStorage.setItem("shn_provider", currentProvider);
  localStorage.setItem("shn_apikey", apiKey);
  localStorage.setItem("shn_threshold", currentThreshold);

  updateProviderFormFields();
  alert("Settings saved successfully!");
}

// Helper: Markdown to HTML
function formatMarkdown(text) {
  if (!text) return "";
  let html = text
    .replace(/^### (.*$)/gim, '<div class="font-extrabold text-white mt-3 mb-1.5 text-base">$1</div>')
    .replace(/^## (.*$)/gim, '<div class="font-extrabold text-white mt-3 mb-1.5 text-lg">$1</div>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="text-slate-300">$1</em>')
    .replace(/`([^`]+)`/g, '<code class="bg-[#11241a] text-[#00ff88] px-2 py-0.5 rounded text-xs font-mono border border-[#1b3a28]">$1</code>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n- /g, '<br>• ');
  return html;
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
