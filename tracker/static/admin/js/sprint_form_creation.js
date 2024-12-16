document.addEventListener("DOMContentLoaded", () => {
    // Modal Elements
    const modal = document.getElementById("sprint-form-modal");
    const backdrop = document.getElementById("modal-backdrop");
    const addSprintBtn = document.getElementById("add-sprint-btn");
    const closeModalBtn = document.getElementById("close-modal");

    // Form Elements
    const sprintNameInput = document.getElementById("sprint-name");
    const sprintNameError = document.getElementById("sprint-name-error");
    const startDateInput = document.getElementById("start-date");
    const endDateInput = document.getElementById("end-date");
    const saveSprintBtn = document.getElementById("save-sprint-btn"); // Corrected selector for the save button

    // Regex for sprint name validation
    const nameRegex = /^[A-Za-z0-9 ]{3,30}$/; // Only letters, numbers, and spaces

    // Helper Functions
    const toggleModal = (show) => {
        modal.classList.toggle("hidden", !show);
        backdrop.classList.toggle("hidden", !show);
    };

    const formatDate = (date) => {
        return date.toISOString().split("T")[0];
    };

    const setMinStartDate = () => {
        const today = new Date();
        today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
        return formatDate(today);
    };

    const validateName = () => {
        const name = sprintNameInput.value.trim();
        if (sprintNameInput.dataset.touched === "true") {
            if (!name) {
                sprintNameError.textContent = "This field cannot be empty.";
                return false;
            }
            if (!nameRegex.test(name)) {
                sprintNameError.textContent = "Must have 3-30 characters with only letters, numbers, and spaces.";
                return false;
            }
            sprintNameError.textContent = "";
        }
        return true;
    };

    const validateForm = () => {
        const isNameValid = validateName();
        const isStartDateFilled = startDateInput.value.trim() !== "";
        const isEndDateFilled = endDateInput.value.trim() !== "";
        const isEndDateValid = new Date(endDateInput.value) > new Date(startDateInput.value);

        // Enable the Save Sprint button only if all conditions are true
        saveSprintBtn.disabled = !(isNameValid && isStartDateFilled && isEndDateFilled && isEndDateValid);
    };

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Event Listeners
    addSprintBtn.addEventListener("click", () => toggleModal(true));
    closeModalBtn.addEventListener("click", () => toggleModal(false));

    startDateInput.addEventListener("change", () => {
        const startDate = new Date(startDateInput.value);
        const minEndDate = new Date(startDate);
        minEndDate.setDate(minEndDate.getDate() + 1);

        // Enable and set minimum date for End Date
        endDateInput.disabled = false;
        endDateInput.setAttribute("min", formatDate(minEndDate));

        // Clear invalid end date
        if (endDateInput.value && new Date(endDateInput.value) <= startDate) {
            endDateInput.value = "";
        }
        validateForm();
    });

    endDateInput.addEventListener("change", validateForm);

    sprintNameInput.addEventListener("input", () => {
        validateName();
        validateForm();
    });

    sprintNameInput.addEventListener("blur", () => {
        sprintNameInput.dataset.touched = "true";
        validateName();
        validateForm();
    });

    // Initial Setup
    startDateInput.setAttribute("min", setMinStartDate());
    endDateInput.disabled = true; // Disable end date input until start date is chosen
    saveSprintBtn.disabled = true; // Disable save button initially

    // Handle form submission via AJAX
    const sprintForm = document.getElementById("sprint-form");
    sprintForm.addEventListener("submit", (event) => {
        event.preventDefault();  // Prevent default form submission

        const sprintName = sprintNameInput.value.trim();
        const startDate = startDateInput.value.trim();
        const endDate = endDateInput.value.trim();

        // Collect the data to send
        const formData = {
            sprint_name: sprintName,
            start_date: startDate,
            end_date: endDate,
        };

        const url = saveSprintBtn.getAttribute("data-url");

        // Before submitting, check if the sprint name already exists
        checkIfSprintExists(sprintName, url).then(exists => {
            if (exists) {
                alert("A sprint with this name already exists.");
            } else {
                // Proceed with the normal submission
                saveSprint(url, formData);
            }
        });
    });

    // Function to check if sprint already exists
    const checkIfSprintExists = async (sprintName, url) => {
        try {
            const checkUrl = `${url}?sprint_name=${encodeURIComponent(sprintName)}&check_only=true`;
            const response = await fetch(checkUrl, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
            });
    
            if (!response.ok) {
                throw new Error("Failed to check sprint existence.");
            }
    
            const data = await response.json();
            return data.exists; // Expecting a boolean 'exists' in the JSON response
        } catch (error) {
            console.error("Error checking sprint existence:", error);
            return false; // Assume it does not exist if an error occurs
        }
    };
    

    // Function to save the sprint
    const saveSprint = (url, formData) => {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(formData),
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.text().then(text => { throw new Error(text); });
            }
        })
        .then(data => {
            console.log("Response data:", data);
            if (data.success) {
                alert("Sprint saved successfully!");
                window.location.reload();
            } else {
                alert("Error saving sprint: " + data.error);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred while saving the sprint: " + error.message);
        });
    };

});






