import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import "./Login.css";


function Register(){

  const [username,setUsername] = useState("");
  const [email,setEmail] = useState("");
  const [password,setPassword] = useState("");

  const navigate = useNavigate();



  const handleRegister = async (e)=>{

    e.preventDefault();


    try{


      const response = await axios.post(

        "http://127.0.0.1:8000/auth/register",

        {
          username: username,
          email: email,
          password: password
        }

      );


      console.log(response.data);


      alert("Registration Successful 🚀");


      navigate("/");


    }

    catch(error){


      console.log(
        error.response?.data || error.message
      );


      alert("Registration Failed");


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