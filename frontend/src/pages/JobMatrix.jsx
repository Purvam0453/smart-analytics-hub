import { useState } from "react";
import { Briefcase, CheckCircle2, Star, Search, Filter } from "lucide-react";
import "./JobMatrix.css";

const BENCHMARK_ROLES = [
  {
    role: "Data Scientist",
    category: "AI & Data",
    description: "Build predictive models, machine learning algorithms, and extract insights from enterprise datasets.",
    coreSkills: ["Python", "Machine Learning", "Pandas", "NumPy", "SQL", "Scikit-Learn"],
    goodToHave: ["Deep Learning", "TensorFlow", "Statistics", "Data Visualization"]
  },
  {
    role: "AI / ML Engineer",
    category: "AI & Data",
    description: "Design, develop, and deploy production deep learning models and NLP/vision systems.",
    coreSkills: ["Python", "PyTorch", "TensorFlow", "Machine Learning", "NLP", "Computer Vision"],
    goodToHave: ["Docker", "Kubernetes", "FastAPI", "MLOps"]
  },
  {
    role: "Full Stack Developer",
    category: "Software Engineering",
    description: "Build end-to-end web applications combining React frontends with scalable APIs and databases.",
    coreSkills: ["JavaScript", "TypeScript", "React", "Node.js", "Python", "SQL"],
    goodToHave: ["Docker", "Tailwind", "Git", "REST APIs"]
  },
  {
    role: "DevOps & Cloud Engineer",
    category: "Cloud & Infrastructure",
    description: "Automate CI/CD pipelines, orchestrate containerized workloads, and manage cloud infrastructure.",
    coreSkills: ["AWS", "Azure", "Docker", "Kubernetes", "CI/CD", "Linux"],
    goodToHave: ["Terraform", "GCP", "Git", "Prometheus"]
  },
  {
    role: "Data Engineer",
    category: "AI & Data",
    description: "Architect and maintain large-scale ETL pipelines, data lakes, and distributed data warehouses.",
    coreSkills: ["Python", "SQL", "PySpark", "Databricks", "Azure", "AWS"],
    goodToHave: ["Hadoop", "ETL", "Kafka", "Data Modeling"]
  },
  {
    role: "Backend Developer",
    category: "Software Engineering",
    description: "Develop robust RESTful microservices, optimize database schemas, and manage server logic.",
    coreSkills: ["Python", "FastAPI", "Django", "PostgreSQL", "MongoDB", "REST API"],
    goodToHave: ["Redis", "Docker", "Microservices", "Security"]
  }
];

function JobMatrix() {
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  const categories = ["All", "AI & Data", "Software Engineering", "Cloud & Infrastructure"];

  const filteredRoles = BENCHMARK_ROLES.filter((item) => {
    const matchSearch =
      item.role.toLowerCase().includes(search.toLowerCase()) ||
      item.coreSkills.some((s) => s.toLowerCase().includes(search.toLowerCase()));
    const matchCat = selectedCategory === "All" || item.category === selectedCategory;
    return matchSearch && matchCat;
  });

  return (
    <div className="job-matrix-page">
      <div className="matrix-header">
        <div>
          <span className="badge badge-cyan">Role Intelligence</span>
          <h1 className="matrix-title">Industry Role Skill Matrix</h1>
          <p className="matrix-subtitle">
            Explore standard technical benchmarks used by the ML engine to evaluate candidate qualifications.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="matrix-controls glass-panel">
        <div className="search-input-group">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search roles or skills (e.g. Python, Docker, React)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="matrix-search-field"
          />
        </div>

        <div className="category-tabs">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`cat-tab-btn ${selectedCategory === cat ? "cat-tab-active" : ""}`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Role Cards Grid */}
      <div className="role-cards-grid">
        {filteredRoles.map((role, idx) => (
          <div key={idx} className="glass-panel role-benchmark-card">
            <div className="role-card-top">
              <div className="role-icon-box">
                <Briefcase size={20} className="text-cyan" />
              </div>
              <span className="badge badge-indigo">{role.category}</span>
            </div>

            <h3 className="role-title">{role.role}</h3>
            <p className="role-description">{role.description}</p>

            <div className="skills-section-group">
              <div className="skills-label">
                <CheckCircle2 size={14} className="text-emerald" />
                <span>Must-Have Core Skills</span>
              </div>
              <div className="skills-pills-row">
                {role.coreSkills.map((s, sIdx) => (
                  <span key={sIdx} className="skill-tag core-skill">
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div className="skills-section-group">
              <div className="skills-label">
                <Star size={14} className="text-amber" />
                <span>High-Value Recommended</span>
              </div>
              <div className="skills-pills-row">
                {role.goodToHave.map((s, sIdx) => (
                  <span key={sIdx} className="skill-tag good-skill">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default JobMatrix;
