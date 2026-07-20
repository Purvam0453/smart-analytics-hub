import {
  FaBell,
  FaUserCircle
} from "react-icons/fa";

import "./Navbar.css";


function Navbar() {


  return (

    <nav className="navbar">


      <div className="logo">

        Smart Analytics Hub

      </div>





      <div className="nav-right">


        <div className="notification">

          <FaBell/>

        </div>





        <div className="profile">


          <div className="avatar">

            <FaUserCircle/>

          </div>



          <div>

            <h4>
              Purvam
            </h4>

            <small>
              Admin
            </small>

          </div>



        </div>



      </div>



    </nav>

  );

}


export default Navbar;