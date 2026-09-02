import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/auth";

import {
  FaUser,
  FaLock,
  FaEye,
  FaEyeSlash,
  FaRobot
} from "react-icons/fa";

import "./Login.css";

function Login(){
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    setErrorMessage("");

    if (!email || !password) {
      setErrorMessage("Please enter both email and password.");
      return;
    }

    try {
      setLoading(true);
      await loginUser(email, password);
      navigate("/home");
    } catch (error) {
      console.error("Login error:", error);
      const msg =
        error.response?.data?.detail ||
        (error.code === "ERR_NETWORK" || error.message?.includes("Network Error")
          ? "Cannot connect to backend server. Please verify the backend is running on http://127.0.0.1:8000."
          : "Invalid Email or Password");
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };


  return(

    <div className="login-page">


      <div className="login-card">


        <div className="logo">
          <FaRobot/>
        </div>


        <h1>
          Smart Analytics Hub
        </h1>


        <p>
          AI Resume Screening & Job Prediction System
        </p>

        {errorMessage && (
          <div
            style={{
              backgroundColor: "#fee2e2",
              color: "#b91c1c",
              padding: "10px 14px",
              borderRadius: "8px",
              marginBottom: "15px",
              fontSize: "14px",
              fontWeight: "500",
            }}
          >
            ⚠️ {errorMessage}
          </div>
        )}

        <div className="input-box">

          <FaUser/>

          <input
            type="email"
            placeholder="Enter Email"
            value={email}
            onChange={(e)=>setEmail(e.target.value)}
          />

        </div>




        <div className="input-box">

          <FaLock/>

          <input
            type={showPassword ? "text":"password"}
            placeholder="Enter Password"
            value={password}
            onChange={(e)=>setPassword(e.target.value)}
          />


          <span
            onClick={() =>
              setShowPassword(!showPassword)
            }
          >

          {
            showPassword
            ?
            <FaEyeSlash/>
            :
            <FaEye/>
          }

          </span>


        </div>




        <button
          className="login-btn"
          onClick={handleLogin}
        >

          Login

        </button>



        <p
          onClick={()=>navigate("/register")}
          style={{
            cursor:"pointer",
            marginTop:"15px"
          }}
        >
          Don't have an account? Register
        </p>




        <div className="bottom-text">

          AI Powered Analytics Platform

        </div>


      </div>


    </div>

  );

}


export default Login;