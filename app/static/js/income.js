document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('contactDropdown').addEventListener('click', function(event) {
      event.preventDefault();
      const menu = document.getElementById('contactMenu');
      menu.classList.toggle('hidden');
  });

  document.addEventListener('click', function(event) {
      const menu = document.getElementById('contactMenu');
      const contactDropdown = document.getElementById('contactDropdown');
      if (!contactDropdown.contains(event.target) && !menu.contains(event.target)) {
          menu.classList.add('hidden');
      }
  });
});
document.addEventListener('DOMContentLoaded', function() {
  const button = document.querySelector('.relative.group > button');
  const menu = document.querySelector('.relative.group > div');

  button.addEventListener('click', function(event) {
      event.preventDefault();
      menu.classList.toggle('hidden');
  });

  document.addEventListener('click', function(event) {
      if (!button.contains(event.target) && !menu.contains(event.target)) {
          menu.classList.add('hidden');
      }
  });
});