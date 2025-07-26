document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-jobs');
    const searchButton = document.querySelector('.search-btn');
    const filterButton = document.querySelector('.filter-btn');
    const jobCards = document.querySelectorAll('.job-card');
    const clearSearchButton = document.querySelector('.clear-search-btn');
    const salaryFilter = document.querySelector('.salary-filter');
    const locationFilter = document.querySelector('.location-filter');

    // Search functionality
    searchButton.addEventListener('click', () => {
        const query = searchInput.value.toLowerCase();
        jobCards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const company = card.querySelector('p').textContent.toLowerCase();
            if (title.includes(query) || company.includes(query)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });

    // Clear search functionality
    clearSearchButton.addEventListener('click', () => {
        searchInput.value = '';
        jobCards.forEach(card => {
            card.style.display = 'block';
        });
    });

    // Filter functionality
    filterButton.addEventListener('click', () => {
        const salaryValue = salaryFilter.value;
        const locationValue = locationFilter.value;

        jobCards.forEach(card => {
            const salary = card.dataset.salary; // Assuming you store the salary in data attributes
            const location = card.dataset.location; // Assuming you store the location in data attributes

            let matchesSalary = true;
            let matchesLocation = true;

            if (salaryValue) {
                matchesSalary = salary >= salaryValue;
            }

            if (locationValue) {
                matchesLocation = location.toLowerCase().includes(locationValue.toLowerCase());
            }

            if (matchesSalary && matchesLocation) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });

    // Job card hover effect
    jobCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'scale(1.03)';
            card.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'scale(1)';
            card.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
        });
    });
});
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
   // Handle navigation button clicks
   document.querySelectorAll('.nav-btn').forEach(button => {
    button.addEventListener('click', () => {
      const target = button.getAttribute('data-target');
      document.querySelectorAll('.job-listings').forEach(section => {
        section.classList.add('hidden');
      });
      document.getElementById(target).classList.remove('hidden');
    });
  });