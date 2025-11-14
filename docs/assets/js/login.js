const AUTH_RECORD = {
  email: "facade.engineer@atlaslabs.com",
  digest: "917b4fc087ccf280c13730b26b00575e76a8c16abce6c242f99e9d3b2477df12", // 访问密钥的SHA-256摘要
};

const SESSION_KEY = "facade-session";

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("year").textContent = new Date().getFullYear().toString();
  initialiseTooltips();
  if (window.localStorage.getItem(SESSION_KEY)) {
    window.location.href = "app.html";
    return;
  }
  const loginForm = document.getElementById("loginForm");
  loginForm.addEventListener("submit", handleLogin);
  loginForm.querySelectorAll("input").forEach((input) => {
    input.addEventListener("input", () => hideFeedback());
  });
});

function initialiseTooltips() {
  const triggers = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  triggers.forEach((triggerEl) => new window.bootstrap.Tooltip(triggerEl));
}

async function handleLogin(event) {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }

  const email = form.email.value.trim().toLowerCase();
  const password = form.password.value;

  try {
    const digest = await computeDigest(`${email}:${password}`);
    if (email === AUTH_RECORD.email && digest === AUTH_RECORD.digest) {
      const token = await computeDigest(`${digest}:${Date.now()}`);
      window.localStorage.setItem(
        SESSION_KEY,
        JSON.stringify({ email, token, issuedAt: new Date().toISOString() })
      );
      window.location.href = "app.html";
    } else {
      displayFeedback("凭证校验失败，请检查账号或访问密钥。");
    }
  } catch (error) {
    console.error("login error", error);
    displayFeedback("登录校验模块暂时不可用，请稍后重试。");
  }
}

function hideFeedback() {
  const feedback = document.getElementById("loginFeedback");
  feedback.classList.add("d-none");
}

function displayFeedback(message) {
  const feedback = document.getElementById("loginFeedback");
  feedback.textContent = message;
  feedback.classList.remove("d-none");
}

async function computeDigest(input) {
  const encoder = new TextEncoder();
  const buffer = encoder.encode(input);
  const hashBuffer = await window.crypto.subtle.digest("SHA-256", buffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}
