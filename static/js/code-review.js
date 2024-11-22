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
    const reviewComments = responseData.review_comments;
    const reviewsContainer = document.getElementById("reviews-container");

    reviewComments.forEach(review => {
        const filename = review.filename;
        const reviewData = review.code_review;
        const finalFeedback = reviewData.final_feedback;
        const codeData = reviewData.json_data;

        // Create a container div for each review comment
        const reviewCommentDiv = document.createElement("div");
        reviewCommentDiv.classList.add("review-comment");

        // Add the filename as the title
        const fileTitle = document.createElement("div");
        fileTitle.classList.add("file-title");
        fileTitle.textContent = `File: ${filename}`;
        reviewCommentDiv.appendChild(fileTitle);

        // Display final feedback for the file
        const finalFeedbackContainer = document.createElement("div");
        finalFeedbackContainer.classList.add("final-feedback");
        finalFeedbackContainer.textContent = `Final Feedback: ${finalFeedback}`;
        reviewCommentDiv.appendChild(finalFeedbackContainer);

        // Display code review items for the file
        const codeReviewSectionsContainer = document.createElement("div");
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

            reviewCommentDiv.appendChild(reviewItem);
        });

        // Append the review comment div to the container
        reviewsContainer.appendChild(reviewCommentDiv);
    });
}

