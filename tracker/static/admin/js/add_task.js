document.addEventListener("DOMContentLoaded", () => {

    // ========================== Utility Function to Parse Sprint Date ==========================
    function parseSprintDate(dateStr) {
        const parsedDate = new Date(dateStr);
        if (isNaN(parsedDate)) {
            console.error("Invalid sprint end date format:", dateStr);
            return null;
        }
        return parsedDate.toISOString().split('T')[0]; // Converts to YYYY-MM-DD
    }

    // ========================== Due Date Validation ==========================
    function validateDueDate(dueDateInput, sprintEndDate) {
        const selectedDate = new Date(dueDateInput.value);
        const currentDate = new Date();
        currentDate.setHours(0, 0, 0, 0); // Remove time for comparison

        const sprintEnd = new Date(sprintEndDate);
        sprintEnd.setHours(0, 0, 0, 0);

        // Check if the date is invalid
        if (selectedDate < currentDate) {
            alert("The due date cannot be earlier than today's date.");
            dueDateInput.value = ''; // Clear invalid input
        } else if (selectedDate > sprintEnd) {
            alert("The due date cannot be later than the sprint's end date.");
            dueDateInput.value = ''; // Clear invalid input
        }
    }

    // Dynamically set the min and max attributes for the due date field
    document.addEventListener("focusin", (e) => {
        if (e.target.classList.contains('task-due-date-input')) {
            const dueDateInput = e.target;
            const taskContainer = dueDateInput.closest('.task-container');
            const sprintCard = taskContainer.closest('.sprint-card');

            // Get the sprint's end date from the sprint card
            const sprintEndDateStr = sprintCard.getAttribute('data-sprint-end');
            const sprintEndDate = parseSprintDate(sprintEndDateStr); // Convert to YYYY-MM-DD format

            if (sprintEndDate) {
                const currentDate = new Date().toISOString().split('T')[0]; // Today
                dueDateInput.setAttribute('min', currentDate); // Min is today
                dueDateInput.setAttribute('max', sprintEndDate); // Max is sprint end date
            } else {
                console.error("Could not parse sprint end date:", sprintEndDateStr);
            }
        }
    });

    // Validate when the due date is changed
    document.addEventListener("change", (e) => {
        if (e.target.classList.contains('task-due-date-input')) {
            const dueDateInput = e.target;
            const taskContainer = dueDateInput.closest('.task-container');
            const sprintCard = taskContainer.closest('.sprint-card');

            const sprintEndDateStr = sprintCard.getAttribute('data-sprint-end');
            const sprintEndDate = parseSprintDate(sprintEndDateStr);

            if (sprintEndDate) {
                validateDueDate(dueDateInput, sprintEndDate);
            }
        }
    });
    // ========================== Participant Assignment Logic ==========================
    function filterUsers(query) {
        return window.taskOptions.filter(user =>
            user.full_name.toLowerCase().includes(query.toLowerCase()) || 
            user.username.toLowerCase().includes(query.toLowerCase())
        );
    }

    function displaySuggestions(suggestions, suggestionsContainer) {
        suggestionsContainer.innerHTML = ''; // Clear previous suggestions
        suggestionsContainer.style.display = 'none'; // Hide initially

        if (suggestions.length === 0) {
            const noUsersOption = document.createElement("option");
            noUsersOption.disabled = true;
            noUsersOption.textContent = 'No users found';
            suggestionsContainer.appendChild(noUsersOption);
        } else {
            suggestions.forEach(user => {
                const option = document.createElement("option");
                option.value = user.id;
                option.textContent = `${user.full_name}`;
                suggestionsContainer.appendChild(option);
            });
        }
        suggestionsContainer.style.display = 'block'; // Show dropdown
    }

    function selectUser(user, suggestionsContainer) {
        const selectedUsersContainer = suggestionsContainer.closest('.task-detail-container').querySelector('.selected-users-container');
        const inputField = suggestionsContainer.closest('.task-detail-container').querySelector('.task-assign-input');

        // Prevent adding duplicate users
        if (Array.from(selectedUsersContainer.children).some(tag => tag.dataset.id === user.id.toString())) {
            return;
        }

        // Create a tag for the selected user
        const userTag = document.createElement("span");
        userTag.classList.add("selected-user-tag");
        userTag.dataset.id = user.id;
        userTag.textContent = `${user.full_name}`;

        // Add remove button
        const removeBtn = document.createElement("button");
        removeBtn.textContent = "x";
        removeBtn.classList.add("remove-user-btn");
        removeBtn.addEventListener("click", () => {
            selectedUsersContainer.removeChild(userTag);
            toggleSaveButton(suggestionsContainer.closest('.task-container'));
        });

        userTag.appendChild(removeBtn);
        selectedUsersContainer.appendChild(userTag);

        // Clear input and hide suggestions
        inputField.value = '';
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.style.display = 'none';

        toggleSaveButton(suggestionsContainer.closest('.task-container'));
    }

    document.addEventListener("input", (e) => {
        if (e.target.classList.contains('task-assign-input')) {
            const inputField = e.target;
            const suggestionsContainer = inputField.closest('.task-detail-container').querySelector('#suggestions');
            const query = inputField.value.trim();
            if (query.length > 0) {
                const filteredUsers = filterUsers(query);
                displaySuggestions(filteredUsers, suggestionsContainer);
            } else {
                suggestionsContainer.style.display = 'none';
            }
        }
    });

    document.addEventListener("change", (e) => {
        if (e.target.id === "suggestions") {
            const selectedOption = e.target.options[e.target.selectedIndex];
            const selectedUser = window.taskOptions.find(user => user.id == selectedOption.value);
            if (selectedUser) {
                selectUser(selectedUser, e.target);
            }
        }
    });

    // ========================== Save Button Validation Logic ==========================
    const isTaskValid = (taskContainer) => {
        const titleInput = taskContainer.querySelector('.task-title-input');
        const dueDateInput = taskContainer.querySelector('.task-due-date-input');
        const statusInput = taskContainer.querySelector('.task-status-input');
        const participantContainer = taskContainer.querySelector('.selected-users-container');

        return titleInput.value.trim() &&
               dueDateInput.value &&
               statusInput.value &&
               participantContainer.children.length > 0;
    };

    const toggleSaveButton = (taskContainer) => {
        const saveButton = taskContainer.querySelector('.save-task-btn');
        saveButton.disabled = !isTaskValid(taskContainer);
    };

    document.addEventListener("input", (e) => {
        const taskContainer = e.target.closest('.task-container');
        if (taskContainer) toggleSaveButton(taskContainer);
    });

    document.addEventListener("click", (e) => {
        if (e.target.classList.contains("remove-user-btn")) {
            const taskContainer = e.target.closest('.task-container');
            toggleSaveButton(taskContainer);
        }
    });

    // ========================== Add Task Logic ==========================
    const createTaskContainer = (sprintId, taskCount) => {
        const taskContainer = document.createElement('div');
        taskContainer.classList.add('task-container');
        taskContainer.innerHTML = `
            <div class="task-entry task-row" data-task-id="${sprintId}-task-${taskCount}">
                <div class="form-group">
                    <label for="task-title-${sprintId}-${taskCount}">Task&nbsp;Title</label>
                    <input type="text" class="task-input task-title-input" id="task-title-${sprintId}-${taskCount}" placeholder="Enter task title" required>
                </div>

                <div class="task-detail-container">
                    <div class="form-group">
                        <div class="task-assign-wrapper">
                            <div class="selected-users-container"></div>
                            <input type="text" class="task-assign-input" placeholder="Search for participants" autocomplete="off" />
                            <select id="suggestions" class="suggestions-container" size="5" style="display:none;"></select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Due Date:</label>
                        <input type="date" class="task-due-date-input" required>
                    </div>
                    <div class="form-group">
                        <label>Status:</label>
                        <select class="task-status task-status-input">
                            <option value="to-do">To-Do</option>
                            <option value="in-progress">In Progress</option>
                            <option value="blocked">Blocked</option>
                            <option value="completed">Completed</option>
                        </select>
                    </div>
                    <div class="form-group task-actions">
                        <button type="button" class="save-task-btn" disabled>Save</button>
                        <button type="button" class="delete-task-btn"><i class="fa fa-trash"></i></button>
                    </div>
                </div>
            </div>
        `;
        return taskContainer;
    };

    document.querySelector(".sprint-cards").addEventListener("click", (event) => {
        const addTaskBtn = event.target.closest(".sprint-card-add-task");
        if (addTaskBtn) {
            const sprintCard = addTaskBtn.closest(".sprint-card");
            const sprintId = sprintCard.getAttribute("data-sprint-id");
            const tasksSectionContainer = sprintCard.querySelector(".tasks-section-container") || (() => {
                const container = document.createElement("div");
                container.classList.add("tasks-section-container");
                sprintCard.appendChild(container);
                return container;
            })();

            const taskCount = tasksSectionContainer.childElementCount + 1;
            const newTaskContainer = createTaskContainer(sprintId, taskCount);
            tasksSectionContainer.appendChild(newTaskContainer);
            newTaskContainer.scrollIntoView({ behavior: "smooth" });
        }
    });
});
