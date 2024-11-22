const submitBtn = document.getElementById("send-button")
const repoValue = document.getElementById('repository-select')
const commitHashInput = document.getElementById('commit-input')

submitBtn.addEventListener('click', (event) => {
    event.preventDefault();
    let repoName = repoValue.value.split("/")[1]
    let ownerName = repoValue.value.split("/")[0]
    let commitHash = commitHashInput.value;

    console.log(repoName, ownerName,commitHash);

    fetch('/code-review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ owner: ownerName,
                                    commit_sha: commitHash,
                                    repo_name: repoName }),
        })
        .then(response => response.json())
        .then(data => {
            displayReviewData(data)
        });
})

function displayReviewData(responseData) {
    const review = responseData.review_comments[0].code_review;
    const finalFeedback = review.final_feedback;
    const codeData = review.json_data;
    const finalFeedbackContainer = document.getElementById("final-feedback");
    const codeReviewSectionsContainer = document.getElementById("code-review-sections");

    // Display final feedback
    finalFeedbackContainer.textContent = `Final Feedback: ${finalFeedback}`;

    // Display code review items
    codeData.forEach(item => {
        const reviewItem = document.createElement("div");
        reviewItem.classList.add("code-review-item");

        const sectionTitle = document.createElement("div");
        sectionTitle.classList.add("section-title");
        sectionTitle.textContent = item.section;

        const feedbackText = document.createElement("div");
        feedbackText.classList.add("feedback-text");
        feedbackText.textContent = item.feedback;

        const codeBlock = document.createElement("pre");
        codeBlock.textContent = item.code;

        reviewItem.appendChild(sectionTitle);
        reviewItem.appendChild(feedbackText);
        reviewItem.appendChild(codeBlock);

        codeReviewSectionsContainer.appendChild(reviewItem);
    });
}
