import { Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Form from "./pages/Form";
import Logs from "./pages/Logs.jsx";
import Profile from "./pages/Profile";
import UploadResume from "./pages/UploadResume";

import Sidebar from "./components/layouts/Sidebar";

import "./App.css";


function Layout({ children }) {

  return (

    <div className="layout">

      <Sidebar />

      <main className="main-content">
        {children}
      </main>

    </div>

  );

}



function App(){

  return(

    <Routes>


      <Route path="/" element={<Login />} />


      <Route path="/register" element={<Register />} />



      <Route
        path="/home"
        element={
          <Layout>
            <Home />
          </Layout>
        }
      />



      <Route
        path="/dashboard"
        element={
          <Layout>
            <Dashboard />
          </Layout>
        }
      />



      <Route
        path="/upload-resume"
        element={
          <Layout>
            <UploadResume />
          </Layout>
        }
      />



      <Route
        path="/form"
        element={
          <Layout>
            <Form />
          </Layout>
        }
      />



      <Route
        path="/logs"
        element={
          <Layout>
            <Logs />
          </Layout>
        }
      />



      <Route
        path="/profile"
        element={
          <Layout>
            <Profile />
          </Layout>
        }
      />


    </Routes>

  );

}


export default App;