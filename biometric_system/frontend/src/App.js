import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {

  const [username, setUsername] = useState("");
  const [appName, setAppName] = useState("");
  const [pin, setPin] = useState("");

  const [fingerprint, setFingerprint] = useState("");
  const [iris, setIris] = useState("");

  const [password, setPassword] = useState("");

  const [mode, setMode] = useState("register");

  const [message, setMessage] = useState("");

  const [loading, setLoading] = useState(false);

  const [steps, setSteps] = useState([]);


  // ------------------------------------------------
  // TOAST
  // ------------------------------------------------

  const showMessage = (msg) => {

    setMessage(msg);

    setTimeout(() => {
      setMessage("");
    }, 5000);
  };


  // ------------------------------------------------
  // SWITCH MODE
  // ------------------------------------------------

  const switchMode = (newMode) => {

    setMode(newMode);

    setPassword("");

    setSteps([]);

    setMessage("");
  };


  // ------------------------------------------------
  // REGISTER
  // ------------------------------------------------

  const generate = async () => {

    if (
      !username ||
      !appName ||
      !fingerprint ||
      !iris
    ) {

      showMessage("Fill all required fields");

      return;
    }

    setLoading(true);

    setPassword("");

    setSteps([]);

    try {

      setSteps([
        " Loading fingerprint image",
        " Loading iris image",
        " Extracting random biometric patch",
        " Applying XOR biometric fusion",
        " Initializing quantum walk",
        " Generating quantum signature",
        " Storing latest signature",
        " Constructing password"
      ]);

      const res = await axios.post(
        "http://127.0.0.1:8000/generate",
        {
          username,
          app: appName.toLowerCase(),
          pin,
          fingerprint,
          iris
        }
      );

      setPassword(res.data.password);

      showMessage("New Password Generated");

    } catch (err) {

      console.log(err);

      showMessage("Generation Failed");
    }

    setLoading(false);
  };


  // ------------------------------------------------
  // LOGIN
  // ------------------------------------------------

  const login = async () => {

    if (
      !username ||
      !appName
    ) {

      showMessage("Fill all required fields");

      return;
    }

    setLoading(true);

    setPassword("");

    setSteps([]);

    try {

      setSteps([
        " Fetching latest stored signature",
        " Reconstructing password from signature",
        " Verifying credentials",
        " Login successful"
      ]);

      const res = await axios.post(
        "http://127.0.0.1:8000/login",
        {
          username,
          app: appName.toLowerCase(),
          pin,
          fingerprint,
          iris
        }
      );

      if (res.data.status === "success") {

        setPassword(res.data.password);

        showMessage(
          "Login Successful — Latest Password Retrieved"
        );

      } else {

        showMessage(res.data.message);
      }

    } catch (err) {

      console.log(err);

      showMessage("User not found");
    }

    setLoading(false);
  };


  // ------------------------------------------------
  // COPY PASSWORD
  // ------------------------------------------------

  const copyPassword = () => {

    navigator.clipboard.writeText(password);

    showMessage("Password Copied");
  };


  return (

    <div className="main">

      <div className="bg1"></div>
      <div className="bg2"></div>
      <div className="bg3"></div>

      <div className="glass-card">

        <h1>
          Quantum Biometric Password System
        </h1>

        <p className="subtitle">
          Quantum Walk Based Secure Authentication
        </p>

        {/* ---------------- TOGGLE ---------------- */}

        <div className="toggle">

          <button
            className={
              mode === "register"
              ? "active"
              : ""
            }
            onClick={() => switchMode("register")}
          >
            Register
          </button>

          <button
            className={
              mode === "login"
              ? "active"
              : ""
            }
            onClick={() => switchMode("login")}
          >
            Login
          </button>

        </div>


        {/* ---------------- INPUTS ---------------- */}

        <input
          placeholder="Username"
          value={username}
          onChange={(e) =>
            setUsername(e.target.value)
          }
        />

        <input
          placeholder="Application Name"
          value={appName}
          onChange={(e) =>
            setAppName(e.target.value)
          }
        />

        <input
          type="password"
          placeholder="PIN (optional)"
          value={pin}
          onChange={(e) =>
            setPin(e.target.value)
          }
        />


        {/* ---------------- BIOMETRICS ---------------- */}

        <div className="bio-section">

          <h3>
            Biometric Inputs
          </h3>

          <input
            placeholder="Fingerprint Image Path"
            value={fingerprint}
            onChange={(e) =>
              setFingerprint(e.target.value)
            }
          />

          <input
            placeholder="Iris Image Path"
            value={iris}
            onChange={(e) =>
              setIris(e.target.value)
            }
          />

        </div>


        {/* ---------------- BUTTON ---------------- */}

        {
          mode === "register"
          ? (
            <button
              className="primary"
              onClick={generate}
              disabled={loading}
            >
              {
                loading
                ? "Generating..."
                : "Generate Password"
              }
            </button>
          )
          : (
            <button
              className="primary"
              onClick={login}
              disabled={loading}
            >
              {
                loading
                ? "Logging In..."
                : "Login"
              }
            </button>
          )
        }


        {/* ---------------- PIPELINE ---------------- */}

        {
          steps.length > 0 && (

            <div className="pipeline">

              {
                steps.map((step, index) => (

                  <div
                    key={index}
                    className="step"
                  >
                    {step}
                  </div>

                ))
              }

            </div>
          )
        }


        {/* ---------------- PASSWORD ---------------- */}

        {
          password && (

            <div className="password-box">

              <h3>
                Generated Password
              </h3>

              <p>
                {password}
              </p>

              <button
                onClick={copyPassword}
              >
                Copy
              </button>

            </div>
          )
        }


        {/* ---------------- TOAST ---------------- */}

        {
          message && (
            <div className="toast">
              {message}
            </div>
          )
        }

      </div>
    </div>
  );
}

export default App;