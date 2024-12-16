document.addEventListener("DOMContentLoaded", () => {

    // ========================== Save Button Logic ==========================
    // document.addEventListener("click", (e) => {
    //     if (e.target.classList.contains('save-task-btn')) {
    //         const taskContainer = e.target.closest('.task-container');
    //         const sprintCard = taskContainer.closest('.sprint-card');

    //         // Collecting Task Data
    //         const sprintId = sprintCard.getAttribute('data-sprint-id');
    //         const taskTitle = taskContainer.querySelector('.task-title-input').value;
    //         const dueDate = taskContainer.querySelector('.task-due-date-input').value;
    //         const status = taskContainer.querySelector('.task-status-input').value;

    //         // Collecting Selected Participants
    //         const selectedParticipants = Array.from(
    //             taskContainer.querySelectorAll('.selected-users-container .selected-user-tag')
    //         ).map(tag => tag.dataset.id);

    //         // Logging the Collected Data
    //         console.log("Task Data:");
    //         console.log("Sprint ID:", sprintId);
    //         console.log("Task Title:", taskTitle || "No title entered");
    //         console.log("Assigned Participants:", selectedParticipants.length > 0 ? selectedParticipants : "None");
    //         console.log("Due Date:", dueDate || "No due date set");
    //         console.log("Status:", status);

    //         // Validation before saving
    //         if (!taskTitle) {
    //             alert("Please enter the task title.");
    //             return;
    //         }
    //         if (selectedParticipants.length === 0) {
    //             alert("Please assign at least one participant to the task.");
    //             return;
    //         }
    //         if (!dueDate) {
    //             alert("Please set a valid due date.");
    //             return;
    //         }

    //         alert("Task data logged successfully. Check the console for details.");
    //     }
    // });


    // Function to save the task
    const saveTask = (url, taskData, csrfToken) => {
        fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken, // CSRF Token for Django security
                },
                body: JSON.stringify(taskData), // Convert data to JSON
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    return response.text().then(text => { throw new Error(text); });
                }
            })
            .then(data => {
                console.log("Response data:", data); // Debugging
                if (data.success) {
                    alert("Task saved successfully!");
                    window.location.reload(); // Optional: Reload to refresh data
                } else {
                    alert("Error saving task: " + data.error);
                }
            })
            .catch(error => {
                console.error("Error:", error);
            alert("An error occurred while saving the task: " + error.message);
        });
    };

    // Function to collect task data
    function collectTaskData(taskEntry) {
        const taskTitle = taskEntry.querySelector(".task-title-input").value;
        const dueDate = taskEntry.querySelector(".task-due-date-input").value;
        const status = taskEntry.querySelector(".task-status-input").value;
        const sprintId = taskEntry.closest(".sprint-card").dataset.sprintId;

        // Collect participants' IDs
        const participants = Array.from(
            taskEntry.querySelectorAll(".selected-user-tag")
        ).map(userTag => userTag.dataset.id);

        return {
            title: taskTitle,
            due_date: dueDate,
            status: status,
            sprint_id: sprintId,
            participants: participants
        };
    }

    // Event listener for the save button
    document.addEventListener("click", (e) => {
        if (e.target && e.target.classList.contains("save-task-btn")) {
            const saveButton = e.target;
            const taskEntry = saveButton.closest(".task-entry");

            // Collect Task Data
            const taskData = collectTaskData(taskEntry); // Pass the taskEntry

            // CSRF Token
            const csrfToken = getCSRFToken(); // Function to retrieve CSRF token

            // Validate Data Before Sending
            if (!taskData.title || !taskData.due_date) {
                alert("Task title and due date are required.");
                return;
            }

            // Save Task
            const url = "/save-task/"; // Endpoint for saving task
            saveTask(url, taskData, csrfToken);

            // Optional: Disable the button temporarily
            saveButton.disabled = true;
        }
    });


    // Function to retrieve CSRF Token from cookies
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

});    