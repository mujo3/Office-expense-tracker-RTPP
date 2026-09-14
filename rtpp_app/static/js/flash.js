// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Find the container that wraps all flash messages
  const flashContainer = document.getElementById('flash-messages');
  
  // If there are no flash messages, do nothing
  if (!flashContainer) {
    return;
  }

  // After 2 seconds, start fading out the messages
  setTimeout(function() {
    // Enable CSS transition for opacity over 0.5 seconds
    flashContainer.style.transition = 'opacity 0.5s ease-out';
    // Set opacity to 0 to trigger fade-out
    flashContainer.style.opacity = '0';

    // After the fade-out completes (0.5s), remove the container from the DOM
    setTimeout(function() {
      flashContainer.remove();
    }, 500);
  }, 2000);
});
