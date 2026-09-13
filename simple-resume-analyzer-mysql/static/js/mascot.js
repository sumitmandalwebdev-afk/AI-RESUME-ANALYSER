// ============ LOGIN/SIGNUP LOGIC + MASCOT MOOD CONTROLLER ============

document.addEventListener("DOMContentLoaded", function () {
  const mascot = document.getElementById("mascotSvg");
  const speech = document.getElementById("mascotSpeech");

  const loginBox = document.getElementById("loginBox");
  const signupBox = document.getElementById("signupBox");
  const showSignup = document.getElementById("showSignup");
  const showLogin = document.getElementById("showLogin");

  const loginEmail = document.getElementById("loginEmail");
  const loginPassword = document.getElementById("loginPassword");
  const loginBtn = document.getElementById("loginBtn");
  const loginError = document.getElementById("loginError");

  const signupName = document.getElementById("signupName");
  const signupEmail = document.getElementById("signupEmail");
  const signupPassword = document.getElementById("signupPassword");
  const signupBtn = document.getElementById("signupBtn");
  const signupError = document.getElementById("signupError");

  function setMood(mood, message) {
    if (!mascot) return;
    mascot.classList.remove("idle", "sad", "happy", "checking");
    mascot.classList.add(mood);
    if (speech) speech.textContent = message;
  }

  // ---- Toggle between Login / Signup boxes ----
  if (showSignup) {
    showSignup.addEventListener("click", function (e) {
      e.preventDefault();
      loginBox.style.display = "none";
      signupBox.style.display = "block";
      setMood("idle", "Let's get you signed up!");
    });
  }

  if (showLogin) {
    showLogin.addEventListener("click", function (e) {
      e.preventDefault();
      signupBox.style.display = "none";
      loginBox.style.display = "block";
      setMood("idle", "Welcome back! Login here 👉");
    });
  }

  // ---- Field focus = idle pointing mood ----
  [loginEmail, loginPassword, signupEmail, signupPassword, signupName].forEach(function (field) {
    if (!field) return;
    field.addEventListener("focus", function () {
      setMood("idle", "Almost there, keep going!");
    });
  });

  // ---- LOGIN ----
  if (loginBtn) {
    loginBtn.addEventListener("click", async function () {
      loginError.style.display = "none";
      setMood("checking", "Checking... hang on ⏳");

      try {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: loginEmail.value.trim(),
            password: loginPassword.value,
          }),
        });
        const data = await res.json();

        if (!res.ok) {
          loginError.textContent = data.error || "Login failed";
          loginError.style.display = "block";
          setMood("sad", "Oops! Wrong email or password 😣");
          return;
        }

        setMood("happy", "Welcome! Redirecting...");
        window.location.href = "/dashboard";
      } catch (err) {
        loginError.textContent = "Something went wrong. Try again.";
        loginError.style.display = "block";
        setMood("sad", "Hmm, connection issue!");
      }
    });
  }

  // ---- SIGNUP ----
  if (signupBtn) {
    signupBtn.addEventListener("click", async function () {
      signupError.style.display = "none";
      setMood("checking", "Creating your account... ⏳");

      try {
        const res = await fetch("/api/auth/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            full_name: signupName.value.trim(),
            email: signupEmail.value.trim(),
            password: signupPassword.value,
          }),
        });
        const data = await res.json();

        if (!res.ok) {
          signupError.textContent = data.error || "Signup failed";
          signupError.style.display = "block";
          setMood("sad", "Oops! Something's not right 😣");
          return;
        }

        setMood("happy", "Account created! Redirecting...");
        window.location.href = "/dashboard";
      } catch (err) {
        signupError.textContent = "Something went wrong. Try again.";
        signupError.style.display = "block";
        setMood("sad", "Hmm, connection issue!");
      }
    });
  }
});