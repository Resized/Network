document.addEventListener("DOMContentLoaded", () => {
  const menuLinks = document.querySelectorAll(".nav-link");
  const contentDivs = document.querySelectorAll("#pills-tabContent > div");

  function removeActiveClass() {
    menuLinks.forEach(function (link) {
      link.classList.remove("active");
    });
  }

  function setActiveFeed(feedDivId) {
    // Hide all content divs
    contentDivs.forEach((div) => {
      div.classList.remove("active-page");
    });

    // Show the specified feed div
    const activeFeedDiv = document.getElementById(feedDivId);
    if (activeFeedDiv) {
      activeFeedDiv.classList.add("active-page");
    }
  }

  // menuLinks.forEach(function (link) {
  //   link.addEventListener("click", function (event) {
  //     event.preventDefault(); // Prevent the default link behavior
  //
  //     // Get the target content ID from the data attribute
  //     const targetContentId = this.dataset.target;
  //
  //     // Hide all content divs
  //     contentDivs.forEach(function (div) {
  //       div.classList.remove("active-page");
  //     });
  //
  //     // Show the content div corresponding to the clicked menu item
  //     const targetContentDiv = document.getElementById(targetContentId);
  //     if (targetContentDiv) {
  //       targetContentDiv.classList.add("active-page");
  //     }
  //
  //     // Remove the "active" class from all menu links
  //     removeActiveClass();
  //
  //     // Add the "active" class to the clicked menu item
  //     this.classList.add("active");
  //   });
  // });

  // Define your routes and corresponding handlers
  const routes = [
    { path: "/", handler: defaultHandler },
    { path: "/home", handler: homeHandler },
    { path: "/profile/:username", handler: profileHandler },
    { path: "/following", handler: followingHandler },
    { path: "/login", handler: loginHandler },
    { path: "/register", handler: registerHandler },
  ];

  // Function to handle the route based on the current URL
  function handleRoute() {
    const path = location.pathname;
    const route = routes.find((r) => matchRoute(r.path, path));
    if (route) {
      const params = extractParams(route.path, path);
      route.handler(params);
    } else {
      // Handle not found or default route
    }
  }

  // Function to check if a route matches the current URL
  function matchRoute(pattern, path) {
    const patternRegex = new RegExp(
      "^" + pattern.replace(/:\w+/g, "([^/]+)") + "$"
    );
    return patternRegex.test(path);
  }

  // Function to extract parameters from the URL
  function extractParams(pattern, path) {
    const keys = pattern.match(/:\w+/g) || [];
    const values =
      path.match(new RegExp("^" + pattern.replace(/:\w+/g, "([^/]+)") + "$")) ||
      [];
    return keys.reduce((params, key, index) => {
      params[key.substring(1)] = values[index + 1];
      return params;
    }, {});
  }

  // Handlers for different routes
  function defaultHandler() {
    console.log("Home route");
    // Perform actions or render view for the home route
    removeActiveClass();
    const menuButton = document.getElementById("posts");
    menuButton.classList.add("active");

    setActiveFeed(menuButton.dataset.target);

    view_feed("all");

    history.replaceState(null, null, "/home");
  }

  function homeHandler() {
    console.log("Home route");
    // Perform actions or render view for the home route
    removeActiveClass();
    const menuButton = document.getElementById("posts");
    menuButton.classList.add("active");

    setActiveFeed(menuButton.dataset.target);

    view_feed("all");
  }

  function profileHandler(params) {
    console.log("Profile route", params);
    // Perform actions or render view for the profile route
    removeActiveClass();
    const menuButton = document.getElementById("profile");
    if (menuButton) {
      menuButton.classList.add("active");
      setActiveFeed(menuButton.dataset.target);
    } else {
      setActiveFeed("pills-profile");
    }
    view_profile(params.username);
  }

  function followingHandler() {
    console.log("Following route");
    // Perform actions or render view for the following route
    removeActiveClass();
    const menuButton = document.getElementById("following");
    menuButton.classList.add("active");

    setActiveFeed(menuButton.dataset.target);

    view_feed("following");
  }

  function loginHandler() {
    console.log("Login route");
    // Perform actions or render view for the following route
    removeActiveClass();
    const menuButton = document.getElementById("login");
    menuButton.classList.add("active");

    setActiveFeed(menuButton.dataset.target);
  }

  function registerHandler() {
    console.log("Login route");
    // Perform actions or render view for the following route
    removeActiveClass();
    const menuButton = document.getElementById("register");
    menuButton.classList.add("active");

    setActiveFeed(menuButton.dataset.target);
  }

  // Add event listener for the popstate event to handle back/forward navigation
  window.addEventListener("popstate", handleRoute);

  // Add event listener for the initial page load
  window.addEventListener("load", handleRoute);

  // Add event listener for click events on links
  document.addEventListener("click", function (event) {
    const target = event.target;
    if (target.tagName === "A" && target.getAttribute("href")) {
      const href = target.getAttribute("href");
      const route = routes.find((r) => matchRoute(r.path, href));
      if (route) {
        event.preventDefault();
        if (href === "") history.pushState(null, null, "/home");
        if (window.location.pathname !== href)
          history.pushState(null, null, href);
        handleRoute();
      }
    }
  });

  const toggle_mode = document.getElementById("toggle-mode");
  let darkMode = localStorage.getItem("darkMode");
  if (darkMode === "true") {
    toggle_mode.innerHTML = `<i class="bi bi-moon-fill"></i>`;
    document.documentElement.setAttribute("data-bs-theme", "dark");
  } else {
    toggle_mode.innerHTML = `<i class="bi bi-brightness-high-fill"></i>`;
    document.documentElement.setAttribute("data-bs-theme", "light");
  }

  toggle_mode.addEventListener("click", () => {
    if (darkMode === "true") {
      toggle_mode.innerHTML = `<i class="bi bi-brightness-high-fill"></i>`;
      darkMode = "false";
      document.documentElement.setAttribute("data-bs-theme", "light");
    } else {
      toggle_mode.innerHTML = `<i class="bi bi-moon-fill"></i>`;
      darkMode = "true";
      document.documentElement.setAttribute("data-bs-theme", "dark");
    }
    localStorage.setItem("darkMode", darkMode);
  });
});

