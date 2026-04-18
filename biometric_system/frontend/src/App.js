import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [username, setUsername] = useState("");
  const [appName, setAppName] = useState("");
  const [pin, setPin] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState("register");

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [steps, setSteps] = useState([]);

  // 🔔 Toast message
  const showMessage = (msg) => {
    setMessage(msg);
    setTimeout(() => setMessage(""), 4000);
  };

  // 🔄 Clear state when switching mode
  const switchMode = (newMode) => {
    setMode(newMode);
    setPassword("");
    setSteps([]);
    setMessage("");
  };

  // 🔐 REGISTER
  const generate = async () => {
    if (!username || !appName) {
      showMessage("⚠️ Fill all fields");
      return;
    }

    setLoading(true);
    setPassword("");
    setSteps([]);

    try {
      setSteps([
        "🔍 Reading biometric data",
        "⚛️ Running quantum walk",
        "🧬 Generating signature",
        "💾 Storing signature in database",
        "🔐 Creating password"
      ]);

      const res = await axios.post("http://127.0.0.1:8000/generate", {
        username,
        app: appName,
        pin,
      });

      setPassword(res.data.password);
      showMessage("✅ Password Generated");

    } catch {
      showMessage("❌ Error generating password");
    }

    setLoading(false);
  };

  // 🔓 LOGIN
  const login = async () => {
    if (!username || !appName) {
      showMessage("⚠️ Fill all fields");
      return;
    }

    setLoading(true);
    setPassword("");
    setSteps([]);

    try {
      setSteps([
        "🔎 Fetching stored signature",
        "🔁 Reconstructing password",
        "✅ Matching successful"
      ]);

      const res = await axios.post("http://127.0.0.1:8000/login", {
        username,
        app: appName,
        pin,
      });

      if (res.data.status === "success") {
        setPassword(res.data.password);
        showMessage("🔓 Login Successful");
      } else {
        showMessage(res.data.message);
      }

    } catch {
      showMessage("❌ User not found");
    }

    setLoading(false);
  };

  // 📋 Copy
  const copyPassword = () => {
    navigator.clipboard.writeText(password);
    showMessage("📋 Copied to clipboard");
  };

  return (
    <div className="main">
      <div className="glass-card">

        <h1>🔐 Quantum Vault</h1>

        {/* Toggle */}
        <div className="toggle">
          <button
            className={mode === "register" ? "active" : ""}
            onClick={() => switchMode("register")}
          >
            Register
          </button>
          <button
            className={mode === "login" ? "active" : ""}
            onClick={() => switchMode("login")}
          >
            Login
          </button>
        </div>

        {/* Inputs */}
        <input
          value={username}
          placeholder="Username"
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          value={appName}
          placeholder="App Name"
          onChange={(e) => setAppName(e.target.value)}
        />
        <input
          value={pin}
          placeholder="PIN (optional)"
          type="password"
          onChange={(e) => setPin(e.target.value)}
        />

        {/* Buttons */}
        {mode === "register" ? (
          <button className="primary" onClick={generate} disabled={loading}>
            {loading ? "Generating..." : "Generate Password"}
          </button>
        ) : (
          <button className="primary" onClick={login} disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        )}

        {/* Pipeline */}
        {steps.length > 0 && (
          <div className="pipeline">
            {steps.map((step, index) => (
              <div key={index} className="step">
                {step}
              </div>
            ))}
          </div>
        )}

        {/* Password */}
        {password && (
          <div className="password-box">
            <p>{password}</p>
            <button onClick={copyPassword}>Copy</button>
          </div>
        )}

        {/* Toast */}
        {message && <div className="toast">{message}</div>}

      </div>
    </div>
  );
}

export default App;