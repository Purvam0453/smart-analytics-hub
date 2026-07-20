import { useEffect, useState } from "react";

import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

import "./Dashboard.css";


function Dashboard(){


const [data,setData] = useState(null);
const [loginData,setLoginData] = useState([]);



useEffect(()=>{


fetch("http://127.0.0.1:8000/dashboard-stats")

.then(res=>res.json())

.then(result=>{

setData(result);

})

.catch(err=>console.log(err));





fetch("http://127.0.0.1:8000/login-stats")

.then(res=>res.json())

.then(result=>{


setLoginData(

result.login_trend || []

);


})

.catch(err=>console.log(err));



},[]);





if(!data){

return(

<div className="dashboard">

<h2>
Loading Dashboard...
</h2>

</div>

)

}





const roleData = Object.keys(
data.roles || {}
).map(role=>({

name:role,

value:data.roles[role]

}));






const skillData = Object.keys(
data.skills || {}
).map(skill=>({

name:skill,

value:data.skills[skill]

}));






const scoreData = data.score_analysis || [];





return(


<div className="dashboard">


<h1>
AI Resume Screening Dashboard 🤖
</h1>


<p className="subtitle">
Smart Analytics Hub - Resume Intelligence System
</p>





<div className="cards">


<div className="card">

<h2>
📄 {data.total_resumes}
</h2>

<p>
Total Resumes
</p>

</div>




<div className="card">

<h2>
🎯 {data.average_score}%
</h2>

<p>
Average Score
</p>

</div>




<div className="card">

<h2>
💼 {roleData[0]?.name || "N/A"}
</h2>

<p>
Top Role
</p>

</div>




<div className="card">

<h2>
🛠 {skillData.length}
</h2>

<p>
Skills Found
</p>

</div>


</div>








<div className="charts">



{/* Skill Chart */}

<div className="chart-box">

<h2>
Skill Analysis 📊
</h2>


<ResponsiveContainer width="100%" height={300}>


<BarChart data={skillData}>


<XAxis dataKey="name"/>

<YAxis/>

<Tooltip/>

<Bar dataKey="value"/>


</BarChart>


</ResponsiveContainer>


</div>






{/* Role Chart */}


<div className="chart-box">


<h2>
Job Role Prediction 🥧
</h2>


<ResponsiveContainer width="100%" height={300}>


<PieChart>


<Pie

data={roleData}

dataKey="value"

nameKey="name"

outerRadius={100}

label

>


{

roleData.map((item,index)=>(

<Cell key={index}/>

))

}


</Pie>


<Tooltip/>

<Legend/>


</PieChart>


</ResponsiveContainer>


</div>








{/* Score Chart */}


<div className="chart-box">


<h2>
Resume Score Analysis 📈
</h2>


<ResponsiveContainer width="100%" height={300}>


<BarChart data={scoreData}>


<XAxis dataKey="score"/>

<YAxis/>

<Tooltip/>


<Bar dataKey="count"/>


</BarChart>


</ResponsiveContainer>


</div>








{/* Login Chart */}


<div className="chart-box">


<h2>
User Login Trend 📈
</h2>



<ResponsiveContainer width="100%" height={300}>


<LineChart data={loginData}>


<XAxis dataKey="date"/>

<YAxis/>

<Tooltip/>

<Legend/>


<Line

type="monotone"

dataKey="count"

strokeWidth={3}

/>


</LineChart>


</ResponsiveContainer>



</div>





</div>






</div>


)


}


export default Dashboard;