document.addEventListener("DOMContentLoaded", function () {
  // Wait 5 seconds before starting to hide messages
  setTimeout(function () {
    document.querySelectorAll(".custom-message").forEach((msg) => {
      // Fade out (set opacity to 0)
      msg.style.opacity = "0";

      // After fade-out animation (0.5s), hide the element
      setTimeout(() => {
        msg.style.display = "none";
      }, 500); // Match this to your CSS transition duration
    });
  }, 5000);
});

function showLogin() {
  document.querySelector(".loginDiv").style.display = "block";
  document.querySelector(".registerDiv").style.display = "none";

  document.getElementById("loginBtn").classList.add("active-btn");
  document.getElementById("registerBtn").classList.remove("active-btn");
}

function showRegister() {
  document.querySelector(".loginDiv").style.display = "none";
  document.querySelector(".registerDiv").style.display = "block";

  document.getElementById("loginBtn").classList.remove("active-btn");
  document.getElementById("registerBtn").classList.add("active-btn");
}

// Optional: Set Login as active by default when modal loads
document.addEventListener("DOMContentLoaded", () => {
  showLogin();
});

//while we are using this formate of ajax we got an error of csrf token
// CSRF token handling for AJAX requests in Django s we not using the classes ajax formate provided by sir bcz we got an error of csrf token
// The CSRF token is automatically included in the headers of AJAX requests

// csrftoken is now read from the cookie.
// It’s passed via the X-CSRFToken header, which Django recognizes safely.

// Function to toggle the favorite status of a task
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie("csrftoken");

function showFavToast(message) {
  const toast = $(`<div class="custom-toast">${message}</div>`);
  $("body").append(toast);
  toast
    .fadeIn(400)
    .delay(2000)
    .fadeOut(400, function () {
      $(this).remove();
    });
}

$(document).on("click", ".add-fav", function (e) {
  e.preventDefault();
  const btn = $(this);
  const courseId = btn.data("id");
  const icon = btn.find("i");

  $.ajax({
    url: `/favorite/toggle/${courseId}/`,
    type: "POST",
    headers: { "X-CSRFToken": csrftoken },
    success: function (response) {
      const countEl = $("#wishlist-count");
      let count = parseInt(countEl.text());

      if (response.status === "added") {
        icon.removeClass("fa-regular").addClass("fa-solid text-danger");
        countEl.text(count + 1);
        showFavToast("✅ Course added to wishlist!");
      } else if (response.status === "removed") {
        icon.removeClass("fa-solid text-danger").addClass("fa-regular");
        countEl.text(count - 1);
        showFavToast("❌ Course removed from wishlist!");
      } else {
        showFavToast("⚠️ Something went wrong.");
      }
    },
    error: function () {
      showFavToast("❌ Failed. Please try again.");
    },
  });
});

$(document).on("click", ".remove-favorite", function (e) {
  e.preventDefault();
  const btn = $(this);
  const courseId = btn.data("id");
  const items = $(`.fav-item[data-id="${courseId}"]`);

  $.ajax({
    url: `/favorites/remove/${courseId}/`,
    type: "POST",
    headers: {
      "X-CSRFToken": csrftoken,
    },
    success: function (response) {
      if (response.status === "success") {
        items.remove(); // remove from both desktop & mobile
        showFavToast("Removed from favorites!");

        // Update wishlist count
        const countEl = $("#wishlist-count");
        let count = parseInt(countEl.text());
        countEl.text(count - 1);
        showFavToast("❌ Course removed from wishlist!");

        // ✅ If no more favorite items left, show empty-cart without reload
        if ($(".fav-item").length === 0) {
          $("#fav-list").remove(); // remove all items
          $(".fav-table").remove(); // remove table
          $(".mobile-cart").remove(); // remove mobile layout

          $(".cart-sec1").append(`
            <div class="empty-cart">
              <p><i class="fa-solid fa-heart-circle-exclamation"></i>Your Wishlist is currently empty.</p>
             <a href="/courses/">
                <button>Return to Courses</button>
              </a>
            </div>
          `);
        }
      }
    },
  });
});

let lastRemoved = null;

$(document).on("click", ".add-to-cart", function (e) {
  e.preventDefault();
  const button = $(this);
  const courseId = button.data("id");

  $.ajax({
    url: "/cart/add/" + courseId + "/",
    type: "POST",
    headers: {
      "X-CSRFToken": csrftoken,
    },
    success: function (response) {
      if (response.status == "success") {
        $("#cart-count").text(response.count);

        if (response.added) {
          button.text("Added to Cart");
          $("#cart-message").text("✔ Course added to cart!");
          showFavToast("✅ Course added to cart!");
        } else {
          button.text("Already in Cart");
          $("#cart-message").text("ℹ Course is already in your cart.");
          showFavToast("✅ Course is already in your cart.");
        }

        // Reload hover cart
        $.get("/cart/load_snippet/", function (data) {
          $("#cart-snippet-wrapper").html(data.html);
        });
      }
    },
    error: function () {
      showFavToast("❌ Failed. Please try again.");
    },
  });
});

