import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import {
  FaUser,
  FaLock,
  FaEye,
  FaEyeSlash,
  FaRobot
} from "react-icons/fa";

import "./Login.css";


function Login(){

  const [showPassword,setShowPassword] = useState(false);

  const [email,setEmail] = useState("");
  const [password,setPassword] = useState("");

  const navigate = useNavigate();


  const handleLogin = async()=>{

    try{

      const response = await axios.post(
        "http://127.0.0.1:8000/auth/login",
        {
          email: email,
          password: password
        }
      );


      localStorage.setItem(
        "token",
        response.data.access_token
      );


      localStorage.setItem(
        "username",
        response.data.username
      );


      alert("Login Successful 🚀");


      navigate("/home");


    }
    catch(error){

      console.log(error);

      alert("Invalid Email or Password");

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