function render_page(fetch_call, page = 1) {
  const pageDiv = document.createElement("div");

  function render_pagination(pagination, goToPage) {
    const paginationDiv = document.createElement("div");
    paginationDiv.className = "pagination justify-content-center";

    const paginationList = document.createElement("ul");
    paginationList.classList.add("pagination");

    // Previous page button
    if (pagination.has_previous) {
      const previousItem = createPaginationItem(
        goToPage,
        pagination.current_page - 1,
        "Previous"
      );
      paginationList.appendChild(previousItem);
    }

    // Page numbers
    for (let i = 1; i <= pagination.total_pages; i++) {
      const pageItem = createPaginationItem(
        goToPage,
        i,
        i.toString(),
        i === pagination.current_page
      );
      paginationList.appendChild(pageItem);
    }

    // Next page button
    if (pagination.has_next) {
      const nextItem = createPaginationItem(
        goToPage,
        pagination.current_page + 1,
        "Next"
      );
      paginationList.appendChild(nextItem);
    }

    paginationDiv.appendChild(paginationList);
    return paginationDiv;
  }

  function createPaginationItem(goToPage, pageNumber, label, isActive = false) {
    const listItem = document.createElement("li");
    listItem.classList.add("page-item");

    if (isActive) {
      listItem.classList.add("active");
    }

    const button = document.createElement("button");
    button.classList.add("page-link");
    button.textContent = label;

    button.addEventListener("click", (event) => {
      event.preventDefault();
      goToPage(pageNumber);
    });

    listItem.appendChild(button);
    return listItem;
  }

  fetch(`${fetch_call}/${page}`)
    .then((response) => response.json())
    .then((data) => {
      const posts = data.posts;
      const pagination = data.pagination;

      // Iterate over the posts
      posts.forEach((post) => {
        // Process each post
        pageDiv.appendChild(render_post(post));
      });

      // Access pagination information
      let currentPage = pagination.current_page;

      function goToPage(num) {
        if (num !== currentPage && num >= 1 && num <= pagination.total_pages) {
          currentPage = num;
          pageDiv.innerHTML = "";
          page = currentPage;
          pageDiv.appendChild(render_page(fetch_call, page));
        }
      }

      pageDiv.appendChild(render_pagination(pagination, goToPage));
    })
    .catch((error) => {
      console.error("Error:", error);
    });

  return pageDiv;
}

