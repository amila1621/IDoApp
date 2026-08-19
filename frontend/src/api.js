

const BASE_URL = "http://127.0.0.1:8000" 


export async function fetchTasks(){
    const res = await fetch(`${BASE_URL}/tasks`);
    if (!res.ok) throw new Error("Failed to fetch tasks");
    return await res.json();
}



export async function updateTask(id, task){
    const res = await fetch(`${BASE_URL}/tasks/${id}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(task)
    });
    if (!res.ok) throw new Error("Failed to update task");
    return await res.json();
}


export async function deleteTask(id){
    const res = await fetch(`${BASE_URL}/tasks/${id}`, {
        method: "DELETE"
    });
    if (!res.ok) throw new Error("Failed to delete task");
}


export async function enrichTask(text){
    const res = await fetch(`${BASE_URL}/tasks/enrich`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error("Failed to enrich task");
    return await res.json();
}
