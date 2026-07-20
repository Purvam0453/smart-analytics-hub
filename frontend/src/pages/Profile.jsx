import "./Profile.css";


function Profile(){


  const username = localStorage.getItem("username") || "User";

  const email = localStorage.getItem("email") || "No email";



  return (


    <div className="profile-container">


      <div className="profile-banner"></div>



      <div className="profile-card">



        <div className="profile-image">

          {
            username
            .substring(0,2)
            .toUpperCase()
          }

        </div>




        <h1>
          {username}
        </h1>



        <p className="designation">

          AI Developer | Smart Analytics Hub

        </p>



        <p>

          {email}

        </p>





        <div className="profile-stats">



          <div className="stat-box">

            <h2>
              120
            </h2>

            <p>
              Resumes
            </p>

          </div>





          <div className="stat-box">

            <h2>
              45
            </h2>

            <p>
              Shortlisted
            </p>

          </div>





          <div className="stat-box">

            <h2>
              92%
            </h2>

            <p>
              Accuracy
            </p>

          </div>



        </div>







        <div className="section">


          <h3>
            About Me
          </h3>


          <p>

            Building AI powered resume screening systems
            using Machine Learning, React and FastAPI.

          </p>


        </div>







        <div className="section">


          <h3>
            Technical Skills
          </h3>



          <div className="tags">


            <span>React</span>

            <span>Python</span>

            <span>SQL</span>

            <span>FastAPI</span>

            <span>Machine Learning</span>

            <span>Azure</span>


          </div>


        </div>







        <button className="edit-btn">

          Edit Profile

        </button>





      </div>


    </div>


  );


}


export default Profile;