function render_post(post) {
  const postDiv = document.createElement("div");
  const postSender = document.createElement("a");
  const postBody = document.createElement("div");
  const postTimestamp = document.createElement("div");
  const postFooterRow = document.createElement("div");
  const postLikesCol = document.createElement("div");
  const postLikes = document.createElement("div");
  const postLikesText = document.createElement("div");
  const postEdit = document.createElement("div");
  const postEditErrorDiv = document.createElement("div");
  const postEditError = document.createElement("small");
  const postEditButton = document.createElement("button");

  postFooterRow.appendChild(postLikesCol);
  postFooterRow.appendChild(postEdit);
  postLikesCol.appendChild(postTimestamp);
  postLikesCol.appendChild(postLikes);
  postBody.className = "fs-5";
  postFooterRow.className = "row align-items-end mt-3";
  postLikesCol.className = "col";
  postEditError.className = "text-danger";
  postEditButton.innerText = "Edit";
  postEditButton.className = "mt-3 btn btn-secondary btn-sm";
  if (current_user === post.user) postEdit.appendChild(postEditButton);
  postEdit.className = "col d-flex justify-content-end";
  postLikes.className = "row g-2";
  postLikes.style.width = "fit-content";

  postTimestamp.className = "text-body-secondary";
  postLikesText.className = "col text-body-secondary d-flex align-items-center";

  // Create a new element
  const heartIcon = document.createElement("div");
  heartIcon.className = "col";
  heartIcon.id = "heart-icon";

  var is_liked = post.likes.some((username) => username === current_user);
  var likes_count = post.likes.length;
  postBody.innerHTML = `${post.body}`;

  // Set the inner HTML of the element to the heart icon markup
  heartIcon.innerHTML = `<i class="bi bi-heart"></i>`;
  if (is_liked) heartIcon.innerHTML = `<i class="bi bi-heart-fill"></i>`;
  heartIcon.style.color = "red";

  const csrftoken = getCookie("csrftoken");

  heartIcon.addEventListener("click", () => {
    if (!is_liked) {
      fetch(`/api/like/${post.id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken, // Include the CSRF token in the request headers
        },
      })
        .then((response) => {
          if (response.ok) return response.json();
          else
            throw new Error("Unable to like the post. " + response.statusText);
        })
        .then((data) => {
          heartIcon.innerHTML = `<i class="bi bi-heart-fill"></i>`;
          is_liked = true;
          likes_count += 1;
          postLikesText.innerHTML = `${likes_count}`;
          console.log(data.message);
        })
        .catch((error) => {
          // Handle any errors
          console.error("Error:", error);
        });
    } else {
      fetch(`/api/unlike/${post.id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken, // Include the CSRF token in the request headers
        },
      })
        .then((response) => {
          if (response.ok) return response.json();
          else
            throw new Error("Unable to like the post. " + response.statusText);
        })
        .then((data) => {
          // Handle the response data
          heartIcon.innerHTML = `<i class="bi bi-heart"></i>`;
          is_liked = false;
          likes_count -= 1;
          postLikesText.innerHTML = `${likes_count}`;
          console.log(data.message);
        })
        .catch((error) => {
          // Handle any errors
          console.error("Error:", error);
        });
    }
  });
  if (current_user === post.user) {
    postEditButton.addEventListener("click", () => {
      postEdit.innerHTML = "";
      const postEditConfirm = document.createElement("button");
      postEditConfirm.innerText = "Confirm";
      postEditConfirm.className = "btn btn-primary ms-1 btn-sm";
      const postEditCancel = document.createElement("button");
      postEditCancel.innerText = "Cancel";
      postEditCancel.className = "btn btn-secondary btn-sm";
      postEdit.appendChild(postEditCancel);
      postEdit.appendChild(postEditConfirm);

      const bodyHeight = postBody.offsetHeight;
      postBody.innerHTML = "";
      const postBodyEdit = document.createElement("TextArea");
      postBodyEdit.className = "form-control mb-3";
      postBodyEdit.style.height = `${bodyHeight}px`;
      postBodyEdit.name = "body";
      postBodyEdit.innerText = `${post.body}`;

      postBody.appendChild(postBodyEdit);

      postEditCancel.addEventListener("click", () => {
        postBody.innerHTML = `${post.body}`;
        postEdit.innerHTML = "";
        postEdit.appendChild(postEditButton);
      });
      postEditConfirm.addEventListener("click", () => {
        postBody.innerHTML = `${post.body}`;
        postEdit.innerHTML = "";
        postEdit.appendChild(postEditButton);

        fetch(`/api/posts/${post.id}/edit`, {
          method: "POST",
          body: JSON.stringify({
            body: postBodyEdit.value,
          }),
          headers: {
            "X-CSRFToken": csrftoken, // Include the CSRF token in the request headers
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.error) {
              // If the response has an error message, handle the error (e.g., show an error message)
              postEditError.innerText = data.error;
              console.error("Failed to edit post", data.error);
            } else {
              // If the response is successful, do something (e.g., show a success message)
              postEditError.innerText = "";
              post.body = postBodyEdit.value;
              postBody.innerHTML = postBodyEdit.value;
              console.log("Post edited successfully");
            }
          })
          .catch((error) => {
            console.error("An error occurred while editing the post:", error);
          });
      });
    });
  }

  postTimestamp.innerHTML = `${post.timestamp}`;
  postLikesText.innerHTML = `${likes_count}`;

  postDiv.className =
    "bg-primary-subtle rounded mb-3 py-3 px-4 text-primary-emphasis border border-3 border-primary-subtle shadow";

  postSender.innerHTML = `${post.user}`;
  postSender.href = `/profile/${post.user}`;
  postSender.style.textDecoration = "none";
  postSender.className = "fs-3 fw-semibold mb-3";
  postSender.addEventListener("click", (event) => {
    event.preventDefault();
    view_profile(post.user);
  });
  postEditErrorDiv.appendChild(postEditError);
  postLikes.appendChild(heartIcon);
  postLikes.appendChild(postLikesText);
  postDiv.appendChild(postSender);
  postDiv.appendChild(postBody);
  postDiv.appendChild(postEditErrorDiv);
  postDiv.appendChild(postFooterRow);
  return postDiv;
}

