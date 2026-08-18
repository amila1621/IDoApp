import { useState, useEffect } from 'react';
import { fetchTasks } from './api';

function App() {
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTasks()
      .then(setTasks)
      .catch(() => setError("Failed to fetch tasks"));
  }, []);

  return (
    <div>
      <h1>I D Todo app</h1>
      {error && <p className="error">{error}</p>}
      <ul className="task-list">
        {tasks.map(task => (
          <li key={task.id}>{task.title}</li>
        ))}
      </ul>
      {tasks.length === 0 && !error && <p className="warning">No tasks available.</p>}
    </div>
  );
}

export default App;
