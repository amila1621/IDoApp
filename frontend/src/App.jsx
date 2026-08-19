import { useState, useEffect } from "react";
import { fetchTasks, enrichTask, updateTask, deleteTask } from "./api";
import "./App.css";

// Folder display config: enum value → label + accent dot colour.
// Order here is the order folders appear on screen.
const FOLDERS = [
  ["health_fitness", "Health & Fitness", "#3FA796"],
  ["finance", "Finance", "#2F6FB0"],
  ["errands_shopping", "Errands & Shopping", "#E0A458"],
  ["work_career", "Work & Career", "#5B6EE1"],
  ["personal_selfcare", "Personal & Self-Care", "#4FB0C6"],
  ["family_relationships", "Family & Relationships", "#B26FB0"],
  ["home_maintenance", "Home Maintenance", "#8C7B68"],
  ["household_chores", "Household & Chores", "#6BA368"],
  ["learning_growth", "Learning & Growth", "#D98BA0"],
];

function App() {
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState(null);
  const [newTitle, setNewTitle] = useState("");

  useEffect(() => {
    fetchTasks()
      .then(setTasks)
      .catch(() => setError("Couldn't load tasks. Is the backend running?"));
  }, []);

  async function handleAdd() {
    const text = newTitle.trim();
    if (!text) return;
    try {
      await enrichTask(text);
      const fresh = await fetchTasks(); // re-fetch so weather is included
      setTasks(fresh);
      setNewTitle("");
    } catch {
      setError("Couldn't add that task.");
    }
  }

  async function handleToggle(task) {
    try {
      const updated = await updateTask(task.id, { done: !task.done });
      setTasks(tasks.map((t) => (t.id === task.id ? updated : t)));
    } catch {
      setError("Couldn't update that task.");
    }
  }

  async function handleDelete(task) {
    try {
      await deleteTask(task.id);
      setTasks(tasks.filter((t) => t.id !== task.id));
    } catch {
      setError("Couldn't delete that task.");
    }
  }

  return (
    <div className="app">
      <header className="header">
       
        <p className="eyebrow">Oulu · today</p> 
        <div className="title">
          <h1>I DO </h1>
          <p>Your Smart To DO app.</p>
        </div>
        {error && <p className="error">{error}</p>}
      </header>

      {tasks.length === 0 && !error && (
        <p className="empty">No tasks yet. Add one below to get started.</p>
      )}

      {FOLDERS.map(([value, label, colour]) => {
        const inFolder = tasks.filter((t) => t.category === value);
        if (inFolder.length === 0) return null;

        return (
          <section className="group" key={value}>
            <div className="group-head">
              <span className="dot" style={{ background: colour }} />
              <span className="group-title">{label}</span>
              <span className="group-count">{inFolder.length}</span>
            </div>

            {inFolder.map((task) => {
              const isRain = task.weather && task.weather.includes("rain");
              return (
                <div
                  className={
                    "card" +
                    (task.done ? " completed" : "") +
                    (isRain ? " rain" : "")
                  }
                  key={task.id}
                >
                  <input
                    type="checkbox"
                    className="check"
                    checked={task.done}
                    onChange={() => handleToggle(task)}
                  />
                  <div className="body">
                    <p className="title">{task.title}</p>
                    <div className="meta">
                      {task.due_at && (
                        <span className="chip date">
                          {new Date(task.due_at).toLocaleDateString(undefined, {
                            weekday: "short",
                            day: "numeric",
                            month: "short",
                          })}
                        </span>
                      )}
                      {task.duration_minutes && (
                        <span className="chip">
                          {task.duration_minutes} min
                        </span>
                      )}
                      {task.best_time && (
                        <span className="chip">{task.best_time}</span>
                      )}
                      {task.is_outdoor && <span className="chip">outdoor</span>}
                    </div>
                    {task.weather && (
                      <div className={"weather" + (isRain ? " warn" : "")}>
                        {isRain ? "☔ " : ""}
                        {task.weather}
                      </div>
                    )}
                  </div>
                  <button className="del" onClick={() => handleDelete(task)}>
                    ✕
                  </button>
                </div>
              );
            })}
          </section>
        );
      })}

      <div className="addtask_btn">
        <div className="addtask_btn-inner">
          <input
            type="text"
            placeholder="What you need to do..."
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAdd()}
          />
          <button onClick={handleAdd}>Add</button>
        </div>
        
      </div>
    </div>
  );
}

export default App;