function showRemoveToast(msg) {
  $("#remove-toast").text(msg).fadeIn(400).delay(1500).fadeOut(400);
}

$(document).on("click", ".remove-cart", function (e) {
  e.preventDefault();
  const button = $(this);
  const itemId = button.data("id");

  $.ajax({
    url: "/cart/remove/" + itemId + "/",
    type: "POST",
    headers: {
      "X-CSRFToken": csrftoken,
    },
    success: function (response) {
      if (response.status === "success") {
        // Update cart count
        $("#cart-count").text(response.count);
        showFavToast("❌ Course removed from cart!");

        // Reload hover cart
        $.get("/cart/load_snippet/", function (data) {
          $("#cart-snippet-wrapper").html(data.html);
        });

        // Remove item from cart.html
        const cartItem = $('.cart-item[data-id="' + itemId + '"]');
        if (cartItem.length) {
          const courseName = cartItem.find("p").first().text().trim();
          const courseId = cartItem.data("course-id"); // ✅ Must be in template

          // Store last removed item
          lastRemoved = {
            cartId: itemId,
            courseId: courseId, // ✅ used for Undo
            html: cartItem.prop("outerHTML"),
            name: courseName,
          };

          cartItem.remove();

          // Recalculate total
          let newTotal = 0;
          $(".cart-item").each(function () {
            newTotal += parseFloat($(this).data("price"));
          });

          $("#cart-total").text(parseFloat(response.total).toFixed(2));
          $("#cart-total1").text(parseFloat(response.total).toFixed(2));

          if ($(".cart-item").length === 0) {
            $("#cart-items-list").remove(); // remove all items
            $(".cart-table").remove(); // remove table
            $(".mobile-cart").remove(); // remove mobile layout
            $(".cart-totals").remove(); // remove mobile layout

            $(".cart-sec1").append(`
            <div class="empty-cart">
        <p><i class="fa-solid fa-cart-shopping"></i>Your cart is currently empty.</p>
        <a href="/courses/">
            <button>Return to Courses</button>
        </a>
    </div>
          `);
          }

          // Show Undo message
          if (lastRemoved) {
            $("#undo-text").text(`"${lastRemoved.name}" removed.`);
            $("#undo-message").slideDown();

            // Auto-hide after 5s
            setTimeout(() => {
              $("#undo-message").slideUp();
              lastRemoved = null;
            }, 7000);
          }
        }

        // Toast message
        showRemoveToast("✔ Course removed from cart!");
      }
    },
  });
});

// ✅ Undo handler
$(document).on("click", "#undo-btn", function () {
  if (!lastRemoved) return;

  const courseId = lastRemoved.courseId;

  $.ajax({
    url: "/cart/add/" + courseId + "/", // ✅ now using courseId
    type: "POST",
    headers: {
      "X-CSRFToken": csrftoken,
    },
    success: function (response) {
      if (response.status === "success") {
        $("#cart-count").text(response.count);
        $("#cart-items-list").prepend(lastRemoved.html);

        // Reload hover cart
        $.get("/cart/load_snippet/", function (data) {
          $("#cart-snippet-wrapper").html(data.html);
        });

        // Refresh total
        $.get("/cart/total/", function (data) {
          $("#cart-total").text(parseFloat(data.total).toFixed(2));
          $("#cart-total1").text(parseFloat(data.total).toFixed(2));
        });

        $("#undo-message").slideUp();
        lastRemoved = null;
        setTimeout(() => {
          location.reload();
        }, 300);
      }
    },
  });
});

// header scroll effect

window.addEventListener("scroll", function () {
  const header = document.querySelector("header");
  if (window.scrollY > 60) {
    header.classList.add("fixed-header");
  } else {
    header.classList.remove("fixed-header");
  }
});

// count section

function animateCounter(counter) {
  const target = parseFloat(counter.getAttribute("data-target"));
  const suffix = counter.getAttribute("data-suffix") || "K";
  const isDecimal = String(target).includes(".");
  let count = 0;
  const speed = 100;

  const update = () => {
    count += target / speed;
    if (count < target) {
      counter.innerText = isDecimal
        ? count.toFixed(1) + suffix
        : Math.floor(count) + suffix;
      requestAnimationFrame(update);
    } else {
      counter.innerText = isDecimal
        ? target.toFixed(1) + suffix
        : Math.floor(target) + suffix;
    }
  };
  update();
}

function handleScroll() {
  const counters = document.querySelectorAll(".counter");
  counters.forEach((counter) => {
    const rect = counter.getBoundingClientRect();
    if (rect.top < window.innerHeight && !counter.classList.contains("done")) {
      counter.classList.add("done");
      animateCounter(counter);
    }
  });
}

window.addEventListener("scroll", handleScroll);
window.addEventListener("load", handleScroll);

// left right top bottom movements
document.addEventListener("mousemove", (e) => {
  const x = (e.clientX / window.innerWidth - 0.5) * 50; // Adjust range
  const y = (e.clientY / window.innerHeight - 0.5) * 50;

  document.querySelectorAll(".follow-cursor").forEach((el) => {
    el.style.transform = `translate(${x}px, ${y}px)`;
  });
});

