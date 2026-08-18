const API_URL = "http://localhost:5000/api/applications";

const form = document.getElementById("applicationForm");
const submitBtn = document.getElementById("submitBtn");
const btnText = document.getElementById("btnText");
const spinner = document.getElementById("spinner");
const banner = document.getElementById("banner");

const VALID_DEPARTMENTS = ["engineering", "design", "marketing", "sales", "hr", "finance"];
const ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "webp"];
const MAX_FILE_SIZE = 5 * 1024 * 1024;

function showError(field, message) {
  document.getElementById("err_" + field).textContent = message || "";
  const input = document.getElementById(field);
  if (message) {
    input.classList.add("invalid");
  } else {
    input.classList.remove("invalid");
  }
}

function clearAllErrors() {
  ["full_name", "email", "phone", "department", "date_of_birth", "bio", "photo"].forEach(function (f) {
    showError(f, "");
  });
}

function showBanner(type, message) {
  banner.textContent = message;
  banner.className = "banner " + type;
  banner.classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function hideBanner() {
  banner.classList.add("hidden");
}

function validateForm() {
  let isValid = true;
  clearAllErrors();

  const fullName = document.getElementById("full_name").value.trim();
  if (!fullName) {
    showError("full_name", "Full name is required.");
    isValid = false;
  } else if (fullName.length < 3) {
    showError("full_name", "Full name must be at least 3 characters.");
    isValid = false;
  } else if (fullName.length > 80) {
    showError("full_name", "Full name must be under 80 characters.");
    isValid = false;
  }

  const email = document.getElementById("email").value.trim();
  const emailRegex = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  if (!email) {
    showError("email", "Email is required.");
    isValid = false;
  } else if (!emailRegex.test(email)) {
    showError("email", "Enter a valid email address.");
    isValid = false;
  }

  const phone = document.getElementById("phone").value.trim();
  const phoneRegex = /^\+?[0-9\-\s]{7,15}$/;
  if (!phone) {
    showError("phone", "Phone number is required.");
    isValid = false;
  } else if (!phoneRegex.test(phone)) {
    showError("phone", "Enter a valid phone number (7-15 digits).");
    isValid = false;
  }

  const department = document.getElementById("department").value;
  if (!department) {
    showError("department", "Please select a department.");
    isValid = false;
  } else if (!VALID_DEPARTMENTS.includes(department)) {
    showError("department", "Selected department is not valid.");
    isValid = false;
  }

  const dob = document.getElementById("date_of_birth").value;
  if (!dob) {
    showError("date_of_birth", "Date of birth is required.");
    isValid = false;
  } else {
    const dobDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - dobDate.getFullYear();
    const monthDiff = today.getMonth() - dobDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dobDate.getDate())) {
      age--;
    }
    if (dobDate > today) {
      showError("date_of_birth", "Date of birth cannot be in the future.");
      isValid = false;
    } else if (age < 16) {
      showError("date_of_birth", "You must be at least 16 years old.");
      isValid = false;
    } else if (age > 100) {
      showError("date_of_birth", "Enter a valid date of birth.");
      isValid = false;
    }
  }

  const bio = document.getElementById("bio").value.trim();
  if (bio.length > 500) {
    showError("bio", "Bio must be under 500 characters.");
    isValid = false;
  }

  const photoInput = document.getElementById("photo");
  const photoFile = photoInput.files[0];
  if (!photoFile) {
    showError("photo", "A profile photo is required.");
    isValid = false;
  } else {
    const ext = photoFile.name.split(".").pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      showError("photo", "Only PNG, JPG, JPEG, GIF, or WEBP files are allowed.");
      isValid = false;
    } else if (photoFile.size > MAX_FILE_SIZE) {
      showError("photo", "Photo must be under 5MB.");
      isValid = false;
    }
  }

  return isValid;
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  if (isLoading) {
    btnText.textContent = "Submitting...";
    spinner.classList.remove("hidden");
  } else {
    btnText.textContent = "Submit Application";
    spinner.classList.add("hidden");
  }
}

form.addEventListener("submit", async function (e) {
  e.preventDefault();
  hideBanner();

  const clientValid = validateForm();
  if (!clientValid) {
    showBanner("error", "Please fix the highlighted fields before submitting.");
    return;
  }

  setLoading(true);

  const formData = new FormData(form);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (response.ok && result.success) {
      showBanner("success", result.message || "Application submitted successfully!");
      form.reset();
      clearAllErrors();
    } else if (result.errors) {
      Object.keys(result.errors).forEach(function (field) {
        showError(field, result.errors[field]);
      });
      showBanner("error", "Server rejected the submission. Please check the fields.");
    } else {
      showBanner("error", "Something went wrong. Please try again.");
    }
  } catch (err) {
    showBanner("error", "Could not reach the server. Please try again later.");
  } finally {
    setLoading(false);
  }
});

["full_name", "email", "phone", "department", "date_of_birth", "bio", "photo"].forEach(function (field) {
  document.getElementById(field).addEventListener("input", function () {
    showError(field, "");
  });
});
