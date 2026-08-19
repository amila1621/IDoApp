import { useState, useEffect } from 'react';
import { fetchTasks, createTask, updateTask, deleteTask, enrichTask } from './api';

function App() {
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState(null);
  const [newTitle, setNewTitle] = useState('');

  useEffect(() => {
    fetchTasks()
      .then(setTasks)
      .catch(() => setError("Failed to fetch tasks"));
  }, []);


async function handleAdd(){
  const text = newTitle.trim();
  if (!text) return;

  try {
    const result = await enrichTask(text);
    setTasks([...tasks, result.task]);
    setNewTitle('');
  } catch {
    setError("Failed to add task");
  }
}


async function handleToggle(task){
  try{
    const updated = await updateTask(task.id, { done: !task.done });
    setTasks(tasks.map(t => t.id === task.id ? updated : t));

  } catch {
    setError("Failed to update task");
  }
}

async function handleDelete(task){
  try{
    await deleteTask(task.id);
    setTasks(tasks.filter(t => t.id !== task.id));
  } catch {
    setError("Failed to delete task");
  }
}


  return (
    <div>
      <h1>I Do Todo app</h1>
      {error && <p className="error">{error}</p>}

    <div className="task-input">
      <input
        type="text"
        placeholder="Add a new task"
        value={newTitle}
        onChange={(e) => setNewTitle(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <button onClick={handleAdd}>Add Task</button>
    </div>
     
      <h2>Tasks</h2>
       <ul className="task-list">
        {tasks.map(task => (
         <li
            key={task.id}
            className="tasks" >
            <input
              type="checkbox"
              checked={task.done}
              onChange={() => handleToggle(task)}
            />
            <span className={task.done ? "done" : ""} style={{ flex: 1 }}>
              {task.title}
              <small style={{ color: "#888", marginLeft: "0.5rem" }}>
                {task.category?.replace("_", " ")}
                {task.due_at && ` · ${new Date(task.due_at).toLocaleDateString()}`}
                {task.is_outdoor && " · outdoor"}
              </small>
            </span>
            <button onClick={() => handleDelete(task)}>Delete</button>


          </li>
        ))} 
      
      </ul>
      {tasks.length === 0 && !error && <p className="warning">No tasks available.</p>}
    </div>
  );
}

export default App;
