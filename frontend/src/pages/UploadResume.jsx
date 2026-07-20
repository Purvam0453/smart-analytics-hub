import { useState } from "react";
import axios from "axios";
import "./UploadResume.css";


function UploadResume(){


const [file,setFile]=useState(null);
const [result,setResult]=useState(null);
const [loading,setLoading]=useState(false);
const [progress,setProgress]=useState(0);



const uploadResume=async()=>{


if(!file){

alert("Please select PDF file");
return;

}



const formData=new FormData();

formData.append("file",file);



try{


setLoading(true);


const response=await axios.post(

"http://127.0.0.1:8000/resume/upload",

formData,

{

headers:{
"Content-Type":"multipart/form-data"
},

onUploadProgress:(progressEvent)=>{

const percent=Math.round(

(progressEvent.loaded * 100) /
progressEvent.total

);

setProgress(percent);

}

}

);



setResult(response.data);


}

catch(error){

console.log(error);

alert("Upload failed");

}


finally{

setLoading(false);

}


};






const downloadReport=async()=>{


try{


const response=await axios.post(

"http://127.0.0.1:8000/resume/report",

result,

{
responseType:"blob"
}

);



const url=window.URL.createObjectURL(

new Blob([response.data])

);



const link=document.createElement("a");

link.href=url;

link.download="AI_Resume_Report.pdf";

link.click();


}

catch(error){

console.log(error);

alert("Report download failed");

}


};






return(

<div className="ai-upload-page">



<div className="hero">



<div className="intro">


<h1>
🤖 AI Resume Analyzer
</h1>



<p>

Smart AI system that analyzes your resume,
detects skills and predicts career opportunities.

</p>



<div className="features">


<div>
⚡ AI Skill Detection
</div>


<div>
🎯 Job Role Prediction
</div>


<div>
📊 Resume Scoring
</div>


</div>



</div>





<div className="upload-container">


<h2>
Upload Resume
</h2>




<div className="drop-box">


<input

type="file"

accept=".pdf"

onChange={(e)=>{

setFile(e.target.files[0]);
setProgress(0);

}}

/>



<div>


<div className="upload-icon">

📄

</div>



<h3>

Choose PDF Resume

</h3>



<p>

Click to browse PDF file

</p>



</div>



</div>





{

file &&

<div className="file-card">


<div className="file-icon">

📑

</div>



<div className="file-name">

{file.name}

</div>



</div>

}





{

loading &&

<div className="progress-box">


<div className="progress-bar">


<div

className="progress-fill"

style={{

width:`${progress}%`

}}

/>


</div>



<div className="progress-text">

Uploading {progress}%

</div>



</div>

}




<button

onClick={uploadResume}

className="ai-btn"

disabled={loading}

>


{

loading

?

"🤖 AI Analyzing..."

:

"Analyze Resume"

}



</button>



</div>



</div>







{

result &&


<div className="result-dashboard">



<h2>

📊 AI Analysis Result

</h2>





<div className="result-grid">



<div className="glass-card score-card">



<div className="score-circle">

{result.resume_score}%

</div>



<h3>

Resume Score

</h3>



</div>






<div className="glass-card">


<h3>

🎯 Predicted Role

</h3>


<h2>

{result.predicted_role}

</h2>


</div>



</div>







<div className="glass-card">


<h3>

🛠 Skills Detected

</h3>



<div className="skills">



{

result.skills.map((skill,index)=>(


<span key={index}>

{skill}

</span>


))

}



</div>



</div>







<div className="glass-card">


<h3>

💼 Job Recommendations

</h3>



{

result.recommendations.map((job,index)=>(


<div className="job-card" key={index}>


<strong>

#{job.rank} {job.job}

</strong>



<span>

{job.match}% Match

</span>



</div>


))

}



</div>







<button

className="download-btn"

onClick={downloadReport}

>

📄 Download AI Report

</button>






</div>


}



</div>


);


}



export default UploadResume;