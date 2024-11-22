const profileReview = document.getElementById("profile-review")
const readme = document.getElementById("readme")
const repoValue = document.getElementById('repository-select')
// const commitHashInput = document.getElementById('commit-input')
const mainStuff = document.getElementById('main')
const loaderStuff = document.getElementById('loader')

profileReview.addEventListener('click', (event) => {
    mainStuff.style.display = "none";
    loaderStuff.style.display = "flex"
    event.preventDefault();
    // let repoName = repoValue.value.split("/")[1]
    let ownerName = repoValue.value.split("/")[0]
    // let commitHash = commitHashInput.value;

    // console.log(repoName, ownerName,commitHash);

    fetch('/profile-review', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            // body: JSON.stringify({ username: ownerName}),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data["analysis"])
            displayReviewDataProfile(data["analysis"])
        }).then(val => {
                mainStuff.style.display = "block";
                loaderStuff.style.display = "none"
        }).finally(val => {
             mainStuff.style.display = "block";
                loaderStuff.style.display = "none"
        });
})



readme.addEventListener('click', (event) => {
    mainStuff.style.display = "none";
    loaderStuff.style.display = "flex"
    event.preventDefault();
    // let repoName = repoValue.value.split("/")[1]
    let ownerName = repoValue.value.split("/")[0]
    // let commitHash = commitHashInput.value;

    // console.log(repoName, ownerName,commitHash);

    fetch('/readme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ repo_name: repoValue, owner: ownerName}),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data["readMe"])
            displayReviewDataReadme(data["readMe"])
        }).then(val => {
                mainStuff.style.display = "block";
                loaderStuff.style.display = "none"
        }).finally(val => {
             mainStuff.style.display = "block";
                loaderStuff.style.display = "none"
        });
})



function displayReviewDataProfile(content)
{
    const output = document.getElementById('html-output-profile');
        var text = ""
        const formattedText = content.replace(/\n/g, "<br/>");
        output.style.display = "block"
            output.addEventListener("click", () => {
                // Create a blob with the content of xyz
                const blob = new Blob([formattedText], { type: "text/markdown" });
                
                // Create a temporary anchor element
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = "profile-review.html"; // Set the filename
                
                // Trigger the download
                a.click();
                
                // Clean up
                URL.revokeObjectURL(a.href);
                 output.style.display = "none"
            });
}

function displayReviewDataReadme(content)
{
    const output = document.getElementById('html-output-readme');
        var text = ""
        output.style.display = "block"
            output.addEventListener("click", () => {
                // Create a blob with the content of xyz
                const blob = new Blob([content], { type: "text/markdown" });
                
                // Create a temporary anchor element
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = "README.md"; // Set the filename
                
                // Trigger the download
                a.click();
                
                // Clean up
                URL.revokeObjectURL(a.href);
                 output.style.display = "none"
            });
}


