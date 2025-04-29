async function uploadResume() {
    const input = document.getElementById('resumeInput') as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      alert('Please select a resume file!');
      return;
    }
  
    const file = input.files[0];
    const formData = new FormData();
    formData.append('file', file);
  
    try {
      const response = await fetch('http://localhost:8001/upload_resume', {
        method: 'POST',
        body: formData,
      });
  
      const jobs = await response.json();
  
      const jobList = document.getElementById('jobList')!;
      jobList.innerHTML = '';
  
      jobs.forEach((job: any) => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${job.title}</strong> (${job.location}) - Match: ${job.similarity}%`;
        jobList.appendChild(li);
      });
    } catch (error) {
      console.error('Error uploading resume:', error);
      alert('Failed to upload resume.');
    }
  }
  
  const uploadButton = document.getElementById('uploadButton')!;
  uploadButton.addEventListener('click', uploadResume);
  