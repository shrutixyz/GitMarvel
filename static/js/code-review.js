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

function displayReviewData(content)
{
    if (typeof marked === 'undefined') {
        console.error('Marked is not loaded properly!');
    } else {
        const output = document.getElementById('html-output');

        content["review_comments"].forEach(c => {

            const markdown = c.code_review;
            const html = marked.parse(markdown); // Convert Markdown to HTML
            output.innerHTML += html;
    
            // Initialize with current value
            // output.innerHTML += marked.parse(c);
        })
    }
}

