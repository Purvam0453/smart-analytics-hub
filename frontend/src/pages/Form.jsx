
import { useState } from "react";
import axios from "axios";
import "./Form.css";


function Form() {

  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);



  const uploadResume = async () => {

    if (!file) {

      setMessage("Please select a resume first!");

      return;
    }



    const formData = new FormData();

    formData.append(
      "file",
      file
    );



    try {

      setLoading(true);

      setMessage("Uploading resume...");

      setResult(null);



      const response = await axios.post(

        "http://127.0.0.1:8000/upload-resume",

        formData,

        {
          headers: {
            "Content-Type": "multipart/form-data"
          }
        }

      );



      setMessage(
        "✅ " + response.data.message
      );


      setResult(
        response.data.analysis
      );



    } catch(error) {

      console.log(error);

      setMessage(
        "❌ Upload failed"
      );

    }


    finally {

      setLoading(false);

    }

  };





  return (

    <div className="upload-page">


      <h1>
        Upload Resume 📄
      </h1>


      <p>
        Upload candidate resume for AI based screening and job role prediction.
      </p>




      <div className="upload-box">


        <h2>
          Select Resume
        </h2>



        <input

          type="file"

          accept=".pdf"

          onChange={(e)=>
            setFile(e.target.files[0])
          }

        />



        {
          file &&

          <p className="file-name">

            Selected: {file.name}

          </p>
        }




        <button onClick={uploadResume}>

          {
            loading
            ?
            "Analyzing..."
            :
            "Analyze Resume 🤖"
          }

        </button>




        {
          message &&

          <p>
            {message}
          </p>
        }




        {
          result && (

            <div className="analysis-result">


              <h2>
                AI Analysis Result 🤖
              </h2>



              <h3>
                🎯 Role:
                {" "}
                {result.predicted_role}
              </h3>



              <h3>
                📊 Resume Score:
                {" "}
                {result.resume_score}%
              </h3>



              <h3>
                🛠 Skills:
              </h3>


              <p>

                {
                  result.skills.length > 0
                  ?
                  result.skills.join(", ")
                  :
                  "No skills detected"
                }

              </p>



            </div>

          )
        }



      </div>





      <div className="features">


        <div>
          <h3>🔍 Skill Extraction</h3>
          <p>
            Find technical skills from resume.
          </p>
        </div>


        <div>
          <h3>🎯 Job Prediction</h3>
          <p>
            Predict suitable job role.
          </p>
        </div>


        <div>
          <h3>📊 Resume Score</h3>
          <p>
            Generate candidate score.
          </p>
        </div>


      </div>


    </div>

  );

}


export default Form;