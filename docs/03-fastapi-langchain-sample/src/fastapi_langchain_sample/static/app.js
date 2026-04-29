const messages = document.querySelector("#messages");
const statusEl = document.querySelector("#status");
const environmentEl = document.querySelector("#environment");
const indexedCountEl = document.querySelector("#indexedCount");
const emptyEl = document.querySelector("#empty");
const form = document.querySelector("#form");
const input = document.querySelector("#message");
const submit = document.querySelector("#submit");
const chips = document.querySelectorAll(".chip");

function append(role, text, sources = []) {
  emptyEl?.remove();

  const item = document.createElement("div");
  item.className = `message ${role}`;
  item.textContent = text;

  if (sources.length) {
    const sourceBox = document.createElement("div");
    sourceBox.className = "sources";
    const uniqueSources = [...new Set(sources.map((source) => source.source))];
    uniqueSources.forEach((source) => {
      const pill = document.createElement("span");
      pill.className = "source-pill";
      pill.textContent = source;
      sourceBox.appendChild(pill);
    });
    item.appendChild(sourceBox);
  }

  messages.appendChild(item);
  item.scrollIntoView({ behavior: "smooth", block: "end" });
}

fetch("/api/v1/health")
  .then((response) => response.json())
  .then((data) => {
    statusEl.textContent = `${data.environment} / ${data.indexed_documents}개 인덱싱`;
    environmentEl.textContent = data.environment;
    indexedCountEl.textContent = data.indexed_documents.toLocaleString("ko-KR");
  })
  .catch(() => {
    statusEl.textContent = "서버 상태를 확인하지 못했습니다.";
  });

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    input.value = chip.textContent.trim();
    input.focus();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  append("user", message);
  input.value = "";
  submit.disabled = true;
  submit.textContent = "처리 중";

  try {
    const response = await fetch("/api/v1/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "요청 실패");
    append("assistant", data.answer, data.sources || []);
  } catch (error) {
    input.value = message;
    append("assistant", `오류: ${error.message}`);
  } finally {
    submit.disabled = false;
    submit.textContent = "전송";
  }
});
