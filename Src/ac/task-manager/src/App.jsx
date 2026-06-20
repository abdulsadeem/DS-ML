import { useState, useEffect } from "react";
import "./App.css";

function App() {
const [tasks, setTasks] = useState(() => {
const saved = localStorage.getItem("tasks");
return saved ? JSON.parse(saved) : [];
});

const [taskText, setTaskText] = useState("");
const [priority, setPriority] = useState("Medium");
const [dueDate, setDueDate] = useState("");
const [search, setSearch] = useState("");

const [editingIndex, setEditingIndex] = useState(null);
const [editText, setEditText] = useState("");
const [editPriority, setEditPriority] = useState("Medium");
const [editDueDate, setEditDueDate] = useState("");

useEffect(() => {
localStorage.setItem("tasks", JSON.stringify(tasks));
}, [tasks]);

const addTask = () => {
if (!taskText.trim()) return;


const newTask = {
  text: taskText,
  priority,
  dueDate,
  completed: false,
  createdAt: new Date().toLocaleString(),
};

setTasks([...tasks, newTask]);

setTaskText("");
setPriority("Medium");
setDueDate("");



};

const deleteTask = (index) => {
setTasks(tasks.filter((_, i) => i !== index));
};

const toggleComplete = (index) => {
const updated = [...tasks];
updated[index].completed = !updated[index].completed;
setTasks(updated);
};

const editTask = (index) => {
setEditingIndex(index);
setEditText(tasks[index].text);
setEditPriority(tasks[index].priority);
setEditDueDate(tasks[index].dueDate);
};

const saveEdit = (index) => {
const updated = [...tasks];


updated[index].text = editText;
updated[index].priority = editPriority;
updated[index].dueDate = editDueDate;

setTasks(updated);
setEditingIndex(null);


};

const isOverdue = (date) => {
if (!date) return false;


const today = new Date();
const due = new Date(date);

today.setHours(0, 0, 0, 0);
due.setHours(0, 0, 0, 0);

return due < today;


};

const filteredTasks = tasks.filter((task) =>
task.text.toLowerCase().includes(search.toLowerCase())
);

const completedCount = tasks.filter(
(task) => task.completed
).length;

const pendingCount = tasks.length - completedCount;

const progress =
tasks.length === 0
? 0
: Math.round((completedCount / tasks.length) * 100);

return ( <div className="container"> <h1>📚 Student Task Planner</h1>


  <div className="dashboard">
    <div>Total: {tasks.length}</div>
    <div>Completed: {completedCount}</div>
    <div>Pending: {pendingCount}</div>
  </div>

  <div className="progress-container">
    <div
      className="progress-bar"
      style={{ width: `${progress}%` }}
    ></div>
  </div>

  <p>{progress}% Completed</p>

  <input
    type="text"
    placeholder="Search task..."
    value={search}
    onChange={(e) => setSearch(e.target.value)}
  />

  <div className="input-section">
    <input
      type="text"
      placeholder="Enter task..."
      value={taskText}
      onChange={(e) => setTaskText(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === "Enter") addTask();
      }}
    />

    <select
      value={priority}
      onChange={(e) => setPriority(e.target.value)}
    >
      <option>High</option>
      <option>Medium</option>
      <option>Low</option>
    </select>

    <input
      type="date"
      value={dueDate}
      onChange={(e) => setDueDate(e.target.value)}
    />
  </div>

  <ul>
    {filteredTasks.map((task, index) => (
      <li key={index}>
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => toggleComplete(index)}
        />

        <div className="task-info">
          {editingIndex === index ? (
            <>
              <input
                type="text"
                value={editText}
                onChange={(e) =>
                  setEditText(e.target.value)
                }
              />

              <select
                value={editPriority}
                onChange={(e) =>
                  setEditPriority(e.target.value)
                }
              >
                <option>High</option>
                <option>Medium</option>
                <option>Low</option>
              </select>

              <input
                type="date"
                value={editDueDate}
                onChange={(e) =>
                  setEditDueDate(e.target.value)
                }
              />

              <button
                onClick={() => saveEdit(index)}
              >
                Save
              </button>

              <button
                onClick={() =>
                  setEditingIndex(null)
                }
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <strong
                className={
                  task.completed
                    ? "completed-text"
                    : ""
                }
              >
                {task.text}
              </strong>

              <p>
                Priority:
                <span
                 className={(task.priority || "medium").toLowerCase()}
                >
                  {" "}
                  {task.priority || "Medium"}
                </span>
              </p>

              <p>
                Due: {task.dueDate || "Not Set"}
              </p>

              {isOverdue(task.dueDate) &&
                !task.completed && (
                  <p style={{ color: "red" }}>
                    ⚠️ Overdue
                  </p>
                )}

              <small>
                Created: {task.createdAt}
              </small>

              <div>
                <button
                  onClick={() =>
                    editTask(index)
                  }
                >
                  Edit
                </button>

                <button
                  onClick={() =>
                    deleteTask(index)
                  }
                >
                  Delete
                </button>
              </div>
            </>
          )}
        </div>
      </li>
    ))}
  </ul>
</div>

);
}

export default App;
