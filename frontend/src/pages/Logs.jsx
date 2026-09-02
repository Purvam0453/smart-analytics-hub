import { useState, useEffect } from "react";
import api from "../services/api";
import "./Logs.css";

function Logs() {
  const [logsData, setLogsData] = useState([
    {
      time: "10:30 AM",
      candidate: "Rahul Sharma",
      action: "Resume Uploaded",
      role: "Data Engineer",
      score: "92%",
      status: "Shortlisted"
    },
    {
      time: "10:45 AM",
      candidate: "Amit Patel",
      action: "AI Analysis Completed",
      role: "Frontend Developer",
      score: "78%",
      status: "Review"
    },
    {
      time: "11:00 AM",
      candidate: "Neha Shah",
      action: "Resume Prediction",
      role: "ML Engineer",
      score: "88%",
      status: "Shortlisted"
    },
    {
      time: "11:20 AM",
      candidate: "Vivek Mehta",
      action: "Resume Uploaded",
      role: "Data Analyst",
      score: "65%",
      status: "Rejected"
    }
  ]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.get("/logs/all");
        if (res.data?.logs && res.data.logs.length > 0) {
          const formatted = res.data.logs.map((l) => ({
            time: l.date_time ? l.date_time.split(" ")[1] || l.date_time : "Recent",
            candidate: l.username || "Guest",
            action: l.action || "Activity",
            role: l.details || "General",
            score: "N/A",
            status: "Completed"
          }));
          setLogsData(formatted);
        }
      } catch (err) {
        console.warn("Could not fetch server logs, using default view:", err);
      }
    };
    fetchLogs();
  }, []);

  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");



  const filteredLogs = logsData.filter((log)=>{


    const matchSearch =

      log.candidate
      .toLowerCase()
      .includes(search.toLowerCase())
      ||
      log.action
      .toLowerCase()
      .includes(search.toLowerCase());



    const matchFilter =

      filter==="All"
      ||
      log.status===filter;



    return matchSearch && matchFilter;


  });



  const exportCSV = ()=>{


    const csv = [

      [
        "Time",
        "Candidate",
        "Action",
        "Role",
        "Score",
        "Status"
      ],


      ...logsData.map(log=>[

        log.time,
        log.candidate,
        log.action,
        log.role,
        log.score,
        log.status

      ])

    ]

    .map(row=>row.join(","))
    .join("\n");



    const blob = new Blob([csv],{
      type:"text/csv"
    });


    const url = URL.createObjectURL(blob);


    const link = document.createElement("a");

    link.href=url;

    link.download="resume_logs.csv";

    link.click();


  };




  return (


    <div className="logs">


      <h1>
        Resume Screening Logs 📋
      </h1>


      <p className="subtitle">
        AI generated candidate analysis history
      </p>




      <div className="log-tools">


        <input

          type="text"

          placeholder="Search candidate or activity..."

          value={search}

          onChange={(e)=>setSearch(e.target.value)}

        />



        <select

          value={filter}

          onChange={(e)=>setFilter(e.target.value)}

        >

          <option>
            All
          </option>

          <option>
            Shortlisted
          </option>

          <option>
            Review
          </option>

          <option>
            Rejected
          </option>


        </select>



        <button onClick={exportCSV}>

          ⬇ Export CSV

        </button>



      </div>






      <div className="log-card">


        <table>


          <thead>

            <tr>

              <th>
                Time
              </th>

              <th>
                Candidate
              </th>

              <th>
                Activity
              </th>

              <th>
                Role
              </th>

              <th>
                AI Score
              </th>

              <th>
                Status
              </th>


            </tr>

          </thead>




          <tbody>


          {

            filteredLogs.map((log,index)=>(


              <tr key={index}>


                <td>
                  {log.time}
                </td>


                <td>
                  {log.candidate}
                </td>


                <td>
                  {log.action}
                </td>


                <td>
                  {log.role}
                </td>



                <td>

                  <span className="score">

                    {log.score}

                  </span>

                </td>



                <td>

                  <span

                    className={

                      log.status==="Shortlisted"

                      ?

                      "status success"

                      :

                      log.status==="Review"

                      ?

                      "status review"

                      :

                      "status rejected"

                    }

                  >

                    {log.status}

                  </span>


                </td>


              </tr>


            ))

          }



          </tbody>



        </table>



      </div>



    </div>


  );

}


export default Logs;