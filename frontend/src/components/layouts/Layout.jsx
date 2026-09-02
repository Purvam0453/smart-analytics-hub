import Sidebar from "./Sidebar";
import Header from "./Header";
import "./Layout.css";

function Layout({ children }) {
  return (
    <div className="app-layout-root">
      <Sidebar />
      <div className="app-main-wrapper">
        <Header />
        <main className="app-content-container">
          {children}
        </main>
      </div>
    </div>
  );
}

export default Layout;
