var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};

// Helper to select elements
function $(id) {
  return document.getElementById(id);
}

const resumeInput = $("resumeInput");
const uploadArea = $("uploadArea");
const fileNameDiv = $("fileName");
const loadingMessage = $("loadingMessage");
const errorMessage = $("errorMessage");
const jobList = $("jobList");

// Drag & Drop functionality
uploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadArea.classList.add("dragover");
});
uploadArea.addEventListener("dragleave", (e) => {
  e.preventDefault();
  uploadArea.classList.remove("dragover");
});
uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadArea.classList.remove("dragover");
  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    resumeInput.files = e.dataTransfer.files;
    showFileName();
    handleUpload();
  }
});

// Clicking the upload area triggers file dialog
uploadArea.addEventListener("click", () => {
  resumeInput.click();
});

// Show selected file name
resumeInput.addEventListener("change", function () {
  showFileName();
  if (resumeInput.files && resumeInput.files.length > 0) {
    handleUpload();
  }
});

function showFileName() {
  if (resumeInput.files && resumeInput.files.length > 0) {
    fileNameDiv.textContent = resumeInput.files[0].name;
  } else {
    fileNameDiv.textContent = "";
  }
}

function handleUpload() {
  errorMessage.style.display = "none";
  jobList.innerHTML = "";

  if (!resumeInput.files || resumeInput.files.length === 0) {
    errorMessage.textContent = "Please select a resume file!";
    errorMessage.style.display = "block";
    return;
  }

  const file = resumeInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  loadingMessage.innerHTML = '<span class="spinner"></span> Analyzing your resume...';
  loadingMessage.style.display = "block";

  fetch("http://localhost:8000/upload_resume", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (!response.ok) throw new Error("Upload failed");
      return response.json();
    })
    .then((jobs) => {
      renderJobs(jobs);
    })
    .catch((err) => {
      errorMessage.textContent = "Failed to upload resume. Please try again.";
      errorMessage.style.display = "block";
    })
    .finally(() => {
      loadingMessage.style.display = "none";
    });
}

function renderJobs(jobs) {
  jobList.innerHTML = "";
  if (!jobs || jobs.length === 0) {
    jobList.innerHTML = '<li>No jobs found.</li>';
    return;
  }
  jobs.forEach((job) => {
    const li = document.createElement("li");
    li.className = "job-card";
    // Choose an icon based on job title (simple example)
    let icon = "&#128188;"; // briefcase
    if (job.title.toLowerCase().includes("engineer")) icon = "&#128187;"; // laptop
    if (job.title.toLowerCase().includes("analyst")) icon = "&#128200;"; // chart
    if (job.title.toLowerCase().includes("manager")) icon = "&#128221;"; // clipboard
    // Color code match
    let matchClass = "";
    if (job.similarity >= 90) matchClass = "";
    else if (job.similarity >= 75) matchClass = "low";
    else matchClass = "very-low";
    li.innerHTML = `
      <span class="job-icon">${icon}</span>
      <div class="job-details">
        <div class="job-title">${job.title}</div>
        <div class="job-location">${job.location}</div>
        <div class="job-match ${matchClass}">Match: ${job.similarity}%</div>
      </div>
    `;
    jobList.appendChild(li);
  });
}
