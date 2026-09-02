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
import api from "../services/api";
import "./Dashboard.css";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"];

function Dashboard() {
  const [data, setData] = useState(null);
  const [loginData, setLoginData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const [statsRes, loginRes] = await Promise.all([
          api.get("/dashboard-stats"),
          api.get("/login-stats")
        ]);

        setData(statsRes.data);
        setLoginData(loginRes.data?.login_trend || []);
      } catch (err) {
        console.error("Failed to load dashboard data:", err);
        setError("Unable to connect to backend server.");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);





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


                  {roleData.map((item, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}


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