// Optional reset on mouse leave
document.addEventListener("mouseleave", () => {
  document.querySelectorAll(".follow-cursor").forEach((el) => {
    el.style.transform = "translate(0px, 0px)";
  });
});

function toggleSubcategory(element) {
  const wrapper = element.closest("li");
  const content = wrapper.querySelector(".subcategory-content");
  const icons = wrapper.querySelector(".toggle-icons");

  content.style.display = content.style.display === "block" ? "none" : "block";
  icons.classList.toggle("expanded");
}

// profile btn edit/update
document.getElementById("editBtn").addEventListener("click", function () {
  const inputs = document.querySelectorAll("#profileForm input");
  inputs.forEach((input) => (input.disabled = false));

  document.getElementById("editBtn").style.display = "none";
  document.getElementById("updateBtn").style.display = "inline-block";
});

// password show hide
document.querySelectorAll(".toggle-password").forEach((icon) => {
  icon.addEventListener("click", function () {
    const input = document.getElementById(this.getAttribute("data-target"));
    if (input.type === "password") {
      input.type = "text";
      this.classList.remove("fa-eye");
      this.classList.add("fa-eye-slash");
    } else {
      input.type = "password";
      this.classList.remove("fa-eye-slash");
      this.classList.add("fa-eye");
    }
  });
});

document.querySelectorAll(".toggle-password").forEach((icon) => {
  icon.addEventListener("click", function () {
    const input = document.getElementById(this.getAttribute("data-target"));
    if (input.type === "password") {
      input.type = "text";
      this.classList.remove("fa-eye");
      this.classList.add("fa-eye-slash");
    } else {
      input.type = "password";
      this.classList.remove("fa-eye-slash");
      this.classList.add("fa-eye");
    }
  });
});

// This auto triggers filtering when arriving via URL (like /courses/?category=full_stack)
document.addEventListener("DOMContentLoaded", function () {
  const params = new URLSearchParams(window.location.search);
  const categoryFromURL = params.get("category");

  // Highlight category and filter courses on page load
  if (categoryFromURL) {
    const categoryElement = document.querySelector(
      `.filter-category-text p[data-category="${categoryFromURL}"]`
    );
    if (categoryElement) {
      filterCourses(categoryElement, true); // true = don't push URL again
    }
  } else {
    // Default to all
    const allCategory = document.querySelector(
      '.filter-category-text p[data-category="all"]'
    );
    if (allCategory) {
      filterCourses(allCategory, true);
    }
  }
});

function redirectToCourses(category) {
  window.location.href = `/courses/?category=${category}`;
}

function filterCourses(element, skipPush = false) {
  // Set active class
  document
    .querySelectorAll(".filter-category-text p, .div-grid")
    .forEach((p) => p.classList.remove("active"));
  element.classList.add("active");

  const selectedCategory = element.getAttribute("data-category");

  // Update the URL if needed
  if (!skipPush) {
    const newURL =
      selectedCategory === "all"
        ? window.location.pathname
        : `${window.location.pathname}?category=${selectedCategory}`;
    window.history.pushState({}, "", newURL);
  }

  // Show/hide courses
  document.querySelectorAll(".courses-maindiv").forEach((card) => {
    const courseCategory = card.getAttribute("data-category");
    if (selectedCategory === "all" || courseCategory === selectedCategory) {
      card.style.display = "block";
    } else {
      card.style.display = "none";
    }
  });
}

// ṣhow mesaage if user is try add to fav if user is not login

function showLoginMessage() {
  setTimeout(() => {
    const msgBox = document.createElement("div");
    msgBox.innerText = "🔒 Please login or register to add to your wishlist.";
    msgBox.style.position = "fixed";
    msgBox.style.top = "20px";
    msgBox.style.right = "20px";
    msgBox.style.backgroundColor = "#1ab69d";
    msgBox.style.color = "#fff";
    msgBox.style.padding = "10px 20px";
    msgBox.style.borderRadius = "8px";
    msgBox.style.zIndex = "9999";
    msgBox.style.boxShadow = "0px 0px 10px rgba(0,0,0,0.2)";
    msgBox.style.fontWeight = "600";
    msgBox.style.transition = "opacity 0.3s";

    document.body.appendChild(msgBox);

    setTimeout(() => {
      msgBox.style.opacity = "0";
      setTimeout(() => msgBox.remove(), 500);
    }, 3000);
  }, 500); // Delay to show after modal opens
}

/*
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script> use this link for loadd the ajax 

ajax simple and understa formate 
<script>


    $(document).on('click','.liked',function(e){
      e.preventDefault();
      const button = $(this)
      const taskId = button.attr('id');
      console.log(taskId);
      $.ajax({
        url:"favorite/"+taskId,
        type:"POST",
        data:{
          "csrfmiddlewaretoken":'{{ csrf_token }}',
        },
        success: function(response) {
          if(response.status == 'success') {
            const isFavourite = response.favorite;
            button.html(isFavourite ? '<i class="fa-solid fa-heart text-red-500"></i>' : '<i class="fa-regular fa-heart text-gray-400"></i>')
           }
        }
      })
    })


  </script>
*/
