const submitBtn = document.getElementById("send-button")
const repoValue = document.getElementById('repository-select')
const commitHashInput = document.getElementById('commit-input')
const mainStuff = document.getElementById('main')
const loaderStuff = document.getElementById('loader')

submitBtn.addEventListener('click', (event) => {
    mainStuff.style.display = "none";
    loaderStuff.style.display = "flex"
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
        }).then(val => {
                mainStuff.style.display = "block";
                loaderStuff.style.display = "none"
        }).finally(val => {
             mainStuff.style.display = "block";
                loaderStuff.style.display = "none"
        });
})

function displayReviewData(content)
{
    if (typeof marked === 'undefined') {
        console.error('Marked is not loaded properly!');
    } else {
        const output = document.getElementById('html-output');
        var text = ""
        content["review_comments"].forEach(c => {

            const markdown = c.code_review;
            const html = marked.parse(markdown); // Convert Markdown to HTML
            // output.innerHTML += html;
            text += html
            output.style.display = "block"
            output.addEventListener("click", () => {
                // Create a blob with the content of xyz
                const blob = new Blob([text], { type: "text/markdown" });
                
                // Create a temporary anchor element
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = "code-review.html"; // Set the filename
                
                // Trigger the download
                a.click();
                
                // Clean up
                URL.revokeObjectURL(a.href);
            });
            // Initialize with current value
            // output.innerHTML += marked.parse(c);
        })
    }
}