function render_new_post() {
  const newPost = document.createElement("div");
  const newPostForm = document.createElement("form");
  const newPostTitle = document.createElement("div");
  const newPostTextArea = document.createElement("textarea");
  const newPostFormErrorDiv = document.createElement("div");
  const newPostFormError = document.createElement("small");
  const newPostButton = document.createElement("button");
  newPostForm.method = "POST";
  newPostTitle.innerHTML = "New Post";
  newPostTitle.className = "fs-3 fw-semibold mb-3";
  newPostButton.innerText = "Post";
  newPostButton.className = "btn btn-primary mt-3";
  newPost.className =
    "bg-primary-subtle rounded mb-3 py-3 px-4 text-primary-emphasis border border-3 border-primary-subtle shadow";
  newPostTextArea.className = "form-control";
  newPostTextArea.name = "body";
  newPostFormError.className = "text-danger";
  newPost.appendChild(newPostTitle);
  newPostFormErrorDiv.appendChild(newPostFormError);
  newPostForm.appendChild(newPostTextArea);
  newPostForm.appendChild(newPostFormErrorDiv);
  newPostForm.appendChild(newPostButton);
  newPost.appendChild(newPostForm);

  // Get the CSRF token from the cookie
  const csrftoken = getCookie("csrftoken");

  // Add event listener to the form submit event
  newPostForm.addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    // Send form data to the server using fetch API
    fetch("/api/post", {
      method: "POST",
      body: JSON.stringify({
        body: newPostTextArea.value,
      }),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          // If the response has an error message, handle the error (e.g., show an error message)
          newPostFormError.innerText = data.error;
          console.error("Failed to create post", data.error);
        } else {
          // If the response is successful, do something (e.g., show a success message)
          view_feed("all");
          newPostFormError.innerText = "";
          console.log("Post created successfully");
        }
      })
      .catch((error) => {
        console.error("An error occurred while creating the post:", error);
      });
  });

  return newPost;
}

