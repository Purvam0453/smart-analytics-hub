import { NavLink, useNavigate } from "react-router-dom";

import {
  FaHome,
  FaChartBar,
  FaFileUpload,
  FaHistory,
  FaUser,
  FaSignOutAlt,
  FaRobot
} from "react-icons/fa";

import "./Sidebar.css";


function Sidebar() {


  const navigate = useNavigate();



  const logoutHandler = () => {


    localStorage.removeItem("token");

    localStorage.removeItem("user");


    navigate("/");


  };



  const menuClass = ({isActive}) =>

    isActive 
    ? "menu-item active"
    : "menu-item";



  return (


    <aside className="sidebar">



      <div className="logo-section">


        <div className="logo-icon">

          <FaRobot />

        </div>



        <div className="logo-text">

          Smart

          <br/>

          <span>
            Analytics Hub
          </span>


        </div>


      </div>





      <nav className="menu">



        <NavLink 
          to="/home"
          className={menuClass}
        >

          <FaHome/>

          <span>
            Home
          </span>


        </NavLink>





        <NavLink 
          to="/dashboard"
          className={menuClass}
        >

          <FaChartBar/>

          <span>
            Dashboard
          </span>


        </NavLink>





        <NavLink 
          to="/upload-resume"
          className={menuClass}
        >

          <FaFileUpload/>

          <span>
            Upload Resume
          </span>


        </NavLink>





        <NavLink 
          to="/logs"
          className={menuClass}
        >

          <FaHistory/>

          <span>
            Logs
          </span>


        </NavLink>





        <NavLink 
          to="/profile"
          className={menuClass}
        >

          <FaUser/>

          <span>
            Profile
          </span>


        </NavLink>



      </nav>






      <div className="logout">


        <button onClick={logoutHandler}>


          <FaSignOutAlt/>


          <span>
            Logout
          </span>


        </button>


      </div>



    </aside>


  );

}


export default Sidebar;