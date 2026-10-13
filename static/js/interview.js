// IntelliHire Interactive Interview Engine Client
document.addEventListener("DOMContentLoaded", () => {
    const answerInput = document.getElementById("answerInput");
    const wordCountSpan = document.getElementById("wordCount");
    const charCountSpan = document.getElementById("charCount");
    const submitBtn = document.getElementById("submitAnswerBtn");
    const submitSpinner = document.getElementById("submitSpinner");
    const submitText = document.getElementById("submitText");
    const timerDisplay = document.getElementById("timerDisplay");
    const evaluationModal = new bootstrap.Modal(document.getElementById("evaluationModal"), {
        backdrop: 'static',
        keyboard: false
    });

    // 1. Live Word & Character Counter
    if (answerInput) {
        answerInput.addEventListener("input", () => {
            const text = answerInput.value.trim();
            const words = text ? text.split(/\s+/).length : 0;
            if (wordCountSpan) wordCountSpan.textContent = words;
            if (charCountSpan) charCountSpan.textContent = text.length;
        });
    }

    // 2. Stopwatch per Question
    let secondsElapsed = 0;
    if (timerDisplay) {
        setInterval(() => {
            secondsElapsed++;
            const mins = String(Math.floor(secondsElapsed / 60)).padStart(2, "0");
            const secs = String(secondsElapsed % 60).padStart(2, "0");
            timerDisplay.textContent = `${mins}:${secs}`;
        }, 1000);
    }

    // 3. Submit Answer Handler
    if (submitBtn) {
        submitBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            const text = answerInput.value.trim();

            if (text.length < 5) {
                if (!confirm("Your answer is quite short. Are you sure you want to submit?")) {
                    answerInput.focus();
                    return;
                }
            }

            // Lock UI
            submitBtn.disabled = true;
            if (submitSpinner) submitSpinner.classList.remove("d-none");
            if (submitText) submitText.textContent = "Evaluating with NLP...";

            const sessionUuid = submitBtn.dataset.sessionUuid;
            const submitUrl = `/interview/${sessionUuid}/submit`;

            try {
                const response = await fetch(submitUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify({ user_answer: text })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    alert(data.error || "Failed to submit answer. Please try again.");
                    submitBtn.disabled = false;
                    if (submitSpinner) submitSpinner.classList.add("d-none");
                    if (submitText) submitText.textContent = "Submit Answer";
                    return;
                }

                // Populate Evaluation Modal
                const evalData = data.evaluation;
                document.getElementById("modalScore").textContent = `${evalData.score}/100`;
                document.getElementById("modalSim").textContent = `${evalData.similarity}%`;
                document.getElementById("modalCov").textContent = `${evalData.coverage}%`;
                document.getElementById("modalFeedback").textContent = evalData.feedback;

                // Strengths List
                const strengthsEl = document.getElementById("modalStrengths");
                strengthsEl.innerHTML = "";
                if (evalData.strengths && evalData.strengths.length > 0) {
                    evalData.strengths.forEach(s => {
                        const li = document.createElement("li");
                        li.textContent = s;
                        strengthsEl.appendChild(li);
                    });
                } else {
                    strengthsEl.innerHTML = "<li class='text-muted'>No particular strengths detected.</li>";
                }

                // Missing Concepts
                const missingEl = document.getElementById("modalMissing");
                missingEl.innerHTML = "";
                if (evalData.missing_concepts && evalData.missing_concepts.length > 0) {
                    evalData.missing_concepts.forEach(m => {
                        const badge = document.createElement("span");
                        badge.className = "badge bg-danger bg-opacity-25 text-danger border border-danger border-opacity-50 me-1 mb-1";
                        badge.textContent = m;
                        missingEl.appendChild(badge);
                    });
                } else {
                    missingEl.innerHTML = "<span class='text-success small'><i class='bi bi-check-circle me-1'></i>All key concepts covered!</span>";
                }

                // Configure Continue Button
                const continueBtn = document.getElementById("modalContinueBtn");
                if (data.completed) {
                    continueBtn.innerHTML = "<i class='bi bi-award me-1'></i>View Final Performance Report";
                    continueBtn.classList.remove("btn-primary-custom");
                    continueBtn.classList.add("btn-success");
                } else {
                    continueBtn.innerHTML = `Proceed to Question ${data.next_question_number} <i class='bi bi-arrow-right ms-1'></i>`;
                }

                continueBtn.onclick = () => {
                    window.location.href = data.redirect_url;
                };

                // Show modal
                evaluationModal.show();

            } catch (err) {
                console.error("Submission error:", err);
                alert("A network error occurred. Please check your connection and retry.");
                submitBtn.disabled = false;
                if (submitSpinner) submitSpinner.classList.add("d-none");
                if (submitText) submitText.textContent = "Submit Answer";
            }
        });
    }
});
