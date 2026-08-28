const apiCodeCard = document.querySelector("#quickstart .code-card");
if (apiCodeCard) {
  const linuxLabel = apiCodeCard.querySelector(".code-card-head span");
  if (linuxLabel) linuxLabel.textContent = "Linux / macOS";
  apiCodeCard.insertAdjacentHTML("beforeend", '<div class="platform-example"><div class="code-card-head"><span>Windows PowerShell</span><button class="copy-button" type="button" data-copy="curl.exe --request GET &quot;https://jan-ration.vercel.app/api/shops?state=Tamil%20Nadu&quot; --header &quot;Authorization: Bearer demo-shop-token&quot;">Copy</button></div><pre><code>curl.exe --request GET "https://jan-ration.vercel.app/api/shops?state=Tamil%20Nadu" \\\n  --header "Authorization: Bearer demo-shop-token"</code></pre></div>');
}

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const value = button.dataset.copy;
    try {
      await navigator.clipboard.writeText(value);
      button.textContent = "Copied";
    } catch {
      button.textContent = "Select to copy";
    }
    window.setTimeout(() => { button.textContent = "Copy"; }, 1800);
  });
});
