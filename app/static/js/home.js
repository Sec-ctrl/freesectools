document.addEventListener('DOMContentLoaded', function() {
    const ticker = document.getElementById('cve-ticker-content');
    const tickerContainer = document.getElementById('cve-ticker');

    // Check if the elements exist
    if (!ticker || !tickerContainer) {
        console.error("Ticker or ticker container not found.");
        return; // Exit if elements are not found
    }

    console.log("Ticker and container found.");

    // Immediately show the ticker for debugging
    tickerContainer.style.display = 'block';

    function startTicker() {
        // Calculate the dimensions
        let tickerWidth = ticker.scrollWidth; // Full content width
        let containerWidth = tickerContainer.offsetWidth; // Visible container width
        let position = containerWidth; // Start off-screen

        // Debugging: Check the dimensions
        console.log("Ticker Width:", tickerWidth);
        console.log("Container Width:", containerWidth);

        // Ensure ticker content width is calculated correctly
        if (tickerWidth <= containerWidth) {
            console.error("Ticker content is smaller than or equal to container width, nothing to scroll.");
            return;
        }

        // Position the ticker off-screen initially
        ticker.style.transform = `translateX(${containerWidth}px)`;

        // Function to slide the ticker
        function slideTicker() {
            if (position <= -tickerWidth) {
                position = containerWidth; // Reset to the right side
            } else {
                position -= 0.6; // Adjust speed here
            }
            ticker.style.transform = `translateX(${position}px)`;
            requestAnimationFrame(slideTicker);
        }

        // Start the ticker animation
        requestAnimationFrame(slideTicker);
    }

    // Start the ticker after a delay to ensure rendering is complete
    setTimeout(startTicker, 1000); // 1 second delay for testing
});