function view_feed(feed, username = null) {
  let feed_view;
  let url;

  if (feed === "all") {
    feed_view = document.querySelector("#home-posts");
    url = "/home";
  } else if (feed === "following") {
    feed_view = document.querySelector("#following-posts");
    url = "/following";
  } else if (feed === "profile") {
    feed_view = document.querySelector("#profile-posts");
    if (!username) username = current_user;
    url = `/profile/${username}`;
  }
  feed_view.innerHTML = "";

  if (feed === "all") {
    if (current_user) feed_view.appendChild(render_new_post());
    feed_view.appendChild(render_page(`/api/posts`));
  } else feed_view.appendChild(render_page(`/api${url}`));
}

function view_profile(username) {
  view_feed("profile", username);
  const profileFollowage = document.getElementById("profile-followage");
  const profileFollow = document.getElementById("profile-follow");
  profileFollow.innerHTML = "";
  const profileFollowButton = document.createElement("button");
  profileFollow.appendChild(profileFollowButton);
  const profileTitle = document.getElementById("profile-title");
  profileFollowButton.className = "btn btn-primary";
  profileFollowButton.style.display = "none";
  const csrftoken = getCookie("csrftoken");

  fetch(`/api/profile/${username}`)
    .then((response) => response.json())
    .then((data) => {
      profileTitle.innerHTML = `${username}'s profile`;
      profileFollowage.innerHTML = `Following: ${data.user.following} Followers: ${data.user.followers}`;
      if (!data.is_following) {
        profileFollowButton.innerText = "Follow";
      } else {
        profileFollowButton.innerText = "Unfollow";
      }

      if (username !== current_user && current_user) {
        profileFollowButton.style.display = "block";
        profileFollowButton.addEventListener("click", () => {
          if (!data.is_following) {
            fetch(`/api/follow/${username}`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken, // Include the CSRF token in the request headers
              },
            })
              .then((response) => response.json())
              .then((data) => {
                // Handle the response data
                view_profile(username);
                console.log(data.message);
              })
              .catch((error) => {
                // Handle any errors
                console.error("Error:", error);
              });
          } else {
            fetch(`/api/unfollow/${username}`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken, // Include the CSRF token in the request headers
              },
            })
              .then((response) => response.json())
              .then((data) => {
                // Handle the response data
                view_profile(username);
                console.log(data.message);
              })
              .catch((error) => {
                // Handle any errors
                console.error("Error:", error);
              });
          }
        });
      }
    });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
