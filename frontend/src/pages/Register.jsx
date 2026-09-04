import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../services/auth";

import "./Login.css";

function Register(){
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMessage("");

    if (!username || !email || !password) {
      setErrorMessage("Please fill in all registration fields.");
      return;
    }

    try {
      setLoading(true);
      await registerUser(username, email, password);
      navigate("/");
    } catch (error) {
      console.error("Registration error:", error);
      const msg =
        error.response?.data?.detail ||
        (error.code === "ERR_NETWORK" || error.message?.includes("Network Error")
          ? "Cannot connect to the backend server. Please check the backend URL and that it is running."
          : "Registration Failed. Please try again.");
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };



  return(

    <div className="login-page">


      <div className="login-card">


        <h1>
          Create Account
        </h1>


        <p>
          Smart Analytics Hub
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

        <form onSubmit={handleRegister}>


          <div className="input-box">

            <input

              type="text"

              placeholder="Username"

              value={username}

              onChange={(e)=>setUsername(e.target.value)}

            />

          </div>



          <div className="input-box">

            <input

              type="email"

              placeholder="Email"

              value={email}

              onChange={(e)=>setEmail(e.target.value)}

            />

          </div>




          <div className="input-box">

            <input

              type="password"

              placeholder="Password"

              value={password}

              onChange={(e)=>setPassword(e.target.value)}

            />

          </div>




          <button

            type="submit"

            className="login-btn"

          >

            Register

          </button>



        </form>


      </div>


    </div>


  );

}


export default Register;