import { useState, useEffect } from "react";
import { fetchTasks, enrichTask, updateTask, deleteTask } from "./api";
import "./App.css";

// Folder display config: enum value → label + accent dot colour.
// Order here is the order folders appear on screen.
const FOLDERS = [
  ["health_fitness", "Health & Fitness", "#3FA796"],
  ["finance", "Finance", "#2F6FB0"],
  ["shopping", "Errands & Shopping", "#E0A458"],
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
  const [showVoicePopup, setShowVoicePopup] = useState(false);

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
      await updateTask(task.id, { done: !task.done });
      setTasks(await fetchTasks());
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
                    {task.priority && (
                      <span className={"priority priority-" + task.priority}>
                        {task.priority}
                      </span>
                    )}
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

                    {task.steps && task.steps.length > 0 && (
                      <ul className="steps">
                        {task.steps.map((step, i) => (
                          <li key={i}>{step}</li>
                        ))}
                      </ul>
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
          <button className="mic-btn" onClick={() => setShowVoicePopup(true)}>
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          </button>
        </div>
      </div>

      {showVoicePopup && (
        <div
          className="voice-popup-overlay"
          onClick={() => setShowVoicePopup(false)}
        >
          <div className="voice-popup" onClick={(e) => e.stopPropagation()}>
            <button
              className="popup-close"
              onClick={() => setShowVoicePopup(false)}
            >
              ✕
            </button>
            <div className="popup-content">
              <div className="popup-emoji">😊</div>
              <h2>Hah!! Gotch You</h2>
              <p>
                This is not working yet.I did not have time to add it to it even
                with Claude help.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
