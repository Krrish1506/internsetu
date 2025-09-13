// Custom JS for Student Home Page and Navigation

document.addEventListener('DOMContentLoaded', function () {
    // Navigation: load pages
    document.querySelectorAll('.nav-link').forEach(function (link) {
        link.addEventListener('click', function (e) {
            const text = link.textContent.trim();
            if (text === 'Profile') {
                e.preventDefault();
                window.location.href = "{{ url_for('profile') }}";
            } else if (text === 'My Applications') {
                e.preventDefault();
                window.location.href = "{{ url_for('recommend') }}";
            } else if (text === 'Dashboard') {
                e.preventDefault();
                window.location.href = "{{ url_for('alhome') }}";
            } else if (text.startsWith('Logout')) {
                e.preventDefault();
                if (confirm('Are you sure you want to logout?')) {
                    // Redirect to login page or home
                    window.location.href = "{{ url_for('home') }}";
                }
            }
        });
    });

    // Function to check login status
    function checkLoginStatus() {
        // Assuming localStorage key "isLoggedIn" is set to "true" after login/signup
        const isLoggedIn = localStorage.getItem('isLoggedIn');

        if (isLoggedIn === 'true') {
            // User is logged in → Redirect to alhome.html
            window.location.href = "{{ url_for('alhome') }}";
        } else {
            // User is not logged in → Redirect to home.html
            window.location.href = "{{ url_for('home') }}";
        }
    }

    // Call the function on page load
    window.onload = checkLoginStatus;


    $(".sign-up--btn").click(function () {
        $(".sign-up-form").css("display", "block");
    });

    // Apply Now button
    document.querySelectorAll('.site__btn-2.btn-sm').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            alert('Your application has been submitted!');
        });
    });

    // Highlight profile card if incomplete
    document.querySelectorAll('.dashboard-card').forEach(function (card) {
        if (card.textContent.includes('Complete your profile')) {
            card.style.border = '2px solid #FFD700';
            card.style.boxShadow = '0 0 10px #FFD70055';
        }
    });
});

// document.getElementById('loginForm').addEventListener('submit', function (e) {
//     e.preventDefault();
//     var email = document.getElementById('loginEmail').value.trim();
//     var password = document.getElementById('loginPassword').value.trim();
//     var errorDiv = document.getElementById('loginError');
//     errorDiv.style.display = 'none';

//     // Demo: Accept any non-empty credentials
//     if (email === "" || password === "") {
//         errorDiv.textContent = "Please enter both email and password.";
//         errorDiv.style.display = 'block';
//         return;
//     }
//     // You can add real authentication here
//     if (email === "student@email.com" && password === "123456") {
//         window.location.href = "{{ url_for('alhome') }}";
//     } else {
//         errorDiv.textContent = "Invalid email or password.";
//         errorDiv.style.display = 'block';
//     }
// });