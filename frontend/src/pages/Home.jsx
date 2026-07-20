import {
  FaRobot,
  FaFileAlt,
  FaChartLine,
  FaUpload,
  FaBrain,
  FaCheckCircle,
  FaUsers,
  FaStar,
  FaBolt
} from "react-icons/fa";

import { useNavigate } from "react-router-dom";

import "./Home.css";


function Home(){

const navigate = useNavigate();


return(

<div className="home">



{/* HERO SECTION */}

<div className="home-hero">


<div className="hero-icon">

<FaRobot/>

</div>



<h1>

AI Resume Screening

<br/>

<span>
Smart Analytics Hub
</span>

</h1>



<p>

Analyze resumes, predict job roles and discover the best candidates using Artificial Intelligence.

</p>




<button

className="home-btn"

onClick={()=>navigate("/upload-resume")}

>

<FaUpload/>

&nbsp;

Analyze Resume

</button>



</div>







{/* STATS */}

<div className="home-cards">


<div className="home-card">

<FaFileAlt className="card-icon"/>

<h2>
120+
</h2>

<p>
Resumes Processed
</p>

</div>




<div className="home-card">

<FaUsers className="card-icon"/>

<h2>
85+
</h2>

<p>
Candidates Evaluated
</p>

</div>





<div className="home-card">

<FaStar className="card-icon"/>

<h2>
92%
</h2>

<p>
Prediction Accuracy
</p>

</div>





<div className="home-card">

<FaBolt className="card-icon"/>

<h2>
AI
</h2>

<p>
Smart Matching
</p>

</div>



</div>








{/* FEATURES */}


<h2 className="section-title">

Powerful AI Features

</h2>




<div className="home-features">





<div className="feature-box">


<FaRobot className="big-icon"/>


<h3>

AI Resume Screening

</h3>


<p>

Machine learning models analyze candidate profiles and identify suitable job roles.

</p>


</div>







<div className="feature-box">


<FaFileAlt className="big-icon"/>


<h3>

Resume Intelligence

</h3>


<p>

Extract skills, education, experience and important candidate information.

</p>


</div>







<div className="feature-box">


<FaChartLine className="big-icon"/>


<h3>

Analytics Dashboard

</h3>


<p>

Visualize hiring insights and candidate performance reports.

</p>


</div>




</div>









{/* WORKFLOW */}



<div className="workflow-box">


<h2>

How It Works ⚡

</h2>




<div className="workflow">





<div>

<FaUpload/>

<span>
01
</span>

<p>
Upload Resume
</p>

</div>







<div>

<FaBrain/>

<span>
02
</span>

<p>
AI Processing
</p>

</div>







<div>

<FaCheckCircle/>

<span>
03
</span>

<p>
Role Prediction
</p>

</div>







<div>

📊

<span>
04
</span>

<p>
Generate Report
</p>

</div>






</div>



</div>





</div>

);

}


export default Home;